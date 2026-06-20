# skill-guide

> Made by [anastasia-mogu](https://github.com/anastasia-mogu) · MIT License

把陌生 skill 解读成一份可以直接用的 HTML 说明书 —— 完整度评分、第一次试用提示词、搭配建议、产出对照、改善点全在一份报告里。

> 适用平台:Claude Code、Codex / OpenAI Agent SDK、以及任何能加载 skill 目录的 Claude Agent。

## 它能做什么

丢给它一个 skill 目录、一个 SKILL.md、一个压缩包,或一个 multi-skill 仓库的根目录,它会:

1. 识别对象类型(单 skill / skill 包 / 多 skill 仓库 / 普通项目内嵌 / 不是 skill)
2. 给出 **0–100 完整度评分**和一句话推荐动作
3. 写一段可直接复制的**第一次试用提示词**
4. 在开始用的最下方给出**失败反馈入口**(哪里不对、带回什么、该改规则还是模板)
5. 列出**搭配建议**(标明每个搭配对象是「已有」「需安装」还是「不确定」)
6. 列出**产出物对照**(你多给什么,通常多拿到什么)
7. 列出**改善点**和**适合边界 / 文件关系图**,默认产出自包含 HTML 报告到当前工作区

## 安装

推荐做法:**真身放 cc-switch,各平台只放软链接**。这样 Claude Code 和 Codex 共用同一份源,改一处两边生效。

```bash
# 1. 把 skill 真身放到统一目录(本仓库就是这个真身)
mkdir -p ~/.cc-switch/skills
# 假设你 git clone 到了 ~/Downloads/skill-guide/
mv ~/Downloads/skill-guide ~/.cc-switch/skills/skill-guide

# 2. 给两个平台各做一个软链接(只链入口,不复制)
mkdir -p ~/.claude/skills ~/.codex/skills
ln -s ~/.cc-switch/skills/skill-guide ~/.claude/skills/skill-guide
ln -s ~/.cc-switch/skills/skill-guide ~/.codex/skills/skill-guide

# 3. 验证(看到 lrwxr-xr-x 和 -> 箭头才算对)
ls -la ~/.claude/skills/skill-guide ~/.codex/skills/skill-guide
```

**不要 `cp -r`**。复制会让两个平台各持一份,以后修一边另一边就过期 ——「split state」是这类 skill 最常见的内伤。

如果只用一个平台,只做对应那一边的软链接即可,不影响后续添加另一边。

## 怎么触发

skill-guide 的 `description` 已经覆盖以下问法,直接说就行,不用记命令:

- "这个 skill 是干嘛的 / 怎么用 / 完整度怎样"
- "我能不能直接用 / 要准备什么"
- "帮我评估一下这个 skill 包"
- "把这份 SKILL.md 解读一下"
- "这个仓库里有几个 skill,哪个值得装"
- "给我一份这个 skill 的使用说明书"
- "它和 X 应该搭配吗 / 应不应该合并"
- "我跑了一次没成功,帮我看看怎么修"

输入支持:本地目录路径、SKILL.md 文件路径、GitHub URL(需先下载到本地)、压缩包(需先解压)。

## 第一次试用提示词

```
用 skill-guide 解读这个 skill,生成 HTML 说明书:

<这里放路径>

要求:
- 给完整度评分和推荐动作
- 列出搭配建议(标明已有 / 需安装)
- 给一段第一次试用提示词
- HTML 报告保存在当前工作区,聊天里只给摘要和路径
```

## 看产物长什么样

仓库内已有三份示例,都是真实跑出来的产物(非编造):

- [`examples/sample-report.html`](examples/sample-report.html) — skill-guide **自我解读**:展示对纯指导型 skill 的标准产物
- [`examples/frontend-design-report.html`](examples/frontend-design-report.html) — skill-guide 解读 **Anthropic 官方 frontend-design**:展示对单 skill(指导型)的报告形态
- [`examples/ppt-master-report.html`](examples/ppt-master-report.html) — skill-guide 解读 **ppt-master**:展示对工作流型 / 文件产物型 skill 的报告形态

这些示例可以 `open` 直接用浏览器查看;也可以作为「我希望产物长这样」的参考喂给 skill-guide。

## 文件结构

```
skill-guide/
├── SKILL.md                       # 主流程 + 全部约束(LLM 实际读这份)
├── README.md                      # 本文件 — 给人看的入口
├── agents/
│   └── openai.yaml                # Codex / OpenAI 端的 UI 元数据
├── assets/
│   └── report-template.html       # HTML 报告模板(自包含 CSS/JS)
└── examples/
    ├── sample-report.html         # 自我解读示例
    ├── frontend-design-report.html # 解读 frontend-design 示例
    └── ppt-master-report.html      # 解读 ppt-master 示例
```

`SKILL.md` 是 skill 的主入口,定义了「读什么 → 评什么 → 输出什么」的 7 节流程;`assets/report-template.html` 是最终报告的 HTML 容器,包含响应式 CSS、复制按钮 JS、移动端适配,不依赖任何 CDN。当前报告顺序是:结论、快速判断、直接开始用、搭配、产出物对照、完整度与改善点、适合谁用与文件关系。`agents/openai.yaml` 只在 Codex / OpenAI 端用来渲染 skill 卡片,Claude Code 端不读它,但保留它对跨平台分发无害。

## 不做什么

- **不安装其他 skill** —— 那是 `ln -s` 或包管理器的事
- **不修改原 skill** —— 解读阶段强制只读,要修就明说「做修复副本」
- **不验证 skill 真的能跑** —— 它评的是「看起来完整度」,真正的功能验证要靠 `verify` 这类 skill 或人工试用
- **不深读 multi-skill 仓库的每个 skill** —— 默认只做包级解读 + 推荐 1–3 个深读对象,你确认后再继续

## 反馈与修复

跑完一次发现产物不对,把以下信息一起带回:

```
我跑了 skill-guide,输入是: [skill 路径]
生成的 HTML: [path]

不对劲的地方:
1. [比如:快速判断 5 格里某一格没标色]
2. [比如:文件关系块只用了一句话,没用 .relation-flow]
3. [比如:产出表格写成了承诺]

期望但没出现的:
- [比如:multi-skill 仓库该有的工作流地图]
- [比如:搭配对象的「已有 / 需安装」状态]

修哪里:
- 改 SKILL.md 的约束 / 改 report-template.html / 改我下次的提示词
```

修复优先做副本,不直接动 cc-switch 里的源:

```bash
cp -r ~/.cc-switch/skills/skill-guide ~/.cc-switch/skills/skill-guide-fix-001
# 在副本里改、验证,通过后再合回 skill-guide
```

如果决定不用,删两个软链接即可,源目录保留:

```bash
rm ~/.claude/skills/skill-guide ~/.codex/skills/skill-guide
```

## 已知缺口

- 输出前会做最小结构自检,用于防止 7 节结构、复制按钮、搭配标签、文件关系图等关键规则漂移;但它不替代人工审美判断和浏览器渲染检查。同一个 skill 跑两次,内容判断和版式细节仍可能需要人工把关。
- 示例已有 3 份(自我解读 + 单 skill 指导型 + PPT 文件产物型),但 multi-skill 仓库 / 不是 skill 项目 / 文件编辑类高风险 skill 还缺对照样例。

## License

[MIT](LICENSE) © 2026 anastasia-mogu。可自由使用、修改、商用,只需在分发时保留 LICENSE 文件和版权声明。
