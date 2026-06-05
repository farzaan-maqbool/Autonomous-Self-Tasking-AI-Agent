"""AI-style resource and report generation module.

The generator uses the detected subject, domain, goal type, and generated
tasks to produce resource recommendations, task support material, execution
strategy, and a professional final report.
"""


class ResourceGenerator:
    """Generate subject-aware resources and planning reports."""

    CATEGORY_NAMES = ["Books", "Websites", "Videos", "Notes", "Tools", "Practice Resources"]

    def generate(self, interpretation, subject_analysis, tasks, breakdown, complexity):
        """Return resource categories, task resources, strategy, roadmap, and report."""
        subject = subject_analysis.get("subject", "the goal")
        domain = subject_analysis.get("domain", "General")
        goal_type = subject_analysis.get("goalType", "General Planning")
        topics = subject_analysis.get("topics", [])
        categories = self._category_resources(subject, domain, goal_type, topics)
        task_resources = self._task_resources(breakdown, subject, domain, categories)
        execution_strategy = self._execution_strategy(breakdown, subject_analysis, complexity)
        roadmap = self._roadmap(subject_analysis, complexity)
        report = self._professional_report(
            interpretation=interpretation,
            subject_analysis=subject_analysis,
            breakdown=breakdown,
            complexity=complexity,
            categories=categories,
            execution_strategy=execution_strategy,
            roadmap=roadmap,
        )

        return {
            "categories": categories,
            "taskResources": task_resources,
            "executionStrategy": execution_strategy,
            "roadmap": roadmap,
            "report": report,
        }

    def _category_resources(self, subject, domain, goal_type, topics):
        """Generate categorized resources for the detected subject."""
        lowered_subject = subject.lower()

        if "theory of computation" in lowered_subject:
            return {
                "Books": [
                    self._resource("Introduction to Automata Theory, Languages, and Computation - Hopcroft & Ullman", "Advanced", "High"),
                    self._resource("An Introduction to Formal Languages and Automata - Peter Linz", "Intermediate", "High"),
                    self._resource("Theory of Computer Science - K. L. P. Mishra", "Intermediate", "Medium"),
                ],
                "Websites": [
                    self._resource("GeeksforGeeks Theory of Computation", "Beginner", "High"),
                    self._resource("NPTEL Theory of Computation Course", "Intermediate", "High"),
                    self._resource("Tutorialspoint Automata Theory", "Beginner", "Medium"),
                ],
                "Videos": [
                    self._resource("Gate Smashers Theory of Computation", "Beginner", "High"),
                    self._resource("Neso Academy Theory of Computation", "Beginner", "High"),
                    self._resource("NPTEL Automata Theory Lectures", "Intermediate", "Medium"),
                ],
                "Notes": [
                    self._resource("Finite Automata Quick Notes", "Beginner", "High"),
                    self._resource("PDA Notes", "Intermediate", "High"),
                    self._resource("CFG, CNF, and GNF Cheat Sheets", "Intermediate", "High"),
                ],
                "Tools": [
                    self._resource("Automata simulator for DFA/NFA practice", "Intermediate", "Medium"),
                    self._resource("Graph paper or diagram tool for state machines", "Beginner", "Medium"),
                    self._resource("Flashcard app for definitions and closure properties", "Beginner", "Low"),
                ],
                "Practice Resources": [
                    self._resource("Previous-year Theory of Computation questions", "Intermediate", "High"),
                    self._resource("DFA/NFA conversion problem sets", "Beginner", "High"),
                    self._resource("PDA and Turing Machine construction exercises", "Advanced", "High"),
                ],
            }

        if any(term in lowered_subject for term in ["ias", "upsc", "civil services"]):
            return {
                "Books": [
                    self._resource("Indian Polity - M. Laxmikanth", "Beginner", "High"),
                    self._resource("Spectrum Modern History", "Beginner", "High"),
                    self._resource("NCERT Class 6-12 core books", "Beginner", "High"),
                ],
                "Websites": [
                    self._resource("PIB", "Intermediate", "High"),
                    self._resource("UPSC Official Website", "Beginner", "High"),
                    self._resource("PRS India", "Intermediate", "Medium"),
                ],
                "Videos": [
                    self._resource("StudyIQ current affairs lectures", "Beginner", "Medium"),
                    self._resource("Vision IAS topic lectures", "Intermediate", "Medium"),
                    self._resource("Rajya Sabha TV / Sansad TV discussions", "Advanced", "Medium"),
                ],
                "Notes": [
                    self._resource("NCERT PDFs", "Beginner", "High"),
                    self._resource("Current affairs monthly notes", "Intermediate", "High"),
                    self._resource("Revision notes for Polity, History, and Economy", "Intermediate", "High"),
                ],
                "Tools": [
                    self._resource("Daily newspaper tracker", "Beginner", "High"),
                    self._resource("Answer writing notebook", "Intermediate", "High"),
                    self._resource("Mock test analysis sheet", "Intermediate", "High"),
                ],
                "Practice Resources": [
                    self._resource("UPSC previous-year papers", "Intermediate", "High"),
                    self._resource("Prelims mock tests", "Intermediate", "High"),
                    self._resource("Mains answer writing practice", "Advanced", "High"),
                ],
            }

        if any(term in lowered_subject for term in ["react", "react development"]):
            return {
                "Books": [
                    self._resource("Learning React", "Beginner", "High"),
                    self._resource("React Quickly", "Intermediate", "Medium"),
                ],
                "Websites": [
                    self._resource("React Docs", "Beginner", "High"),
                    self._resource("MDN Web Docs", "Beginner", "High"),
                    self._resource("Vite Documentation", "Beginner", "Medium"),
                ],
                "Videos": [
                    self._resource("Net Ninja React Series", "Beginner", "High"),
                    self._resource("freeCodeCamp React Tutorial", "Beginner", "Medium"),
                ],
                "Notes": [
                    self._resource("React Hooks Cheatsheet", "Intermediate", "High"),
                    self._resource("Component lifecycle notes", "Intermediate", "Medium"),
                ],
                "Tools": [
                    self._resource("VS Code", "Beginner", "High"),
                    self._resource("React Developer Tools", "Beginner", "High"),
                    self._resource("Vite", "Beginner", "Medium"),
                ],
                "Practice Resources": [
                    self._resource("Build small React components daily", "Beginner", "High"),
                    self._resource("Frontend Mentor React challenges", "Intermediate", "Medium"),
                ],
            }

        if domain == "Computer Science":
            return self._computer_science_resources(subject, topics)
        if goal_type == "Writing":
            return self._writing_resources(subject)
        if goal_type == "Research":
            return self._research_resources(subject)
        return self._general_resources(subject, goal_type)

    def _computer_science_resources(self, subject, topics):
        """Generate resources for computer science subjects."""
        primary_topic = topics[0] if topics else subject
        return {
            "Books": [
                self._resource(f"Standard textbook for {subject}", "Intermediate", "High"),
                self._resource(f"Schaum's outline or quick guide for {subject}", "Beginner", "Medium"),
            ],
            "Websites": [
                self._resource(f"GeeksforGeeks {subject}", "Beginner", "High"),
                self._resource(f"NPTEL course related to {subject}", "Intermediate", "High"),
                self._resource(f"Official documentation or university notes for {subject}", "Intermediate", "Medium"),
            ],
            "Videos": [
                self._resource(f"Neso Academy lectures for {subject}", "Beginner", "Medium"),
                self._resource(f"Gate Smashers playlist for {subject}", "Beginner", "High"),
            ],
            "Notes": [
                self._resource(f"{primary_topic} summary notes", "Beginner", "High"),
                self._resource(f"{subject} formula and concept sheet", "Intermediate", "Medium"),
            ],
            "Tools": [
                self._resource("VS Code or notes app for structured study", "Beginner", "Medium"),
                self._resource("Flashcard tool for definitions and algorithms", "Beginner", "Low"),
            ],
            "Practice Resources": [
                self._resource(f"Previous-year questions for {subject}", "Intermediate", "High"),
                self._resource(f"Topic-wise problem sets for {subject}", "Intermediate", "High"),
            ],
        }

    def _writing_resources(self, subject):
        """Generate writing resources."""
        return {
            "Books": [self._resource("The Elements of Style", "Beginner", "Medium")],
            "Websites": [self._resource("Purdue OWL Writing Lab", "Beginner", "High")],
            "Videos": [self._resource("Academic writing tutorials", "Beginner", "Medium")],
            "Notes": [self._resource(f"Outline notes for {subject}", "Beginner", "High")],
            "Tools": [self._resource("Grammarly or language checker", "Beginner", "Medium")],
            "Practice Resources": [self._resource("Draft review checklist", "Beginner", "High")],
        }

    def _research_resources(self, subject):
        """Generate research resources."""
        return {
            "Books": [self._resource(f"Introductory book on {subject}", "Intermediate", "Medium")],
            "Websites": [self._resource("Google Scholar", "Intermediate", "High"), self._resource("Official reports and whitepapers", "Intermediate", "High")],
            "Videos": [self._resource(f"Expert talks on {subject}", "Intermediate", "Medium")],
            "Notes": [self._resource("Research notes template", "Beginner", "High")],
            "Tools": [self._resource("Zotero or reference manager", "Intermediate", "Medium")],
            "Practice Resources": [self._resource("Summary and comparison worksheet", "Beginner", "High")],
        }

    def _general_resources(self, subject, goal_type):
        """Generate fallback resources."""
        return {
            "Books": [self._resource(f"Beginner guide for {subject}", "Beginner", "Medium")],
            "Websites": [self._resource(f"Reliable web sources for {subject}", "Beginner", "High")],
            "Videos": [self._resource(f"Introductory videos for {subject}", "Beginner", "Medium")],
            "Notes": [self._resource(f"{subject} planning notes", "Beginner", "High")],
            "Tools": [self._resource("Checklist or planning tool", "Beginner", "Medium")],
            "Practice Resources": [self._resource(f"Practice tasks for {subject}", "Beginner", "High")],
        }

    def _task_resources(self, breakdown, subject, domain, categories):
        """Generate resources for each generated task."""
        category_pool = [resource for resources in categories.values() for resource in resources]
        task_resources = []

        for task_text in [self._clean_task_text(item) for item in breakdown]:
            lowered_task = task_text.lower()
            selected = self._select_task_resources(lowered_task, subject, category_pool)
            task_resources.append({
                "taskText": task_text,
                "resources": selected,
            })

        return task_resources

    def _select_task_resources(self, lowered_task, subject, resource_pool):
        """Select varied task resources based on task keywords."""
        selected = []
        aliases = {
            "pushdown": ["pda", "pushdown"],
            "pda": ["pda", "pushdown"],
            "context": ["cfg", "context-free", "grammar"],
            "cfg": ["cfg", "context-free", "grammar"],
            "cnf": ["cnf", "gnf", "normal form"],
            "gnf": ["cnf", "gnf", "normal form"],
            "finite": ["finite", "automata", "dfa", "nfa"],
            "automata": ["finite", "automata", "dfa", "nfa"],
            "regular": ["regular", "regex", "expression"],
            "turing": ["turing", "tm"],
            "decidability": ["decidable", "undecidable", "reduction"],
        }
        priority_aliases = {
            "pushdown": ["pda", "pushdown"],
            "pda": ["pda", "pushdown"],
            "context": ["cfg", "context-free", "grammar"],
            "cfg": ["cfg", "context-free", "grammar"],
            "cnf": ["cnf", "gnf", "normal form"],
            "gnf": ["cnf", "gnf", "normal form"],
            "turing": ["turing", "tm"],
            "decidability": ["decidable", "undecidable", "reduction"],
        }
        task_terms = {word for word in lowered_task.replace(":", " ").replace("/", " ").split() if len(word) >= 3}
        expanded_terms = set(task_terms)
        priority_terms = set()
        for term in task_terms:
            alias_terms = aliases.get(term, [])
            expanded_terms.update(alias_terms)
            priority_terms.update(priority_aliases.get(term, []))

        for resource in resource_pool:
            title = resource["title"].lower()
            if priority_terms and any(word in title for word in priority_terms):
                selected.append(resource)
            if len(selected) == 4:
                break

        for resource in resource_pool:
            if resource in selected:
                continue
            title = resource["title"].lower()
            if any(word in title for word in expanded_terms):
                selected.append(resource)
            if len(selected) == 4:
                break

        if len(selected) < 4:
            selected.extend(resource for resource in resource_pool if resource not in selected)

        return selected[:4]

    def _execution_strategy(self, breakdown, subject_analysis, complexity):
        """Explain why, what, effort, dependencies, and outcome for each task."""
        dependencies = complexity.get("dependencies", [])
        strategy = []
        for index, task_text in enumerate([self._clean_task_text(item) for item in breakdown], start=1):
            dependency = dependencies[min(index - 1, len(dependencies) - 1)] if dependencies else "Previous task understanding"
            effort = self._effort_for_task(task_text, complexity.get("difficulty", "Medium"))
            strategy.append({
                "taskText": task_text,
                "why": f"This task builds an important part of {subject_analysis['subject']} and keeps the plan focused.",
                "learn": self._learning_outcome(task_text),
                "effort": effort,
                "dependencies": dependency,
                "outcome": f"You should be able to confidently explain or apply {task_text.split(':')[0].strip()}.",
            })
        return strategy

    def _roadmap(self, subject_analysis, complexity):
        """Create a dynamic AI study roadmap."""
        subject = subject_analysis["subject"]
        goal_type = subject_analysis["goalType"]
        difficulty = complexity.get("difficulty", "Medium")

        if difficulty == "Hard":
            periods = ["Month 1-2", "Month 3-4", "Month 5-6", "Month 7+"]
        elif difficulty == "Medium":
            periods = ["Week 1", "Week 2", "Week 3", "Week 4"]
        else:
            periods = ["Day 1", "Day 2", "Day 3", "Final Review"]

        if goal_type == "Exam Preparation":
            focuses = [
                f"Learn {subject} fundamentals",
                "Practice core topics and examples",
                "Solve previous-year and mixed problems",
                "Mock tests, revision, and weak-area repair",
            ]
        elif goal_type == "Project Building":
            focuses = ["Plan requirements", "Build core features", "Test and refine", "Prepare final demo"]
        else:
            focuses = ["Understand the goal", "Work through key tasks", "Review quality", "Finalize output"]

        return [{"period": period, "focus": focuses[index]} for index, period in enumerate(periods)]

    def _professional_report(self, interpretation, subject_analysis, breakdown, complexity, categories, execution_strategy, roadmap):
        """Build the expanded final answer report."""
        subject = subject_analysis["subject"]
        topics = subject_analysis.get("topics", [])
        resource_names = []
        for resources in categories.values():
            resource_names.extend(item["title"] for item in resources[:2])

        strategy_lines = [
            f"- {item['taskText']}: {item['why']} What you learn: {item['learn']} Effort: {item['effort']}. Dependencies: {item['dependencies']}. Expected outcome: {item['outcome']}"
            for item in execution_strategy[:8]
        ]
        roadmap_lines = [f"{item['period']}: {item['focus']}" for item in roadmap]

        return "\n\n".join([
            "1. Goal Summary\n"
            f"The goal is to work on {subject} with a clear, trackable plan. The system has converted the original goal into practical tasks, calendar-ready actions, and learning resources.",
            "2. Subject Analysis\n"
            f"Detected Subject: {subject}\nGoal Type: {subject_analysis['goalType']}\nDomain: {subject_analysis['domain']}\nAI Confidence Score: {subject_analysis['confidence']}%",
            "3. Why This Goal Matters\n"
            f"{subject} matters because it builds the foundation needed to perform well in the selected goal type. A structured plan prevents random study or work and helps focus on the highest-value topics first.",
            "4. Key Topics Identified\n"
            + "\n".join(f"- {topic}" for topic in topics[:10]),
            "5. Recommended Learning Path\n"
            + "\n".join(breakdown[:8]),
            "6. Detailed Execution Strategy\n"
            + "\n".join(strategy_lines),
            "7. Time Management Advice\n"
            f"Estimated Time: {complexity.get('estimated_time', 'Depends on scope')}. Use short focused sessions, assign due dates on the calendar, and reserve review time before the final deadline.",
            "8. Common Mistakes To Avoid\n"
            "- Studying without solving practice questions\n- Skipping weak topics because they feel difficult\n- Keeping all tasks for the last day\n- Not reviewing completed topics\n- Ignoring overdue tasks",
            "9. Recommended Resources\n"
            + "\n".join(f"- {name}" for name in resource_names[:12]),
            "10. Success Checklist\n"
            "- All important topics are covered\n- Notes are prepared for revision\n- Practice problems are solved\n- Mock tests or reviews are completed\n- Overdue tasks are cleared\n- Progress is above 80%",
            "11. Expected Outcome\n"
            f"By following this plan, the user should gain a structured understanding of {subject}, complete the major tasks on time, and be ready to revise, practice, or present the work confidently.",
            "AI Recommended Roadmap\n"
            + "\n".join(roadmap_lines),
        ])

    def _learning_outcome(self, task_text):
        """Create a learning outcome for a task."""
        topic = task_text.split(":")[0].strip()
        return f"the core idea, use cases, and problem-solving pattern for {topic}"

    def _effort_for_task(self, task_text, difficulty):
        """Estimate task effort."""
        if difficulty == "Hard":
            return "2-4 focused sessions"
        if difficulty == "Medium":
            return "1-2 focused sessions"
        return "30-60 minutes"

    def _clean_task_text(self, step):
        """Remove step prefix from a generated task line."""
        parts = step.split(":", 1)
        if parts[0].strip().lower().startswith("step") and len(parts) > 1:
            return parts[1].strip()
        return step.strip()

    def _resource(self, title, difficulty, priority):
        """Create a resource dictionary."""
        return {
            "title": title,
            "difficulty": difficulty,
            "priority": priority,
        }
