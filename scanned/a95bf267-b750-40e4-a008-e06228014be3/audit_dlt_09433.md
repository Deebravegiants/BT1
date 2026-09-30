# [?] fix: complete GHSA-2026-010 — merge RootClaimed by max() (edit dropped during distribution)

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/818927201e000f30d6cdb3bdfaf17249e6333a03
Type: security-commit

## Details
fix: complete GHSA-2026-010 — merge RootClaimed by max() (edit dropped during distribution)

## Patch
### pallets/subtensor/src/staking/claim_root.rs
```diff
@@ -460,7 +460,10 @@ impl<T: Config> Pallet<T> {
         RootClaimed::<T>::remove((netuid, old_hotkey, old_coldkey));
 
         RootClaimed::<T>::mutate((netuid, new_hotkey, new_coldkey), |new_root_claimed| {
-            *new_root_claimed = old_root_claimed.saturating_add(*new_root_claimed);
+            // Take the maximum rather than summing so that a stale residual watermark
+            // already present on the destination cannot inflate the merged value past
+            // the correct claimable high-water mark (GHSA-2026-010).
+            *new_root_claimed = old_root_claimed.max(*new_root_claimed);
         });
     }
     pub fn transfer_root_claimable_for_new_hotkey(
```
