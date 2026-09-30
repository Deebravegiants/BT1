# [?] Fix non-determinism in account_hash_ignore_slot on genesis (#33692)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-10-16
Source: https://github.com/solana-labs/solana/commit/69495f4c13e025d8dc473438b31cc0f1788dc352
Type: security-commit

## Details
Fix non-determinism in account_hash_ignore_slot on genesis (#33692)

## Patch
### runtime/src/bank.rs
```diff
@@ -3837,6 +3837,16 @@ impl Bank {
         // Bootstrap validator collects fees until `new_from_parent` is called.
         self.fee_rate_governor = genesis_config.fee_rate_governor.clone();
 
+        // Make sure to activate the account_hash_ignore_slot feature
+        // before calculating any account hashes.
+        if genesis_config
+            .accounts
+            .iter()
+            .any(|(pubkey, _)| pubkey == &feature_set::account_hash_ignore_slot::id())
+        {
+            self.activate_feature(&feature_set::account_hash_ignore_slot::id());
+        }
+
         for (pubkey, account) in genesis_config.accounts.iter() {
             assert!(
                 self.get_account(pubkey).is_none(),
```
