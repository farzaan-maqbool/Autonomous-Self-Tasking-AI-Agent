"""Memory module.

This module stores execution history, completed tasks, and progress so the
agent can keep track of what has already happened.
"""


class MemoryModule:
    """Store task status, execution logs, and agent observations."""

    def __init__(self):
        self.completed_tasks = []
        self.execution_log = []
        self.task_results = {}
        self.total_tasks = 0

    def initialize(self, tasks):
        """Initialize memory for a new task plan."""
        self.total_tasks = len(tasks)
        self.completed_tasks = []
        self.execution_log = []
        self.task_results = {
            task["step"]: {
                "title": task["title"],
                "status": task["status"],
                "result": task["result"],
            }
            for task in tasks
        }

    def add_log(self, phase, message, step=None, status=None, attempt=None):
        """Append a structured log entry for the UI."""
        entry = {
            "phase": phase,
            "message": message,
        }

        if step is not None:
            entry["step"] = step
        if status is not None:
            entry["status"] = status
        if attempt is not None:
            entry["attempt"] = attempt

        self.execution_log.append(entry)

    def record_execution(self, task, execution_result):
        """Store the latest status and result for a task."""
        task["status"] = execution_result["status"]
        task["attempts"] = execution_result["attempt"]
        task["result"] = execution_result["result"]
        task["observation"] = execution_result["observation"]

        self.task_results[task["step"]] = {
            "title": task["title"],
            "status": task["status"],
            "result": task["result"],
        }

        if task["status"] == "completed" and task["title"] not in self.completed_tasks:
            self.completed_tasks.append(task["title"])

    def get_progress(self):
        """Return progress information for the current run."""
        completed_count = len(self.completed_tasks)
        percentage = 0
        if self.total_tasks:
            percentage = round((completed_count / self.total_tasks) * 100, 2)

        return {
            "completed": completed_count,
            "total": self.total_tasks,
            "percentage": percentage,
        }

    def get_summary(self):
        """Return a snapshot of the memory state."""
        return {
            "completed_tasks": self.completed_tasks,
            "task_results": self.task_results,
            "progress": self.get_progress(),
        }
