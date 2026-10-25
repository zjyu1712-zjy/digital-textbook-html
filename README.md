# 数字教材转换 · digital-textbook-html

将教材，或教材与课件、提纲、习题解析、真题的组合，制作成一个可离线阅读、作答并保存学习记录的交互 HTML。

**这是跨平台 Agent Skill，不限于 Codex。** 同一套规则、构建器与学习组件可安装到支持 [Agent Skills](https://agentskills.io/specification) 的 AI 助手。Claude Code、Cursor、GitHub Copilot CLI、Gemini CLI 和 Codex 的接入方式见下表。`agents/openai.yaml` 只是可选的 Codex 界面信息，不要求使用 OpenAI 模型或 API。

“支持安装插件”不等于“支持这个技能格式”。AI 还要获准读取资料、写文件、执行 Python/Node、查看原页并检查浏览器。只有聊天功能，或仅支持 MCP/其他专有插件格式的产品，不能仅上传本包就完成转换；需要相应执行环境或另外开发适配。**打开 HTML 模板也不会自动识别教材。** 教材理解、来源匹配、答案推导与语义核查由调用技能的模型完成。

## 安装与调用

在希望使用技能的项目目录运行以下命令，再选择自己的 AI 助手，无需先安装 Codex：

```sh
npx skills add zjyu1712-zjy/digital-textbook-html --skill digital-textbook-html
```

[skills.sh 官方安装工具](https://github.com/vercel-labs/skills) 当前要求 Node.js 22.20+，默认安装在当前项目；需要跨项目使用时添加 `--global`。也可明确指定目标，例如：

```sh
npx skills add zjyu1712-zjy/digital-textbook-html --skill digital-textbook-html --agent claude-code
```

| 你的 AI | `--agent` 参数 | 安装后如何调用 |
| --- | --- | --- |
| Claude Code | `claude-code` | `/digital-textbook-html` 或自然语言指定 |
| Cursor Agent | `cursor` | 输入 `/`，选择 `digital-textbook-html` |
| GitHub Copilot CLI | `github-copilot` | `/digital-textbook-html`；可用 `/skills info digital-textbook-html` 查看 |
| Gemini CLI | `gemini-cli` | `/skills list` 查看，再用自然语言要求使用该技能 |
| Codex | `codex` | `$digital-textbook-html` 或自然语言指定 |

安装后可以直接说：

> 使用 digital-textbook-html 数字教材转换技能，按其中的学习习惯，把我上传的教材转换成完整交互 HTML。先盘点资料与运行环境，再转换、核查和修复，最后交付一个可离线打开的 HTML。

只有一本教材也能开始；没有真题不会生成假真题。分批上传时先说“还没发齐，先不要转换”，发齐后再开始。若宿主没有识别技能，先检查其技能列表、安装目录与权限，不把“复制了文件”等同于“模型已调用”。

## 手动安装或上传技能包

从 [GitHub Releases](https://github.com/zjyu1712-zjy/digital-textbook-html/releases) 下载 `digital-textbook-html-1.1.0.zip`。这是标准技能目录压缩包，不是任意平台通用的插件商店包；仅在目标产品明确支持这种格式时使用其上传功能。

也可以克隆本仓库。手动安装时，保留整个 `digital-textbook-html/` 目录（含 scripts、references、assets 和 tests），放入对应技能目录；不要只上传 `SKILL.md`。已有同名技能或个人改动时先备份，再按目标平台的更新流程操作。各平台目录、Windows 示例与能力边界见 [跨平台说明](references/platform-compatibility.md)。

## 能力与质量

- **资料组织：**教材主导、教师课件主导、提纲主导、组合资料。
- **学科策略：**数学与推导、理论与论述、模型与图形、会计业务与表格、数据与统计、通用教材，可组合使用。
- **学习页面：**独立章节、搜索、知识点与题目跳转、原例题/原练习、真题整卷入口、隐藏答案及来源标记。
- **作答与记录：**文字、填空、数值、选择、多选、公式、矩阵、分录、表格；图片附件、草稿自动保存、追加历次作答、完整备份导入导出。

原题、原答案与 AI 参考答案分别标记。缺页、模糊题设、版本冲突和无法确认的答案须明确报告；不能用摘要、原创自测或编造内容代替教材。更换 AI 不改变这些标准，也不保证不同模型的教学质量相同。

## 运行环境

生成端需要 Python 3.9+；公式验证需要 Node.js。浏览器检查要求 Node 20+、Playwright 与 Chromium 系浏览器，推荐 Node 24。原资料读取、PDF/扫描件识别和查看原页由宿主提供，本仓库不内置万能 OCR，也不自动购买或调用第三方模型。

在任意工作目录，以技能的实际绝对路径检测环境：

```sh
python3 /path/to/digital-textbook-html/scripts/doctor.py --workspace /path/to/textbook-work --out /path/to/textbook-work/checks/environment.json
```

检测器不安装软件、不改全局配置、不联网。`buildReady` 只表示基础构建环境就绪；原页识别、语义核查、真实浏览器存储及视觉检查仍须实际执行，不能用环境检测代替验收。`NODE_BINARY`、`PLAYWRIGHT_MODULE`、`BROWSER_EXECUTABLE` 可以指向宿主已有工具。

**最终学习 HTML 无需上述依赖：**正文、图片、数学资源、样式与脚本均内嵌，可在浏览器离线打开。记录存于当前浏览器，不会写回 HTML；换设备或清理浏览器前应导出完整备份。

## 验证与维护

[1.1.0 验收记录](references/release-1.1.0.md) 区分格式核实、安装测试、模型实际调用与成品浏览器测试；不能把安装器成功写成所有 AI 都已完成真实教材转换。

入口是 [SKILL.md](SKILL.md)，偏好是 [references/preferences.md](references/preferences.md)，通用质量与内容结构分别在 [质量契约](references/quality.md)、[数据契约](references/schema.md)。安装目录作为只读资源；需要定制样式时复制到工作区后修改副本，不影响其他项目。

本仓库只包含方法、组件、工具与自编测试资料，不含五门课程私有教材、课件、真实作答记录、密钥或网页部署工程。KaTeX 与字体保留 [第三方许可证](assets/vendor/KaTeX-LICENSE.txt)。版本升级不改变学习存储键、题目 ID 或备份格式。
