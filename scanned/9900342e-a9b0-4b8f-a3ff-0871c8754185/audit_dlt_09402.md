# [?] Merge pull request #3888 from joostjager/fix-hold-time-overflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-06-24
Source: https://github.com/lightningdevkit/rust-lightning/commit/24063e54cc3df74b93d3468ec98828aed623029a
Type: security-commit

## Details
Merge pull request #3888 from joostjager/fix-hold-time-overflow

Fix multiplication overflow when logging hold times.

## Patch
### lightning/src/ln/onion_utils.rs
```diff
@@ -1226,7 +1226,7 @@ where
 							logger,
 							"Htlc hold time at pos {}: {} ms",
 							route_hop_idx,
-							hold_time * HOLD_TIME_UNIT_MILLIS as u32
+							(hold_time as u128) * HOLD_TIME_UNIT_MILLIS
 						);
 
 						// Shift attribution data to prepare for processing the next hop.
```
