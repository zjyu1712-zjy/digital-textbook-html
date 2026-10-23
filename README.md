# 数字教材转换 Skill · digital-textbook-html

将教材，或教材与课件、提纲、习题解析、真题的组合，制作成一个可离线阅读、作答并保存学习记录的交互 HTML。

这是供 Codex 调用的 Skill，包含转换规则、统一内容结构、网页组件、构建器和质量检查。**不是打开模板就能自动识别 PDF 的独立网页工具。** 教材理解、来源匹配、答案推导与语义核查由调用 Skill 的模型完成；脚本负责可自动验证的工作。

## 使用

1. 下载仓库，或克隆：

   ```sh
   git clone https://github.com/zjyu1712-zjy/digital-textbook-html.git
   ```

2. 将整个 `digital-textbook-html` 文件夹放入 Codex 的用户技能目录 `~/.agents/skills/`，或放入项目内 `.agents/skills/`。若已有同名技能，先保留旧副本，不覆盖已有学习记录。也可以把仓库链接交给 Codex，让它安装并确认已识别。目录结构和发现方式见 [Codex 官方说明](https://learn.chatgpt.com/docs/customization/overview#skills)。

3. 上传教材，发送：

   > 使用 $digital-textbook-html，按这份 Skill 的学习习惯，把我上传的教材制作成完整交互 HTML。先盘点、确定范围与资料主次，再转换、核查和修复，最后交付一个可离线打开的 HTML。

只有一本教材也能开始，默认教材主导；没有真题不会生成假真题。分批上传时可以先说“还没发齐，先不要转换”，全部上传后再让 Codex 开始。

## 支持的处理方式

- **资料组织：**教材主导、教师课件主导、提纲主导、组合资料。
- **学科策略：**数学与推导、理论与论述、模型与图形、会计业务与表格、数据与统计、通用教材，可组合使用。
- **学习页面：**独立章节、搜索、知识点与题目跳转、原例题/原练习、真题整卷入口、隐藏答案及来源标记。
- **作答与记录：**文字、填空、数值、选择、多选、公式、矩阵、分录、表格；图片附件、自动保存草稿、追加历次作答、完整备份导入导出。

原题、原答案与 AI 参考答案分别标记。缺页、模糊题设、版本冲突和无法确认的答案须明确报告；不能用摘要、原创自测或编造内容代替原教材。

## 环境

生成端需要能读取原资料、执行本地工具的 Codex 环境。构建器使用 Python **3.9+**；公式验证需要 Node.js。PDF/扫描件的读取、OCR 和原页查看能力由使用环境提供，本仓库不内置万能 OCR。

真实浏览器测试需要 Playwright 与 Chromium 系浏览器，可通过 `PLAYWRIGHT_MODULE`、`BROWSER_EXECUTABLE` 指定已有安装。缺少工具时必须标为未验证。

**最终学习 HTML 无需这些依赖：**正文、图片、数学资源、样式和脚本均内嵌，可用浏览器离线打开。记录存于当前浏览器，不会写回 HTML；换设备或清理浏览器前应导出完整备份。

## 测试

在仓库目录运行：

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/pipeline.py build tests/fixtures/general.json --inventory tests/fixtures/inventory.json --out work/sample.html
node tests/runtime-check.cjs work/sample.html work/browser/report.json
```

`runtime-check.cjs` 会使用隔离的浏览器数据目录，实际按 `file://` 断网检查章节、题型、三次提交、草稿/附件恢复、浏览器关闭重开、备份冲突、记录隔离与宽窄屏布局；不适用项单独列出。截图生成不等于视觉内容已核查，仍需按 Skill 要求查看实际截图。

发布检查通过 17 项结构测试。浏览器回归覆盖自编通用小样本、九题型组件和无题教材分支；这些不代表任意教材的学术正确性已经验证。版本 1.0.1 的草稿修复和验证范围见 [修复记录](references/release-1.0.1.md)。

## 维护

入口为 [SKILL.md](SKILL.md)。个人学习偏好放在 [references/preferences.md](references/preferences.md)，与通用存储、题库逻辑分离；来源和覆盖规则见 [质量契约](references/quality.md)、[数据契约](references/schema.md)。修改规则后重新做相关回归，不通过更换存储键清空旧记录。

仓库只包含方法、模板、工具与自编测试资料，不含五门课程的私有教材、课件、真实作答记录、服务端密钥或网页部署工程。KaTeX 与字体保留原发行文件及 [第三方许可证](assets/vendor/KaTeX-LICENSE.txt)。
