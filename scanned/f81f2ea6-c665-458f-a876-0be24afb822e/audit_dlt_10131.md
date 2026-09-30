# [?] add RUSTSEC-2022-0090 and remove RUSTSEC-2021-0145 from the deny ignore list.

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-02-18
Source: https://github.com/nervosnetwork/ckb/commit/5d1c41143537b104699d1b2be5af6f87e83c526e
Type: security-commit

## Details
add RUSTSEC-2022-0090 and remove RUSTSEC-2021-0145 from the deny ignore list.

## Patch
### deny.toml
```diff
@@ -6,6 +6,10 @@ notice = "deny"
 ignore = [
     # waiting https://github.com/bheisler/criterion.rs/pull/628 bump release
     "RUSTSEC-2021-0145"
+    # The CVE can be kept under control for its triggering.
+    # See https://github.com/launchbadge/sqlx/pull/2455#issuecomment-1507657825 for more information.
+    # Meanwhile, awaiting SQLx's new version (> 0.7.3) for full support of any DB driver.
+    "RUSTSEC-2022-0090"
 ]
 
 [licenses]
```
