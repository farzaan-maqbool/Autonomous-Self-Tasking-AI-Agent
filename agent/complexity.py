"""Task complexity analyzer.

This module estimates difficulty, time, resources, and dependencies before
the agent presents the step-by-step plan.
"""


class TaskComplexityAnalyzer:
    """Analyze a goal and return a simple complexity summary."""

    HARD_MARKERS = {
        "ias", "upsc", "civil services", "gate", "neet", "jee", "phd",
        "thesis", "dissertation", "full stack", "machine learning",
        "startup", "enterprise", "large", "advanced",
    }

    MEDIUM_MARKERS = {
        "exam", "project", "website", "app", "report", "research",
        "presentation", "portfolio", "dashboard", "analysis",
    }

    def analyze(self, interpretation, tasks):
        """Analyze assistant-mode tasks."""
        goal = interpretation["original_goal"]
        lowered_goal = goal.lower()
        goal_type = tasks[0].get("goal_type", "general") if tasks else "general"
        difficulty = self._difficulty(lowered_goal, goal_type, tasks)

        return {
            "difficulty": difficulty,
            "estimated_time": self._estimated_time(lowered_goal, goal_type, difficulty),
            "resources": self._resources(lowered_goal, goal_type),
            "dependencies": self._dependencies(lowered_goal, goal_type),
        }

    def analyze_system(self, system_command):
        """Analyze system-control tasks."""
        action = system_command.get("action", "blocked")

        if action == "set_alarm":
            return {
                "difficulty": "Easy",
                "estimated_time": "A few seconds to set up",
                "resources": ["Windows computer", "Python time module", "winsound for alarm sound"],
                "dependencies": ["Detect alarm request", "Extract time", "Start background alarm", "Play sound"],
            }

        if action == "open_application":
            return {
                "difficulty": "Easy",
                "estimated_time": "Immediate",
                "resources": ["Windows computer", "Allowed application", "Python os module"],
                "dependencies": ["Detect app request", "Check safe app list", "Run launch command"],
            }

        return {
            "difficulty": "Easy",
            "estimated_time": "Immediate",
            "resources": ["Safe command list", "Clear app name or alarm time"],
            "dependencies": ["Read command", "Validate safety", "Block unsupported action"],
        }

    def _difficulty(self, lowered_goal, goal_type, tasks):
        """Estimate Easy, Medium, or Hard using simple rules."""
        if any(marker in lowered_goal for marker in self.HARD_MARKERS):
            return "Hard"

        if goal_type == "study" and any(word in lowered_goal for word in ["exam", "syllabus", "semester"]):
            return "Medium"
        if goal_type == "coding" and any(word in lowered_goal for word in ["backend", "database", "login", "api"]):
            return "Medium"
        if goal_type == "research" and any(word in lowered_goal for word in ["compare", "impact", "analysis"]):
            return "Medium"
        if len(tasks) >= 5 or any(marker in lowered_goal for marker in self.MEDIUM_MARKERS):
            return "Medium"

        return "Easy"

    def _estimated_time(self, lowered_goal, goal_type, difficulty):
        """Estimate task duration from domain and difficulty."""
        if any(marker in lowered_goal for marker in ["ias", "upsc", "civil services"]):
            return "8-12 months"
        if difficulty == "Hard":
            return {
                "study": "3-9 months",
                "coding": "4-8 weeks",
                "writing": "1-3 weeks",
                "research": "3-8 weeks",
                "general": "2-6 weeks",
            }.get(goal_type, "2-6 weeks")

        if difficulty == "Medium":
            return {
                "study": "2-6 weeks",
                "coding": "1-3 weeks",
                "writing": "2-5 days",
                "research": "1-3 weeks",
                "general": "3-10 days",
            }.get(goal_type, "3-10 days")

        return {
            "study": "2-5 days",
            "coding": "1-3 days",
            "writing": "1-2 days",
            "research": "2-4 days",
            "general": "1-2 days",
        }.get(goal_type, "1-2 days")

    def _resources(self, lowered_goal, goal_type):
        """Suggest resources needed for the task."""
        if any(marker in lowered_goal for marker in ["ias", "upsc", "civil services"]):
            return ["NCERT Books", "Current Affairs", "Standard reference books", "Answer writing practice", "Mock Tests"]

        resources_by_type = {
            "study": ["Textbook or notes", "Topic-wise syllabus", "Practice questions", "Revision schedule"],
            "coding": ["Code editor", "Programming language or framework", "Documentation", "Testing tools"],
            "writing": ["Outline", "Key points or references", "Drafting tool", "Proofreading checklist"],
            "research": ["Reliable web sources", "Research papers or reports", "Notes document", "Summary template"],
            "general": ["Checklist", "Required information", "Useful tools or materials", "Time block for execution"],
        }

        resources = list(resources_by_type.get(goal_type, resources_by_type["general"]))

        if "exam" in lowered_goal and "Mock Tests" not in resources:
            resources.append("Mock Tests")
        if any(word in lowered_goal for word in ["website", "app", "project"]) and "Git or version control" not in resources:
            resources.append("Git or version control")
        if "presentation" in lowered_goal:
            resources.append("Slides or presentation tool")

        return resources[:6]

    def _dependencies(self, lowered_goal, goal_type):
        """Create a dependency chain for the task."""
        if any(marker in lowered_goal for marker in ["ias", "upsc", "civil services"]):
            return ["NCERT Basics", "Current Affairs", "Optional or core subjects", "Answer Writing", "Mock Tests"]

        dependencies_by_type = {
            "study": ["Topics", "Concept Notes", "Practice Questions", "Revision", "Self Test"],
            "coding": ["Requirements", "Technology Stack", "Core Features", "Testing", "Final Polish"],
            "writing": ["Outline", "Key Points", "First Draft", "Editing", "Final Version"],
            "research": ["Research Questions", "Sources", "Notes", "Analysis", "Summary"],
            "general": ["Goal Details", "Resources", "Action Plan", "Execution", "Review"],
        }

        return dependencies_by_type.get(goal_type, dependencies_by_type["general"])
