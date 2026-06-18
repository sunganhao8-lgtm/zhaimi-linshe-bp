(function(){
  window.AMapLoader = {
    load: function(opts) {
      return new Promise(function(resolve, reject) {
        // 立即检测 AMap 已存在
        if (window.AMap && typeof window.AMap.Map === 'function') {
          resolve(window.AMap);
          return;
        }

        // 关键：用 fetch + script.textContent 注入（避开 CORB 对 fetch 响应体的拦截）
        var url = 'vendor/amap/maps.js?callback=___onAPILoaded&v=' + (opts.version || '2.0')
                + '&key=' + encodeURIComponent(opts.key || '')
                + (opts.plugins && opts.plugins.length ? '&plugin=' + opts.plugins.join(',') : '');

        // 5 秒超时
        var timeoutId = setTimeout(function() {
          if (window.AMap && typeof window.AMap.Map === 'function') {
            resolve(window.AMap);
          } else {
            reject('AMap 加载超时（5秒）');
          }
        }, 5000);

        fetch(url, { cache: 'no-store' })
          .then(function(r) { return r.text(); })
          .then(function(text) {
            // 去掉 callback= 参数对执行的影响（直接注入文本）
            var s = document.createElement('script');
            s.textContent = text;
            document.body.appendChild(s);
            // 等待 AMap 全局定义
            setTimeout(function() {
              clearTimeout(timeoutId);
              if (window.AMap && typeof window.AMap.Map === 'function') {
                resolve(window.AMap);
              } else {
                reject('AMap 未定义（maps.js 文本注入后仍未就绪）');
              }
            }, 200);
          })
          .catch(function(e) {
            clearTimeout(timeoutId);
            reject('fetch maps.js 失败：' + e.message);
          });
      });
    }
  };
})();
