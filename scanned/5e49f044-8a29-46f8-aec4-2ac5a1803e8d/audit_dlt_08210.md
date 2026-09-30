# [?] ci: remove --ignore RUSTSEC-2022-0093 (#33019)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-08-29
Source: https://github.com/solana-labs/solana/commit/37887d487ce9b87297d9a20dd07a89adf4c66cd5
Type: security-commit

## Details
ci: remove --ignore RUSTSEC-2022-0093 (#33019)

ci: remove --ignore RUSTSEC-2023-0052

## Patch
### ci/do-audit.sh
```diff
@@ -30,10 +30,6 @@ cargo_audit_ignores=(
   --ignore RUSTSEC-2023-0001
 
   --ignore RUSTSEC-2022-0093
-
-  # webpki: CPU denial of service in certificate path building
-  # No fixed upgrade is available!
-  --ignore RUSTSEC-2023-0052
 )
 scripts/cargo-for-all-lock-files.sh audit "${cargo_audit_ignores[@]}" | $dep_tree_filter
 # we want the `cargo audit` exit code, not `$dep_tree_filter`'s
```
