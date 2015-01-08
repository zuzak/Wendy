import unittest
from abbott.pluginbase import PluginBoss

from abbott.plugins.wotd import is_parrot


class TestParrot(unittest.TestCase):
    parrot_words = [
        ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
        ["My", "name", "is", "rajesh", "I'm", "a", "rajesh"]
    ]

    matches = [
        ["The", "quick", "brown", "fox", "jumps", "jumps", "with", "a", "cat"],
        ["My", "name", "is", "rajesh", "I'm", "a", "walrus"]
    ]
    non_matches = [
        ["The", "quick", "red", "fox", "jumps", "jumps", "with", "two", "cats"],
        ["Your", "name", "is", "bob", "you're", "a", "walrus"]
    ]

    high_match_ratio = 0.8
    matches_high_ratio = [
        ["The", "quick", "brown", "fox", "jumps", "over", "the", "energetic", "dog"],
        ["My", "name", "is", "rajesh", "I'm", "the", "rajesh"],
    ]
    non_matches_high_ratio = [
        ["The", "quick", "red", "fox", "jumps", "behind", "the", "energetic", "dog"],
        ["My", "name", "maybe", "rajesh", "I'm", "the", "rajesh"]
    ]

    low_match_ratio = 0.4
    matches_low_ratio = [
        ["The", "slow", "red", "fox", "falls", "over", "the", "crazy", "dog"],
        ["Your", "name", "is", "rajesh", "you're", "a", "rajesh"]
    ]
    non_matches_low_ratio = [
        ["The", "slow", "red", "hippopotamus", "falls", "over", "the", "crazy", "dog"],
        ["Your", "cat", "won't", "rajesh", "you're", "a", "walrus"]
    ]

    def test_matches(self):
        for match in self.matches:
            self.assertTrue(is_parrot(match, self.parrot_words))

    def test_non_matches(self):
        for non_match in self.non_matches:
            self.assertFalse(is_parrot(non_match, self.parrot_words))

    def test_matches_matchratio_high(self):
        for match in self.matches_high_ratio:
            self.assertTrue(is_parrot(match, self.parrot_words, self.high_match_ratio))

    def test_non_matches_matchratio_high(self):
        for match in self.non_matches_high_ratio:
            self.assertFalse(is_parrot(match, self.parrot_words, self.high_match_ratio))

    def test_matches_matchratio_low(self):
        for match in self.matches_low_ratio:
            self.assertTrue(is_parrot(match, self.parrot_words, self.low_match_ratio))

    def test_non_matches_matchratio_low(self):
        for match in self.non_matches_low_ratio:
            self.assertFalse(is_parrot(match, self.parrot_words, self.low_match_ratio))


if __name__ == "__main__":
    unittest.main()

