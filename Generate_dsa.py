import os
import json
import datetime
from pathlib import Path
from google import genai

# Structured curriculum covering Sem-1 C/Python + Summer 2027 Internship DSA
CURRICULUM = [
    ("Arrays", "Two Sum & Pair Target Lookup"),
    ("Arrays", "Kadane's Algorithm - Maximum Subarray Sum"),
    ("Arrays", "Dutch National Flag - Sort 0s, 1s, and 2s"),
    ("Arrays", "Rotate Matrix by 90 Degrees In-Place"),
    ("Strings", "Valid Anagram & Frequency Counter"),
    ("Strings", "Longest Palindromic Substring"),
    ("Pointers & Memory", "Reverse an Array Using Pointers in C"),
    ("Searching", "Binary Search on Sorted Array & First/Last Occurrence"),
    ("Searching", "Search in Rotated Sorted Array"),
    ("Sorting", "Merge Sort with Step-by-Step Divide and Conquer"),
    ("Sorting", "Quick Sort with Partition Dry Run"),
    ("Recursion", "Tower of Hanoi & Call Stack Trace"),
    ("Recursion", "Generate All Subsets (Power Set)"),
    ("Linked List", "Reverse a Singly Linked List (Iterative & Recursive)"),
    ("Linked List", "Floyd's Cycle Detection (Tortoise and Hare)"),
    ("Stacks", "Valid Parentheses & Expression Balancing"),
    ("Stacks", "Next Greater Element Using Monotonic Stack"),
    ("Queues", "Circular Queue Implementation Using Arrays"),
    ("Trees", "Binary Tree Inorder, Preorder, and Postorder Traversals"),
    ("Trees", "Lowest Common Ancestor in a Binary Search Tree"),
    ("Graphs", "Breadth-First Search (BFS) & Shortest Path in Unweighted Graph"),
    ("Graphs", "Depth-First Search (DFS) & Cycle Detection"),
    ("Dynamic Programming", "0/1 Knapsack Problem (Memoization & Tabulation)"),
    ("Dynamic Programming", "Longest Common Subsequence (LCS)"),
    ("OS Algorithms", "CPU Scheduling - Shortest Job First (SJF) & Round Robin"),
]

PROGRESS_FILE = Path("progress.json")
README_FILE = Path("README.md")


def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed_days": 0, "history": []}


def generate_content(client, day_num, category, title):
    prompt = f"""You are a senior CSE mentor helping a B.Tech CSE student build a daily DSA & C/Python portfolio for Summer 2027 internships.
Generate a complete, well-structured Markdown study & code guide for:
- **Day**: Day {day_num:02d}
- **Category**: {category}
- **Problem**: {title}

Include these exact sections:
1. **Problem Statement & Real-World Intuition** (with sample input/output)
2. **Step-by-Step Dry Run Table** (showing how variables/pointers change at each step)
3. **Optimal Python Solution** (clean, well-commented code)
4. **Optimal C Solution** (clean, pointer-safe code for university exams)
5. **Time & Space Complexity Analysis** (Best, Average, and Worst case)
6. **3 Key Interview / Viva Takeaways**
"""
    for model_name in ["gemini-2.5-pro", "gemini-2.5-flash"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Model {model_name} failed: {e}. Trying fallback...")
    raise RuntimeError("All Gemini models failed to generate DSA content.")


def update_readme(history):
    lines = [
        "# 🚀 Daily DSA & Systems Engineering Log",
        "",
        "Automated daily problem-solving repository maintained by **Nayan Gadhiya** (B.Tech CSE). Covers **Data Structures, Algorithms, C Pointers, Python, and OS Concepts** with step-by-step dry runs and complexity analysis.",
        "",
        f"**Total Days Completed:** `{len(history)}` | **Last Updated:** `{datetime.date.today().isoformat()}`",
        "",
        "## 📚 Progress Tracker",
        "",
        "| Day | Date | Category | Problem | Solution Link |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for item in reversed(history):
        lines.append(
            f"| **Day {item['day']:02d}** | {item['date']} | `{item['category']}` | {item['title']} | [View Guide]({item['path']}) |"
        )
    README_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing!")

    client = genai.Client(api_key=api_key)
    progress = load_progress()
    day_num = progress["completed_days"] + 1

    # Pick curriculum topic or dynamically expand after list finishes
    if day_num <= len(CURRICULUM):
        category, title = CURRICULUM[day_num - 1]
    else:
        category = "Advanced DSA & Interview Prep"
        title = f"Must-Know Coding Interview Pattern #{day_num}"

    markdown_body = generate_content(client, day_num, category, title)

    safe_slug = (
        title.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("'", "")
        .replace("-", "_")[:35]
    )
    folder = Path(f"solutions/Day_{day_num:02d}_{safe_slug}")
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / "README.md"
    file_path.write_text(markdown_body, encoding="utf-8")

    today_str = datetime.date.today().isoformat()
    progress["completed_days"] = day_num
    progress["history"].append(
        {
            "day": day_num,
            "date": today_str,
            "category": category,
            "title": title,
            "path": file_path.as_posix(),
        }
    )

    PROGRESS_FILE.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    update_readme(progress["history"])
    print(f"Successfully generated Day {day_num:02d}: {title}")


if __name__ == "__main__":
    main()
  
