# [?] ignore cargo deny RUSTSEC-2026-0173

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/ecaae6ed9463bf66d02a8acf7b8d331acebec55c
Type: security-commit

## Details
ignore cargo deny RUSTSEC-2026-0173

## Patch
### deny.toml
```diff
@@ -92,6 +92,8 @@ ignore = [
     # method and triggers a reseed there, which this repo does not do.
     # Follow-ups will migrate pos/diem-crypto and replace parity-secp256k1.
     { id = "RUSTSEC-2026-0097", reason = "rand 0.9 patched; 0.7/0.8 forced by transitive deps and upstream pins; vulnerable code path not reachable here." },
+    # proc-macro-error2 is unmaintained; pulled by alloy-sol-macro 1.6.0
+    "RUSTSEC-2026-0173",
 ]
 # If this is true, then cargo deny will use the git executable to fetch advisory database.
 # If this is false, then it uses a built-in git library.
```
