# [?] Merge fix/swap-owner-stale-test into security/ghsa-2026-011-hotkey-swap-subnet-interval-bypass

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-12
Source: https://github.com/RaoFoundation/subtensor/commit/ccb7331356c1399c5ededc5fd686dbb0687aceed
Type: security-commit

## Details
Merge fix/swap-owner-stale-test into security/ghsa-2026-011-hotkey-swap-subnet-interval-bypass

## Patch
### pallets/subtensor/src/tests/swap_hotkey_with_subnet.rs
```diff
@@ -907,14 +907,15 @@ fn test_swap_owner_new_hotkey_already_exists() {
         let old_hotkey = U256::from(1);
         let new_hotkey = U256::from(2);
         let coldkey = U256::from(3);
-        let another_coldkey = U256::from(4);
 
         let netuid = add_dynamic_network(&new_hotkey, &coldkey);
         add_balance_to_coldkey_account(&coldkey, 1_000_000_000_000_u64.into());
 
-        // Initialize Owner for old_hotkey and new_hotkey
+        // old_hotkey is owned by coldkey; new_hotkey was already registered on `netuid`
+        // by add_dynamic_network (the condition under test). Do NOT reassign new_hotkey to
+        // a foreign coldkey — the new_hotkey-ownership check (NonAssociatedColdKey) would
+        // then fire before the already-registered-in-subnet check this test targets.
         Owner::<Test>::insert(old_hotkey, coldkey);
-        Owner::<Test>::insert(new_hotkey, another_coldkey);
 
         // Perform the swap
         System::set_block_number(System::block_number() + HotkeySwapOnSubnetInterval::get());
```
