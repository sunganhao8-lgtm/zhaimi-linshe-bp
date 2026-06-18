# -*- coding: utf-8 -*-
"""Fix remaining issues 2 (walking route) and 3 (POI clickable) + CSS"""

with open('site-map.html','r',encoding='utf-8') as f:
    s = f.read()

changes = 0

# ===== 2. Replace computeWalkingRoute with AMap.Walking API =====
old_route = '''  // 计算 store→wanda 步行路径（本地近似，沿 S2 沪芦高速 → 鸿音路）
  // 返回 polyline points + 距离 + 时长
  function computeWalkingRoute() {
    const a = [STORE_DATA.store.lng, STORE_DATA.store.lat];
    const b = [STORE_DATA.wanda.lng, STORE_DATA.wanda.lat];
    // 沿途关键节点（沿 S2 沪芦高速 → 鸿音路 → 万达）
    const mid1 = [STORE_DATA.store.lng + 0.003, STORE_DATA.store.lat + 0.0025]; // 入口 S2
    const mid2 = [STORE_DATA.wanda.lng - 0.002, STORE_DATA.wanda.lat + 0.001];   // 万达东南角
    const path = [a, mid1, mid2, b];
    // 累计距离（用 haversine 沿 path）
    let total = 0;
    for (let i = 1; i < path.length; i++) total += haversine(path[i-1], path[i]);
    // 步行 5km/h，路径系数 ×1.15 模拟实际绕行
    const distance = total * 1.15;
    const minutes = Math.round(distance / 5000 * 60);
    return { path, distance, duration: minutes };
  }'''

new_route = '''  // 计算 store→wanda 真实步行路线（AMap.Walking API）
  // 返回 polyline points + 距离 + 时长
  function computeWalkingRoute(callback) {
    if (typeof AMap === 'undefined' || typeof AMap.Walking !== 'function') {
      // fallback：直线距离 ×1.4
      var a = [STORE_DATA.store.lng, STORE_DATA.store.lat];
      var b = [STORE_DATA.wanda.lng, STORE_DATA.wanda.lat];
      var straight = haversine(a, b);
      var dist = straight * 1.4;
      var min = Math.round(dist / 5000 * 60);
      callback({ path: [a, b], distance: dist, duration: min, source: '估算（Walking API 不可用）' });
      return;
    }
    var walking = new AMap.Walking({ map: STATE.map, hideMarkers: true, panel: false });
    walking.search(
      new AMap.LngLat(STORE_DATA.store.lng, STORE_DATA.store.lat),
      new AMap.LngLat(STORE_DATA.wanda.lng, STORE_DATA.wanda.lat),
      function(status, result) {
        if (status === 'complete' && result.routes && result.routes.length > 0) {
          var route = result.routes[0];
          var path = [];
          route.steps.forEach(function(step) {
            step.path.forEach(function(p) { path.push([p.lng, p.lat]); });
          });
          callback({ path: path, distance: route.distance, duration: Math.round(route.time / 60), source: 'AMap 真实步行路径' });
        } else {
          // fallback
          var a = [STORE_DATA.store.lng, STORE_DATA.store.lat];
          var b = [STORE_DATA.wanda.lng, STORE_DATA.wanda.lat];
          var straight = haversine(a, b);
          var dist = straight * 1.4;
          var min = Math.round(dist / 5000 * 60);
          callback({ path: [a, b], distance: dist, duration: min, source: '估算（步行 API 无结果）' });
        }
      }
    );
  }'''

if old_route in s:
    s = s.replace(old_route, new_route)
    changes += 1
    print('OK: computeWalkingRoute')
else:
    # try with const instead of let
    old_route2 = old_route.replace('let total', 'const total')
    if old_route2 in s:
        s = s.replace(old_route2, new_route)
        changes += 1
        print('OK: computeWalkingRoute (const variant)')
    else:
        print('FAIL: computeWalkingRoute not matched')

# ===== 2. planWalkingRoute -> async callback =====
old_plan = '''  function planWalkingRoute() {
    const route = computeWalkingRoute();
    STATE.routeInfo = { distance: route.distance, duration: route.duration };
    STATE.routePolyline = new AMap.Polyline({
      path: route.path,
      strokeColor: '#F4B860',
      strokeWeight: 4,
      strokeOpacity: 0.9,
      lineJoin: 'round',
      lineCap: 'round',
      zIndex: 50,
      showDir: true
    });
    STATE.map.add(STATE.routePolyline);
    updateKPIs();
  }'''

new_plan = '''  function planWalkingRoute() {
    computeWalkingRoute(function(route) {
      STATE.routeInfo = { distance: route.distance, duration: route.duration, source: route.source };
      if (STATE.routePolyline) STATE.map.remove(STATE.routePolyline);
      STATE.routePolyline = new AMap.Polyline({
        path: route.path,
        strokeColor: '#F4B860',
        strokeWeight: 4,
        strokeOpacity: 0.9,
        lineJoin: 'round',
        lineCap: 'round',
        zIndex: 50,
        showDir: true
      });
      STATE.map.add(STATE.routePolyline);
      updateKPIs();
    });
  }'''

if old_plan in s:
    s = s.replace(old_plan, new_plan)
    changes += 1
    print('OK: planWalkingRoute')
else:
    print('FAIL: planWalkingRoute not matched')

# ===== 2. Update KPI desc to show route source =====
old_kpi = '''      document.getElementById('kpi-distance-desc').textContent = `约 ${min} 分钟 · AMap 真实步行路径`;
    } else if (STATE.results.store && STATE.results.wanda) {'''

new_kpi = '''      document.getElementById('kpi-distance-desc').textContent = `约 ${min} 分钟 · ${STATE.routeInfo.source}`;
    } else if (STATE.results.store && STATE.results.wanda) {'''

if old_kpi in s:
    s = s.replace(old_kpi, new_kpi)
    changes += 1
    print('OK: KPI route source')
else:
    print('FAIL: KPI not matched')

# ===== 3. POI list clickable =====
# Find the renderPOIList function
old_render_start = "    ul.innerHTML = items.map(r => {"
old_render_end = "    }).join('');"

idx_start = s.find(old_render_start, s.find('renderPOIList'))
idx_end = s.find(old_render_end, idx_start) + len(old_render_end)

if idx_start > 0 and idx_end > idx_start:
    old_block = s[idx_start:idx_end]
    
    new_block = old_block.replace(
        '      return `<li class="poi-item ${cls}">',
        '''      const dataId = r.missing ? '' : ` data-id="${escapeHTML(r.id)}"`;
      return `<li class="poi-item ${cls}"${dataId}>'''
    )
    
    click_handler = '''
    // 点击 POI 条目→视角在宅咪和该 POI 之间
    ul.querySelectorAll('.poi-item[data-id]').forEach(function(li) {
      li.addEventListener('click', function() {
        var id = this.getAttribute('data-id');
        var target = STATE.results[id];
        if (!target || !target.lng || !target.lat || !STATE.map) return;
        var store = STATE.results.store;
        if (!store || !store.lng || !store.lat) return;
        var cx = (store.lng + target.lng) / 2;
        var cy = (store.lat + target.lat) / 2;
        STATE.map.setZoomAndCenter(17, [cx, cy]);
        ul.querySelectorAll('.poi-item').forEach(function(x) { x.classList.remove('active'); });
        this.classList.add('active');
      });
    });'''
    
    s = s[:idx_end] + '\n' + click_handler + s[idx_end:]
    changes += 1
    print('OK: POI clickable added')
else:
    print('FAIL: renderPOIList not found')

# ===== 3. CSS: poi-item active/hover =====
old_css = '''  .poi-item .coord {
    font-size: 10px;
    color: #8a7560;
    margin-top: 2px;
  }'''

new_css = '''  .poi-item .coord {
    font-size: 10px;
    color: #8a7560;
    margin-top: 2px;
  }
  .poi-item.active {
    border-color: var(--brand-orange) !important;
    background: rgba(244, 184, 96, 0.15) !important;
    box-shadow: 0 0 0 1px rgba(244, 184, 96, 0.3);
    cursor: pointer;
  }
  .poi-item[data-id] {
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .poi-item[data-id]:hover {
    border-color: var(--brand-orange);
    background: rgba(244, 184, 96, 0.08);
  }'''

if old_css in s:
    s = s.replace(old_css, new_css)
    changes += 1
    print('OK: poi-item CSS')
else:
    print('FAIL: poi-item CSS not matched')

# Save
with open('site-map.html','w',encoding='utf-8') as f:
    f.write(s)
print(f'\nTotal changes: {changes}')
