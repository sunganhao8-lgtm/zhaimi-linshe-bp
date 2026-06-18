# 临港 LIN 舍宠物店 · 商业计划书 · 离线版

## 目录结构

```
final/
├── index.html              ← 入口页（推荐从这个进）
├── bp.html                 ← 商业计划书演示页（8 大章节 + 4 摄像头布局图）
├── site-map.html           ← 选址地图（高德地图·本地 POI 数据）
├── layout-editor.html      ← 49㎡ 门店布局交互编辑器
├── layout.svg              ← 布局 SVG 图
├── bp.md                   ← BP 完整 markdown 源文档
├── README.md               ← 本文件
│
├── data/
│   └── poi.json            ← 11 个 POI 的真实坐标（高德 POI 实测 2026-06）
│                              + 步行路径（高德 Walking API 实测）
│
└── vendor/
    ├── amap/
    │   ├── loader.js       ← 高德地图 JS API 加载器
    │   └── maps.js         ← （首次访问 site-map.html 时由本地缓存 fetch）
    └── osm-tiles/
        └── 13/14/15/16/   ← OSM 离线瓦片缓存（约 50 张，覆盖临港泥城片区）
```

## 如何发送给合伙人预览

**整文件夹打包发送**（zip/7z），让对方解压后**双击 `index.html`** 即可打开。

或部署到任何静态服务器：
```bash
cd final
python -m http.server 8090
# 然后访问 http://localhost:8090/
```

## 依赖说明

| 页面 | 依赖 | 是否需联网 |
|---|---|---|
| `index.html` | 纯静态 | ❌ 离线可用 |
| `bp.html` | 内联 CSS/JS | ❌ 离线可用 |
| `site-map.html` | `data/poi.json` + `vendor/amap/*` + `vendor/osm-tiles/` | ❌ **完全离线**（瓦片和 POI 都在本地） |
| `layout-editor.html` | Konva.js（CDN） | ⚠️ **首次需联网拉 Konva CDN**（约 200KB），之后浏览器缓存 |

## site-map.html 离线原理

1. **POI 数据**：从 `data/poi.json` 加载（11 个 POI + 步行路径 polyline，2026-06 通过高德 POI 实测）
2. **底图瓦片**：从 `vendor/osm-tiles/` 加载（约 50 张预下载 PNG 切片），完整覆盖临港 LIN 舍 + 万达 + 8 个小区
3. **AMap 库**：`vendor/amap/loader.js` 在本地（不调用高德远程 CDN）
4. **步行路径**：从 `data/poi.json` 直接读取，**不再调用任何 API**

## 布局编辑器首次使用

第一次打开 `layout-editor.html` 时需要联网拉 Konva.js（200KB）：
```
https://unpkg.com/konva@9/konva.min.js
```
之后浏览器自动缓存。如果想完全离线，把 konva.min.js 下载到 `vendor/konva.min.js` 并改 layout-editor.html 里 `<script src=...>`。

## 关键真实数据

- **门店面积**：49㎡（7m × 7m 实地复测）
- **坐标**：高德 POI 实测校准 2026-06
- **启动资金**：22.0 万元（含 9-10 万转让费 + 4 万半年房租）
- **月固定成本**：1.57 万元（6 个月后续签 8 万/年房租）
- **回本周期**：24-32 个月

## 浏览器兼容

✅ Chrome / Edge / Safari / Firefox（桌面端 + 移动端）

❌ IE 浏览器（不兼容 ES6+ / Konva / flexbox）