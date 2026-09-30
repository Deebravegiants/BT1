# [?] Add exception for RUSTSEC-2023-0001 to unblock CI. (#29585)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-01-09
Source: https://github.com/solana-labs/solana/commit/3aa0a005f942406968a29c81822564ec994959c9
Type: security-commit

## Details
Add exception for RUSTSEC-2023-0001 to unblock CI. (#29585)

* Add exception for RUSTSEC-2023-0001 to unblock CI. This Tokio issue only affects windows.

## Patch
### ci/do-audit.sh
```diff
@@ -12,5 +12,11 @@ cargo_audit_ignores=(
   #
   # Blocked on chrono updating `time` to >= 0.2.23
   --ignore RUSTSEC-2020-0071
+
+  # tokio: vulnerability affecting named pipes on Windows
+  #
+  # Exception is a stopgap to unblock CI
+  # https://github.com/solana-labs/solana/issues/29586
+  --ignore RUSTSEC-2023-0001
 )
 scripts/cargo-for-all-lock-files.sh stable audit "${cargo_audit_ignores[@]}"
```
