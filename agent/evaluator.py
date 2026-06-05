"""Evaluation module.

This module checks progress after execution and recommends retries when
something is incomplete or has failed.
"""


class EvaluationModule:
    """Evaluate task completion and adjust tasks for retries."""

    def evaluate(self, tasks):
        """Return an evaluation summary for the current task list."""
        failed_tasks = [task for task in tasks if task["status"] == "failed"]
        pending_tasks = [task for task in tasks if task["status"] == "pending"]
        completed_tasks = [task for task in tasks if task["status"] == "completed"]

        return {
            "all_completed": len(completed_tasks) == len(tasks),
            "failed_steps": [task["step"] for task in failed_tasks],
            "pending_steps": [task["step"] for task in pending_tasks],
            "completed_steps": [task["step"] for task in completed_tasks],
            "message": self._build_message(failed_tasks, pending_tasks, tasks),
        }

    def adjust_task(self, task):
        """Adjust a failed task before retrying it."""
        if "retry_note" not in task:
            task["retry_note"] = "Adjusted after evaluation to address the observed gap."
            task["description"] += " Retry with extra validation and a clearer check."
        return task

    def _build_message(self, failed_tasks, pending_tasks, tasks):
        """Generate a human-readable evaluation message."""
        if failed_tasks:
            return (
                f"{len(failed_tasks)} task(s) need another attempt before the goal is complete."
            )

        if len(tasks) and not pending_tasks:
            return "All planned tasks were completed successfully."

        return "The agent still has work remaining in the current plan."
