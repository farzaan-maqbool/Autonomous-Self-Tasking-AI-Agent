"""Subject detection module.

This module extracts the real study/work subject from a natural language goal
so downstream planning does not repeat fragments of the user's sentence.
"""

import re


class SubjectDetector:
    """Detect subject, goal type, domain, topics, and confidence."""

    SUBJECT_PROFILES = {
        "theory of computation": {
            "subject": "Theory of Computation",
            "domain": "Computer Science",
            "topics": [
                "Finite Automata",
                "Regular Expressions",
                "Context-Free Grammars",
                "CNF and GNF",
                "Pushdown Automata",
                "Turing Machines",
                "Decidability",
            ],
            "topic_tasks": {
                "Finite Automata": ["Learn DFA", "Learn NFA", "Solve automata conversion problems"],
                "Regular Expressions": ["Study regex operators", "Convert regex to automata", "Practice language matching"],
                "Context-Free Grammars": ["Revise grammar rules", "Practice derivations", "Remove ambiguity examples"],
                "CNF and GNF": ["Learn CNF conversion", "Learn GNF conversion", "Solve normal form problems"],
                "Pushdown Automata": ["Practice PDA construction", "Design PDA for CFLs", "Compare PDA and CFG"],
                "Turing Machines": ["Review TM model", "Design simple TMs", "Practice decidability examples"],
                "Decidability": ["Study decidable languages", "Study undecidable problems", "Revise reductions"],
            },
        },
        "data structures": {
            "subject": "Data Structures",
            "domain": "Computer Science",
            "topics": ["Arrays", "Linked Lists", "Stacks", "Queues", "Trees", "Graphs", "Sorting and Searching"],
        },
        "operating systems": {
            "subject": "Operating Systems",
            "domain": "Computer Science",
            "topics": ["Processes", "CPU Scheduling", "Memory Management", "File Systems", "Deadlocks", "Synchronization"],
        },
        "database management system": {
            "subject": "Database Management System",
            "domain": "Computer Science",
            "topics": ["ER Model", "Relational Model", "SQL", "Normalization", "Transactions", "Indexing"],
        },
        "ias": {
            "subject": "IAS Exam",
            "domain": "Civil Services",
            "topics": ["NCERT Basics", "Polity", "History", "Geography", "Economy", "Current Affairs", "Mock Tests"],
        },
        "upsc": {
            "subject": "UPSC Exam",
            "domain": "Civil Services",
            "topics": ["NCERT Basics", "Polity", "History", "Geography", "Economy", "Current Affairs", "Mock Tests"],
        },
    }

    DOMAIN_KEYWORDS = {
        "Computer Science": [
            "computer", "programming", "software", "data structures", "algorithm",
            "database", "operating system", "theory of computation", "compiler",
            "network", "python", "java", "web", "machine learning",
        ],
        "Civil Services": ["ias", "upsc", "civil services", "general studies"],
        "Science": ["physics", "chemistry", "biology", "science"],
        "Mathematics": ["math", "mathematics", "calculus", "algebra", "statistics"],
        "Business": ["business", "marketing", "finance", "management"],
        "Writing": ["essay", "report", "article", "blog", "documentation"],
    }

    def detect(self, goal):
        """Return a structured subject analysis for the goal."""
        cleaned_goal = self._normalize_spaces(goal)
        lowered_goal = cleaned_goal.lower()
        goal_type = self._detect_goal_type(lowered_goal)
        subject = self._extract_subject(cleaned_goal, lowered_goal)
        profile = self._match_profile(subject, lowered_goal)

        if profile:
            subject = profile["subject"]
            domain = profile["domain"]
            topics = profile["topics"]
            topic_tasks = profile.get("topic_tasks") or self._default_topic_tasks(topics, goal_type)
            confidence = self._confidence(lowered_goal, subject, profile_found=True)
        else:
            domain = self._detect_domain(subject, lowered_goal)
            topics = self._generic_topics(subject, goal_type, domain)
            topic_tasks = self._default_topic_tasks(topics, goal_type)
            confidence = self._confidence(lowered_goal, subject, profile_found=False)

        return {
            "subject": subject,
            "goalType": goal_type,
            "domain": domain,
            "confidence": confidence,
            "topics": topics,
            "topicTasks": topic_tasks,
            "pipeline": [
                "Goal Analysis Agent",
                "Subject Detection Agent",
                "Topic Extraction Agent",
                "Task Planning Agent",
                "Scheduling Agent",
                "Report Generation Agent",
            ],
            "flowSteps": [
                "Goal",
                "Subject Detection",
                "Topic Extraction",
                "Study Fundamentals",
                "Practice Problems",
                "Mock Tests",
                "Revision",
                "Exam Ready",
            ] if goal_type == "Exam Preparation" else [
                "Goal",
                "Subject Detection",
                "Topic Extraction",
                "Plan Tasks",
                "Execute Work",
                "Review Output",
                "Complete",
            ],
        }

    def _extract_subject(self, cleaned_goal, lowered_goal):
        """Extract the actual subject phrase from common goal patterns."""
        known_profile = self._profile_from_text(lowered_goal)
        if known_profile:
            return known_profile["subject"]

        patterns = [
            r"(?:examination|exam|test|revision|preparation)\s+of\s+(.+)$",
            r"(?:prepare|study|revise|learn)\s+(?:for\s+)?(?:my\s+)?(?:final\s+)?(?:examination|exam|test)?\s*(?:of|for|on|in)?\s+(.+)$",
            r"(?:write|create|build|develop|research|analyze)\s+(?:a|an|the)?\s*(?:report|essay|project|app|website)?\s*(?:on|about|for)?\s+(.+)$",
            r"(?:about|on|of|for)\s+(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, lowered_goal)
            if match:
                subject = self._clean_subject(match.group(1))
                if subject:
                    return subject

        return self._clean_subject(cleaned_goal)

    def _clean_subject(self, text):
        """Remove filler words and convert a phrase into title case."""
        text = re.sub(r"[^A-Za-z0-9\s+-]", " ", text)
        words = self._normalize_spaces(text).split()
        removable = {
            "i", "want", "to", "my", "final", "examination", "exam", "test",
            "prepare", "preparation", "study", "revise", "learn", "for", "of",
            "the", "a", "an", "please", "need", "make", "create", "build",
            "write", "research", "about", "on", "in",
        }
        subject_words = [word for word in words if word.lower() not in removable]
        if not subject_words:
            return "General Task"

        acronyms = {"ias", "upsc", "dbms", "os", "toc", "ai", "ml", "pda", "cfg"}
        formatted = []
        for word in subject_words[:8]:
            lowered = word.lower()
            formatted.append(lowered.upper() if lowered in acronyms else word.capitalize())

        return " ".join(formatted)

    def _detect_goal_type(self, lowered_goal):
        """Infer the type of user goal."""
        if any(word in lowered_goal for word in ["exam", "examination", "test", "revision", "prepare"]):
            return "Exam Preparation"
        if any(word in lowered_goal for word in ["build", "develop", "code", "app", "website", "project"]):
            return "Project Building"
        if any(word in lowered_goal for word in ["write", "essay", "report", "article", "blog"]):
            return "Writing"
        if any(word in lowered_goal for word in ["research", "analyze", "investigate", "survey"]):
            return "Research"
        return "General Planning"

    def _detect_domain(self, subject, lowered_goal):
        """Infer domain from subject and goal keywords."""
        search_text = f"{subject.lower()} {lowered_goal}"
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in search_text for keyword in keywords):
                return domain
        return "General"

    def _match_profile(self, subject, lowered_goal):
        """Find a known subject profile."""
        subject_lower = subject.lower()
        return self._profile_from_text(subject_lower) or self._profile_from_text(lowered_goal)

    def _profile_from_text(self, text):
        """Return profile if a known subject appears in text."""
        for key, profile in self.SUBJECT_PROFILES.items():
            if key in text:
                return profile
        return None

    def _generic_topics(self, subject, goal_type, domain):
        """Generate practical topics for unknown subjects."""
        if goal_type == "Exam Preparation":
            return [
                f"{subject} fundamentals",
                f"Important concepts in {subject}",
                f"Previous-year {subject} questions",
                f"Common problem types in {subject}",
                f"{subject} revision notes",
                "Mock tests",
            ]
        if goal_type == "Project Building":
            return ["Requirements", "Technology Stack", "Core Features", "Testing", "Deployment", "Documentation"]
        if goal_type == "Writing":
            return ["Introduction", "Key Arguments", "Examples and Evidence", "Drafting", "Editing", "Final Review"]
        if goal_type == "Research":
            return ["Research Questions", "Reliable Sources", "Collected Notes", "Analysis", "Findings", "Summary"]
        return ["Goal Details", "Resources", "Action Plan", "Execution", "Review", "Final Output"]

    def _default_topic_tasks(self, topics, goal_type):
        """Create child task nodes for each topic."""
        task_map = {}
        for topic in topics:
            if goal_type == "Exam Preparation":
                task_map[topic] = [f"Study {topic}", f"Make notes for {topic}", f"Practice questions on {topic}"]
            elif goal_type == "Project Building":
                task_map[topic] = [f"Plan {topic}", f"Implement {topic}", f"Test {topic}"]
            else:
                task_map[topic] = [f"Understand {topic}", f"Work on {topic}", f"Review {topic}"]
        return task_map

    def _confidence(self, lowered_goal, subject, profile_found):
        """Estimate confidence from profile and extraction quality."""
        score = 72
        if profile_found:
            score += 20
        if len(subject.split()) >= 2:
            score += 5
        if any(word in lowered_goal for word in ["exam", "prepare", "build", "write", "research"]):
            score += 3
        return min(score, 97)

    def _normalize_spaces(self, text):
        """Collapse repeated whitespace."""
        return re.sub(r"\s+", " ", text).strip()
