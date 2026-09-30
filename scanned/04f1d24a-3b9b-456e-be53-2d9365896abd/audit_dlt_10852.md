# [?] [stress test] fix tx-factory crash when account_num is less than TXN_LIMIT (#1612)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-11-09
Source: https://github.com/starcoinorg/starcoin/commit/00eaf59909a559497123ca4a6f06a6c0423caa6b
Type: security-commit

## Details
[stress test] fix tx-factory crash when account_num is less than TXN_LIMIT (#1612)

## Patch
### cmd/tx-factory/src/main.rs
```diff
@@ -14,6 +14,7 @@ use starcoin_state_api::AccountStateReader;
 use starcoin_tx_factory::txn_generator::MockTxnGenerator;
 use starcoin_types::account_address::AccountAddress;
 use starcoin_types::account_config::association_address;
+use std::cmp::min;
 use std::path::PathBuf;
 use std::sync::atomic::{AtomicBool, Ordering};
 use std::sync::Arc;
@@ -505,7 +506,7 @@ impl TxnMocker {
             let seq = self.sequence_number(accounts[i].address)?;
             if let Some(seq) = seq {
                 let mut seq_num = seq;
-                while j < TXN_LIMIT {
+                while j < min(length, TXN_LIMIT) {
                     if i != j {
                         let result = self.gen_and_submit_transfer_txn(
                             accounts[i].address,
```
