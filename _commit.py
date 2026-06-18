"""一次性 commit + push"""
import subprocess

msg = """feat(map): 加竞品 POI + 修 BP 启动资金 16→22 + 重生成 PDF

data/poi.json:
- 加 competitors section（6 家宠物店：艾米尔/牛妞/萌萌哒/萌宠Family/萌喜/喵汪家）
- 坐标为用户截图视觉估算，标 estimated:true（待浏览器精修）
- 计算到本店距离 356-1189m，最近萌宠Family 356m

site-map.html:
- STORE_DATA 加 competitors 数组
- bootstrapLocalResults 加载竞品到 STATE.results
- 新增 CSS .marker-competitor（红色圆形 + ⚔ 图标）
- makeMarker 加 competitor role 分支
- InfoWindow 竞品显示：⚔ 距本店 X 米 + 备注 + 坐标估算提示
- 测试通过：17 个 POI 加载，6 个竞品 marker 渲染

bp.html:
- 修文档 tab KPI 卡：启动资金 16万→22万元（之前漏改了文档视图）
- bp.md 之前已修
- URL 参数 ?tab=slide&slide=N 支持（用于 PDF 截屏）

bp.pdf:
- 重新生成 16 页（基于 16 张最新截图）
- 文件 2.21 MB
- 验证：页码动态显示 x/16（已修）

清理：
- 删除 5 个 _fix_*.py 临时脚本
- 新增预览截图（preview-sitemap-competitors / preview-bp-pdf-p1-final / preview-bp-pdf-p12-final）"""

for cmd in [
    ['git', 'add', '-A'],
    ['git', 'commit', '-m', msg],
    ['git', 'push', 'origin', 'main'],
]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f'{" ".join(cmd[:3])}: rc={r.returncode}')
    print(r.stdout[-400:])
    if r.stderr:
        print('ERR:', r.stderr[-200:])