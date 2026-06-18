# 🤝 贡献指南

欢迎合伙人和开发者一起维护本项目！本指南说明协作流程。

## 👥 角色与权限

| 角色 | 权限 | 适合 |
|---|---|---|
| **Owner** | 全部权限（管理 collaborator、改 repo 设置） | 项目发起人 |
| **Collaborator** | 直接 push 到 main / 创建分支 / 提 PR / 关 Issue | 合伙人、核心维护者 |
| **Contributor** | Fork + PR / 提 Issue | 外部贡献者 |

**合伙人通常用 Collaborator 角色**——只需在 GitHub 仓库 Settings → Collaborators → Add people 输入他的 GitHub 用户名，他会收到邮件邀请。

## 📝 协作流程

### 内容更新（不需要技术背景）

1. 在 [Issues](../../issues) 页面选「📊 内容更新」模板
2. 填写更新前/更新后内容
3. 维护者会直接修改文件并标注贡献者

### 代码改动（开发者）

1. **从 main 拉新分支**：`git checkout -b feat/xxx` 或 `fix/xxx`
2. **本地改 + 验证**：`python -m http.server 8090` 浏览器测试
3. **Commit**：`git commit -m "feat: 描述改了什么"`（参考下面的 Commit 规范）
4. **Push + 开 PR**：`git push origin feat/xxx` 后到 GitHub 开 Pull Request
5. **等 CI 通过 + 合伙人 review** → merge

### 紧急修复

- 直接在 main 上 commit（hotfix），事后补 CHANGELOG

## 📐 Commit 规范

格式：`<类型>: <简短描述>`

- `feat:` 新功能
- `fix:` 修 bug
- `docs:` 改文档（README、CHANGELOG、注释）
- `style:` 格式（不影响代码运行）
- `refactor:` 重构
- `test:` 加测试
- `chore:` 杂项（构建、依赖）

**示例**：
```
feat: 在布局编辑器增加宠物展示柜组件
fix: 修复 site-map 移动端坐标清单文字溢出
docs: 更新 BP 财务模型（房租 6700 → 7000）
```

## 🏷️ Issue / PR 标签

- `bug` / `feature` / `content` / `docs` — 类别
- `priority: high` / `medium` / `low` — 紧急程度
- `mobile` / `desktop` — 影响的端
- `good first issue` — 适合新人

## 🧪 本地测试清单

提交前自查：

- [ ] 在 Chrome 桌面端打开 `index.html` 正常
- [ ] 在手机/平板模拟器看 3 个子页面布局不碎
- [ ] 浏览器 Console 0 错误
- [ ] 如果改了 `data/poi.json`，验证 `site-map.html` 能加载
- [ ] 如果改了 `bp.md`，验证 `bp.html` 的数字与之一致
- [ ] 如果改了 `layout-editor.html` 默认布局，验证所有 30 个组件不碰撞

## 📞 沟通

- **日常问题**：提 Issue
- **紧急协调**：微信群（见 README 顶部链接）
- **代码 review**：在 PR 里 @合伙人

---

感谢你的贡献！🎉