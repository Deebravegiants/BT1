# [?] ci: Ignore tungstenite security advisory (#5404)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2023-10-02
Source: https://github.com/solana-labs/solana-program-library/commit/a95c6d14d9305d6a77656bc6bc36c10d54ad7e97
Type: security-commit

## Details
ci: Ignore tungstenite security advisory (#5404)

## Patch
### ci/do-audit.sh
```diff
@@ -25,5 +25,10 @@ cargo_audit_ignores=(
   #
   # No fixed upgrade is available! Only fix is switching to rustls-webpki
   --ignore RUSTSEC-2023-0052
+
+  # tungstenite
+  #
+  # Remove once SPL upgrades to Solana v1.17 or greater
+  --ignore RUSTSEC-2023-0065
 )
 cargo +"$rust_stable" audit "${cargo_audit_ignores[@]}"
```
