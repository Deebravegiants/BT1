# [?] chore: suppress RUSTSEC-2025-0046 (#2187)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/ref-fvm
Published: 2025-08-01
Source: https://github.com/filecoin-project/ref-fvm/commit/927371723752c2d7a82163f4993c4697762563ec
Type: security-commit

## Details
chore: suppress RUSTSEC-2025-0046 (#2187)

* chore: suppress RUSTSEC-2025-0046

* Update deny.toml

Co-authored-by: Rod Vagg <rod@vagg.org>

---------

Co-authored-by: Rod Vagg <rod@vagg.org>

## Patch
### deny.toml
```diff
@@ -1,6 +1,7 @@
 [advisories]
 ignore = [
   "RUSTSEC-2024-0436", # Paste is unmaintained, whatever.
+  "RUSTSEC-2025-0046", # wasmtime, only impacting WASI, tracked in https://github.com/filecoin-project/ref-fvm/issues/2186
 ]
 
 [bans]
```
