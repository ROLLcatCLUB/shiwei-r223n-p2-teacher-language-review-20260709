from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "R223N_P2_teacher_default_reading_draft_v3.md",
    "R223N_P2_teacher_default_reading_draft_v3.html",
    "R223N_P2_label_humanization_rules.md",
    "R223N_P2_template_phrase_cleanup_report.md",
    "R223N_P2_before_after_compare_with_P1.md",
    "R223N_P2_report.md",
    "validate_1013R_R223N_P2_teacher_language_humanization.py",
    "PACKAGE_MANIFEST.json",
    "README_FOR_GPT_REVIEW.md",
]

TECH_LABELS = [
    "本环节在做什么",
    "教师关注",
    "课堂展开",
    "任务释放",
    "学生观察 / 操作",
    "教师追问 / 调控",
    "投屏 / 对比 / 示范",
    "可能偏差与应对",
    "证据收束与过渡",
    "下游影响",
]

TEMPLATE_PHRASES = [
    "教师用一句任务语把问题抛出来",
    "学生先做最小动作",
    "预期能出现",
    "教师让学生把看到、摸到或试到的证据指出来",
    "追问只抓一个关键点，避免把环节讲散",
    "随后过渡到下一环节",
]

BANNED = ["【小教判断】", "review_view_only", "xiaojiao_judgement_full", "完整组件触发矩阵", "聊天"]
BOUNDARY_FALSE = ["r97b_modified", "ui_modified", "runtime_connected", "provider_model_connected", "database_written", "formal_apply_allowed"]


def clean_code(md):
    return re.sub(r"```.*?```", "", md, flags=re.S)


def paras(md):
    return [p.strip() for p in re.split(r"\n\s*\n", clean_code(md)) if p.strip()]


def check(cond, msg, failures):
    if not cond:
        failures.append(msg)


def main():
    failures = []
    check_count = 0
    for name in REQUIRED:
        check_count += 1
        check((ROOT / name).exists(), f"missing {name}", failures)

    md = (ROOT / "R223N_P2_teacher_default_reading_draft_v3.md").read_text(encoding="utf-8")
    html = (ROOT / "R223N_P2_teacher_default_reading_draft_v3.html").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    cleanup = (ROOT / "R223N_P2_template_phrase_cleanup_report.md").read_text(encoding="utf-8")
    compare = (ROOT / "R223N_P2_before_after_compare_with_P1.md").read_text(encoding="utf-8")

    body = clean_code(md)
    tech_count = sum(body.count(t) for t in TECH_LABELS)
    phrase_count = sum(body.count(t) for t in TEMPLATE_PHRASES)

    check_count += 1
    check(md.count("### （") == 7, "expected 7 event sections", failures)
    check_count += 1
    check(md.count("**这一环节要解决什么。**") == 7, "expected 7 humanized intent blocks", failures)
    check_count += 1
    check(md.count("**如果学生卡住。**") == 7, "expected 7 stuck blocks", failures)
    check_count += 1
    check(md.count("**留下什么，再往哪走。**") == 7, "expected 7 evidence transition blocks", failures)
    check_count += 1
    check(md.count("**大屏、学习单和评价怎么跟上。**") == 7, "expected 7 downstream summaries", failures)
    check_count += 1
    check(tech_count == 0, f"technical labels remain: {tech_count}", failures)
    check_count += 1
    check(phrase_count == 0, f"template phrases remain: {phrase_count}", failures)
    for term in BANNED:
        check_count += 1
        check(term not in md, f"default draft exposes banned term: {term}", failures)
    check_count += 1
    check("投屏" in md and "学习单" in md and "评价" in md, "screen/sheet/evaluation signals missing", failures)
    check_count += 1
    check("学生" in md and "教师" in md, "student/teacher signals missing", failures)
    check_count += 1
    check("<p class='intent'>" in html and "<p class='stuck'>" in html, "html lacks humanized styling", failures)
    check_count += 1
    check("显性技术标签数量" in compare and "大幅减少" in compare, "comparison report lacks technical-label reduction evidence", failures)
    check_count += 1
    check("模板句数量" in compare and "清理到 0" in compare and "P1 次数" in cleanup, "cleanup report lacks template-phrase cleanup evidence", failures)

    long_count = sum(1 for p in paras(md) if len(p) > 360)
    max_para = max((len(p) for p in paras(md)), default=0)
    check_count += 1
    check(long_count <= 2, "too many long paragraphs", failures)
    check_count += 1
    check(max_para <= 520, "max paragraph too long", failures)

    boundary = manifest.get("boundary", {})
    for key in BOUNDARY_FALSE:
        check_count += 1
        check(boundary.get(key) is False, f"boundary {key} must be false", failures)

    result = {
        "passed": not failures,
        "check_count": check_count,
        "failed": len(failures),
        "failures": failures,
        "event_count": 7,
        "technical_label_count": tech_count,
        "template_phrase_count": phrase_count,
        "long_paragraph_count": long_count,
        "max_paragraph_chars": max_para,
    }
    (ROOT / "validate_1013R_R223N_P2_teacher_language_humanization_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
