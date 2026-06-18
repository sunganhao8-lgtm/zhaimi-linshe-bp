# -*- coding: utf-8 -*-
with open('site-map.html','r',encoding='utf-8') as f:
    s = f.read()

changes = 0

# 1. Restore pick-modal-content label
old_label_css = '    box-sizing: border-box;\n  }\n  .pick-modal-actions {'
new_label_css = '    box-sizing: border-box;\n  }\n  .pick-modal-content label {\n    display: block;\n    font-size: 12px;\n    color: var(--ink-dim);\n    margin-top: 12px;\n  }\n  .pick-modal-actions {'

if old_label_css in s:
    s = s.replace(old_label_css, new_label_css, 1)
    changes += 1
    print('OK: label CSS')
else:
    print('FAIL: label CSS')

# 2. Remove duplicate click handler
dup = '    // 点击 POI 条目→视角在宅咪和该 POI 之间\n    ul.querySelectorAll'
first = s.find(dup)
if first >= 0:
    second = s.find(dup, first + 10)
    if second >= 0:
        # Find next major section after the duplicate
        next_section = s.find('// ==========', second)
        if next_section >= 0:
            s = s[:second] + s[next_section:]
            changes += 1
            print('OK: removed duplicate')
        else:
            print('FAIL: no section marker')
    else:
        print('OK: no duplicate')
else:
    print('FAIL: no click handler')

with open('site-map.html','w',encoding='utf-8') as f:
    f.write(s)
print(f'Done. {changes} changes. Size: {len(s)}')
