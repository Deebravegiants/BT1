# [?] fix: cargo audit RUSTSEC-2025-0057 (#6102)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-09-08
Source: https://github.com/chainflip-io/chainflip-backend/commit/148a0dc488ac53d883772d4e1ed4272ff42eaa9d
Type: security-commit

## Details
fix: cargo audit RUSTSEC-2025-0057 (#6102)

## Patch
### .cargo/config.toml
```diff
@@ -52,6 +52,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2023-0091: Low severity, difficult to exploit of wasmtime, dependency of substrate.
 # - RUSTSEC-2024-0438: Wasmtime security issue for Windows devices, so not applicable. Dependency of substrate.
 # - RUSTSEC-2024-0442: Wasmtime jit debugger issue.
+# - RUSTSEC-2025-0057: fxhash is unmaintained, but we can't remove it because it's used in substrate.
 cf-audit = '''
 audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2021-0139
@@ -72,6 +73,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2023-0091
 	--ignore RUSTSEC-2024-0438
 	--ignore RUSTSEC-2024-0442
+	--ignore RUSTSEC-2025-0057
 '''
 
 [build]
```
