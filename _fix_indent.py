# -*- coding: utf-8 -*-
"""Fix: close renderPOIList function, fix startup section indentation"""
with open('site-map.html','r',encoding='utf-8') as f:
    s = f.read()

# Find the area around the broken forEach closing
old = '''    });
  }

// ============================================================
  // 启动入口：fetch + 文本注入（绕过 CORB）
  // ============================================================
  setStatus'''

new = '''    });
  }

  // ============================================================
  // 启动入口：fetch + 文本注入（绕过 CORB）
  // ============================================================
  setStatus'''

if old in s:
    s = s.replace(old, new)
    print('OK: fixed indentation')
else:
    print('FAIL: pattern not found')
    idx = s.find('// ============================================================')
    ctx = s[idx:idx+200]
    print(repr(ctx[:200]))

with open('site-map.html','w',encoding='utf-8') as f:
    f.write(s)
print('Done.')
