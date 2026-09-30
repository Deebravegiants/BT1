# [?] fix panic in host env functions

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-01-31
Source: https://github.com/namada-net/namada/commit/e8fc61bb3225d6d755bef639d208fac6198805c9
Type: security-commit

## Details
fix panic in host env functions

## Patch
### crates/core/src/types/token.rs
```diff
@@ -18,7 +18,7 @@ use serde::{Deserialize, Serialize};
 use thiserror::Error;
 
 use crate::ibc::apps::transfer::types::Amount as IbcAmount;
-use crate::types::address::{Address, DecodeError as AddressError};
+use crate::types::address::Address;
 use crate::types::dec::{Dec, POS_DECIMAL_PRECISION};
 use crate::types::hash::Hash;
 use crate::types::storage;
@@ -99,9 +99,12 @@ impl Amount {
     }
 
     /// Spend a given amount.
-    /// Panics when given `amount` > `self.raw` amount.
-    pub fn spend(&mut self, amount: &Amount) {
-        self.raw = self.raw.checked_sub(amount.raw).unwrap();
+    pub fn spend(&mut self, amount: &Amount) -> Result<(), AmountError> {
+        self.raw = self
+            .raw
+            .checked_sub(amount.raw)
+            .ok_or(AmountError::Insufficient)?;
+        Ok(())
     }
 
     /// Check if there are enough funds.
@@ -110,9 +113,12 @@ impl Amount {
     }
 
     /// Receive a given amount.
-    /// Panics on overflow and when [`uint::MAX_SIGNED_VALUE`] is exceeded.
-    pub fn receive(&mut self, amount: &Amount) {
-        self.raw = self.raw.checked_add(amount.raw).unwrap();
+    pub fn receive(&mut self, amount: &Amount) -> Result<(), AmountError> {
+        self.raw = self
+            .raw
+            .checked_add(amount.raw)
+            .ok_or(AmountError::Overflow)?;
+        Ok(())
     }
 
     /// Create a new amount of native token from whole number of tokens
@@ -1060,13 +1066,11 @@ pub struct Transfer {
 
 #[allow(missing_docs)]
 #[derive(Error, Debug)]
-pub enum TransferError {
-    #[error("Invalid address is specified: {0}")]
-    Address(AddressError),
-    #[error("Invalid amount: {0}")]
-    Amount(AmountParseError),
-    #[error("No token is specified")]
-    NoToken,
+pub enum AmountError {
+    #[error("Insufficient amount")]
+    Insufficient,
+    #[error("Amount overlofow")]
+    Overflow,
 }
 
 #[cfg(any(test, feature = "testing"))]
```

### crates/ethereum_bridge/src/protocol/transactions/ethereum_events/events.rs
```diff
@@ -176,12 +176,13 @@ where
                 ?balance,
                 "Existing value found",
             );
-            balance.spend(amount);
+            balance.spend(amount)?;
             tracing::debug!(
                 %eth_bridge_native_token_balance_key,
                 ?balance,
                 "New value calculated",
             );
+            Ok(())
         },
     )?;
     update::amount(
@@ -193,12 +194,13 @@ where
                 ?balance,
                 "Existing value found",
             );
-            balance.receive(amount);
+            balance.receive(amount)?;
             tracing::debug!(
                 %receiver_native_token_balance_key,
                 ?balance,
                 "New value calculated",
             );
+            Ok(())
         },
     )?;
     update::amount(wl_storage, &native_werc20_supply_key, |balance| {
@@ -207,12 +209,13 @@ where
             ?balance,
             "Existing value found",
         );
-        balance.spend(amount);
+        balance.spend(amount)?;
         tracing::debug!(
             %native_werc20_supply_key,
             ?balance,
             "New value calculated",
         );
+        Ok(())
     })?;
 
     tracing::info!(
@@ -272,12 +275,13 @@ where
                 ?balance,
                 "Existing value found",
             );
-            balance.receive(amount);
+            balance.receive(amount)?;
             tracing::debug!(
                 %balance_key,
                 ?balance,
                 "New value calculated",
             );
+            Ok(())
         })?;
         _ = changed_keys.insert(balance_key);
 
@@ -288,12 +292,13 @@ where
                 ?supply,
                 "Existing value found",
             );
-            supply.receive(amount);
+            supply.receive(amount)?;
             tracing::debug!(
                 %supply_key,
                 ?supply,
                 "New value calculated",
             );
+            Ok(())
         })?;
         _ = changed_keys.insert(supply_key);
     }
@@ -357,11 +362,11 @@ where
             balance_key(&pending_transfer.gas_fee.token, relayer);
         // give the relayer the gas fee for this transfer.
         update::amount(wl_storage, &relayer_rewards_key, |balance| {
-            balance.receive(&pending_transfer.gas_fee.amount);
+            balance.receive(&pending_transfer.gas_fee.amount)
         })?;
         // the gas fee is removed from escrow.
         update::amount(wl_storage, &pool_balance_key, |balance| {
-            balance.spend(&pending_transfer.gas_fee.amount);
+            balance.spend(&pending_transfer.gas_fee.amount)
         })?;
         wl_storage.delete(&key)?;
         _ = pending_keys.remove(&key);
@@ -464,10 +469,10 @@ where
     let pool_balance_key =
         balance_key(&transfer.gas_fee.token, &BRIDGE_POOL_ADDRESS);
     update::amount(wl_storage, &payer_balance_key, |balance| {
-        balance.receive(&transfer.gas_fee.amount);
+        balance.receive(&transfer.gas_fee.amount)
     })?;
     update::amount(wl_storage, &pool_balance_key, |balance| {
-        balance.spend(&transfer.gas_fee.amount);
+        balance.spend(&transfer.gas_fee.amount)
     })?;
 
     tracing::debug!(?transfer, "Refunded Bridge pool transfer fees");
@@ -509,10 +514,10 @@ where
         (escrow_balance_key, sender_balance_key)
     };
     update::amount(wl_storage, &source, |balance| {
-        balance.spend(&transfer.transfer.amount);
+        balance.spend(&transfer.transfer.amount)
     })?;
     update::amount(wl_storage, &target, |balance| {
-        balance.receive(&transfer.transfer.amount);
+        balance.receive(&transfer.transfer.amount)
     })?;
 
     tracing::debug!(?transfer, "Refunded Bridge pool transferred assets");
@@ -550,7 +555,7 @@ where
         }
         let supply_key = minted_balance_key(&token);
         update::amount(wl_storage, &supply_key, |supply| {
-            supply.receive(&transfer.transfer.amount);
+            supply.receive(&transfer.transfer.amount)
         })?;
         _ = changed_keys.insert(supply_key);
         tracing::debug!(?transfer, "Updated wrapped NAM supply");
@@ -561,13 +566,13 @@ where
 
     let escrow_balance_key = balance_key(&token, &BRIDGE_POOL_ADDRESS);
     update::amount(wl_storage, &escrow_balance_key, |balance| {
-        balance.spend(&transfer.transfer.amount);
+        balance.spend(&transfer.transfer.amount)
     })?;
     _ = changed_keys.insert(escrow_balance_key);
 
     let supply_key = minted_balance_key(&token);
     update::amount(wl_storage, &supply_key, |supply| {
-        supply.spend(&transfer.transfer.amount);
+        supply.spend(&transfer.transfer.amount)
     })?;
     _ = changed_keys.insert(supply_key);
 
@@ -763,7 +768,7 @@ mod tests {
                 balance_key(&transfer.gas_fee.token, &BRIDGE_POOL_ADDRESS);
             update::amount(wl_storage, &escrow_key, |balance| {
                 let gas_fee = Amount::from_u64(1);
-                balance.receive(&gas_fee);
+                balance.receive(&gas_fee)
             })
             .expect("Test failed");
 
@@ -794,9 +799,7 @@ mod tests {
                 update::amount(
                     wl_storage,
                     &minted_balance_key(&token),
-                    |supply| {
-                        supply.receive(&transfer.transfer.amount);
-                    },
+                    |supply| supply.receive(&transfer.transfer.amount),
                 )
                 .expect("Test failed");
             };
@@ -1117,11 +1120,11 @@ mod tests {
         )
         .expect("Test failed");
 
-        bp_nam_balance_pre.spend(&bp_nam_balance_post);
+        bp_nam_balance_pre.spend(&bp_nam_balance_post).unwrap();
         assert_eq!(bp_nam_balance_pre, Amount::from(3));
         assert_eq!(bp_nam_balance_post, Amount::from(0));
 
-        bp_erc_balance_pre.spend(&bp_erc_balance_post);
+        bp_erc_balance_pre.spend(&bp_erc_balance_post).unwrap();
         assert_eq!(bp_erc_balance_pre, Amount::from(2));
         assert_eq!(bp_erc_balance_post, Amount::from(0));
     }
```

### crates/ethereum_bridge/src/protocol/transactions/update.rs
```diff
@@ -3,22 +3,22 @@ use eyre::Result;
 use namada_core::borsh::{BorshDeserialize, BorshSerialize};
 use namada_core::types::hash::StorageHasher;
 use namada_core::types::storage;
-use namada_core::types::token::Amount;
+use namada_core::types::token::{Amount, AmountError};
 use namada_state::{DBIter, WlStorage, DB};
 use namada_storage::StorageWrite;
 
 /// Reads the `Amount` from key, applies update then writes it back
 pub fn amount<D, H>(
     wl_storage: &mut WlStorage<D, H>,
     key: &storage::Key,
-    update: impl FnOnce(&mut Amount),
+    update: impl FnOnce(&mut Amount) -> Result<(), AmountError>,
 ) -> Result<Amount>
 where
     D: 'static + DB + for<'iter> DBIter<'iter> + Sync,
     H: 'static + StorageHasher + Sync,
 {
     let mut amount = super::read::amount_or_default(wl_storage, key)?;
-    update(&mut amount);
+    update(&mut amount)?;
     wl_storage.write(key, amount)?;
     Ok(amount)
 }
```

### crates/namada/src/ledger/native_vp/ibc/context.rs
```diff
@@ -3,9 +3,10 @@
 use std::collections::{BTreeSet, HashMap, HashSet};
 
 use borsh_ext::BorshSerializeExt;
+use ledger_storage::ResultExt;
 use namada_core::types::storage::Epochs;
 use namada_ibc::{IbcCommonContext, IbcStorageContext};
-use namada_state::{StorageRead, StorageWrite};
+use namada_state::{StorageRead, StorageWrite, StorageError};
 
 use crate::ledger::ibc::storage::is_ibc_key;
 use crate::ledger::native_vp::CtxPreStorageRead;
@@ -83,10 +84,10 @@ where
             }
             Some(StorageModification::Delete) => Ok(None),
             Some(StorageModification::Temp { .. }) => {
-                unreachable!("Temp shouldn't be inserted")
+                Err(StorageError::new_const("Temp shouldn't be inserted in an IBC transaction"))
             }
             Some(StorageModification::InitAccount { .. }) => {
-                unreachable!("InitAccount shouldn't be inserted")
+                Err(StorageError::new_const("InitAccount shouldn't be inserted"))
             }
             None => self.ctx.read_bytes(key),
         }
@@ -207,11 +208,13 @@ where
         let src_key = token::storage_key::balance_key(token, src);
         let dest_key = token::storage_key::balance_key(token, dest);
         let src_bal: Option<Amount> = self.ctx.read(&src_key)?;
-        let mut src_bal = src_bal.expect("The source has no balance");
-        src_bal.spend(&amount);
+        let mut src_bal = src_bal.ok_or_else(|| {
+            StorageError::new_const("the source has no balance")
+        })?;
+        src_bal.spend(&amount).into_storage_result()?;
         let mut dest_bal: Amount =
             self.ctx.read(&dest_key)?.unwrap_or_default();
-        dest_bal.receive(&amount);
+        dest_bal.receive(&amount).into_storage_result()?;
 
         self.write(&src_key, src_bal.serialize_to_vec())?;
         self.write(&dest_key, dest_bal.serialize_to_vec())
@@ -236,12 +239,12 @@ where
         let target_key = token::storage_key::balance_key(token, target);
         let mut target_bal: Amount =
             self.ctx.read(&target_key)?.unwrap_or_default();
-        target_bal.receive(&amount);
+        target_bal.receive(&amount).into_storage_result()?;
 
         let minted_key = token::storage_key::minted_balance_key(token);
         let mut minted_bal: Amount =
             self.ctx.read(&minted_key)?.unwrap_or_default();
-        minted_bal.receive(&amount);
+        minted_bal.receive(&amount).into_storage_result()?;
 
         self.write(&target_key, target_bal.serialize_to_vec())?;
         self.write(&minted_key, minted_bal.serialize_to_vec())?;
@@ -263,12 +266,12 @@ where
         let target_key = token::storage_key::balance_key(token, target);
         let mut target_bal: Amount =
             self.ctx.read(&target_key)?.unwrap_or_default();
-        target_bal.spend(&amount);
+        target_bal.spend(&amount).into_storage_result()?;
 
         let minted_key = token::storage_key::minted_balance_key(token);
         let mut minted_bal: Amount =
             self.ctx.read(&minted_key)?.unwrap_or_default();
-        minted_bal.spend(&amount);
+        minted_bal.spend(&amount).into_storage_result()?;
 
         self.write(&target_key, target_bal.serialize_to_vec())?;
         self.write(&minted_key, minted_bal.serialize_to_vec())
```

### crates/namada/src/vm/host_env.rs
```diff
@@ -16,7 +16,7 @@ use namada_gas::{
     MEMORY_ACCESS_GAS_PER_BYTE,
 };
 use namada_state::write_log::{self, WriteLog};
-use namada_state::{self, ResultExt, State, StorageHasher};
+use namada_state::{self, ResultExt, State, StorageError, StorageHasher};
 use namada_token::storage_key::is_any_token_parameter_key;
 use namada_tx::data::TxSentinel;
 use namada_tx::Tx;
@@ -61,7 +61,7 @@ pub enum TxRuntimeError {
     #[error("State error: {0}")]
     StateError(#[from] namada_state::Error),
     #[error("Storage error: {0}")]
-    StorageError(#[from] namada_state::StorageError),
+    StorageError(#[from] StorageError),
     #[error("Storage data error: {0}")]
     StorageDataError(crate::types::storage::Error),
     #[error("Encoding error: {0}")]
@@ -2380,7 +2380,7 @@ where
     fn read_bytes(
         &self,
         key: &Key,
-    ) -> std::result::Result<Option<Vec<u8>>, namada_state::StorageError> {
+    ) -> std::result::Result<Option<Vec<u8>>, StorageError> {
         let write_log = unsafe { self.write_log.get() };
         let (log_val, gas) = write_log.read(key);
         ibc_tx_charge_gas(self, gas)?;
@@ -2405,7 +2405,7 @@ where
         })
     }
 
-    fn has_key(&self, key: &Key) -> Result<bool, namada_state::StorageError> {
+    fn has_key(&self, key: &Key) -> Result<bool, StorageError> {
         // try to read from the write log first
         let write_log = unsafe { self.write_log.get() };
         let (log_val, gas) = write_log.read(key);
@@ -2429,7 +2429,7 @@ where
     fn iter_prefix<'iter>(
         &'iter self,
         prefix: &Key,
-    ) -> Result<Self::PrefixIter<'iter>, namada_state::StorageError> {
+    ) -> Result<Self::PrefixIter<'iter>, StorageError> {
         let write_log = unsafe { self.write_log.get() };
         let storage = unsafe { self.storage.get() };
         let (iter, gas) =
@@ -2443,7 +2443,7 @@ where
     fn iter_next<'iter>(
         &'iter self,
         iter_id: &mut Self::PrefixIter<'iter>,
-    ) -> Result<Option<(String, Vec<u8>)>, namada_state::StorageError> {
+    ) -> Result<Option<(String, Vec<u8>)>, StorageError> {
         let write_log = unsafe { self.write_log.get() };
         let iterators = unsafe { self.iterators.get() };
         let iter_id = PrefixIteratorId::new(*iter_id);
@@ -2476,16 +2476,14 @@ where
         Ok(None)
     }
 
-    fn get_chain_id(&self) -> Result<String, namada_state::StorageError> {
+    fn get_chain_id(&self) -> Result<String, StorageError> {
         let storage = unsafe { self.storage.get() };
         let (chain_id, gas) = storage.get_chain_id();
         ibc_tx_charge_gas(self, gas)?;
         Ok(chain_id)
     }
 
-    fn get_block_height(
-        &self,
-    ) -> Result<BlockHeight, namada_state::StorageError> {
+    fn get_block_height(&self) -> Result<BlockHeight, StorageError> {
         let storage = unsafe { self.storage.get() };
         let (height, gas) = storage.get_block_height();
         ibc_tx_charge_gas(self, gas)?;
@@ -2495,10 +2493,7 @@ where
     fn get_block_header(
         &self,
         height: BlockHeight,
-    ) -> Result<
-        Option<namada_core::types::storage::Header>,
-        namada_state::StorageError,
-    > {
+    ) -> Result<Option<namada_core::types::storage::Header>, StorageError> {
         let storage = unsafe { self.storage.get() };
         let (header, gas) = storage
             .get_block_header(Some(height))
@@ -2507,21 +2502,21 @@ where
         Ok(header)
     }
 
-    fn get_block_hash(&self) -> Result<BlockHash, namada_state::StorageError> {
+    fn get_block_hash(&self) -> Result<BlockHash, StorageError> {
         let storage = unsafe { self.storage.get() };
         let (hash, gas) = storage.get_block_hash();
         ibc_tx_charge_gas(self, gas)?;
         Ok(hash)
     }
 
-    fn get_block_epoch(&self) -> Result<Epoch, namada_state::StorageError> {
+    fn get_block_epoch(&self) -> Result<Epoch, StorageError> {
         let storage = unsafe { self.storage.get() };
         let (epoch, gas) = storage.get_current_epoch();
         ibc_tx_charge_gas(self, gas)?;
         Ok(epoch)
     }
 
-    fn get_tx_index(&self) -> Result<TxIndex, namada_state::StorageError> {
+    fn get_tx_index(&self) -> Result<TxIndex, StorageError> {
         let tx_index = unsafe { self.tx_index.get() };
         ibc_tx_charge_gas(
             self,
@@ -2530,7 +2525,7 @@ where
         Ok(TxIndex(tx_index.0))
     }
 
-    fn get_native_token(&self) -> Result<Address, namada_state::StorageError> {
+    fn get_native_token(&self) -> Result<Address, StorageError> {
         let storage = unsafe { self.storage.get() };
         let native_token = storage.native_token.clone();
         ibc_tx_charge_gas(
@@ -2562,15 +2557,15 @@ where
         &mut self,
         key: &Key,
         data: impl AsRef<[u8]>,
-    ) -> Result<(), namada_state::StorageError> {
+    ) -> Result<(), StorageError> {
         let write_log = unsafe { self.write_log.get() };
         let (gas, _size_diff) = write_log
             .write(key, data.as_ref().to_vec())
             .into_storage_result()?;
         ibc_tx_charge_gas(self, gas)
     }
 
-    fn delete(&mut self, key: &Key) -> Result<(), namada_state::StorageError> {
+    fn delete(&mut self, key: &Key) -> Result<(), StorageError> {
         if key.is_validity_predicate().is_some() {
             return Err(TxRuntimeError::CannotDeleteVp).into_storage_result();
         }
@@ -2588,10 +2583,7 @@ where
     H: StorageHasher,
     CA: WasmCacheAccess,
 {
-    fn emit_ibc_event(
-        &mut self,
-        event: IbcEvent,
-    ) -> Result<(), namada_state::StorageError> {
+    fn emit_ibc_event(&mut self, event: IbcEvent) -> Result<(), StorageError> {
         let write_log = unsafe { self.write_log.get() };
         let gas = write_log.emit_ibc_event(event);
         ibc_tx_charge_gas(self, gas)
@@ -2600,7 +2592,7 @@ where
     fn get_ibc_events(
         &self,
         event_type: impl AsRef<str>,
-    ) -> Result<Vec<IbcEvent>, namada_state::StorageError> {
+    ) -> Result<Vec<IbcEvent>, StorageError> {
         let write_log = unsafe { self.write_log.get() };
         Ok(write_log
             .get_ibc_events()
@@ -2616,22 +2608,21 @@ where
         dest: &Address,
         token: &Address,
         amount: crate::token::DenominatedAmount,
-    ) -> Result<(), namada_state::StorageError> {
+    ) -> Result<(), StorageError> {
         use crate::token;
 
         let amount = token::denom_to_amount(amount, token, self)?;
         if amount != token::Amount::default() && src != dest {
             let src_key = balance_key(token, src);
             let dest_key = balance_key(token, dest);
             let src_bal = self.read::<token::Amount>(&src_key)?;
-            let mut src_bal = src_bal.unwrap_or_else(|| {
-                self.log_string(format!("src {} has no balance", src_key));
-                unreachable!()
-            });
-            src_bal.spend(&amount);
+            let mut src_bal = src_bal.ok_or_else(|| {
+                StorageError::new_const("the source has no balance")
+            })?;
+            src_bal.spend(&amount).into_storage_result()?;
             let mut dest_bal =
                 self.read::<token::Amount>(&dest_key)?.unwrap_or_default();
-            dest_bal.receive(&amount);
+            dest_bal.receive(&amount).into_storage_result()?;
             self.write(&src_key, src_bal)?;
             self.write(&dest_key, dest_bal)?;
         }
@@ -2642,7 +2633,7 @@ where
         &mut self,
         shielded: &masp_primitives::transaction::Transaction,
         pin_key: Option<&str>,
-    ) -> Result<(), namada_state::StorageError> {
+    ) -> Result<(), StorageError> {
         crate::token::utils::handle_masp_tx(self, shielded, pin_key)?;
         crate::token::utils::update_note_commitment_tree(self, shielded)
     }
@@ -2652,19 +2643,19 @@ where
         target: &Address,
         token: &Address,
         amount: crate::token::DenominatedAmount,
-    ) -> Result<(), namada_state::StorageError> {
+    ) -> Result<(), StorageError> {
         use crate::token;
 
         let amount = token::denom_to_amount(amount, token, self)?;
         let target_key = balance_key(token, target);
         let mut target_bal =
             self.read::<token::Amount>(&target_key)?.unwrap_or_default();
-        target_bal.receive(&amount);
+        target_bal.receive(&amount).into_storage_result()?;
 
         let minted_key = minted_balance_key(token);
         let mut minted_bal =
             self.read::<token::Amount>(&minted_key)?.unwrap_or_default();
-        minted_bal.receive(&amount);
+        minted_bal.receive(&amount).into_storage_result()?;
 
         self.write(&target_key, target_bal)?;
         self.write(&minted_key, minted_bal)?;
@@ -2681,20 +2672,20 @@ where
         target: &Address,
         token: &Address,
         amount: crate::token::DenominatedAmount,
-    ) -> Result<(), namada_state::StorageError> {
+    ) -> Result<(), StorageError> {
         use crate::token;
 
         let amount = token::denom_to_amount(amount, token, self)?;
         let target_key = balance_key(token, target);
         let mut target_bal =
             self.read::<token::Amount>(&target_key)?.unwrap_or_default();
-        target_bal.spend(&amount);
+        target_bal.spend(&amount).into_storage_result()?;
 
         // burn the minted amount
         let minted_key = minted_balance_key(token);
         let mut minted_bal =
             self.read::<token::Amount>(&minted_key)?.unwrap_or_default();
-        minted_bal.spend(&amount);
+        minted_bal.spend(&amount).into_storage_result()?;
 
         self.write(&target_key, target_bal)?;
         self.write(&minted_key, minted_bal)
@@ -2710,7 +2701,7 @@ where
 fn ibc_tx_charge_gas<'a, DB, H, CA>(
     ctx: &TxCtx<'a, DB, H, CA>,
     used_gas: u64,
-) -> Result<(), namada_state::StorageError>
+) -> Result<(), StorageError>
 where
     DB: namada_state::DB + for<'iter> namada_state::DBIter<'iter>,
     H: StorageHasher,
```

### crates/sdk/src/eth_bridge/bridge_pool.rs
```diff
@@ -537,19 +537,20 @@ pub async fn construct_proof(
         relayer_address: args.relayer,
         total_fees: appendices
             .map(|appendices| {
-                appendices.into_iter().fold(
+                appendices.into_iter().try_fold(
                     HashMap::new(),
                     |mut total_fees, app| {
                         let GasFee { token, amount, .. } =
                             app.gas_fee.into_owned();
                         let fees = total_fees
                             .entry(token)
                             .or_insert_with(Amount::zero);
-                        fees.receive(&amount);
-                        total_fees
+                        fees.receive(&amount).map_err(|e| Error::Other(e.to_string()))?;
+                        Ok::<_, Error>(total_fees)
                     },
                 )
             })
+            .transpose()?
             .unwrap_or_default(),
         abi_encoded_args,
     };
```

### crates/tests/src/native_vp/pos.rs
```diff
@@ -1319,10 +1319,10 @@ pub mod testing {
                     tx::ctx().read(&balance_key).unwrap().unwrap_or_default();
                 if !delta.non_negative() {
                     let to_spend = token::Amount::from_change(delta);
-                    balance.spend(&to_spend);
+                    balance.spend(&to_spend).unwrap();
                 } else {
                     let to_recv = token::Amount::from_change(delta);
-                    balance.receive(&to_recv);
+                    balance.receive(&to_recv).unwrap();
                 }
                 tx::ctx().write(&balance_key, balance).unwrap();
             }
```

### crates/tx_prelude/src/token.rs
```diff
@@ -2,9 +2,10 @@ use namada_core::types::address::Address;
 use namada_proof_of_stake::token::storage_key::{
     balance_key, minted_balance_key, minter_key,
 };
+use namada_storage::{Error as StorageError, ResultExt};
 pub use namada_token::*;
 
-use crate::{log_string, Ctx, StorageRead, StorageWrite, TxResult};
+use crate::{Ctx, StorageRead, StorageWrite, TxResult};
 
 #[allow(clippy::too_many_arguments)]
 /// A token transfer that can be used in a transaction.
@@ -20,13 +21,12 @@ pub fn transfer(
         let src_key = balance_key(token, src);
         let dest_key = balance_key(token, dest);
         let src_bal: Option<Amount> = ctx.read(&src_key)?;
-        let mut src_bal = src_bal.unwrap_or_else(|| {
-            log_string(format!("src {} has no balance", src_key));
-            unreachable!()
-        });
-        src_bal.spend(&amount);
+        let mut src_bal = src_bal.ok_or_else(|| {
+            StorageError::new_const("the source has no balance")
+        })?;
+        src_bal.spend(&amount).into_storage_result()?;
         let mut dest_bal: Amount = ctx.read(&dest_key)?.unwrap_or_default();
-        dest_bal.receive(&amount);
+        dest_bal.receive(&amount).into_storage_result()?;
         ctx.write(&src_key, src_bal)?;
         ctx.write(&dest_key, dest_bal)?;
     }
@@ -45,13 +45,12 @@ pub fn undenominated_transfer(
         let src_key = balance_key(token, src);
         let dest_key = balance_key(token, dest);
         let src_bal: Option<Amount> = ctx.read(&src_key)?;
-        let mut src_bal = src_bal.unwrap_or_else(|| {
-            log_string(format!("src {} has no balance", src_key));
-            unreachable!()
-        });
-        src_bal.spend(&amount);
+        let mut src_bal = src_bal.ok_or_else(|| {
+            StorageError::new_const("the source has no balance")
+        })?;
+        src_bal.spend(&amount).into_storage_result()?;
         let mut dest_bal: Amount = ctx.read(&dest_key)?.unwrap_or_default();
-        dest_bal.receive(&amount);
+        dest_bal.receive(&amount).into_storage_result()?;
         ctx.write(&src_key, src_bal)?;
         ctx.write(&dest_key, dest_bal)?;
     }
@@ -68,11 +67,11 @@ pub fn mint(
 ) -> TxResult {
     let target_key = balance_key(token, target);
     let mut target_bal: Amount = ctx.read(&target_key)?.unwrap_or_default();
-    target_bal.receive(&amount);
+    target_bal.receive(&amount).into_storage_result()?;
 
     let minted_key = minted_balance_key(token);
     let mut minted_bal: Amount = ctx.read(&minted_key)?.unwrap_or_default();
-    minted_bal.receive(&amount);
+    minted_bal.receive(&amount).into_storage_result()?;
 
     ctx.write(&target_key, target_bal)?;
     ctx.write(&minted_key, minted_bal)?;
@@ -92,12 +91,12 @@ pub fn burn(
 ) -> TxResult {
     let target_key = balance_key(token, target);
     let mut target_bal: Amount = ctx.read(&target_key)?.unwrap_or_default();
-    target_bal.spend(&amount);
+    target_bal.spend(&amount).into_storage_result()?;
 
     // burn the minted amount
     let minted_key = minted_balance_key(token);
     let mut minted_bal: Amount = ctx.read(&minted_key)?.unwrap_or_default();
-    minted_bal.spend(&amount);
+    minted_bal.spend(&amount).into_storage_result()?;
 
     ctx.write(&target_key, target_bal)?;
     ctx.write(&minted_key, minted_bal)?;
```
