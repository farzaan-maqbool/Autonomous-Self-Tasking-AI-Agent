"""Goal interpretation module.

This module accepts a natural language goal and extracts a lightweight,
rule-based understanding of the user's intent.
"""

import re
from datetime import datetime, timedelta


class GoalInterpreter:
    """Interpret high-level goals using simple keyword rules."""

    SAFE_APPLICATIONS = {
        "notepad": {
            "command": "notepad",
            "display_name": "Notepad",
            "aliases": ["notepad"],
        },
        "chrome": {
            "command": "chrome",
            "display_name": "Google Chrome",
            "aliases": ["chrome", "google chrome"],
        },
        "word": {
            "command": "winword",
            "display_name": "Microsoft Word",
            "aliases": ["word", "ms word", "microsoft word", "winword"],
        },
    }

    def interpret(self, goal):
        """Return a structured interpretation of the user's goal."""
        normalized_goal = goal.strip()
        lowered_goal = normalized_goal.lower()

        intent = self._detect_intent(lowered_goal)
        focus_areas = self._detect_focus_areas(lowered_goal)
        keywords = self._extract_keywords(lowered_goal)

        summary = (
            f"The agent understood the goal as a {intent} task"
            f" focused on {', '.join(focus_areas)}."
        )

        return {
            "original_goal": normalized_goal,
            "intent": intent,
            "focus_areas": focus_areas,
            "keywords": keywords,
            "summary": summary,
        }

    def detect_system_command(self, goal):
        """Detect safe system commands for System Control Mode."""
        normalized_goal = goal.strip()
        lowered_goal = normalized_goal.lower()

        if "alarm" in lowered_goal:
            return self._extract_alarm_command(normalized_goal, lowered_goal)

        if any(trigger in lowered_goal for trigger in ["open", "start", "launch"]):
            return self._extract_application_command(normalized_goal, lowered_goal)

        return None

    def _detect_intent(self, goal):
        """Detect the main intent behind the goal."""
        intent_rules = {
            "build": ["build", "create", "develop", "make"],
            "research": ["research", "study", "analyze", "investigate", "learn"],
            "write": ["write", "draft", "report", "summary", "presentation"],
            "improve": ["improve", "optimize", "fix", "debug", "test"],
            "plan": ["plan", "organize", "schedule", "prepare"],
        }

        for intent, keywords in intent_rules.items():
            if any(keyword in goal for keyword in keywords):
                return intent

        return "general"

    def _detect_focus_areas(self, goal):
        """Detect broad areas the agent should focus on."""
        focus_rules = {
            "user interface": ["ui", "frontend", "website", "web", "screen", "design"],
            "system logic": ["backend", "logic", "workflow", "automation", "server"],
            "content": ["report", "essay", "summary", "document", "presentation"],
            "data": ["data", "analysis", "numbers", "dataset", "insights"],
            "quality": ["test", "fix", "debug", "review", "improve"],
        }

        detected_areas = [
            area for area, keywords in focus_rules.items()
            if any(keyword in goal for keyword in keywords)
        ]

        return detected_areas or ["overall outcome"]

    def _extract_keywords(self, goal):
        """Extract goal keywords by removing common filler words."""
        stop_words = {
            "a", "an", "and", "the", "to", "for", "of", "with", "in",
            "on", "my", "is", "be", "that", "this", "from", "by",
        }

        keywords = []
        for word in goal.replace(",", " ").replace(".", " ").split():
            cleaned_word = word.strip().lower()
            if len(cleaned_word) > 2 and cleaned_word not in stop_words:
                keywords.append(cleaned_word)

        unique_keywords = list(dict.fromkeys(keywords))
        return unique_keywords[:8]

    def _extract_application_command(self, original_goal, lowered_goal):
        """Extract a safe application launch command from the goal."""
        for app_key, app_info in self.SAFE_APPLICATIONS.items():
            if any(self._contains_phrase(lowered_goal, alias) for alias in app_info["aliases"]):
                return {
                    "action": "open_application",
                    "application": app_key,
                    "command": app_info["command"],
                    "display_name": app_info["display_name"],
                    "original_goal": original_goal,
                }

        return {
            "action": "blocked",
            "reason": "unsupported_application",
            "original_goal": original_goal,
            "message": (
                "Only Notepad, Chrome, and Microsoft Word are allowed in "
                "System Control Mode."
            ),
        }

    def _extract_alarm_command(self, original_goal, lowered_goal):
        """Extract alarm timing from the goal."""
        seconds_match = re.search(
            r"(\d+)\s*(second|seconds|sec|secs|minute|minutes|min|mins)\b",
            lowered_goal,
        )
        if seconds_match:
            amount = int(seconds_match.group(1))
            unit = seconds_match.group(2)
            seconds = amount * 60 if unit.startswith("min") else amount
            return {
                "action": "set_alarm",
                "seconds": seconds,
                "time_text": f"{amount} {'minutes' if unit.startswith('min') else 'seconds'}",
                "original_goal": original_goal,
            }

        time_match = re.search(r"\b(\d{1,2}):(\d{2})\s*(am|pm)?\b", lowered_goal)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            meridiem = time_match.group(3)

            if minute > 59 or hour > 23 or (meridiem and hour > 12):
                return {
                    "action": "blocked",
                    "reason": "invalid_alarm_time",
                    "original_goal": original_goal,
                    "message": "Please use a valid time such as 7:30 am or 19:30.",
                }

            target_time = self._calculate_alarm_seconds(hour, minute, meridiem)
            return {
                "action": "set_alarm",
                "seconds": target_time["seconds_until"],
                "time_text": target_time["display_time"],
                "original_goal": original_goal,
            }

        return {
            "action": "blocked",
            "reason": "invalid_alarm_format",
            "original_goal": original_goal,
            "message": (
                "Please say something like 'set alarm for 10 seconds' or "
                "'set alarm at 7:30 am'."
            ),
        }

    def _calculate_alarm_seconds(self, hour, minute, meridiem):
        """Convert a clock time into seconds from now."""
        now = datetime.now()

        if meridiem:
            meridiem = meridiem.lower()
            if hour == 12:
                hour = 0
            if meridiem == "pm":
                hour += 12

        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        seconds_until = int((target - now).total_seconds())
        display_time = target.strftime("%I:%M %p").lstrip("0")

        return {
            "seconds_until": seconds_until,
            "display_time": display_time,
        }

    def _contains_phrase(self, text, phrase):
        """Check whether a phrase appears as a whole word or words."""
        pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
        return re.search(pattern, text) is not None
