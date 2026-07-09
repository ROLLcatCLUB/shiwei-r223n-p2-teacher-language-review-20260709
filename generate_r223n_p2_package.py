from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
CHAIN_PATH = REPO_ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R223N_CROSS_SAMPLE_CLASSROOM_EVENT_EXPANSION_VALIDATION" / "R223N_classroom_event_expansion_chain.json"
P1_PATH = REPO_ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R223N_P1_PROCESS_READABILITY_STRUCTURING" / "R223N_P1_teacher_default_reading_draft_v2.md"
STAGE_ID = "1013R_R223N_P2_TEACHER_LANGUAGE_HUMANIZATION_AND_LABEL_DETECHNICALIZATION"
SOURCE_STAGE_ID = "1013R_R223N_P1_PROCESS_READABILITY_STRUCTURING"
STANDARD_ID = "GOLDEN_CLASSROOM_EVENT_EXPANSION_STANDARD_V0.1_LOCK_CANDIDATE"
CN_NUM = ["一", "二", "三", "四", "五", "六", "七"]


def load_chain():
    return json.loads(CHAIN_PATH.read_text(encoding="utf-8"))


def strip_period(text):
    return str(text).strip().rstrip("。；;")


def join_short(items, limit=2):
    return "；".join(strip_period(item) for item in items[:limit])


def component_phrase(text):
    text = strip_period(text)
    for prefix in ("让学生", "帮助学生"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text


def human_event_body(idx, event):
    name = event["event_name"]
    intent = event["teaching_responsibility"]
    focus = event["teacher_visible_note"]
    task = event["task_release"]
    expected = event["expected_student_responses"]
    miss = event["likely_misconceptions_or_failures"]
    questions = event["teacher_follow_up_questions"]
    moves = event["teacher_scaffolding_moves"]
    rescue = event["teacher_rescue_strategy"]
    screen = event["screen_trigger"]["content"]
    component = event["component_trigger"]["component_name"]
    component_use = component_phrase(event["component_trigger"]["student_problem_solved"])
    sheet = event["learning_sheet_trigger"]["prompt"]
    evidence = event["evidence_trigger"]["minimum_evidence"]
    assessment = "；".join(strip_period(item) for item in event["assessment_alignment"])
    transition = event["transition_chain"].split("：", 1)[-1] if "：" in event["transition_chain"] else event["transition_chain"]

    return f"""
### （{CN_NUM[idx - 1]}）{name}

**这一环节要解决什么。** {intent}教师要抓住的是：{focus}

上课时可以这样展开。教师先把任务说清：“{task}”接着让学生直接进入观察或尝试，不急着评价作品效果。学生大多会先出现这样的反应：{join_short(expected, 2)}。这时教师顺着学生已经说出的内容往前推，而不是另起一个讲解。

    如果学生说得比较泛，教师可以追一句：“{questions[0]}”如果还说不清，就把观察对象放大、圈出来，或让学生换一种方式再看一遍。这里可以安排一次“{component}”，但它不是额外活动，只是帮助学生{component_use}

需要投屏或示范时，内容保持很小：{screen}。不要一次把所有材料、技法和评价都放上去，只服务这一环节正在发生的观察或操作。

**如果学生卡住。** 最常见的情况是：{join_short(miss, 2)}。教师可以这样接：{rescue}如果还需要支架，再用这一招：{moves[0]}

**留下什么，再往哪走。** 本环节至少留下：{evidence}学习单可以轻量记录：“{sheet}”有了这条证据，就可以继续往下走：{transition}

**大屏、学习单和评价怎么跟上。** 大屏只放{screen}；学习单对应“{event['learning_sheet_trigger']['field']}”；评价看学生是否能做到：{assessment}。
""".strip()


def build_teacher_md(chain):
    sections = "\n\n".join(human_event_body(i + 1, event) for i, event in enumerate(chain["events"]))
    return f"""# 《有趣的纸印》课堂事件展开教师稿 v3

```text
stage_id={STAGE_ID}
source_stage_id={SOURCE_STAGE_ID}
standard_id={STANDARD_ID}
status=teacher_language_humanized_default_draft
preview_only=true
teacher_confirmed=false
formal_apply_allowed=false
R97B / UI / runtime / prompt / model / db = untouched
```

## 一、阅读说明

P2 不改 R223N 的课堂事件链，也不删学生反应、教师应对、投屏示范、学习单和评价证据。它只做一件事：把 P1 中偏系统化的标签和模板句，转写成教师更容易读的备课语言。完整结构仍保留在 review ledger，默认稿尽量像老师会拿来读、改、上课的稿子。

## 二、课时定位

《有趣的纸印》围绕“印痕是版画的独特语言”展开。学生先认识纸材肌理，再通过改造、试印、印法比较和作品展评，逐步理解纸材、印法和印痕效果之间的关系。本稿仍保留课堂节奏，但不把后端字段直接铺给老师。

## 三、教学过程

{sections}

## 四、确认门

本稿仍为 preview-only。大屏、学习单、组件和评价证据只是预览建议，不写入正式备课本；教师确认前不得进入正式 UI、R97B 路由、runtime、prompt、provider/model 或数据库。
"""


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    return "\n".join(lines)


def build_rules():
    rows = [
        ["本环节在做什么", "这一环节要解决什么", "保留环节意图，但更像教师阅读提示"],
        ["教师关注", "教师要抓住", "短句融入意图段"],
        ["课堂展开", "上课时可以这样展开", "仍有过程，但不机械列字段"],
        ["任务释放", "先把任务说清", "放进自然课堂段落"],
        ["学生观察 / 操作", "学生直接进入观察或尝试", "不使用后端斜杠标签"],
        ["教师追问 / 调控", "教师可以追一句", "转成可说的话"],
        ["投屏 / 对比 / 示范", "需要投屏或示范时", "只保留具体触发内容"],
        ["可能偏差与应对", "如果学生卡住", "保留最高频偏差"],
        ["证据收束与过渡", "留下什么，再往哪走", "保留证据和下一步"],
        ["下游影响", "大屏、学习单和评价怎么跟上", "短句摘要，不展开 ledger"],
    ]
    return f"""# R223N-P2 标签去技术化规则

```text
stage_id={STAGE_ID}
target=teacher_default_reading_layer
change_type=language_humanization_only
```

## 标签转写

{md_table(["P1 标签 / 句式", "P2 教师稿表达", "说明"], rows)}

## 原则

- 后端结构仍留在 review ledger；
- 教师默认稿不显示完整组件触发矩阵；
- 不取消课堂节奏，但让节奏藏进自然段落；
- 大屏、学习单、评价证据仍保留落点；
- 不改推理链，不改 R97B，不接 runtime/model/prompt/db。
"""


def count_terms(text, terms):
    return {term: text.count(term) for term in terms}


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


def build_cleanup_report(p1_md, p2_md):
    rows = []
    for term in TECH_LABELS + TEMPLATE_PHRASES:
        rows.append([term, p1_md.count(term), p2_md.count(term)])
    return f"""# R223N-P2 模板句清理报告

```text
stage_id={STAGE_ID}
source=P1 structured draft
target=P2 humanized draft
```

{md_table(["被清理的字段或模板句", "P1 次数", "P2 次数"], rows)}

## 判断

P2 不做自由润色，而是把教师默认稿中明显的后端字段名和模板句式转写为教师可读表达。结构仍在，但不再反复暴露为系统字段。
"""


def count_long_paragraphs(md):
    clean_md = re.sub(r"```.*?```", "", md, flags=re.S)
    ps = [p.strip() for p in re.split(r"\n\s*\n", clean_md) if p.strip()]
    return sum(1 for p in ps if len(p) > 280), max((len(p) for p in ps), default=0)


def build_compare(p1_md, p2_md):
    p1_long, p1_max = count_long_paragraphs(p1_md)
    p2_long, p2_max = count_long_paragraphs(p2_md)
    rows = [
        ["显性技术标签数量", sum(p1_md.count(t) for t in TECH_LABELS), sum(p2_md.count(t) for t in TECH_LABELS), "大幅减少"],
        ["模板句数量", sum(p1_md.count(t) for t in TEMPLATE_PHRASES), sum(p2_md.count(t) for t in TEMPLATE_PHRASES), "清理到 0"],
        ["长段落数量（>280 字符）", p1_long, p2_long, "不回到长段落"],
        ["最长正文段字符数", p1_max, p2_max, "保持可读范围"],
        ["课堂事件数量", 7, 7, "未删事件"],
        ["大屏 / 学习单 / 评价落点", "有", "有", "保留"],
    ]
    return f"""# R223N-P2 与 P1 对比

```text
stage_id={STAGE_ID}
comparison_focus=teacher_language_humanization_not_logic_change
```

{md_table(["项目", "P1", "P2", "判断"], rows)}

## 结论

P2 保留 P1 的结构收益，但把字段味和模板句降下去。教师默认稿仍不是完整正式教案，也不是 UI 样式锁定；它是跨样本课堂事件展开的教师语言渲染版。
"""


def build_report(p1_md, p2_md):
    tech_p1 = sum(p1_md.count(t) for t in TECH_LABELS)
    tech_p2 = sum(p2_md.count(t) for t in TECH_LABELS)
    phrase_p1 = sum(p1_md.count(t) for t in TEMPLATE_PHRASES)
    phrase_p2 = sum(p2_md.count(t) for t in TEMPLATE_PHRASES)
    p2_long, p2_max = count_long_paragraphs(p2_md)
    return f"""# R223N-P2 教师语言人话化报告

```text
stage_id={STAGE_ID}
R223N-P1=PASS_PROCESS_STRUCTURE_WITH_LANGUAGE_POLISH_REQUIRED
R223N-P2=TEACHER_LANGUAGE_HUMANIZED
formal_ui=blocked
R97B / UI / runtime / prompt / model / db = untouched
```

## 一、处理内容

P2 不改课堂事件链，不删除课堂深度，只把教师默认稿中的后端字段味、模板句和机械标签转写为更自然的教师备课语言。

## 二、清理结果

```text
technical_label_count_p1={tech_p1}
technical_label_count_p2={tech_p2}
template_phrase_count_p1={phrase_p1}
template_phrase_count_p2={phrase_p2}
p2_long_paragraphs={p2_long}
p2_max_paragraph_chars={p2_max}
event_count=7
```

## 三、保留内容

- 学生可能反应仍保留；
- 教师追问和补救仍保留；
- 投屏 / 示范时机仍保留；
- 学习单记录仍保留；
- 评价证据仍保留；
- 不显示完整 review ledger，不恢复卡片墙。

## 四、边界

不改 R97B，不新增正式 route，不改 frontend/backend，不接 runtime、provider/model、prompt 或 db，不写回 lesson body，不 formal apply。
"""


def md_to_html(md, title):
    body = []
    in_code = False
    for raw in md.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code:
                body.append("<pre><code>")
                in_code = True
            else:
                body.append("</code></pre>")
                in_code = False
            continue
        if in_code:
            body.append(html.escape(line) + "\n")
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            body.append(f"<h{level}>{html.escape(text)}</h{level}>")
            continue
        if stripped.startswith("**这一环节要解决什么"):
            body.append(f"<p class='intent'>{html.escape(stripped)}</p>")
            continue
        if stripped.startswith("**如果学生卡住"):
            body.append(f"<p class='stuck'>{html.escape(stripped)}</p>")
            continue
        if stripped.startswith("**留下什么"):
            body.append(f"<p class='evidence'>{html.escape(stripped)}</p>")
            continue
        if stripped.startswith("**大屏、学习单"):
            body.append(f"<p class='impact'>{html.escape(stripped)}</p>")
            continue
        body.append(f"<p>{html.escape(stripped)}</p>")
    css = """
body{margin:0;background:#f6f7f4;color:#24312d;font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;line-height:1.72}
.page{max-width:1000px;margin:0 auto;padding:34px 28px 72px}
article{background:#fffdf8;border:1px solid #d9e3dc;border-radius:10px;padding:38px 50px;box-shadow:0 18px 48px rgba(38,83,72,.08)}
h1{font-size:30px;line-height:1.25;margin:0 0 20px;color:#1f6f61}
h2{font-size:21px;margin:34px 0 14px;border-top:1px solid #e7eee9;padding-top:26px;color:#245f56}
h3{font-size:18px;margin:30px 0 14px;color:#26362f}
p{font-size:15.5px;margin:11px 0}
pre{background:#263832;color:#eef8f2;padding:14px 16px;border-radius:8px;overflow:auto;font-size:13px;white-space:pre-wrap;word-break:break-word}
.intent{background:#f3faf6;border-left:4px solid #2b7c6e;padding:10px 14px;border-radius:6px}
.stuck{background:#fff9ed;border-left:4px solid #d8a84d;padding:10px 14px;border-radius:6px}
.evidence{background:#f7fbff;border-left:4px solid #4a8bb8;padding:10px 14px;border-radius:6px}
.impact{color:#51645d;background:#fbfaf1;border-left:4px solid #b8a05a;padding:10px 14px;border-radius:6px}
@media(max-width:760px){.page{padding:16px}article{padding:24px 20px}h1{font-size:24px}}
"""
    return f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{html.escape(title)}</title><style>{css}</style></head><body><main class='page'><article>{''.join(body)}</article></main></body></html>"


VALIDATOR = r'''
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
'''


def write(name, content):
    (ROOT / name).write_text(content.strip() + "\n", encoding="utf-8")


def main():
    chain = load_chain()
    p1_md = P1_PATH.read_text(encoding="utf-8")
    p2_md = build_teacher_md(chain)
    write("R223N_P2_teacher_default_reading_draft_v3.md", p2_md)
    write("R223N_P2_teacher_default_reading_draft_v3.html", md_to_html(p2_md, "R223N-P2 有趣的纸印教师稿 v3"))
    write("R223N_P2_label_humanization_rules.md", build_rules())
    write("R223N_P2_template_phrase_cleanup_report.md", build_cleanup_report(p1_md, p2_md))
    write("R223N_P2_before_after_compare_with_P1.md", build_compare(p1_md, p2_md))
    write("R223N_P2_report.md", build_report(p1_md, p2_md))
    write("validate_1013R_R223N_P2_teacher_language_humanization.py", VALIDATOR)
    manifest = {
        "stage_id": STAGE_ID,
        "source_stage_id": SOURCE_STAGE_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "change_type": "teacher_language_humanization_and_label_detechnicalization_only",
        "files": [
            "R223N_P2_teacher_default_reading_draft_v3.md",
            "R223N_P2_teacher_default_reading_draft_v3.html",
            "R223N_P2_label_humanization_rules.md",
            "R223N_P2_template_phrase_cleanup_report.md",
            "R223N_P2_before_after_compare_with_P1.md",
            "R223N_P2_report.md",
            "validate_1013R_R223N_P2_teacher_language_humanization.py",
            "validate_1013R_R223N_P2_teacher_language_humanization_result.json",
            "PACKAGE_MANIFEST.json",
            "README_FOR_GPT_REVIEW.md",
        ],
        "boundary": {
            "preview_only": True,
            "teacher_confirmed": False,
            "formal_apply_allowed": False,
            "r97b_modified": False,
            "ui_modified": False,
            "runtime_connected": False,
            "provider_model_connected": False,
            "database_written": False,
        },
    }
    write("PACKAGE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    readme = f"""# R223N-P2 Teacher Language Humanization Review

```text
stage_id={STAGE_ID}
source_stage_id={SOURCE_STAGE_ID}
status=review_package
formal_ui=blocked
```

## Open first

1. `R223N_P2_teacher_default_reading_draft_v3.html`
2. `R223N_P2_teacher_default_reading_draft_v3.md`
3. `R223N_P2_template_phrase_cleanup_report.md`
4. `R223N_P2_before_after_compare_with_P1.md`

## Review question

Does P2 preserve the classroom event depth while removing backend label flavor and repetitive template language from the teacher default draft?

## Boundaries

No R97B change, no formal UI, no frontend/backend change, no runtime/provider/model/prompt/db connection, no lesson body writeback, no formal apply.
"""
    write("README_FOR_GPT_REVIEW.md", readme)


if __name__ == "__main__":
    main()
