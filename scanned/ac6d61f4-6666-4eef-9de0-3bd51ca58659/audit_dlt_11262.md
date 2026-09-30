# [?] chore: remove stale RUSTSEC-2026-0002 advisory (#11231)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-16
Source: https://github.com/noir-lang/noir/commit/6e7a757eaf5da6313c99878da9b026e09957c213
Type: security-commit

## Details
chore: remove stale RUSTSEC-2026-0002 advisory (#11231)

## Patch
### deny.toml
```diff
@@ -8,7 +8,6 @@ yanked = "warn"
 ignore = [
     "RUSTSEC-2024-0388", # derivative unmaintained
     "RUSTSEC-2024-0436", # paste unmaintained
-    "RUSTSEC-2026-0002", # Blocked on https://github.com/cmpute/num-prime/pull/26
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
