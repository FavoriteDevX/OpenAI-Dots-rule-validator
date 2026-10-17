#!/usr/bin/env python3
import unittest
import os
from dot_validator import DotRuleValidator

class TestDotRuleValidator(unittest.TestCase):
    def setUp(self):
        # Create temporary clean and dirty rule files for testing
        self.valid_file = "temp_valid_rules.txt"
        self.invalid_file = "temp_invalid_rules.txt"
        
        with open(self.valid_file, "w", encoding="utf-8") as f:
            f.write("Rule 1: Always be concise.\nRule 2: Keep API keys private.")
            
        with open(self.invalid_file, "w", encoding="utf-8") as f:
            f.write("Rule 1: Always be concise and follow Rule 2.\n")
            f.write("Rule 2: Always be verbose and follow Rule 1.\n")
            f.write("Rule 3: {{broken_variable")

    def tearDown(self):
        # Clean up temporary files after tests run
        if os.path.exists(self.valid_file):
            os.remove(self.valid_file)
        if os.path.exists(self.invalid_file):
            os.remove(self.invalid_file)

    def test_valid_rules_pass(self):
        validator = DotRuleValidator(self.valid_file)
        validator.load_rules()
        
        syntax_errs = validator.check_syntax_and_placeholders()
        validator.detect_contradictions()
        
        self.assertEqual(len(syntax_errs), 0)
        self.assertEqual(len(validator.contradictions_found), 0)

    def test_invalid_rules_fail(self):
        validator = DotRuleValidator(self.invalid_file)
        validator.load_rules()
        
        syntax_errs = validator.check_syntax_and_placeholders()
        validator.detect_contradictions()
        circular_errs = validator.detect_circular_dependencies()
        
        # Should catch the missing closing bracket
        self.assertTrue(len(syntax_errs) > 0)
        # Should catch the concise vs verbose contradiction on shared topics
        self.assertTrue(len(validator.contradictions_found) > 0)
        # Should catch Rule 1 referencing Rule 2 and vice-versa
        self.assertTrue(len(circular_errs) > 0)

if __name__ == "__main__":
    unittest.main()
