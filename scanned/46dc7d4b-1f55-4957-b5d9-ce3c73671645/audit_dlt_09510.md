# [?] fix: add audit exception for RUSTSEC-2024-0375 (#5303)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-09-30
Source: https://github.com/chainflip-io/chainflip-backend/commit/6594d20990c44a84078780bd6c6a4932d5b751a2
Type: security-commit

## Details
fix: add audit exception for RUSTSEC-2024-0375 (#5303)

## Patch
### .cargo/config.toml
```diff
@@ -43,6 +43,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2024-0336: This adivsory comes from rustls, which is a dependency of the `try-runtime-cli` crate.
 # - RUSTSEC-2024-0320: Unmaintained transitive `yaml-rust` dependency of `insta` crate. We only use insta for testing.
 # - RUSTSEC-2024-0370: Unmaintained transitive dependency. Only affects macro generation efficiency.
+# - RUSTSEC-2024-0375: Unmaintained transitive dependency used by clap.
 cf-audit = '''
 audit -D unmaintained -D unsound
     --ignore RUSTSEC-2022-0093
@@ -54,4 +55,5 @@ audit -D unmaintained -D unsound
     --ignore RUSTSEC-2024-0336
     --ignore RUSTSEC-2024-0344
     --ignore RUSTSEC-2024-0370
+    --ignore RUSTSEC-2024-0375
 '''
```
