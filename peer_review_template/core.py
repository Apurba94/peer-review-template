"""Questionnaires per manuscript type; answers (JSON) are rendered into a report for authors and a
confidential note for the editor."""
import re

RECOMMENDATIONS = ("accept", "minor revision", "major revision", "reject and resubmit", "reject")

COMMON = [
    ("summary", "Summarize the manuscript's question, approach and main findings in 3-5 sentences.", "text"),
    ("contribution", "What is new and why does it matter to the field?", "text"),
    ("major", "Major issues (validity of conclusions, design flaws, missing analyses).", "list"),
    ("minor", "Minor issues (clarity, presentation, typos, references).", "list"),
]
CHECKS = {
    "empirical": [
        "Is the research question clearly stated?",
        "Are the methods described in enough detail to reproduce the work?",
        "Is the sample size justified?",
        "Are statistical analyses appropriate and fully reported (effect sizes, uncertainty)?",
        "Do the conclusions follow from the results?",
        "Are data and code available or is their absence justified?",
        "Are limitations discussed?",
        "Are ethics approvals and consent reported where relevant?",
    ],
    "computational": [
        "Is the method compared with appropriate baselines and the state of the art?",
        "Are datasets, splits and preprocessing fully described?",
        "Are results averaged over several runs/seeds with variability reported?",
        "Is the code available and documented?",
        "Are ablations provided for the main design choices?",
        "Are computational costs reported?",
        "Do the claims match the evidence?",
    ],
    "review": [
        "Is the literature search systematic and transparently reported (e.g. PRISMA)?",
        "Is the coverage of the literature balanced and up to date?",
        "Are inclusion/exclusion criteria stated?",
        "Is risk of bias assessed?",
        "Does the review offer synthesis rather than a list of studies?",
    ],
}
QUESTIONNAIRES = {k: COMMON for k in CHECKS}


def blank_answers(kind="empirical"):
    if kind not in CHECKS:
        raise ValueError("kind must be one of %s" % ", ".join(CHECKS))
    a = {"manuscript_id": "", "title": "", "kind": kind, "recommendation": "", "confidential": ""}
    for key, _, typ in QUESTIONNAIRES[kind]:
        a[key] = [] if typ == "list" else ""
    a["checks"] = {q: "" for q in CHECKS[kind]}      # yes / no / partly / n/a, optional comment after ':'
    return a


def validate(a):
    problems = []
    kind = a.get("kind", "empirical")
    if a.get("recommendation", "").lower() not in RECOMMENDATIONS:
        problems.append("recommendation must be one of: " + ", ".join(RECOMMENDATIONS))
    if len(re.findall(r"\w+", a.get("summary", ""))) < 25:
        problems.append("summary is very short (editors use it to judge whether you understood the paper)")
    if a.get("recommendation") in ("major revision", "reject", "reject and resubmit") and not a.get("major"):
        problems.append("a %s recommendation should be supported by major issues" % a["recommendation"])
    unanswered = [q for q, v in a.get("checks", {}).items() if not str(v).strip()]
    if unanswered:
        problems.append("%d checklist item(s) unanswered" % len(unanswered))
    harsh = re.findall(r"(?i)\b(stupid|nonsense|incompetent|ridiculous|worthless|sloppy|lazy)\b",
                       " ".join([a.get("summary", ""), a.get("contribution", "")] + a.get("major", []) + a.get("minor", [])))
    if harsh:
        problems.append("consider rephrasing unprofessional wording: %s" % ", ".join(sorted(set(w.lower() for w in harsh))))
    if kind not in CHECKS:
        problems.append("unknown manuscript kind %r" % kind)
    return problems


def render_report(a):
    """Return (report_for_authors, note_for_editor) as Markdown strings."""
    lines = ["# Review of manuscript %s" % (a.get("manuscript_id") or ""), ""]
    if a.get("title"):
        lines += ["*%s*" % a["title"], ""]
    lines += ["## Summary", "", a.get("summary", "").strip(), ""]
    if a.get("contribution"):
        lines += ["## Assessment of the contribution", "", a["contribution"].strip(), ""]
    for key, head in (("major", "Major comments"), ("minor", "Minor comments")):
        items = [x for x in a.get(key, []) if x.strip()]
        if items:
            lines += ["## %s" % head, ""] + ["%d. %s" % (i, x.strip()) for i, x in enumerate(items, 1)] + [""]
    checks = a.get("checks", {})
    if checks:
        lines += ["## Checklist", "", "| Question | Answer |", "|---|---|"]
        lines += ["| %s | %s |" % (q, (v or "-").replace("|", "/")) for q, v in checks.items()]
        lines.append("")
    words = len(re.findall(r"\w+", "\n".join(lines)))
    editor = ["# Confidential comments to the editor", "", "**Recommendation:** %s" % (a.get("recommendation") or "?"), "",
              (a.get("confidential") or "").strip(), "", "Report length: %d words; %d major and %d minor comment(s)." % (
                  words, len(a.get("major", [])), len(a.get("minor", [])))]
    return "\n".join(lines) + "\n", "\n".join(editor) + "\n"
