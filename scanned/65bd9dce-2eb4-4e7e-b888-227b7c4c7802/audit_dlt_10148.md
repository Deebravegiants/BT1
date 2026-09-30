# [?] chore: ignore RUSTSEC-2020-0159

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-10-19
Source: https://github.com/nervosnetwork/ckb/commit/80cdce36b80b4a2c47670d52fb5ed74b87dd4c39
Type: security-commit

## Details
chore: ignore RUSTSEC-2020-0159

## Patch
### deny.toml
```diff
@@ -5,7 +5,9 @@ yanked = "deny"
 notice = "deny"
 ignore = [
     # TODO Potential segfault in the time crate; waiting for the fix from upstream (chrono)
-    "RUSTSEC-2020-0071"
+    "RUSTSEC-2020-0071",
+    # TODO Potential segfault in the chrono crate; waiting for the new release of chrono
+    "RUSTSEC-2020-0159"
 ]
 
 [licenses]
```
