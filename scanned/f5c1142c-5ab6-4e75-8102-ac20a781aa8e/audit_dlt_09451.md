# [?] fix: do not gate the first all-subnets hotkey swap by chain age (GHSA-2026-011)

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-12
Source: https://github.com/RaoFoundation/subtensor/commit/3f4fa5dc3a50c0191d5f2b0a013977c50d047054
Type: security-commit

## Details
fix: do not gate the first all-subnets hotkey swap by chain age (GHSA-2026-011)

## Patch
### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -142,10 +142,16 @@ impl<T: Config> Pallet<T> {
         );
         for netuid in affected_netuids.iter() {
             let last_hotkey_swap_block = LastHotkeySwapOnNetuid::<T>::get(*netuid, &coldkey);
-            ensure!(
-                last_hotkey_swap_block.saturating_add(hotkey_swap_interval) < block,
-                Error::<T>::HotKeySwapOnSubnetIntervalNotPassed
-            );
+            // Only enforce the cooldown when a prior swap was recorded on this subnet.
+            // A first swap (no recorded timestamp) must not be gated by chain age — that
+            // would block the very first swap and never closes a bypass, since any swap
+            // records the timestamp and subsequent swaps within the interval are rejected.
+            if last_hotkey_swap_block != 0 {
+                ensure!(
+                    last_hotkey_swap_block.saturating_add(hotkey_swap_interval) < block,
+                    Error::<T>::HotKeySwapOnSubnetIntervalNotPassed
+                );
+            }
             weight.saturating_accrue(T::DbWeight::get().reads(1));
         }
 
```
