# [?] Merge pull request #2916 from pyth-network/devin/1753996233-debug-guardian-set-split-at-crash

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2025-07-31
Source: https://github.com/pyth-network/pyth-crosschain/commit/dcd8dae8838c97f7ad6354fe61c55373bd1881cb
Type: security-commit

## Details
Merge pull request #2916 from pyth-network/devin/1753996233-debug-guardian-set-split-at-crash

Fix guardian set parsing crash in Fuel contracts

## Patch
### target_chains/fuel/contracts/pyth-interface/src/data_structures/wormhole_light.sw
```diff
@@ -112,27 +112,16 @@ impl GuardianSetUpgrade {
             StorageKey::<StorageVec<b256>>::new(ZERO_B256, 0, sha256(("guardian_set_keys", new_guardian_set_index))),
         );
         let mut i: u8 = 0;
-        log(encoded_upgrade);
-        log(encoded_upgrade.len());
-        log(guardian_length);
         while i < guardian_length {
             let (_, slice) = encoded_upgrade.split_at(index);
-            
-            log(index);
-            log(slice);
-            
             let (key, _) = slice.split_at(20);
-
-            log(key);
-
-            revert(0u64);
             let mut full_address_key = Bytes::with_capacity(32);
 
 
-            let mut i = 0;
-            while i < 12 {
+            let mut j = 0;
+            while j < 12 {
                 full_address_key.push(0u8);
-                i += 1;
+                j += 1;
             }
 
             // Append the 20-byte data
@@ -143,13 +132,11 @@ impl GuardianSetUpgrade {
             let key: b256 = b256::from_be_bytes(full_address_key.clone());
 
             
-            new_guardian_set.keys.push(key.rsh(96));
+            new_guardian_set.keys.push(key);
             index += 20;
             i += 1;
         }
 
-        log("finished key extraction");
-
         require(
             new_guardian_set
                 .keys
```
