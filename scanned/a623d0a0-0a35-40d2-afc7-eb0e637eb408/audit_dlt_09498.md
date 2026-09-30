# [?] chore: cargo audit RUSTSEC-2025-0120 (#6252)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2025-11-18
Source: https://github.com/chainflip-io/chainflip-backend/commit/efd4d59bbe55ad14c0287747f6d05a3a96de98f7
Type: security-commit

## Details
chore: cargo audit RUSTSEC-2025-0120 (#6252)

## Patch
### .cargo/config.toml
```diff
@@ -55,6 +55,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2025-0055: logging injection vulnerability, requires display of arbitrary user input. Fixing this causes color sequence to be escaped and displayed in logs.
 # - RUSTSEC-2025-0057: fxhash is unmaintained, but we can't remove it because it's used in substrate.
 # - RUSTSEC-2025-0118: Unsound API access to a WebAssembly shared linear memory.
+# - RUSTSEC-2025-0120: Unmaintained JSON crate. Only used for config.
 cf-audit = '''
 audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2021-0139
@@ -78,6 +79,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2025-0055
 	--ignore RUSTSEC-2025-0057
 	--ignore RUSTSEC-2025-0118
+	--ignore RUSTSEC-2025-0120
 '''
 
 [build]
```
