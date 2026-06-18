# -*- coding: utf-8 -*-
"""Fix CSS: remove corrupted pick-modal label block, restore correct CSS"""

with open('site-map.html','r',encoding='utf-8') as f:
    lines = f.readlines()

# Lines are 0-indexed in list but 1-indexed in file
# The corrupted block is around lines 274-293 (1-indexed)
# Line 274: "  .pick-modal-content label {" 
# It was corrupted by a bad patch that replaced its content with poi-item styles

# Find the exact corrupted block
target_start = None
target_end = None

for i, line in enumerate(lines):
    # Find ".pick-modal-content label {" that's NOT in a valid state
    if '.pick-modal-content label {' in line and i >= 270:
        target_start = i
        # Check if next line has nested .poi-item
        if i + 1 < len(lines) and '.poi-item .coord {' in lines[i+1]:
            # Corrupted block - find the matching closing brace
            # It's at the line before the next CSS rule starts at column 0
            for j in range(i+1, min(i+30, len(lines))):
                if lines[j].strip().startswith('.pick-modal-actions'):
                    target_end = j
                    break
            break

if target_start is not None and target_end is not None:
    print(f'Removing corrupted lines {target_start+1}-{target_end} ({target_end-target_start} lines)')
    # Remove the corrupted pick-modal-content label block
    del lines[target_start:target_end]
    
    # Find the real .poi-item .coord block to add active/hover after it
    for i, line in enumerate(lines):
        if '.poi-item .coord {' in line and i > 400:
            # Find the closing brace of this block
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip() == '}':
                    # Insert active/hover styles after this `}`
                    insert_pos = j + 1
                    new_css = [
                        '  .poi-item.active {\n',
                        '    border-color: var(--brand-orange) !important;\n',
                        '    background: rgba(244, 184, 96, 0.15) !important;\n',
                        '    box-shadow: 0 0 0 1px rgba(244, 184, 96, 0.3);\n',
                        '    cursor: pointer;\n',
                        '  }\n',
                        '  .poi-item[data-id] {\n',
                        '    cursor: pointer;\n',
                        '    transition: all 0.15s ease;\n',
                        '  }\n',
                        '  .poi-item[data-id]:hover {\n',
                        '    border-color: var(--brand-orange);\n',
                        '    background: rgba(244, 184, 96, 0.08);\n',
                        '  }\n',
                    ]
                    for idx, css_line in enumerate(new_css):
                        lines.insert(insert_pos + idx, css_line)
                    print(f'Added poi-item CSS at line {insert_pos+1}')
                    break
            break
else:
    print('Could not find corrupted block. Check manually.')

with open('site-map.html','w',encoding='utf-8') as f:
    f.writelines(lines)
print(f'Done. Total lines: {len(lines)}')
