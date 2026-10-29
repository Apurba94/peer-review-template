"""Structured peer-review reports from a guided questionnaire."""
from .core import QUESTIONNAIRES, RECOMMENDATIONS, blank_answers, validate, render_report

__version__ = "0.1.0"
__all__ = ["QUESTIONNAIRES", "RECOMMENDATIONS", "blank_answers", "validate", "render_report"]
