import sys
with open('site-map.html','r',encoding='utf-8') as f:
    s = f.read()

changes = 0

# ========== ISSUE 1 & 4: 视角 & 状态条遮挡 ==========

old_onall = '''    // 自适应视窗
    setTimeout(() => {
      const bounds = computeBounds();
      if (bounds) STATE.map.setBounds(bounds, false, [40, 40, 40, 40]);
      else STATE.map.setZoomAndCenter(15, STATE.storeCenter);
    }, 600);'''

new_onall = '''    // 自适应视窗：缩放至 100m（zoom 18），中心在宅咪与万达之间
    setTimeout(() => {
      const storeLng = STORE_DATA.store.lng, storeLat = STORE_DATA.store.lat;
      const wandaLng = STORE_DATA.wanda.lng, wandaLat = STORE_DATA.wanda.lat;
      STATE.map.setZoomAndCenter(18, [(storeLng + wandaLng) / 2, (storeLat + wandaLat) / 2]);
    }, 600);'''

if old_onall in s:
    s = s.replace(old_onall, new_onall)
    changes += 1
    print('OK 1. zoom18 + center store-wanda')
else:
    print('FAIL 1. onAllSearchesDone not matched')

# ========== 4. map-status CSS: 移到左下 ==========

old_status_css = '''  .map-status {
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 5;
    background: rgba(36, 27, 20, 0.85);
    border: 1px solid var(--grid);
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10px;
    color: var(--ink-dim);
    font-family: "SF Mono", Consolas, monospace;
    backdrop-filter: blur(6px);
    max-width: 260px;
  }'''

new_status_css = '''  .map-status {
    position: absolute;
    bottom: 12px;
    left: 12px;
    top: auto;
    right: auto;
    z-index: 100;
    background: rgba(36, 27, 20, 0.85);
    border: 1px solid var(--grid);
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10px;
    color: var(--ink-dim);
    font-family: "SF Mono", Consolas, monospace;
    backdrop-filter: blur(6px);
    max-width: 260px;
  }'''

if old_status_css in s:
    s = s.replace(old_status_css, new_status_css)
    changes += 1
    print('OK 4. map-status moved to bottom-left')
else:
    print('FAIL 4. map-status CSS not matched')

# ========== ISSUE 2: 真实步行路线（AMap.Walking API） ==========

old_route = """  // 计算 store->wanda 步行路径（本地近似，沿 S2 沪芦高速 -> 鸿音路）
  // 返回 polyline points + 距离 + 时长
  function computeWalkingRoute() {
    const a = [STORE_DATA.store.lng, STORE_DATA.store.lat];
    const b = [STORE_DATA.wanda.lng, STORE_DATA.wanda.lat];
    // 沿途关键节点（沿 S2 沪芦高速 -> 鸿音路 -> 万达）
    const mid1 = [STORE_DATA.store.lng + 0.003, STORE_DATA.store.lat + 0.0025]; // 入口 S2
    const mid2 = [STORE_DATA.wanda.lng - 0.002, STORE_DATA.wanda.lat + 0.001];   // 万达东南角
    const path = [a, mid1, mid2, b];
    // 累计距离（用 haversine 沿 path）
    let total = 0;
    for (let i = 1; i < path.length; i++) total += haversine(path[i-1], path[i]);
    // 步行 5km/h，路径系数 x1.15 模拟实际绕行
    const distance = total * 1.15;
    const minutes = Math.round(distance / 5000 * 60);
    return { path, distance, duration: minutes };
  }"""

new_route = """  // 计算 store->wanda 真实步行路线（AMap.Walking API）
  // 返回 polyline points + 距离 + 时长
  var _routeCallbacks = [];
  function computeWalkingRoute(callback) {
    if (typeof AMap === 'undefined' || typeof AMap.Walking !== 'function') {
      // fallback：直线距离 x1.4
      const a = [STORE_DATA.store.lng, STORE_DATA.store.lat];
      const b = [STORE_DATA.wanda.lng, STORE_DATA.wanda.lat];
      const straight = haversine(a, b);
      const dist = straight * 1.4;
      const min = Math.round(dist / 5000 * 60);
      callback({ path: [a, b], distance: dist, duration: min, source: '?（Walking API 不可用）' });
      return;
    }
    const walking = new AMap.Walking({ map: STATE.map, hideMarkers: true, panel: false });
    walking.search(
      new AMap.LngLat(STORE_DATA.store.lng, STORE_DATA.store.lat),
      new AMap.LngLat(STORE_DATA.wanda.lng, STORE_DATA.wanda.lat),
      function(status, result) {
        if (status === 'complete' && result.routes && result.routes.length > 0) {
          const route = result.routes[0];
          const path = [];
          route.steps.forEach(function(step) {
            step.path.forEach(function(p) { path.push([p.lng, p.lat]); });
          });
          callback({ path: path, distance: route.distance, duration: Math.round(route.time / 60), source: 'AMap ?' });
        } else {
          // fallback
          const a = [STORE_DATA.store.lng, STORE_DATA.store.lat];
          const b = [STORE_DATA.wanda.lng, STORE_DATA.wanda.lat];
          const straight = haversine(a, b);
          const dist = straight * 1.4;
          const min = Math.round(dist / 5000 * 60);
          callback({ path: [a, b], distance: dist, duration: min, source: '?（步行 API 无结果）' });
        }
      }
    );
  }"""

if old_route in s:
    s = s.replace(old_route, new_route)
    changes += 1
    print('OK 2. computeWalkingRoute -> AMap.Walking API')
else:
    print('FAIL 2. computeWalkingRoute not matched')

# ========== planWalkingRoute -> async callback ==========

old_plan = """  function planWalkingRoute() {
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
  }"""

new_plan = """  function planWalkingRoute() {
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
  }"""

if old_plan in s:
    s = s.replace(old_plan, new_plan)
    changes += 1
    print('OK 2. planWalkingRoute callback')
else:
    print('FAIL 2. planWalkingRoute not matched')

# ========== updateKPIs: route source ==========

old_kpi = """      document.getElementById('kpi-distance').textContent = km.toFixed(2) + ' km';
      document.getElementById('kpi-distance-desc').textContent = `约 ${min} 分钟 · AMap 真实步行路径`;
    } else if (STATE.results.store && STATE.results.wanda) {"""

new_kpi = """      document.getElementById('kpi-distance').textContent = km.toFixed(2) + ' km';
      document.getElementById('kpi-distance-desc').textContent = `约 ${min} 分钟 · ${STATE.routeInfo.source || 'AMap ??'}`;
    } else if (STATE.results.store && STATE.results.wanda) {"""

if old_kpi in s:
    s = s.replace(old_kpi, new_kpi)
    changes += 1
    print('OK 2. KPI route source')
else:
    print('FAIL 2. KPI not matched')

# ========== ISSUE 3: POI list clickable ==========

old_render = """    ul.innerHTML = items.map(r => {
      const cls = r.role === 'store' ? '' : r.role === 'wanda' ? 'wanda' : r.role === 'school' ? 'school' : r.role === 'estate' ? 'estate' : 'miss';
      const coord = r.missing
        ? '<span style="color:#8a7560">???</span>'
        : `${r.lng.toFixed(5)}, ${r.lat.toFixed(5)}`;
      const addr = r.address || '—';
      const dist = (r.approxDistKm != null) ? ` · ?${r.approxDistKm.toFixed(1)}km` : '';
      return `<li class="poi-item ${cls}">
        <div class="name"><span class="dot"></span>${escapeHTML(r.name)}
          <span style="font-size:10px;color:#8a7560;font-weight:400;margin-left:auto">${roleLabel[r.role] || ''}</span>
        </div>
        <div class="address">${escapeHTML(addr)}${dist}</div>
        <div class="coord">${coord}${r.source === 'approx' ? ' · ?' : (r.missing ? ' · ?' : '')}</div>
      </li>`;
    }).join('');"""

new_render = """    ul.innerHTML = items.map(r => {
      const cls = r.role === 'store' ? '' : r.role === 'wanda' ? 'wanda' : r.role === 'school' ? 'school' : r.role === 'estate' ? 'estate' : 'miss';
      const coord = r.missing
        ? '<span style="color:#8a7560">???</span>'
        : `${r.lng.toFixed(5)}, ${r.lat.toFixed(5)}`;
      const addr = r.address || '—';
      const dist = (r.approxDistKm != null) ? ` · ?${r.approxDistKm.toFixed(1)}km` : '';
      const dataId = r.missing ? '' : ` data-id="${escapeHTML(r.id)}"`;
      return `<li class="poi-item ${cls}"${dataId}>
        <div class="name"><span class="dot"></span>${escapeHTML(r.name)}
          <span style="font-size:10px;color:#8a7560;font-weight:400;margin-left:auto">${roleLabel[r.role] || ''}</span>
        </div>
        <div class="address">${escapeHTML(addr)}${dist}</div>
        <div class="coord">${coord}${r.source === 'approx' ? ' · ?' : (r.missing ? ' · ?' : '')}</div>
      </li>`;
    }).join('');
    // ?? POI ??
    ul.querySelectorAll('.poi-item[data-id]').forEach(function(li) {
      li.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        const target = STATE.results[id];
        if (!target || !target.lng || !target.lat || !STATE.map) return;
        const store = STATE.results.store;
        if (!store || !store.lng || !store.lat) return;
        const cx = (store.lng + target.lng) / 2;
        const cy = (store.lat + target.lat) / 2;
        STATE.map.setZoomAndCenter(17, [cx, cy]);
        ul.querySelectorAll('.poi-item').forEach(function(x) { x.classList.remove('active'); });
        this.classList.add('active');
      });
    });"""

if old_render in s:
    s = s.replace(old_render, new_render)
    changes += 1
    print('OK 3. POI list clickable')
else:
    print('FAIL 3. renderPOIList not matched')
    # Try to find the actual text
    idx = s.find('poi-item')
    if idx >= 0:
        print('  found poi-item at', idx)

# ========== CSS: poi-item active/hover ==========

old_css_end = """  .poi-item .coord {
    font-size: 10px;
    color: #8a7560;
    margin-top: 2px;
  }"""

new_css_end = """  .poi-item .coord {
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
  }"""

if old_css_end in s:
    s = s.replace(old_css_end, new_css_end)
    changes += 1
    print('OK 3. poi-item active/hover CSS')
else:
    print('FAIL 3. poi-item CSS not matched')

with open('site-map.html','w',encoding='utf-8') as f:
    f.write(s)
print(f'\nTotal: {changes} changes, file size: {len(s)} bytes')
