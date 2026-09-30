# [?] add balance to cap overflow message (#28975)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-11-29
Source: https://github.com/solana-labs/solana/commit/19d86bd2b1223e127a40596e97277ebdd5b5340d
Type: security-commit

## Details
add balance to cap overflow message (#28975)

## Patch
### runtime/src/accounts_hash.rs
```diff
@@ -706,9 +706,12 @@ impl AccountsHasher {
     }
 
     pub fn checked_cast_for_capitalization(balance: u128) -> u64 {
-        balance
-            .try_into()
-            .expect("overflow is detected while summing capitalization")
+        balance.try_into().unwrap_or_else(|_| {
+            panic!(
+                "overflow is detected while summing capitalization: {}",
+                balance
+            )
+        })
     }
 
     /// return references to cache hash data, grouped by bin, sourced from 'sorted_data_by_pubkey',
```
