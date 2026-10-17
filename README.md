# OpenAI Dot Custom Rules Validator 🤖🛡️

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/6bf63407-78d6-4588-b0ae-a3e84fa163c4" />

An advanced static analysis linter engineered to prevent **logical contradictions**, **circular reference loops**, and **structural code/markdown failures** within custom behavioral rule files deployed to OpenAI's autonomous agents (Dots).

As OpenAI Dots run 24/7 in cloud environments with persistent memory, corrupted rules or paradoxical commands can cause execution loops, data leaks, or complete agent freeze states. This toolkit ensures code stability before production deployment.

## Key Features
* 🔍 **Contradiction Matrix Detection:** Flags logical locks (e.g., instructing the agent to "Always use public scopes" and "Keep everything private" within the same runtime context).
* 🔄 **Circular Dependency Identification:** Utilizes graph theory computation to parse and catch infinite reference loops across multi-line prompt rules.
* 📦 **Token & Variable Verification:** Analyzes unclosed tags and corrupted bracket structure (`{{variable}}`).

## Installation

```bash
git clone https://github.com
cd dot-rule-validator
pip install -r requirements.txt
```

## How To Run

To run a deep analysis linting check on your OpenAI Dot rule files, execute the following script target:

```bash
python dot_validator.py examples/invalid_rules.txt
```

## Contribution
Feel free to open an issue or submit a Pull Request to enrich the keywords dictionary inside the logical contradiction semantic matrix matrix.
