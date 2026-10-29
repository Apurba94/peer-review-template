"""Command-line interface for peer-review-template."""
import argparse
import json
import sys

from .core import CHECKS, QUESTIONNAIRES, RECOMMENDATIONS, blank_answers, render_report, validate


def interactive(kind, ask=input):
    a = blank_answers(kind)
    a["manuscript_id"] = ask("Manuscript ID: ").strip()
    a["title"] = ask("Title: ").strip()
    for key, prompt, typ in QUESTIONNAIRES[kind]:
        if typ == "list":
            print(prompt + " (one per line, empty line to finish)")
            while True:
                item = ask("  - ").strip()
                if not item:
                    break
                a[key].append(item)
        else:
            a[key] = ask(prompt + "\n> ").strip()
    for q in CHECKS[kind]:
        a["checks"][q] = ask("%s [yes/no/partly/n/a]: " % q).strip() or "n/a"
    rec = ""
    while rec not in RECOMMENDATIONS:
        rec = ask("Recommendation (%s): " % " / ".join(RECOMMENDATIONS)).strip().lower()
    a["recommendation"] = rec
    a["confidential"] = ask("Confidential comments to the editor (optional): ").strip()
    return a


def main(argv=None, ask=input):
    ap = argparse.ArgumentParser(prog="peer-review-template", description="Write structured peer-review reports.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="write a blank answers JSON to fill in")
    n.add_argument("-k", "--kind", choices=sorted(CHECKS), default="empirical")
    n.add_argument("-o", "--output", default="review.json")
    i = sub.add_parser("interactive", help="answer the questionnaire in the terminal")
    i.add_argument("-k", "--kind", choices=sorted(CHECKS), default="empirical")
    i.add_argument("-o", "--output", default="review.json")
    r = sub.add_parser("render", help="turn an answers JSON into the report")
    r.add_argument("answers")
    r.add_argument("-o", "--output", help="report file for authors (Markdown)")
    r.add_argument("--editor", help="file for the confidential editor note")
    r.add_argument("--force", action="store_true", help="render even if validation finds problems")
    args = ap.parse_args(argv)
    if args.cmd in ("new", "interactive"):
        a = blank_answers(args.kind) if args.cmd == "new" else interactive(args.kind, ask)
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(a, fh, indent=2)
        print("wrote %s" % args.output)
        return 0
    with open(args.answers, encoding="utf-8") as fh:
        a = json.load(fh)
    problems = validate(a)
    for p in problems:
        print("check: " + p, file=sys.stderr)
    if problems and not args.force:
        print("fix the issues above or use --force", file=sys.stderr)
        return 1
    report, editor = render_report(a)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
    else:
        sys.stdout.write(report)
    if args.editor:
        with open(args.editor, "w", encoding="utf-8") as fh:
            fh.write(editor)
    return 0
