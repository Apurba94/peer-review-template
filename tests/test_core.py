import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from peer_review_template.cli import main
from peer_review_template.core import blank_answers, render_report, validate

SUMMARY = ("The authors test whether drought alters soil microbial diversity using a gradient of twelve field sites "
           "and amplicon sequencing, and report that diversity declines with aridity while carbon cycling slows.")


def filled():
    a = blank_answers("empirical")
    a.update({"manuscript_id": "MS-1", "title": "Drought and microbes", "summary": SUMMARY,
              "contribution": "Useful field evidence.", "major": ["Site effects are confounded with aridity."],
              "minor": ["Figure 2 axis labels are missing."], "recommendation": "major revision",
              "confidential": "Solid but overclaimed."})
    a["checks"] = {q: "yes" for q in a["checks"]}
    return a


class ReviewTests(unittest.TestCase):
    def test_blank_and_kinds(self):
        self.assertEqual(len(blank_answers("computational")["checks"]), 7)
        with self.assertRaises(ValueError):
            blank_answers("poem")

    def test_validation(self):
        self.assertEqual(validate(filled()), [])
        a = filled()
        a.update({"recommendation": "maybe", "summary": "Short.", "major": ["This is nonsense."]})
        a["checks"][next(iter(a["checks"]))] = ""
        text = " ".join(validate(a))
        for frag in ("recommendation must be", "summary is very short", "1 checklist item", "nonsense"):
            self.assertIn(frag, text)
        b = filled()
        b["major"] = []
        self.assertTrue(any("supported by major issues" in p for p in validate(b)))

    def test_render(self):
        report, editor = render_report(filled())
        self.assertIn("## Major comments\n\n1. Site effects", report)
        self.assertIn("| Is the sample size justified? | yes |", report)
        self.assertNotIn("Solid but overclaimed", report)
        self.assertIn("**Recommendation:** major revision", editor)

    def test_cli_render_and_interactive(self):
        with tempfile.TemporaryDirectory() as d:
            p, out, ed = (os.path.join(d, n) for n in ("a.json", "r.md", "e.md"))
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(filled(), fh)
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(["render", p, "-o", out, "--editor", ed]), 0)
            self.assertTrue(os.path.exists(ed))
            answers = iter(["MS-2", "T", SUMMARY, "contrib", "major 1", "", "", ] + ["yes"] * 8 + ["accept", ""])
            with redirect_stdout(io.StringIO()):
                main(["interactive", "-o", os.path.join(d, "i.json")], ask=lambda prompt: next(answers))
            with open(os.path.join(d, "i.json"), encoding="utf-8") as fh:
                a = json.load(fh)
            self.assertEqual((a["recommendation"], a["major"]), ("accept", ["major 1"]))


if __name__ == "__main__":
    unittest.main()
