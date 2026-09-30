# [?] Fix parser panic on empty file (#4507)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-04-28
Source: https://github.com/FuelLabs/sway/commit/3976cd3d8258c8e2a5d873c9de1f82c905e79479
Type: security-commit

## Details
Fix parser panic on empty file (#4507)

Fix #4505

## Patch
### sway-parse/src/parser.rs
```diff
@@ -42,8 +42,8 @@ impl<'a, 'e> Parser<'a, 'e> {
                 };
                 Span::new(
                     self.full_span.src().clone(),
-                    self.full_span.end() - trim_offset,
-                    self.full_span.end() - trim_offset + 1,
+                    self.full_span.end().saturating_sub(trim_offset),
+                    (self.full_span.end() + 1).saturating_sub(trim_offset),
                     self.full_span.path().cloned(),
                 )
             }
```
