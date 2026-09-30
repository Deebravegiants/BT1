# [?] fix windows stack overflow (#375)

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2022-08-19
Source: https://github.com/move-language/move/commit/9ad1087baa8940506483183717ba6a1e84e5a647
Type: security-commit

## Details
fix windows stack overflow (#375)

## Patch
### .cargo/config
```diff
@@ -8,3 +8,6 @@ xtest = "run --package x --bin x -- test"
 xlint = "run --package x --bin x -- lint"
 xbuild = "run --package x --bin x -- build"
 nextest = "run --package x --bin x -- nextest"
+
+[target.x86_64-pc-windows-msvc]
+rustflags = ["-C", "link-arg=/STACK:8000000"]
```
