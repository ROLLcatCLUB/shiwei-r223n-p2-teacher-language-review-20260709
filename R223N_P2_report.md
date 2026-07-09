# R223N-P2 教师语言人话化报告

```text
stage_id=1013R_R223N_P2_TEACHER_LANGUAGE_HUMANIZATION_AND_LABEL_DETECHNICALIZATION
R223N-P1=PASS_PROCESS_STRUCTURE_WITH_LANGUAGE_POLISH_REQUIRED
R223N-P2=TEACHER_LANGUAGE_HUMANIZED
formal_ui=blocked
R97B / UI / runtime / prompt / model / db = untouched
```

## 一、处理内容

P2 不改课堂事件链，不删除课堂深度，只把教师默认稿中的后端字段味、模板句和机械标签转写为更自然的教师备课语言。

## 二、清理结果

```text
technical_label_count_p1=72
technical_label_count_p2=0
template_phrase_count_p1=42
template_phrase_count_p2=0
p2_long_paragraphs=0
p2_max_paragraph_chars=189
event_count=7
```

## 三、保留内容

- 学生可能反应仍保留；
- 教师追问和补救仍保留；
- 投屏 / 示范时机仍保留；
- 学习单记录仍保留；
- 评价证据仍保留；
- 不显示完整 review ledger，不恢复卡片墙。

## 四、浏览器 smoke

```text
url=http://127.0.0.1:8906/R223N_P2_teacher_default_reading_draft_v3.html
h3_count=7
intent_blocks=7
stuck_blocks=7
evidence_blocks=7
impact_blocks=7
includes_tech_label=false
includes_template_phrase=false
includes_xiaojiao=false
includes_chat=false
horizontal_overflow=false
screenshot=R223N_P2_teacher_default_reading_draft_v3_screenshot.png
```

## 五、边界

不改 R97B，不新增正式 route，不改 frontend/backend，不接 runtime、provider/model、prompt 或 db，不写回 lesson body，不 formal apply。
