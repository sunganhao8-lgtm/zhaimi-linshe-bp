# 📝 Changelog

本项目所有重要变更的记录。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 🚧 进行中
- 合伙人协作流程文档化
- 移动端布局优化（待办）

---

## [1.0.0] - 2026-06-17

### 🎉 首次发布

#### ✨ 新增
- **首页 `index.html`**：4 大模块入口（文档/演示/门店布局/选址）
- **商业计划书 `bp.html` + `bp.md`**：16 页幻灯片
  - 启动资金 22 万、月固定成本 1.57 万、回本 24-32 个月
  - 49㎡ (7×7) 门店
- **选址地图 `site-map.html`**：
  - 11 个真实 POI（高德地图 API 实测）
  - 真实步行路径 polyline（932m / 12 分钟）
  - POI 点击高亮 + InfoWindow
  - 本地 OSM 瓦片缓存
- **门店布局编辑器 `layout-editor.html`**：
  - 30 个组件（4 外墙 + 2 分区墙 + 3 洗护单间 + 家具设备）
  - 碰撞检测（普通组件 vs 墙 vs 锁组件）
  - 拖动 rAF 节流（移动端流畅）
  - SVG / PNG 导出
- **数据本地化** `data/poi.json`：4427 字节，包含 11 POI + 步行路径
- **品牌资源** `assets/`：Logo、主页背景图
- **GitHub Pages 部署**：在线预览可用

#### 🔧 技术栈
- 高德地图 JS API（离线 loader）
- Konva.js 画布（本地化）
- 纯静态 HTML / CSS / JS，零后端依赖

#### 📚 文档
- `README.md` - 项目说明 + 在线预览链接
- `LICENSE` - MIT 协议
- `CONTRIBUTING.md` - 贡献指南
- `CHANGELOG.md` - 本文件
- `.github/ISSUE_TEMPLATE/` - Issue 模板（bug / feature / 内容更新）
- `.github/workflows/lint.yml` - 自动 HTML/JSON 校验

---

## 版本历史格式说明

- **Added** / **新增**：新功能
- **Changed** / **变更**：已有功能的改动
- **Deprecated** / **弃用**：即将移除的功能
- **Removed** / **移除**：已移除的功能
- **Fixed** / **修复**：Bug 修复
- **Security** / **安全**：安全相关

每条变更需注明作者（如 `@username`）以便追溯贡献。