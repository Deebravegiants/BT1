# [?] ignore cargo deny RUSTSEC-2025-0056

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2025-09-12
Source: https://github.com/Conflux-Chain/conflux-rust/commit/6a34a4c6f7ac0ccbcf46dc831033b839ffdb511c
Type: security-commit

## Details
ignore cargo deny RUSTSEC-2025-0056

## Patch
### deny.toml
```diff
@@ -88,6 +88,7 @@ ignore = [
     "RUSTSEC-2021-0059", # aesni unmaintained
     "RUSTSEC-2021-0060", # aes-soft unmaintained
     "RUSTSEC-2021-0061", # aes-ctr unmaintained
+    "RUSTSEC-2025-0056", # adler is unmaintained, use adler2 instead
 ]
 # If this is true, then cargo deny will use the git executable to fetch advisory database.
 # If this is false, then it uses a built-in git library.
```
