# [?] chore: ignore RUSTSEC-2025-0118 (Unsound API access to a WebAssembly shared linear memory) (#6241)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-11-14
Source: https://github.com/chainflip-io/chainflip-backend/commit/abfcdde4a9d692146608dcf02da832b407b85a32
Type: security-commit

## Details
chore: ignore RUSTSEC-2025-0118 (Unsound API access to a WebAssembly shared linear memory) (#6241)

chore: ignore RUSTSEC-2025-0118 (Unsound API access to a WebAssembly shared linear memory).

## Patch
### .cargo/config.toml
```diff
@@ -54,6 +54,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2024-0442: Wasmtime jit debugger issue.
 # - RUSTSEC-2025-0055: logging injection vulnerability, requires display of arbitrary user input. Fixing this causes color sequence to be escaped and displayed in logs.
 # - RUSTSEC-2025-0057: fxhash is unmaintained, but we can't remove it because it's used in substrate.
+# - RUSTSEC-2025-0118: Unsound API access to a WebAssembly shared linear memory.
 cf-audit = '''
 audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2021-0139
@@ -76,6 +77,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2024-0442
 	--ignore RUSTSEC-2025-0055
 	--ignore RUSTSEC-2025-0057
+	--ignore RUSTSEC-2025-0118
 '''
 
 [build]
```
