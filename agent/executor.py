"""Task execution module.

This module simulates the execution of tasks in sequence. It does not call
external APIs; instead, it returns deterministic mock results that help
demonstrate agent behavior.
"""

import os
import threading
import time

try:
    import winsound
except ImportError:  # pragma: no cover - winsound is Windows-specific
    winsound = None


class Executor:
    """Execute one planned task at a time."""

    SAFE_APPLICATIONS = {
        "notepad": {
            "command": "notepad",
            "display_name": "Notepad",
        },
        "chrome": {
            "command": "chrome",
            "display_name": "Google Chrome",
        },
        "word": {
            "command": "winword",
            "display_name": "Microsoft Word",
        },
    }

    def execute_task(self, task):
        """Simulate execution for a single task."""
        attempt = task["attempts"] + 1
        task_type = task["type"]

        # Review tasks intentionally fail on the first attempt so the
        # evaluator can demonstrate a retry-and-adjust loop.
        if task_type == "review" and attempt == 1:
            return {
                "status": "failed",
                "attempt": attempt,
                "result": "Initial validation found a gap that needs another pass.",
                "observation": (
                    "The agent observed that the task needs refinement, "
                    "so it will adjust and retry."
                ),
            }

        result = self._build_result(task)
        return {
            "status": "completed",
            "attempt": attempt,
            "result": result,
            "observation": "The task completed successfully and its output was stored in memory.",
        }

    def _build_result(self, task):
        """Return a readable mock result for the given task type."""
        task_type = task["type"]
        title = task["title"]

        result_templates = {
            "analysis": f"{title}: key requirements and constraints were identified.",
            "planning": f"{title}: a structured sequence of actions was prepared.",
            "implementation": f"{title}: the main working steps were carried out in order.",
            "research": f"{title}: relevant information was gathered and organized.",
            "writing": f"{title}: the content was drafted in a concise format.",
            "design": f"{title}: a user-facing interaction flow was outlined.",
            "review": f"{title}: the work passed the final quality check after refinement.",
        }

        return result_templates.get(
            task_type,
            f"{title}: the task was completed by the simulated execution engine.",
        )

    def execute_system_task(self, task):
        """Execute a safe predefined system task."""
        action = task.get("action")

        if action == "open_application":
            return self._open_application(task.get("application"))
        if action == "set_alarm":
            return self._set_alarm(task.get("seconds", 0), task.get("time_text", ""))

        return {
            "status": "blocked",
            "attempt": 1,
            "result": "Unknown or unsafe system command.",
            "observation": "The request was blocked because it is not in the safe allow-list.",
        }

    def _open_application(self, application):
        """Open an allowed application using the Windows shell."""
        app_info = self.SAFE_APPLICATIONS.get(application)
        if not app_info:
            return {
                "status": "blocked",
                "attempt": 1,
                "result": "Only Notepad, Chrome, and Microsoft Word are allowed.",
                "observation": "The app name was not in the safe application list.",
            }

        command = f'start "" {app_info["command"]}'
        exit_code = os.system(command)

        if exit_code == 0:
            return {
                "status": "completed",
                "attempt": 1,
                "result": f'{app_info["display_name"]} opened successfully.',
                "observation": "The application launch command was sent successfully.",
            }

        return {
            "status": "failed",
            "attempt": 1,
            "result": f'Unable to open {app_info["display_name"]}.',
            "observation": "The system tried to launch the application but it did not complete cleanly.",
        }

    def _set_alarm(self, seconds, time_text):
        """Set a simple background alarm."""
        if seconds <= 0:
            return {
                "status": "blocked",
                "attempt": 1,
                "result": "Please use a valid alarm duration.",
                "observation": "The alarm request did not include a positive time value.",
            }

        alarm_thread = threading.Thread(
            target=self._alarm_worker,
            args=(seconds,),
            daemon=True,
        )
        alarm_thread.start()

        label = time_text or f"{seconds} seconds"
        return {
            "status": "completed",
            "attempt": 1,
            "result": f"Alarm set successfully for {label}.",
            "observation": "The alarm was scheduled in the background.",
        }

    def _alarm_worker(self, seconds):
        """Wait for the alarm time and then play a simple sound."""
        time.sleep(seconds)

        if winsound:
            for _ in range(3):
                winsound.Beep(1200, 500)
                time.sleep(0.2)
            return

        print("\aAlarm finished.")
