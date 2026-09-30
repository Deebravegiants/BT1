# [?] fix(debugger): a potential underflow in memory highlighting (#6508)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2023-12-04
Source: https://github.com/foundry-rs/foundry/commit/3ee4135ce8512dae0e6cea60f143c2e6672213c5
Type: security-commit

## Details
fix(debugger): a potential underflow in memory highlighting (#6508)

The debugger colors memory region for a variety of instructions that
access the memory, as described in #5940. But there is a potential
underflow if the size is 0 (where offset + size - 1 underflows).
Change to a simpler and more robust way to index the memory region.

Co-authored-by: DaniPopes <57450786+DaniPopes@users.noreply.github.com>

## Patch
### crates/debugger/src/tui/draw.rs
```diff
@@ -782,7 +782,13 @@ Line::from(Span::styled("[t]: stack labels | [m]: memory decoding | [shift + j/k
             -2 => Some(1),
             -1 => Some(32),
             0 => None,
-            1.. => Some(stack[stack_len - stack_index as usize].saturating_to()),
+            1.. => {
+                if (stack_index as usize) <= stack_len {
+                    Some(stack[stack_len - stack_index as usize].saturating_to())
+                } else {
+                    None
+                }
+            }
             _ => panic!("invalid stack index"),
         };
 
@@ -862,11 +868,7 @@ Line::from(Span::styled("[t]: stack labels | [m]: memory decoding | [shift + j/k
                         Span::styled(
                             format!("{byte:02x} "),
                             if let (Some(offset), Some(size), Some(color)) = (offset, size, color) {
-                                if (i == offset / 32 && j >= offset % 32) ||
-                                    (i > offset / 32 && i < (offset + size - 1) / 32) ||
-                                    (i == (offset + size - 1) / 32 &&
-                                        j <= (offset + size - 1) % 32)
-                                {
+                                if i * 32 + j >= offset && i * 32 + j < offset + size {
                                     // [offset, offset + size] is the memory region to be colored.
                                     // If a byte at row i and column j in the memory panel
                                     // falls in this region, set the color.
```
