# [?] Merge branch 'devnet-ready' into fix-crowdloan-reentrancy

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-23
Source: https://github.com/RaoFoundation/subtensor/commit/ab383133d8860591d8f3e8979fd50eac819dfdda
Type: security-commit

## Details
Merge branch 'devnet-ready' into fix-crowdloan-reentrancy

## Patch
### pallets/subtensor/src/subnets/subnet.rs
```diff
@@ -283,6 +283,9 @@ impl<T: Config> Pallet<T> {
         log::info!("NetworkAdded( netuid:{netuid_to_register:?}, mechanism:{mechid:?} )");
         Self::deposit_event(Event::NetworkAdded(netuid_to_register, mechid));
 
+        // --- 20. Default emission off
+        SubnetEmissionEnabled::<T>::insert(netuid_to_register, false);
+
         // --- 20. Return success.
         Ok(())
     }
```

### pallets/subtensor/src/tests/coinbase.rs
```diff
@@ -81,6 +81,8 @@ fn test_coinbase_tao_issuance_base() {
         let subnet_owner_ck = U256::from(1001);
         let subnet_owner_hk = U256::from(1002);
         let netuid = add_dynamic_network(&subnet_owner_hk, &subnet_owner_ck);
+        // Dynamic subnets register with emission disabled by default.
+        SubnetEmissionEnabled::<Test>::insert(netuid, true);
         // Price-based emission shares require a non-zero moving price.
         SubnetMovingPrice::<Test>::insert(netuid, I96F32::from_num(1));
         // Keep root_proportion ~1 so the injection cap does not bind.
```
