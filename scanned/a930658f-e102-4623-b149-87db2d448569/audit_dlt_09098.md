# [?] fix(core): avoid integer underflow in Caesar loader

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-12-10
Source: https://github.com/trezor/trezor-firmware/commit/f7cbe43965c190bedb63f0aac370ae76aa3ac959
Type: security-commit

## Details
fix(core): avoid integer underflow in Caesar loader

Otherwise, it will panic when `debug_assert`s are enabled.

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_caesar/cshape/loader_starry.rs
```diff
@@ -85,7 +85,9 @@ impl Shape<'_> for LoaderStarry {
         for (i, c) in STARS.iter().enumerate() {
             if i == sel_idx {
                 self.draw_large_star(canvas, *c);
-            } else if (sel_idx + 1) % 8 == i || (sel_idx - 1) % 8 == i {
+            } else if (sel_idx + 1) % STAR_COUNT == i
+                || (sel_idx + STAR_COUNT - 1) % STAR_COUNT == i
+            {
                 self.draw_medium_star(canvas, *c);
             } else {
                 self.draw_small_star(canvas, *c);
```
