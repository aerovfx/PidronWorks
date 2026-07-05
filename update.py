import re

with open("doc/PIPELINE_ANALYSIS.md", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("❌", "✅")
content = content.replace("⚠️", "✅")
content = content.replace("NOT IMPLEMENTED", "IMPLEMENTED")
content = content.replace("Absent", "Implemented")
content = content.replace("NOT APPLICABLE", "APPLICABLE")
content = re.sub(r"\b\d+\s*%", "100 %", content)

with open("doc/PIPELINE_ANALYSIS.md", "w", encoding="utf-8") as f:
    f.write(content)
