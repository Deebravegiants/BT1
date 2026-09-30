# [?] Ignore RUSTSEC-2024-0336

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-04-22
Source: https://github.com/nervosnetwork/ckb/commit/ca197a4a2813bc191bf97ea1119f8381d6d49823
Type: security-commit

## Details
Ignore RUSTSEC-2024-0336

Signed-off-by: Eval EXEC <execvy@gmail.com>

## Patch
### deny.toml
```diff
@@ -4,12 +4,13 @@ unmaintained = "warn"
 yanked = "deny"
 notice = "deny"
 ignore = [
-    # waiting https://github.com/bheisler/criterion.rs/pull/628 bump release
-    "RUSTSEC-2021-0145",
     # The CVE can be kept under control for its triggering.
     # See https://github.com/launchbadge/sqlx/pull/2455#issuecomment-1507657825 for more information.
     # Meanwhile, awaiting SQLx's new version (> 0.7.3) for full support of any DB driver.
-    "RUSTSEC-2022-0090"
+    "RUSTSEC-2022-0090",
+    # ckb-rich-indexer need sqlx's runtime-tokio-rustls feature, 
+    # ignore https://rustsec.org/advisories/RUSTSEC-2024-0336
+    "RUSTSEC-2024-0336"
 ]
 
 [licenses]
```
