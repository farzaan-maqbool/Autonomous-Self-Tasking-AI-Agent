"""Flask web application for the Autonomous Self-Tasking AI Agent."""

from flask import Flask, jsonify, render_template, request

try:
    from .complexity import TaskComplexityAnalyzer
    from .evaluator import EvaluationModule
    from .executor import Executor
    from .interpreter import GoalInterpreter
    from .memory import MemoryModule
    from .planner import TaskPlanner
    from .resource_generator import ResourceGenerator
    from .subject_detector import SubjectDetector
except ImportError:  # pragma: no cover - fallback for direct script execution
    from complexity import TaskComplexityAnalyzer
    from evaluator import EvaluationModule
    from executor import Executor
    from interpreter import GoalInterpreter
    from memory import MemoryModule
    from planner import TaskPlanner
    from resource_generator import ResourceGenerator
    from subject_detector import SubjectDetector


app = Flask(__name__)


class AutonomousAgent:
    """Coordinate the modules and return a simple beginner-friendly result."""

    def __init__(self):
        self.interpreter = GoalInterpreter()
        self.planner = TaskPlanner()
        self.executor = Executor()
        self.evaluator = EvaluationModule()
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.subject_detector = SubjectDetector()
        self.resource_generator = ResourceGenerator()

    def run(self, goal, mode="assistant"):
        """Run the agent in assistant mode or system control mode."""
        if mode == "system":
            system_command = self.interpreter.detect_system_command(goal)
            if system_command:
                if system_command["action"] == "blocked":
                    return self._build_system_blocked_response(goal, system_command["message"])

                return self._run_system_mode(goal, system_command)

        return self._run_assistant_mode(goal)

    def _run_assistant_mode(self, goal):
        """Run the normal assistant planning flow."""
        interpretation = self.interpreter.interpret(goal)
        subject_analysis = self.subject_detector.detect(goal)
        interpretation["subject_analysis"] = subject_analysis
        tasks = self.planner.plan_tasks(interpretation)
        memory = MemoryModule()
        memory.initialize(tasks)

        current_index = 0
        while current_index < len(tasks):
            current_task = tasks[current_index]

            memory.add_log(
                phase="think",
                step=current_task["step"],
                message=f"Thinking about Step {current_task['step']}: {current_task['title']}",
                status=current_task["status"],
                attempt=current_task["attempts"] + 1,
            )

            memory.add_log(
                phase="plan",
                step=current_task["step"],
                message=current_task["description"],
                status=current_task["status"],
                attempt=current_task["attempts"] + 1,
            )

            execution_result = self.executor.execute_task(current_task)
            memory.record_execution(current_task, execution_result)

            memory.add_log(
                phase="act",
                step=current_task["step"],
                message=execution_result["result"],
                status=execution_result["status"],
                attempt=execution_result["attempt"],
            )

            memory.add_log(
                phase="observe",
                step=current_task["step"],
                message=execution_result["observation"],
                status=execution_result["status"],
                attempt=execution_result["attempt"],
            )

            evaluation = self.evaluator.evaluate(tasks)
            memory.add_log(
                phase="evaluate",
                step=current_task["step"],
                message=evaluation["message"],
                status=current_task["status"],
                attempt=current_task["attempts"],
            )

            if current_task["status"] == "failed":
                self.evaluator.adjust_task(current_task)
                memory.add_log(
                    phase="replan",
                    step=current_task["step"],
                    message=(
                        f"Step {current_task['step']} was adjusted and will be retried "
                        "with a refined check."
                    ),
                    status="retrying",
                    attempt=current_task["attempts"],
                )
                continue

            current_index += 1

        final_evaluation = self.evaluator.evaluate(tasks)
        breakdown = self._build_breakdown(tasks)
        complexity = self.complexity_analyzer.analyze(interpretation, tasks)
        resources = self.resource_generator.generate(
            interpretation=interpretation,
            subject_analysis=subject_analysis,
            tasks=tasks,
            breakdown=breakdown,
            complexity=complexity,
        )
        final_answer = resources["report"]

        return {
            "goal": interpretation["original_goal"],
            "subject_analysis": subject_analysis,
            "complexity": complexity,
            "resources": resources,
            "breakdown": breakdown,
            "final_answer": final_answer,
            "mode_used": "assistant",
            "status_message": "Assistant response ready.",
        }

    def _run_system_mode(self, goal, system_command):
        """Run a real system action for a safe predefined command."""
        execution_result = self.executor.execute_system_task(system_command)
        breakdown = self._build_system_breakdown(system_command)

        status_message = "Executing system command..."
        if execution_result["status"] == "completed":
            status_message = execution_result["result"]
        elif execution_result["status"] == "blocked":
            status_message = "System command blocked."
        elif execution_result["status"] == "failed":
            status_message = "System command failed."

        return {
            "goal": goal,
            "complexity": self.complexity_analyzer.analyze_system(system_command),
            "breakdown": breakdown,
            "final_answer": self._build_system_final_answer(system_command, execution_result),
            "mode_used": "system",
            "status_message": status_message,
        }

    def _build_breakdown(self, tasks):
        """Create a detailed 6-10 step breakdown for display."""
        step_candidates = []

        for task in tasks:
            details = task.get("details") or []
            for detail in details:
                cleaned_detail = self._format_breakdown_detail(task, detail)
                if cleaned_detail:
                    step_candidates.append(cleaned_detail)

            deliverable = task.get("deliverable", "").strip().rstrip(".")
            if deliverable:
                step_candidates.append(f"Complete the deliverable: {deliverable}")

        breakdown = []
        seen = set()
        for detail in step_candidates:
            normalized = detail.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            breakdown.append(detail)
            if len(breakdown) == 8:
                break

        if len(breakdown) < 6:
            fallback_steps = [
                "Identify the exact topics, parts, or deliverables involved in the goal",
                "Break the work into smaller sections that can be handled one by one",
                "Choose the tools, resources, or references needed before starting",
                "Create a structured plan with a clear order of execution",
                "Complete the important tasks first before adding extra improvements",
                "Review the result, fix weak points, and make the final version more polished",
            ]
            for fallback in fallback_steps:
                if fallback.lower() not in seen:
                    breakdown.append(fallback)
                if len(breakdown) == 8:
                    break

        return [f"Step {index}: {item}." for index, item in enumerate(breakdown, start=1)]

    def _build_system_breakdown(self, system_command):
        """Create a more detailed breakdown for a system control task."""
        if system_command["action"] == "open_application":
            display_name = system_command["display_name"]
            return [
                "Step 1: Detect that the request is asking to open an application.",
                f"Step 2: Extract the application name as {display_name}.",
                f"Step 3: Confirm that {display_name} is in the safe allowed list.",
                "Step 4: Build the Windows command needed to launch the app.",
                f"Step 5: Execute the launch command for {display_name}.",
                "Step 6: Return a success or failure message to the user.",
            ]

        if system_command["action"] == "set_alarm":
            time_text = system_command.get("time_text", f"{system_command.get('seconds', 0)} seconds")
            return [
                "Step 1: Detect that the request is asking to set an alarm.",
                f"Step 2: Extract the alarm time as {time_text}.",
                "Step 3: Convert the request into a simple number of seconds.",
                "Step 4: Start a background alarm thread so the UI stays responsive.",
                "Step 5: Wait until the alarm duration is complete.",
                "Step 6: Play a simple sound to notify the user.",
            ]

        return [
            "Step 1: Read the request.",
            "Step 2: Detect whether it matches a safe system action.",
            "Step 3: Check it against the safe command list.",
            "Step 4: Block the request if it is not clearly allowed.",
            "Step 5: Execute only if it is safe.",
            "Step 6: Return a clear result message to the user.",
        ]

    def _build_final_answer(self, interpretation, tasks, breakdown, evaluation):
        """Create a longer, more helpful assistant-style explanation."""
        goal_type = tasks[0].get("goal_type", "general") if tasks else "general"
        suggested_plan = "\n".join(breakdown[:5])

        if goal_type == "study":
            approach = (
                "Here's how you can approach this:\n"
                "Treat this as a structured study target instead of trying to learn everything at once. "
                "Start by identifying the most important topics, then match each topic with the right study "
                "method such as note review, active recall, and practice questions. This works better because "
                "it gives you a clear sequence and makes revision easier."
            )
            tips = (
                "Tips:\n"
                "- Study in short focused sessions instead of long passive reading sessions.\n"
                "- End each session with a self-test so you know what still needs revision.\n"
                "- Keep one short summary sheet for formulas, definitions, or difficult points."
            )
        elif goal_type == "coding":
            approach = (
                "Here's how you can approach this:\n"
                "Handle this like a small real project. First decide the technologies and tools, then build "
                "the core functionality in stages instead of trying to finish everything in one go. After the main "
                "flow works, improve the interface, add error handling, and test the important cases carefully."
            )
            tips = (
                "Tips:\n"
                "- Build the simplest working version first before adding extra features.\n"
                "- Keep your files and folders organized so changes stay easy to manage.\n"
                "- Test after every major feature so bugs do not pile up at the end."
            )
        elif goal_type == "writing":
            approach = (
                "Here's how you can approach this:\n"
                "Write it in a structured way so the final piece feels clear and complete. Begin with a "
                "simple outline, collect the key points you want to include, and then draft each section with one "
                "main idea at a time. After the draft is ready, improve the flow, examples, and wording."
            )
            tips = (
                "Tips:\n"
                "- Use short, clear sentences before trying to make the writing sound advanced.\n"
                "- Keep each paragraph focused on one idea.\n"
                "- Edit once for content and once for grammar instead of fixing everything together."
            )
        elif goal_type == "research":
            approach = (
                "Here's how you can approach this:\n"
                "Treat this as a research problem that needs clear questions, reliable sources, and organized "
                "findings. Start by deciding the main angles to explore, then gather information from trusted web "
                "sources, papers, or reports. After that, compare the findings by theme so the final summary is more "
                "useful than just a list of sources."
            )
            tips = (
                "Tips:\n"
                "- Prefer recent and trustworthy sources when the topic changes quickly.\n"
                "- Group notes by theme so repeated ideas stand out.\n"
                "- Highlight only the strongest findings instead of collecting too much weak information."
            )
        else:
            approach = (
                "Here's how you can approach this:\n"
                "Take the goal step by step and turn it into a clear action plan. Start by identifying what needs "
                "to be done, what resources are required, and which actions will give the fastest progress. Then carry "
                "out the work in order and finish with a review so the result is actually useful."
            )
            tips = (
                "Tips:\n"
                "- Do the highest-impact task first so the rest becomes easier.\n"
                "- Keep the plan practical and avoid adding unnecessary extra work.\n"
                "- Review the final result against the original goal before stopping."
            )

        suggested = f"Suggested plan:\n{suggested_plan}"
        message = f"{approach}\n\n{suggested}\n\n{tips}"
        if not evaluation["all_completed"]:
            message += (
                "\n\nA few parts may still need another pass, but this plan gives you a strong and practical starting point."
            )

        return message

    def _build_system_final_answer(self, system_command, execution_result):
        """Create a longer final answer for system control tasks."""
        if execution_result["status"] == "completed":
            if system_command["action"] == "open_application":
                return (
                    "Here's how you can approach this:\n"
                    f"The request was recognized as a safe application launch for {system_command['display_name']}. "
                    "The agent checked the app name against the allowed list and then sent the launch command to Windows.\n\n"
                    f"Suggested plan:\n"
                    f"Step 1: Detect the application request.\n"
                    f"Step 2: Confirm that {system_command['display_name']} is allowed.\n"
                    f"Step 3: Execute the launch command and report the result.\n\n"
                    "Tips:\n"
                    "- Use only the supported app names in System Control Mode.\n"
                    "- Keep system commands short and clear.\n"
                    "- If an app does not open, check whether it is installed on the computer."
                )

            if system_command["action"] == "set_alarm":
                return (
                    "Here's how you can approach this:\n"
                    f"The alarm was recognized and scheduled for {system_command['time_text']}. "
                    "The agent converts the request into time, starts a background wait process, and then plays a simple sound when the time is reached.\n\n"
                    f"Suggested plan:\n"
                    "Step 1: Detect the alarm request.\n"
                    f"Step 2: Convert the request into {system_command['time_text']}.\n"
                    "Step 3: Start the background alarm and wait for the reminder.\n\n"
                    "Tips:\n"
                    "- Use formats like '10 seconds' or '7:30 am' for better detection.\n"
                    "- Keep alarm requests simple and specific.\n"
                    "- Use short test durations first while demonstrating the project."
                )

        return (
            "Here's how you can approach this:\n"
            f"{execution_result['result']}\n\n"
            "Suggested plan:\n"
            "Step 1: Use a supported application name or a simple alarm request.\n"
            "Step 2: Keep the command short and direct.\n"
            "Step 3: Try the request again in System Control Mode.\n\n"
            "Tips:\n"
            "- Only the predefined safe commands are allowed.\n"
            "- Use Notepad, Chrome, Microsoft Word, or a simple alarm.\n"
            "- Avoid unknown or unsupported system actions."
        )

    def _build_system_blocked_response(self, goal, message):
        """Return a safe response when a system command is not allowed."""
        return {
            "goal": goal,
            "complexity": {
                "difficulty": "Easy",
                "estimated_time": "Immediate",
                "resources": ["Safe command list", "Clear app name or alarm time"],
                "dependencies": ["Read command", "Validate safety", "Block unsupported action"],
            },
            "breakdown": [
                "Step 1: Read the system request.",
                "Step 2: Compare it with the safe command list.",
                "Step 3: Block it if it is not allowed or not understood clearly.",
            ],
            "final_answer": f"{message} Please use Notepad, Chrome, Microsoft Word, or a simple alarm request.",
            "mode_used": "system",
            "status_message": "System command blocked.",
        }

    def _format_breakdown_detail(self, task, detail):
        """Turn planner details into clearer, action-oriented breakdown steps."""
        cleaned_detail = detail.strip().rstrip(".")
        if not cleaned_detail:
            return ""

        lower_title = task.get("title", "").lower()
        lower_detail = cleaned_detail.lower()

        if lower_detail.startswith(("day ", "step ", "use ", "apply ", "end ", "start ", "finish ", "run ", "test ", "check ", "call ", "open ", "write ", "read ", "group ", "note ", "mark ", "close ", "cover ", "focus ", "practice ", "solve ", "revise ", "attempt ", "keep ", "collect ", "compare ", "create ", "prepare ", "identify ", "list ", "separate ")):
            return cleaned_detail

        if "technologies" in lower_title:
            return f"Choose {self._sentence_case_tail(cleaned_detail)}"
        if "tools and libraries" in lower_title:
            return f"Prepare {self._sentence_case_tail(cleaned_detail)}"
        if "resources" in lower_title or "sources" in lower_title:
            return f"Use {self._sentence_case_tail(cleaned_detail)}"
        if "study topics" in lower_title:
            return f"Cover {self._sentence_case_tail(cleaned_detail)}"
        if "key points" in lower_title:
            return f"List {self._sentence_case_tail(cleaned_detail)}"
        if "structure" in lower_title:
            return f"Create {self._sentence_case_tail(cleaned_detail)}"
        if "research angles" in lower_title:
            return f"Explore {self._sentence_case_tail(cleaned_detail)}"

        return cleaned_detail

    def _sentence_case_tail(self, text):
        """Lowercase the first letter when helpful, but preserve acronyms."""
        if len(text) > 1 and text[:2].isupper():
            return text
        return text[:1].lower() + text[1:]


agent = AutonomousAgent()


@app.route("/")
def index():
    """Render the main web interface."""
    return render_template("index.html")


@app.route("/run-agent", methods=["POST"])
def run_agent():
    """Receive a goal from the frontend and return the agent result."""
    data = request.get_json(silent=True) or {}
    goal = (data.get("goal") or "").strip()
    mode = (data.get("mode") or "assistant").strip().lower()

    if not goal:
        return jsonify({"error": "Please enter a goal before running the agent."}), 400

    if mode not in {"assistant", "system"}:
        return jsonify({"error": "Invalid mode selected."}), 400

    result = agent.run(goal, mode=mode)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
