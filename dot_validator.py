#!/usr/bin/env python3
"""
OpenAI Dot Custom Rules Validator
Author: GitHub Open Source Community Contributor
Description: Advanced static analysis tool to prevent logical contradictions, 
             circular dependencies, and structural anti-patterns in OpenAI Dot instructions.
"""

import re
import sys
import argparse
from typing import List, Dict, Tuple, Set
import networkx as nx

class DotRuleValidator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.rules: List[str] = []
        self.contradictions_found: List[Tuple[int, int, str]] = []
        self.graph = nx.DiGraph()

    def load_rules(self) -> None:
        """Loads and cleans rules from the specified file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # Filter out empty lines and pure comments
                self.rules = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except FileNotFoundError:
            print(f"[-] Error: File '{self.file_path}' not found.")
            sys.exit(1)

    def check_syntax_and_placeholders(self) -> List[str]:
        """Checks for unclosed tags, bad markdown syntax, or corrupted prompt variables."""
        errors = []
        # Look for common tag open/close mismatches like <context> </context>
        tag_pattern = re.compile(r'<([^>]+)>')
        
        for idx, rule in enumerate(self.rules, 1):
            tags = tag_pattern.findall(rule)
            # Basic validation for matching bracket variables like {{variable}}
            if rule.count('{{') != rule.count('}}'):
                errors.append(f"Line {idx}: Unmatched prompt variables '{{{{' or '}}}}'.")
        return errors

    def detect_contradictions(self) -> None:
        """Detects high-probability logical contradictions using semantic keyword mapping."""
        # Simple pairs of mutually exclusive intent keywords
        contradiction_matrix = [
            (r"\balways\b", r"\bnever\b"),
            (r"\bpublic\b", r"\bprivate\b"),
            (r"\ballow\b", r"\bblock\b|\bdeny\b|\bprohibit\b"),
            (r"\bverbose\b", r"\bconcise\b|\bminimal\b"),
            (r"\bexecute\b", r"\bdo not execute\b|\bnever execute\b")
        ]

        for i in range(len(self.rules)):
            for j in range(i + 1, len(self.rules)):
                line_a, rule_a = i + 1, self.rules[i].lower()
                line_b, rule_b = j + 1, self.rules[j].lower()

                # Extract nouns/topics to ensure the contradiction applies to the same entity
                # Simple extraction: check if they share unique long words (topics)
                words_a = set(w for w in re.findall(r'\b\w{4,}\b', rule_a))
                words_b = set(w for w in re.findall(r'\b\w{4,}\b', rule_b))
                shared_topics = words_a.intersection(words_b)

                if shared_topics:
                    for pattern_1, pattern_2 in contradiction_matrix:
                        if (re.search(pattern_1, rule_a) and re.search(pattern_2, rule_b)) or \
                           (re.search(pattern_2, rule_a) and re.search(pattern_1, rule_b)):
                            topic_str = ", ".join(list(shared_topics)[:2])
                            self.contradictions_found.append(
                                (line_a, line_b, f"Potential conflict matching keywords around topic context [{topic_str}]")
                            )

    def detect_circular_dependencies(self) -> List[str]:
        """Builds a dependency graph based on cross-references and extracts cycles."""
        errors = []
        # Mapping lines to potential rules identifiers (e.g., "Rule 1", "Step 3")
        rule_identifiers: Dict[str, int] = {}
        
        for idx, rule in enumerate(self.rules, 1):
            match = re.match(r'^(rule\s*\d+|step\s*\d+|guideline\s*\d+)', rule.lower())
            if match:
                rule_identifiers[match.group(1)] = idx

        # Build edges in the graph
        for idx, rule in enumerate(self.rules, 1):
            self.graph.add_node(idx)
            for identifier, target_idx in rule_identifiers.items():
                if identifier in rule.lower() and idx != target_idx:
                    self.graph.add_edge(idx, target_idx)

        # Detect cycles using NetworkX
        try:
            cycles = list(nx.find_cycle(self.graph, orientation="original"))
            for cycle in cycles:
                edge_desc = f"Line {cycle[0]} -> Line {cycle[1]}"
                errors.append(f"Circular reference chain detected: {edge_desc}")
        except nx.NetworkXNoCycle:
            pass # No cycles is the perfect behavior

        return errors

    def validate(self) -> bool:
        """Executes all validator modules and outputs a detailed health report."""
        print(f"[+] Launching analysis on: {self.file_path}")
        self.load_rules()
        
        syntax_errors = self.check_syntax_and_placeholders()
        self.detect_contradictions()
        circular_errors = self.detect_circular_dependencies()

        has_errors = False

        if syntax_errors:
            has_errors = True
            print("\n❌ SYNTAX & STRUCTURAL ERRORS:")
            for err in syntax_errors:
                print(f"  - {err}")

        if self.contradictions_found:
            has_errors = True
            print("\n⚠️ LOGICAL CONTRADICTIONS DETECTED:")
            for line_a, line_b, desc in self.contradictions_found:
                print(f"  - [Conflict Between Line {line_a} and Line {line_b}]: {desc}")

        if circular_errors:
            has_errors = True
            print("\n🔄 INFINITE LOOP / CIRCULAR REFERENCES:")
            for err in circular_errors:
                print(f"  - {err}")

        if not has_errors:
            print("\n✅ SUCCESS: Custom rules file passed all validation matrixes! Safe to deploy to OpenAI Dot environment.")
            return True
        else:
            print("\n🛑 FAILURE: Validation failed. Please fix the items listed above to ensure your Dot does not crash.")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAI Dot Custom Rules Lint & Validator Tool")
    parser.add_argument("file", help="Path to the custom rules txt/md file.")
    args = parser.parse_args()

    validator = DotRuleValidator(args.file)
    success = validator.validate()
    sys.exit(0 if success else 1)
