# [?] Fix crash in notify_settlement_transactions_ready (#24583)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-12-10
Source: https://github.com/MystenLabs/sui/commit/de5226bd24bca56ebbff9d3ba43aa41a2c99b6d6
Type: security-commit

## Details
Fix crash in notify_settlement_transactions_ready (#24583)

## Patch
### crates/sui-core/src/authority/authority_per_epoch_store.rs
```diff
@@ -1893,7 +1893,9 @@ impl AuthorityPerEpochStore {
             let SettlementRegistration::Waiting(tx) = registration else {
                 fatal!("Settlement registration should be waiting");
             };
-            tx.send(txns).unwrap();
+            // Receiver is held in a `within_alive_epoch` task, so it may have
+            // been dropped already.
+            tx.send(txns).ok();
         } else {
             registrations.insert(tx_key, SettlementRegistration::Ready(txns));
         }
```
