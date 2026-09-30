# [?] Fix for Panic Issue in Historical Replay Tests Due to DAO Parameter Initialization

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2023-12-26
Source: https://github.com/Conflux-Chain/conflux-rust/commit/9ee4ab2b3e0d0692c2ee256395dfbd4a4d0226c8
Type: security-commit

## Details
Fix for Panic Issue in Historical Replay Tests Due to DAO Parameter Initialization

## Patch
### core/executor/src/context.rs
```diff
@@ -111,15 +111,15 @@ impl<'a> Context<'a> {
 
 impl<'a> ContextTrait for Context<'a> {
     fn storage_at(&self, key: &Vec<u8>) -> vm::Result<U256> {
-        let caller = AddressWithSpace {
+        let receiver = AddressWithSpace {
             address: self.origin.address,
             space: self.space,
         };
-        self.state.storage_at(&caller, key).map_err(Into::into)
+        self.state.storage_at(&receiver, key).map_err(Into::into)
     }
 
     fn set_storage(&mut self, key: Vec<u8>, value: U256) -> vm::Result<()> {
-        let caller = AddressWithSpace {
+        let receiver = AddressWithSpace {
             address: self.origin.address,
             space: self.space,
         };
@@ -128,7 +128,7 @@ impl<'a> ContextTrait for Context<'a> {
         } else {
             self.state
                 .set_storage(
-                    &caller,
+                    &receiver,
                     key,
                     value,
                     self.origin.storage_owner,
```

### core/executor/src/state/mod.rs
```diff
@@ -18,13 +18,12 @@ mod overlay_account;
 /// State Object: Represents the core object of the state module.
 mod state_object;
 
-pub use overlay_account::COMMISSION_PRIVILEGE_SPECIAL_KEY;
 #[cfg(test)]
 pub use state_object::get_state_for_genesis_write;
 pub use state_object::{
     distribute_pos_interest, initialize_cip107,
     initialize_or_update_dao_voted_params, settle_collateral_for_all,
-    update_pos_status, State,
+    update_pos_status, State, COMMISSION_PRIVILEGE_SPECIAL_KEY,
 };
 
 use cfx_types::AddressWithSpace;
```

### core/executor/src/state/overlay_account/mod.rs
```diff
@@ -48,7 +48,6 @@ mod tests;
 
 pub use account_entry::AccountEntry;
 pub use ext_fields::RequireFields;
-pub use sponsor::COMMISSION_PRIVILEGE_SPECIAL_KEY;
 
 use crate::substate::Substate;
 use cfx_types::{
```

### core/executor/src/state/overlay_account/sponsor.rs
```diff
@@ -1,15 +1,8 @@
 use cfx_parameters::consensus::ONE_CFX_IN_DRIP;
-use cfx_statedb::{Result as DbResult, StateDbGeneric};
 use cfx_types::{Address, U256};
 use primitives::SponsorInfo;
 
-use super::{OverlayAccount, Substate};
-
-lazy_static! {
-    static ref COMMISSION_PRIVILEGE_STORAGE_VALUE: U256 = U256::one();
-    /// If we set this key, it means every account has commission privilege.
-    pub static ref COMMISSION_PRIVILEGE_SPECIAL_KEY: Address = Address::zero();
-}
+use super::OverlayAccount;
 
 impl OverlayAccount {
     pub fn sponsor_info(&self) -> &SponsorInfo { &self.sponsor_info }
@@ -68,55 +61,4 @@ impl OverlayAccount {
         assert!(self.sponsor_info.sponsor_balance_for_collateral >= *by);
         self.sponsor_info.sponsor_balance_for_collateral -= *by;
     }
-
-    pub fn check_contract_whitelist(
-        &self, db: &StateDbGeneric, contract_address: &Address, user: &Address,
-    ) -> DbResult<bool> {
-        let mut special_key = Vec::with_capacity(Address::len_bytes() * 2);
-        special_key.extend_from_slice(contract_address.as_bytes());
-        special_key
-            .extend_from_slice(COMMISSION_PRIVILEGE_SPECIAL_KEY.as_bytes());
-        let special_value = self.storage_at(db, &special_key)?;
-        if !special_value.is_zero() {
-            Ok(true)
-        } else {
-            let mut key = Vec::with_capacity(Address::len_bytes() * 2);
-            key.extend_from_slice(contract_address.as_bytes());
-            key.extend_from_slice(user.as_bytes());
-            self.storage_at(db, &key).map(|x| !x.is_zero())
-        }
-    }
-
-    /// Add commission privilege of `contract_address` to `user`.
-    /// We set the value to some nonzero value which will be persisted in db.
-    pub fn add_to_contract_whitelist(
-        &mut self, db: &StateDbGeneric, contract_address: Address,
-        user: Address, storage_owner: Address, substate: &mut Substate,
-    ) -> DbResult<()>
-    {
-        let mut key = Vec::with_capacity(Address::len_bytes() * 2);
-        key.extend_from_slice(contract_address.as_bytes());
-        key.extend_from_slice(user.as_bytes());
-        self.set_storage(
-            db,
-            key,
-            COMMISSION_PRIVILEGE_STORAGE_VALUE.clone(),
-            storage_owner,
-            substate,
-        )
-    }
-
-    /// Remove commission privilege of `contract_address` from `user`.
-    /// We set the value to zero, and the key/value will be released at commit
-    /// phase.
-    pub fn remove_from_contract_whitelist(
-        &mut self, db: &StateDbGeneric, contract_address: Address,
-        user: Address, storage_owner: Address, substate: &mut Substate,
-    ) -> DbResult<()>
-    {
-        let mut key = Vec::with_capacity(Address::len_bytes() * 2);
-        key.extend_from_slice(contract_address.as_bytes());
-        key.extend_from_slice(user.as_bytes());
-        self.set_storage(db, key, U256::zero(), storage_owner, substate)
-    }
 }
```

### core/executor/src/state/overlay_account/storage.rs
```diff
@@ -3,9 +3,7 @@ use super::Substate;
 #[cfg(test)]
 use super::StorageLayout;
 use cfx_parameters::{
-    internal_contract_addresses::{
-        SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS, SYSTEM_STORAGE_ADDRESS,
-    },
+    internal_contract_addresses::SYSTEM_STORAGE_ADDRESS,
     staking::COLLATERAL_UNITS_PER_STORAGE_KEY,
 };
 use cfx_statedb::{Result as DbResult, StateDbExt, StateDbGeneric};
@@ -20,16 +18,10 @@ use super::OverlayAccount;
 
 impl OverlayAccount {
     pub fn set_storage(
-        &mut self, db: &StateDbGeneric, key: Vec<u8>, value: U256,
+        &mut self, key: Vec<u8>, value: U256, old_value: StorageValue,
         owner: Address, substate: &mut Substate,
     ) -> DbResult<()>
     {
-        let old_value = self.storage_entry_at(db, &key)?;
-        // Noop if the value does not change.
-        if old_value.value == value && !self.force_reset_owner() {
-            return Ok(());
-        }
-
         // Refund the collateral of old value
         if let Some(old_owner) = old_value.owner {
             substate.record_storage_release(
@@ -59,16 +51,6 @@ impl OverlayAccount {
         Ok(())
     }
 
-    // In most cases, the ownership does not change if the set storage operation
-    // does not change the value. However, some implementations do not follow
-    // this rule. So we must deal with these special cases for backward
-    // compatible.
-    fn force_reset_owner(&self) -> bool {
-        self.address.space == Space::Native
-            && self.address.address
-                == SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS
-    }
-
     #[cfg(test)]
     pub fn set_storage_simple(&mut self, key: Vec<u8>, value: U256) {
         Arc::make_mut(&mut self.storage_write_cache)
```

### core/executor/src/state/state_object/mod.rs
```diff
@@ -45,6 +45,7 @@ mod tests;
 pub use self::{
     collateral::{initialize_cip107, settle_collateral_for_all},
     pos::{distribute_pos_interest, update_pos_status},
+    sponsor::COMMISSION_PRIVILEGE_SPECIAL_KEY,
     staking::initialize_or_update_dao_voted_params,
 };
 #[cfg(test)]
```

### core/executor/src/state/state_object/sponsor.rs
```diff
@@ -4,12 +4,20 @@ use cfx_statedb::{
     global_params::{ConvertedStoragePoints, TotalIssued},
     Result as DbResult,
 };
-use cfx_types::{maybe_address, Address, U256};
+use cfx_types::{
+    maybe_address, Address, AddressSpaceUtil, AddressWithSpace, U256,
+};
 use primitives::{SponsorInfo, StorageKey};
 
 use super::{State, Substate};
 use crate::{return_if, try_loaded};
 
+lazy_static! {
+    static ref COMMISSION_PRIVILEGE_STORAGE_VALUE: U256 = U256::one();
+    /// If we set this key, it means every account has commission privilege.
+    pub static ref COMMISSION_PRIVILEGE_SPECIAL_KEY: Address = Address::zero();
+}
+
 impl State {
     pub fn sponsor_info(
         &self, address: &Address,
@@ -148,10 +156,19 @@ impl State {
     pub fn check_contract_whitelist(
         &self, contract_address: &Address, user: &Address,
     ) -> DbResult<bool> {
-        let acc = try_loaded!(self.read_native_account_lock(
-            &SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS
-        ));
-        acc.check_contract_whitelist(&self.db, contract_address, user)
+        let special_value = self.storage_at(
+            &sponsor_address(),
+            &special_sponsor_key(&contract_address),
+        )?;
+        if !special_value.is_zero() {
+            Ok(true)
+        } else {
+            self.storage_at(
+                &sponsor_address(),
+                &sponsor_key(contract_address, user),
+            )
+            .map(|x| !x.is_zero())
+        }
     }
 
     pub fn add_to_contract_whitelist(
@@ -164,13 +181,10 @@ impl State {
             contract_address, user
         );
 
-        self.write_native_account_lock(
-            &SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS,
-        )?
-        .add_to_contract_whitelist(
-            &self.db,
-            contract_address,
-            user,
+        self.set_storage(
+            &sponsor_address(),
+            sponsor_key(&contract_address, &user),
+            COMMISSION_PRIVILEGE_STORAGE_VALUE.clone(),
             storage_owner,
             substate,
         )?;
@@ -183,16 +197,14 @@ impl State {
         user: Address, substate: &mut Substate,
     ) -> DbResult<()>
     {
-        self.write_native_account_lock(
-            &SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS,
-        )?
-        .remove_from_contract_whitelist(
-            &self.db,
-            contract_address,
-            user,
+        self.set_storage(
+            &sponsor_address(),
+            sponsor_key(&contract_address, &user),
+            U256::zero(),
             storage_owner,
             substate,
         )?;
+
         Ok(())
     }
 
@@ -223,6 +235,26 @@ impl State {
     }
 }
 
+#[inline]
+fn sponsor_address() -> AddressWithSpace {
+    SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS.with_native_space()
+}
+
+#[inline]
+fn sponsor_key(contract: &Address, user: &Address) -> Vec<u8> {
+    let mut key = Vec::with_capacity(Address::len_bytes() * 2);
+    key.extend_from_slice(contract.as_bytes());
+    key.extend_from_slice(user.as_bytes());
+    key
+}
+
+fn special_sponsor_key(contract: &Address) -> Vec<u8> {
+    let mut key = Vec::with_capacity(Address::len_bytes() * 2);
+    key.extend_from_slice(contract.as_bytes());
+    key.extend_from_slice(COMMISSION_PRIVILEGE_SPECIAL_KEY.as_bytes());
+    key
+}
+
 fn storage_range_deletion_for_account(
     state: &mut State, address: &Address, key_prefix: &[u8],
     substate: &mut Substate,
```

### core/executor/src/state/state_object/storage_entry.rs
```diff
@@ -1,8 +1,11 @@
 use super::{State, Substate};
-use crate::try_loaded;
-use cfx_parameters::internal_contract_addresses::SYSTEM_STORAGE_ADDRESS;
+use crate::{return_if, try_loaded};
+use cfx_parameters::internal_contract_addresses::{
+    SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS, SYSTEM_STORAGE_ADDRESS,
+};
 use cfx_statedb::Result as DbResult;
-use cfx_types::{Address, AddressSpaceUtil, AddressWithSpace, U256};
+use cfx_types::{Address, AddressSpaceUtil, AddressWithSpace, Space, U256};
+use primitives::StorageValue;
 
 impl State {
     // System Storage shares the cache and checkpoint mechanisms with
@@ -33,20 +36,36 @@ impl State {
         )
     }
 
+    #[inline]
     pub fn storage_at(
         &self, address: &AddressWithSpace, key: &[u8],
     ) -> DbResult<U256> {
         let acc = try_loaded!(self.read_account_lock(address));
         acc.storage_at(&self.db, key)
     }
 
+    #[inline]
+    pub fn storage_entry_at(
+        &self, address: &AddressWithSpace, key: &[u8],
+    ) -> DbResult<StorageValue> {
+        let acc = try_loaded!(self.read_account_lock(address));
+        acc.storage_entry_at(&self.db, key)
+    }
+
+    #[inline]
     pub fn set_storage(
         &mut self, address: &AddressWithSpace, key: Vec<u8>, value: U256,
         owner: Address, substate: &mut Substate,
     ) -> DbResult<()>
     {
+        let old_value = self.storage_entry_at(address, &key)?;
+        return_if!(
+            old_value.value == value && !Self::force_reset_owner(address)
+        );
+
         self.write_account_lock(address)?
-            .set_storage(&self.db, key, value, owner, substate)?;
+            .set_storage(key, value, old_value, owner, substate)?;
+
         Ok(())
     }
 
@@ -56,6 +75,16 @@ impl State {
         let acc = try_loaded!(self.read_account_lock(address));
         Ok(acc.fresh_storage())
     }
+
+    // In most cases, the ownership does not change if the set storage operation
+    // does not change the value. However, some implementations do not follow
+    // this rule. So we must deal with these special cases for backward
+    // compatible.
+    #[inline]
+    fn force_reset_owner(address: &AddressWithSpace) -> bool {
+        address.space == Space::Native
+            && address.address == SPONSOR_WHITELIST_CONTROL_CONTRACT_ADDRESS
+    }
 }
 
 #[cfg(test)]
@@ -68,7 +97,7 @@ impl State {
     {
         use super::{checkpoints::CheckpointEntry::*, AccountEntry};
         use cfx_statedb::StateDbExt;
-        use primitives::{StorageKey, StorageValue};
+        use primitives::StorageKey;
 
         #[derive(Debug)]
         enum ReturnKind {
```
