# [?] Fix multiplication overflow when logging hold times.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-06-24
Source: https://github.com/lightningdevkit/rust-lightning/commit/2257f682c719ea0f865398fbc25002a0c4d5efcb
Type: security-commit

## Details
Fix multiplication overflow when logging hold times.

With large reported hold times, the unit multiplication may exceed u32.

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
