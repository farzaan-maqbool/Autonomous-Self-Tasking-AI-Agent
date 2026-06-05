"""Task planning module.

This module analyzes the user's goal, detects the goal type, and creates
practical domain-specific steps that can be displayed clearly in the UI.
"""

import re


class TaskPlanner:
    """Create dynamic subtasks for a given interpreted goal."""

    def plan_tasks(self, interpretation):
        """Build an ordered task plan from the interpreted goal."""
        goal = interpretation["original_goal"]
        keywords = interpretation["keywords"]
        intent = interpretation["intent"]
        subject_analysis = interpretation.get("subject_analysis")

        goal_type = self._detect_goal_type(goal, keywords, intent)
        subject = subject_analysis["subject"] if subject_analysis else self._extract_subject(goal, goal_type)

        if goal_type == "study":
            tasks = self._build_study_tasks(subject, keywords, goal, subject_analysis)
        elif goal_type == "coding":
            tasks = self._build_coding_tasks(subject, keywords, goal)
        elif goal_type == "writing":
            tasks = self._build_writing_tasks(subject, keywords, goal)
        elif goal_type == "research":
            tasks = self._build_research_tasks(subject, keywords, goal)
        else:
            tasks = self._build_general_tasks(subject, keywords, goal)

        for index, task in enumerate(tasks, start=1):
            task["step"] = index
            task["goal_type"] = goal_type

        return tasks

    def _detect_goal_type(self, goal, keywords, intent):
        """Detect the goal type using simple keyword rules."""
        lowered_goal = goal.lower()
        keyword_set = set(keywords)

        study_terms = {
            "study", "learn", "exam", "revision", "revise", "subject",
            "chapter", "syllabus", "course", "prepare", "preparation",
        }
        coding_terms = {
            "build", "code", "coding", "develop", "project", "app", "application", "website",
            "web", "software", "system", "api", "backend", "frontend",
        }
        writing_terms = {
            "write", "essay", "report", "article", "blog", "draft",
            "speech", "letter", "statement", "documentation",
        }
        research_terms = {
            "research", "analyze", "analysis", "investigate", "survey",
            "compare", "study trends", "findings", "paper",
        }

        if intent in {"build", "improve"} or self._contains_any(lowered_goal, keyword_set, coding_terms):
            return "coding"
        if intent == "write" or self._contains_any(lowered_goal, keyword_set, writing_terms):
            return "writing"
        if self._contains_any(lowered_goal, keyword_set, study_terms):
            return "study"
        if intent == "research" or self._contains_any(lowered_goal, keyword_set, research_terms):
            return "research"
        return "general"

    def _build_study_tasks(self, subject, keywords, goal, subject_analysis=None):
        """Create a study-focused task plan."""
        topics = subject_analysis["topics"] if subject_analysis else self._study_topics(subject, keywords, goal)
        methods = self._study_methods(goal)
        resources = self._study_resources(subject, keywords)
        day_plan = self._study_day_plan(subject, topics)

        return [
            self._make_task(
                title=f"Study the major topics in {subject}",
                description=f"Focus the study effort on the highest-value areas of {subject}.",
                task_type="planning",
                section="What to Study",
                details=[self._topic_to_study_action(topic, subject_analysis) for topic in topics],
                deliverable="A focused topic list for the subject.",
            ),
            self._make_task(
                title=f"Choose how to study {subject}",
                description=f"Use active learning methods that fit the goal: {goal}.",
                task_type="analysis",
                section="How to Study",
                details=methods,
                deliverable="A practical method for daily study sessions.",
            ),
            self._make_task(
                title=f"Pick strong resources for {subject}",
                description="Use a mix of notes, explanations, and practice material.",
                task_type="research",
                section="Where to Study",
                details=resources,
                deliverable="A short resource stack for studying effectively.",
            ),
            self._make_task(
                title=f"Create a day-wise study plan for {subject}",
                description="Distribute topics across days so revision and practice are built in.",
                task_type="planning",
                section="Study Plan",
                details=day_plan,
                deliverable="A day-wise study schedule.",
            ),
            self._make_task(
                title=f"Check retention for {subject}",
                description="Test understanding and fix weak areas before finishing the plan.",
                task_type="review",
                section="Progress Check",
                details=[
                    "Solve a short self-test or 10 practice questions.",
                    "Mark topics that still feel weak after the first review.",
                    "Revise mistakes using flashcards, quick notes, or one-page summaries.",
                ],
                deliverable="A revision list based on weak points.",
            ),
        ]

    def _build_coding_tasks(self, subject, keywords, goal):
        """Create a coding or build-focused task plan."""
        technologies = self._coding_technologies(subject, keywords, goal)
        build_steps = self._coding_build_steps(subject, keywords)
        tools = self._coding_tools(subject, keywords)
        testing_steps = self._coding_testing_steps(subject, keywords)

        return [
            self._make_task(
                title=f"Select the required technologies for {subject}",
                description="Choose the stack that matches the type of software requested.",
                task_type="planning",
                section="Required Technologies",
                details=technologies,
                deliverable="A suitable project stack.",
            ),
            self._make_task(
                title=f"Build {subject} in implementation stages",
                description="Move from setup to working features in a clear order.",
                task_type="implementation",
                section="Steps to Build",
                details=build_steps,
                deliverable="An implementation sequence from setup to final integration.",
            ),
            self._make_task(
                title=f"Prepare tools and libraries for {subject}",
                description="List the supporting tools that make development faster and cleaner.",
                task_type="implementation",
                section="Tools and Libraries",
                details=tools,
                deliverable="A practical toolkit for development.",
            ),
            self._make_task(
                title=f"Test {subject} before delivery",
                description="Check the important flows, edge cases, and usability before completion.",
                task_type="review",
                section="Testing Steps",
                details=testing_steps,
                deliverable="A test checklist for the project.",
            ),
        ]

    def _build_writing_tasks(self, subject, keywords, goal):
        """Create a writing-focused task plan."""
        structure = self._writing_structure(subject)
        key_points = self._writing_key_points(subject, keywords, goal)
        writing_tips = self._writing_tips(goal)

        return [
            self._make_task(
                title=f"Create the structure for the {subject} piece",
                description="Build the writing around a clean flow from opening to closing.",
                task_type="planning",
                section="Structure",
                details=structure,
                deliverable="An introduction-body-conclusion outline.",
            ),
            self._make_task(
                title=f"Collect key points for {subject}",
                description="Identify the main ideas that each section needs to cover.",
                task_type="research",
                section="Key Points",
                details=key_points,
                deliverable="A list of ideas, examples, or evidence to include.",
            ),
            self._make_task(
                title=f"Draft the {subject} content clearly",
                description="Turn the outline into readable paragraphs with clear transitions.",
                task_type="writing",
                section="Drafting",
                details=[
                    "Write the introduction first to define the topic and the main angle.",
                    "Expand each body section with one idea, explanation, and example.",
                    "Close with a conclusion that reinforces the main message without repeating every line.",
                ],
                deliverable="A first full draft.",
            ),
            self._make_task(
                title=f"Refine the writing quality for {subject}",
                description="Improve clarity, polish, and presentation before submitting.",
                task_type="review",
                section="Writing Tips",
                details=writing_tips,
                deliverable="An edited final version with better readability.",
            ),
        ]

    def _build_research_tasks(self, subject, keywords, goal):
        """Create a research-focused task plan."""
        topics = self._research_topics(subject, keywords, goal)
        sources = self._research_sources(subject, keywords)
        summary_plan = self._research_summary_plan(subject)

        return [
            self._make_task(
                title=f"Define the research angles for {subject}",
                description="Break the topic into a few strong questions worth exploring.",
                task_type="planning",
                section="Topics to Explore",
                details=topics,
                deliverable="A focused set of research questions or themes.",
            ),
            self._make_task(
                title=f"Collect trustworthy sources for {subject}",
                description="Use both quick web references and stronger academic material where possible.",
                task_type="research",
                section="Sources",
                details=sources,
                deliverable="A shortlist of reliable places to gather information.",
            ),
            self._make_task(
                title=f"Compare findings for {subject}",
                description="Look for patterns, disagreements, and repeated insights across sources.",
                task_type="analysis",
                section="Analysis",
                details=[
                    "Group findings by theme instead of source so repeated ideas stand out.",
                    "Note where two sources disagree and what evidence each one uses.",
                    "Mark insights that are recent, measurable, or directly useful for the goal.",
                ],
                deliverable="A comparison of the strongest findings.",
            ),
            self._make_task(
                title=f"Prepare the research summary for {subject}",
                description="Convert the findings into a short, structured summary plan.",
                task_type="review",
                section="Summary Plan",
                details=summary_plan,
                deliverable="A final summary structure for presenting the research.",
            ),
        ]

    def _build_general_tasks(self, subject, keywords, goal):
        """Create a practical action plan for goals that do not fit a specialist domain."""
        action_steps = self._general_action_steps(subject, keywords, goal)

        return [
            self._make_task(
                title=f"Identify the main work items for {subject}",
                description="Split the goal into concrete pieces that can be acted on directly.",
                task_type="planning",
                section="Action Items",
                details=action_steps[:3],
                deliverable="A short list of concrete work items.",
            ),
            self._make_task(
                title=f"Execute the core actions for {subject}",
                description="Handle the work in the order that removes the biggest blockers first.",
                task_type="implementation",
                section="Execution Path",
                details=action_steps[3:6],
                deliverable="A step-by-step execution path.",
            ),
            self._make_task(
                title=f"Review the result for {subject}",
                description="Confirm that the outcome is usable, complete, and aligned with the goal.",
                task_type="review",
                section="Quality Check",
                details=action_steps[6:],
                deliverable="A final quality checklist.",
            ),
        ]

    def _study_topics(self, subject, keywords, goal):
        """Suggest study topics from the goal context."""
        topics = [
            f"Core concepts and definitions related to {subject}.",
            f"Important subtopics, frameworks, or formulas inside {subject}.",
            f"Worked examples or practice problems for {subject}.",
        ]

        lowered_goal = goal.lower()
        if "exam" in lowered_goal or "test" in lowered_goal:
            topics.append(f"Previous-year questions or likely exam-style questions for {subject}.")
        if "interview" in lowered_goal:
            topics.append(f"Common interview questions and concise answers for {subject}.")

        return topics

    def _study_methods(self, goal):
        """Suggest how the user should study."""
        methods = [
            "Use 45-60 minute focused sessions with a 10 minute break after each session.",
            "Apply active recall by closing notes and explaining the topic in your own words.",
            "End each session with 5-10 practice questions or a quick self-quiz.",
        ]

        lowered_goal = goal.lower()
        if "exam" in lowered_goal:
            methods.append("Keep the last session of the day for timed revision and weak-topic review.")
        if "learn" in lowered_goal or "understand" in lowered_goal:
            methods.append("After each topic, write a 3-line summary so the concept is easier to revise later.")

        return methods

    def _study_resources(self, subject, keywords):
        """Suggest resources for studying."""
        resources = [
            f"Class notes or textbook chapters for {subject}.",
            f"Short concept videos or recorded lectures that explain {subject} visually.",
            f"Practice sheets, question banks, or quizzes related to {subject}.",
        ]

        if any(keyword in keywords for keyword in ["python", "java", "coding", "programming", "web"]):
            resources.append("Official documentation and coding practice platforms for hands-on learning.")

        return resources

    def _study_day_plan(self, subject, topics):
        """Create a day-wise study plan."""
        compact_topics = [topic.replace("Study ", "").rstrip(".") for topic in topics[:4]]

        day_plan = [
            f"Day 1: Cover {compact_topics[0]} and prepare short notes.",
            f"Day 2: Focus on {compact_topics[1]} with concept revision.",
            f"Day 3: Practice {compact_topics[2]} and note mistakes.",
            "Day 4: Revise all previous topics and test yourself under time limits.",
        ]

        if len(compact_topics) > 3:
            day_plan[3] = (
                f"Day 4: Cover {compact_topics[3]}, then revise the earlier topics with a short test."
            )
            day_plan.append(
                "Day 5: Attempt a full revision session and fix weak areas from mistakes."
            )

        return day_plan

    def _topic_to_study_action(self, topic, subject_analysis):
        """Convert a topic into a specific study action."""
        if not subject_analysis:
            return f"Study {topic}."

        topic_tasks = subject_analysis.get("topicTasks", {}).get(topic, [])
        if topic_tasks:
            return f"{topic}: {', '.join(topic_tasks[:3])}."

        return f"Study {topic}."

    def _coding_technologies(self, subject, keywords, goal):
        """Suggest a suitable tech stack."""
        technologies = []
        lowered_goal = goal.lower()

        if any(word in keywords for word in ["web", "website", "frontend", "ui"]):
            technologies.append("HTML, CSS, and JavaScript for the user interface.")
        if any(word in keywords for word in ["backend", "server", "api", "automation", "logic"]):
            technologies.append("Python with Flask or a similar lightweight backend framework.")
        if any(word in keywords for word in ["data", "database", "login", "storage"]):
            technologies.append("SQLite or another simple database layer for storing project data.")
        if "mobile" in lowered_goal:
            technologies.append("A mobile-friendly layout or cross-platform framework if the goal targets phones.")

        if not technologies:
            technologies.extend([
                "A primary programming language that fits the goal, such as Python or JavaScript.",
                "A lightweight framework or standard library tools to keep the project manageable.",
            ])

        technologies.append("Git for version control and safe iteration during development.")
        return technologies

    def _coding_build_steps(self, subject, keywords):
        """Suggest practical build stages."""
        build_steps = [
            f"Set up the project folder, basic file structure, and configuration for {subject}.",
            "Implement the main logic or core feature before adding optional extras.",
            "Connect the user-facing part to the backend or internal workflow.",
            "Refine the interface, error handling, and final behavior after the main flow works.",
        ]

        if any(keyword in keywords for keyword in ["api", "backend"]):
            build_steps.insert(2, "Create the main routes, request handling, and response structure.")

        return build_steps

    def _coding_tools(self, subject, keywords):
        """Suggest development tools and libraries."""
        tools = [
            "A code editor such as VS Code for faster navigation and debugging.",
            "Git and GitHub for version tracking and backup.",
        ]

        if any(keyword in keywords for keyword in ["python", "flask", "backend", "automation"]):
            tools.append("A virtual environment plus project dependencies managed through pip.")
        if any(keyword in keywords for keyword in ["web", "frontend", "ui", "website"]):
            tools.append("Browser developer tools for layout checks, console logs, and network inspection.")
        if any(keyword in keywords for keyword in ["test", "testing", "quality"]):
            tools.append("A simple testing library such as pytest or built-in assertions for core flows.")

        return tools

    def _coding_testing_steps(self, subject, keywords):
        """Suggest testing steps for a coding goal."""
        testing_steps = [
            "Run the project locally and confirm the main user flow works from start to finish.",
            "Test incorrect input, missing fields, or invalid actions to confirm error handling.",
            "Check whether outputs, stored data, or visible UI states update correctly after each action.",
        ]

        if any(keyword in keywords for keyword in ["web", "ui", "frontend", "website"]):
            testing_steps.append("Open the interface on desktop and mobile widths to confirm the layout remains usable.")
        if any(keyword in keywords for keyword in ["api", "backend", "server"]):
            testing_steps.append("Call the main endpoints with sample input and confirm the JSON responses are valid.")

        return testing_steps

    def _writing_structure(self, subject):
        """Suggest the structure for a writing task."""
        return [
            f"Introduction: define the topic of {subject} and state the main idea.",
            "Body Paragraph 1: explain the first major point with an example or evidence.",
            "Body Paragraph 2: expand the argument with another perspective, fact, or case.",
            "Conclusion: restate the main message and close with a strong final sentence.",
        ]

    def _writing_key_points(self, subject, keywords, goal):
        """Suggest key points for the writing content."""
        points = [
            f"The main purpose or argument behind {subject}.",
            f"Two or three supporting points that make {subject} convincing or informative.",
            "A real example, statistic, quote, or case study that strengthens the content.",
        ]

        lowered_goal = goal.lower()
        if "report" in lowered_goal:
            points.append("A short findings or observations section supported by facts.")
        if "essay" in lowered_goal:
            points.append("A clear opinion or thesis statement that guides the entire piece.")

        return points

    def _writing_tips(self, goal):
        """Suggest writing tips for refinement."""
        tips = [
            "Keep paragraphs focused on one main idea instead of mixing too many points together.",
            "Use simple transition words so the content flows naturally between sections.",
            "Replace vague statements with examples, facts, or short explanations.",
            "Read the draft once for grammar and once for clarity instead of trying to fix everything at the same time.",
        ]

        if "report" in goal.lower():
            tips.append("Use headings, short sentences, and direct wording so the report feels professional.")

        return tips

    def _research_topics(self, subject, keywords, goal):
        """Suggest angles for research."""
        topics = [
            f"Background and current state of {subject}.",
            f"Key trends, challenges, or debates related to {subject}.",
            f"Recent examples, case studies, or measurable outcomes connected to {subject}.",
        ]

        lowered_goal = goal.lower()
        if "compare" in lowered_goal:
            topics.append(f"Comparison criteria and trade-offs between the main options inside {subject}.")
        if "impact" in lowered_goal:
            topics.append(f"Short-term and long-term impact of {subject}.")

        return topics

    def _research_sources(self, subject, keywords):
        """Suggest research sources."""
        return [
            f"Reliable web articles, official websites, and industry blogs about {subject}.",
            f"Research papers, Google Scholar results, or academic databases for {subject}.",
            "Reports, whitepapers, or government and institutional publications when available.",
        ]

    def _research_summary_plan(self, subject):
        """Suggest a summary plan for research."""
        return [
            "Open with the research objective and the main question being answered.",
            "Group findings into 2-3 themes instead of listing one source after another.",
            "Close with the strongest insights, gaps, and next questions worth exploring.",
        ]

    def _general_action_steps(self, subject, keywords, goal):
        """Suggest logical action steps for a general goal."""
        goal_phrase = self._short_goal_phrase(goal)
        return [
            f"List the concrete outcome expected from {goal_phrase}.",
            f"Identify the main inputs, materials, or information needed for {subject}.",
            "Separate must-do actions from optional improvements so the work stays focused.",
            "Start with the highest-impact action that makes the rest of the work easier.",
            "Finish the remaining tasks in an order that avoids rework and confusion.",
            "Capture the result in a usable form such as notes, a checklist, or a draft output.",
            "Check whether the outcome solves the original need instead of only completing activity.",
            "Fix the weakest part before calling the task complete.",
        ]

    def _extract_subject(self, goal, goal_type):
        """Extract a readable subject phrase from the goal."""
        cleaned_goal = re.sub(r"[^A-Za-z0-9\s\-]", " ", goal).lower()
        words = cleaned_goal.split()
        removable = {
            "build", "create", "develop", "make", "study", "learn", "write",
            "research", "analyze", "investigate", "plan", "prepare", "improve",
            "design", "organize", "essay", "report", "article", "draft",
            "paper", "exam", "test", "assignment", "for", "about", "on",
            "a", "an", "the", "my", "me", "simple", "mini", "project",
        }

        subject_words = [word for word in words if word not in removable]
        if not subject_words:
            fallback = {
                "study": "the study target",
                "coding": "the software solution",
                "writing": "the writing task",
                "research": "the research topic",
                "general": "the main goal",
            }
            return fallback[goal_type]

        subject = " ".join(subject_words[:6]).strip()
        return subject

    def _short_goal_phrase(self, goal):
        """Create a short phrase from the original goal."""
        compact = re.sub(r"\s+", " ", goal.strip())
        if len(compact) <= 60:
            return compact
        return f"{compact[:57]}..."

    def _contains_any(self, lowered_goal, keyword_set, terms):
        """Check whether any term appears in the goal text or keyword list."""
        goal_tokens = set(re.findall(r"[a-z0-9]+", lowered_goal))
        lowered_keywords = {keyword.lower() for keyword in keyword_set}

        for term in terms:
            lowered_term = term.lower()
            if " " in lowered_term:
                if lowered_term in lowered_goal:
                    return True
            elif lowered_term in goal_tokens or lowered_term in lowered_keywords:
                return True

        return False

    def _make_task(self, title, description, task_type, section, details, deliverable):
        """Create a task dictionary for the planner output."""
        return {
            "step": 0,
            "title": title,
            "description": description,
            "type": task_type,
            "section": section,
            "details": details,
            "deliverable": deliverable,
            "status": "pending",
            "attempts": 0,
            "result": "",
            "observation": "",
        }
