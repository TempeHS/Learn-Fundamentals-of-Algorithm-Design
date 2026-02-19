## Guidelines

- Use British English
- Keep Jupyter Notebook and markdown documents synchronised
- Keep requirements.txt updated with any requirements
- Keep .devcontainer/ and .vscode/ updated with any required extensions

## Curriculum Alignment (NESA HSC)

- Define and apply algorithm characteristics
- Use procedural design principles (sequence, selection, iteration)
- Apply decomposition to break down problems
- Design algorithms using flowcharts (NESA standard symbols)
- Write pseudocode following HSC conventions
- Apply standard algorithm patterns
- Understand recursion and advanced techniques

## Stack

- Jupyter Notebooks (primary)
- draw.io (flowchart diagrams embedded via iframes)
- YouTube (embedded instructional videos)
- WeasyPrint (PDF generation)
- Playwright (diagram rendering)

## Target Audience

- High school students (Year 11-12)
- No programming prerequisite (this course teaches algorithm design, not coding)
- Prepares students for HSC Software Design and Development

## VSCode Extensions

- ms-toolsai.jupyter (Jupyter Notebook support)

## Outline

Algorithm Design Fundamentals Curriculum
Course Overview
Duration: 9 lessons × 20-30 minutes each
Target Audience: High school students preparing for HSC
Focus: Flowcharts and pseudocode (NESA HSC standard)
Format: Watch videos, study flowcharts, answer quiz questions, practice writing pseudocode

---

Lesson 1: What is an Algorithm?
Duration: 20-30 minutes

Learning Objectives
- Define "algorithm" and its key characteristics
- Understand procedural algorithm design principles
- Visualise algorithms with flowcharts
- Write algorithms in pseudocode
- Apply decomposition to break down problems

Content
- 📺 Video: What is an Algorithm?
- 📺 Video: Sequence in Algorithms
- Algorithm characteristics (Input, Output, Definiteness, Finiteness, Effectiveness)
- The three pillars: Sequence, Selection, Iteration
- Decomposition with "Make Breakfast" example
- 📊 Flowchart: Make Tea Algorithm
- Representing algorithms: Flowcharts, Pseudocode, Code

Key Concepts
- Algorithm vs Program
- Structured Programming Theorem
- Procedural design

---

Lesson 2: Variables and Input/Output
Duration: 20-30 minutes

Learning Objectives
- Understand what variables are and how to use them
- Apply the IPO (Input-Process-Output) model
- Use flowchart symbols for input and output operations
- Write pseudocode following HSC conventions

Content
- 📺 Video: Variables and Input/Output
- IPO Model explanation
- Variables as named storage locations
- Variable naming best practices
- HSC pseudocode keywords: INPUT, OUTPUT, DISPLAY, SET...TO
- String concatenation
- 📊 Flowchart: Calculate Rectangle Area

Key Concepts
- Parallelogram = Input/Output
- Rectangle = Process
- Rounded Rectangle = Terminal (START/END)

---

Lesson 3: Selection (If-Then-Else)
Duration: 20-30 minutes

Learning Objectives
- Understand selection as a fundamental control structure
- Design algorithms with decision points using flowcharts
- Use IF/ELSE and IF/ELSEIF/ELSE in pseudocode
- Apply boolean logic to conditions

Content
- 📺 Video: Binary Selection (If-Then-Else)
- 📺 Video: Multiway Selection
- Binary selection (two paths)
- 📊 Flowchart: Pass or Fail (diamond decision symbol)
- Boolean logic: AND, OR, NOT
- Comparison operators: =, <>, <, >, <=, >=
- Multiway selection (IF-ELSEIF-ELSE)

Key Concepts
- Diamond (rhombus) = Decision
- True/False branch labelling
- ENDIF required to close IF blocks

---

Lesson 4: Counting and Accumulating Loops (FOR)
Duration: 20-30 minutes

Learning Objectives
- Understand iteration as a fundamental control structure
- Design FOR loops in flowcharts (counted loop structure)
- Write FOR loops in pseudocode using HSC standard syntax
- Apply the counting and accumulator patterns

Content
- 📺 Video: Pre-test Iteration
- 📺 Video: Sequence, Selection & Iteration
- FOR loop structure: FOR counter = start TO end STEP increment
- 📊 Flowchart: Print Numbers 1 to 5
- Definite vs indefinite iteration
- Counting pattern
- Accumulator pattern
- Loop tracing step by step

Key Concepts
- FOR...NEXT syntax
- STEP increment (default 1)
- Inclusive range in pseudocode

---

Lesson 5: Conditional Loops (WHILE) and Input Validation
Duration: 20-30 minutes

Learning Objectives
- Understand indefinite iteration and when to use it
- Design algorithms using pre-test (WHILE) loops
- Implement sentinel-controlled loops
- Apply the input validation pattern

Content
- Choosing the right loop type (FOR vs WHILE)
- WHILE loop structure (pre-test)
- 📊 Flowchart: WHILE Loop (Pre-test Repetition)
- Sentinel values for signalling end of input
- 📊 Flowchart: Input Validation Pattern
- Avoiding infinite loops

Key Concepts
- WHILE...ENDWHILE syntax
- Pre-test = condition checked before each iteration
- Sentinel value must be outside valid data range

---

Lesson 6: Nested Loops (Loops within Loops)
Duration: 20-30 minutes

Learning Objectives
- Understand what nested loops are and when to use them
- Recognise problems that require nested iteration
- Apply 2D thinking to algorithm design
- Trace through nested loop execution

Content
- Recognising nested loop problems
- Clock analogy (inner = minute hand, outer = hour hand)
- Total iterations = outer × inner
- 📊 Flowchart: Nested Loop Structure
- 2D thinking: rows and columns
- Pattern: Rectangle of symbols
- Pattern: Multiplication tables

Key Concepts
- Inner loop completes fully for each outer iteration
- Row-major vs column-major order
- Newline after each row

---

Lesson 7: Working with Lists (Arrays)
Duration: 20-30 minutes

Learning Objectives
- Understand when to use lists vs single variables
- Apply standard list algorithms (traverse, search, find max/min)
- Recognise patterns for list processing

Content
- When to use lists (collections of related items)
- Array basics: declaration, indexing (0-based)
- 📊 Flowchart: List Traversal Pattern
- Standard algorithms:
  - Traversal (visit every element)
  - Sum all elements (accumulator)
  - Find maximum (best-so-far)
- 📊 Flowchart: Find Maximum Algorithm
- Linear search

Key Concepts
- Index starts at 0
- LENGTH(list) - 1 for last index
- "Out of range" errors

---

Lesson 8: Essential Algorithm Patterns
Duration: 20-30 minutes

Learning Objectives
- Recognise and apply the six fundamental patterns
- Choose the correct pattern for a given problem
- Combine patterns to solve complex problems

Content
- Pattern 1: Counter (count occurrences)
- 📊 Flowchart: Counter Pattern
- Pattern 2: Accumulator (compute total)
- 📊 Flowchart: Accumulator Pattern
- Pattern 3: Flag (track true/false state)
- 📊 Flowchart: Flag Pattern
- Pattern 4: Best-So-Far (find max/min)
- Pattern 5: Filter (select matching items)
- Pattern 6: Transform (change each item)

Key Concepts
- Most algorithms are combinations of these 6 patterns
- Pattern recognition is key to problem solving

---

Lesson 9: Advanced Algorithm Patterns
Duration: 20-30 minutes

Learning Objectives
- Understand recursion and its components
- Apply divide and conquer thinking
- Understand permutations and backtracking concepts

Content
- Fibonacci sequence explanation
- Pattern 1: Recursion
  - Base case (when to stop)
  - Recursive case (self-calling)
- 📊 Flowchart: Fibonacci Recursive Algorithm
- Step-by-step trace of Fibonacci(5)
- Divide and conquer concept
- Permutations overview
- Backtracking overview

Key Concepts
- Recursion = subprogram calls itself
- Must have base case to prevent infinite recursion
- Trade-off: elegance vs efficiency

---

## Assessment Focus (HSC)

**Key Skills:**
- Drawing flowcharts with correct NESA symbols
- Writing pseudocode with proper syntax (BEGIN/END, IF/ENDIF, FOR/NEXT, WHILE/ENDWHILE)
- Tracing algorithm execution with sample data
- Choosing appropriate control structures
- Applying algorithm patterns to solve problems

**Flowchart Symbols (NESA Standard):**
| Shape | Purpose |
|-------|---------|
| Rounded Rectangle | Terminal (START/END) |
| Rectangle | Process |
| Parallelogram | Input/Output |
| Diamond (Rhombus) | Decision |
| Arrows | Flow direction |

**Pseudocode Conventions (HSC):**
- BEGIN/END for algorithm boundaries
- IF/THEN/ELSE/ENDIF for selection
- FOR/NEXT with STEP for counted loops
- WHILE/ENDWHILE for conditional loops
- SET...TO or = for assignment
- INPUT/OUTPUT for I/O operations

---

## Notes for Instructor

- Each lesson includes embedded YouTube videos - ensure students watch before proceeding
- Flowchart diagrams use draw.io embedded iframes (NESA HSC standard symbols)
- Quiz questions (🧪) have expandable answers - encourage students to attempt before revealing
- Practice exercises (✍️) should be completed in pseudocode first, then optionally in Python
- Focus is on algorithm design, not Python syntax
- Emphasise tracing through algorithms with sample data
- The 6 fundamental patterns (Lesson 8) are the most important for problem-solving
- Recursion (Lesson 9) is advanced - ensure students have mastered loops first

## Resources

- YouTube videos embedded in each lesson
- draw.io for flowchart creation
- NESA HSC Software Design and Development syllabus
- HSC past papers for additional practice problems
