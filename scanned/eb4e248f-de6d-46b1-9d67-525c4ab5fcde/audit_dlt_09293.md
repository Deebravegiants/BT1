# [?] fix(anvil): prevent panic in `utc_from_secs`  for out-of-range timestamps (#13520)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-02-24
Source: https://github.com/foundry-rs/foundry/commit/7db11a53334ee23e6a275e3569a1e31acf21deda
Type: security-commit

## Details
fix(anvil): prevent panic in `utc_from_secs`  for out-of-range timestamps (#13520)

## Patch
### crates/anvil/src/eth/backend/time.rs
```diff
@@ -7,7 +7,7 @@ use std::{sync::Arc, time::Duration};
 
 /// Returns the `Utc` datetime for the given seconds since unix epoch
 pub fn utc_from_secs(secs: u64) -> DateTime<Utc> {
-    DateTime::from_timestamp(secs as i64, 0).unwrap()
+    DateTime::from_timestamp(secs as i64, 0).unwrap_or(DateTime::<Utc>::MAX_UTC)
 }
 
 /// Manages block time
```
