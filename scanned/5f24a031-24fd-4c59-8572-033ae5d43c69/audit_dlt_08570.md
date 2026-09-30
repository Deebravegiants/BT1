# [?] Catch contract host panics, fix #3535

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2022-09-20
Source: https://github.com/stellar/stellar-core/commit/d421e1f4653ef45930e5ff5cabbadf9d77eb8adc
Type: security-commit

## Details
Catch contract host panics, fix #3535

## Patch
### src/rust/src/contract.rs
```diff
@@ -8,7 +8,7 @@ use crate::{
 };
 use cxx::{CxxVector, UniquePtr};
 use log::info;
-use std::{cell::RefCell, fmt::Display, io::Cursor, pin::Pin, rc::Rc};
+use std::{cell::RefCell, fmt::Display, io::Cursor, panic, pin::Pin, rc::Rc};
 
 use soroban_env_host::{
     budget::Budget,
@@ -24,30 +24,30 @@ use soroban_env_host::{
 use std::error::Error;
 
 #[derive(Debug)]
-enum ContractError {
+enum CoreHostError {
     Host(HostError),
     General(&'static str),
 }
 
-impl Display for ContractError {
+impl Display for CoreHostError {
     fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
         write!(f, "{:?}", self)
     }
 }
 
-impl From<HostError> for ContractError {
+impl From<HostError> for CoreHostError {
     fn from(h: HostError) -> Self {
-        ContractError::Host(h)
+        CoreHostError::Host(h)
     }
 }
 
-impl From<xdr::Error> for ContractError {
+impl From<xdr::Error> for CoreHostError {
     fn from(_: xdr::Error) -> Self {
-        ContractError::Host(ScUnknownErrorCode::Xdr.into())
+        CoreHostError::Host(ScUnknownErrorCode::Xdr.into())
     }
 }
 
-impl std::error::Error for ContractError {}
+impl std::error::Error for CoreHostError {}
 
 fn xdr_from_slice<T: ReadXdr>(v: &[u8]) -> Result<T, HostError> {
     Ok(T::read_xdr(&mut Cursor::new(v)).map_err(|_| ScUnknownErrorCode::Xdr)?)
@@ -90,11 +90,11 @@ fn populate_access_map(
     access: &mut MeteredOrdMap<LedgerKey, AccessType>,
     keys: Vec<LedgerKey>,
     ty: AccessType,
-) -> Result<(), ContractError> {
+) -> Result<(), CoreHostError> {
     for lk in keys {
         match lk {
             LedgerKey::Account(_) | LedgerKey::Trustline(_) | LedgerKey::ContractData(_) => (),
-            _ => return Err(ContractError::General("unexpected ledger entry type")),
+            _ => return Err(CoreHostError::General("unexpected ledger entry type")),
         };
         access.insert(lk, ty.clone())?;
     }
@@ -107,7 +107,7 @@ fn populate_access_map(
 fn build_storage_footprint_from_xdr(
     budget: Budget,
     footprint: &XDRBuf,
-) -> Result<storage::Footprint, ContractError> {
+) -> Result<storage::Footprint, CoreHostError> {
     let xdr::LedgerFootprint {
         read_only,
         read_write,
@@ -119,7 +119,7 @@ fn build_storage_footprint_from_xdr(
     Ok(storage::Footprint(access))
 }
 
-fn ledger_entry_to_ledger_key(le: &LedgerEntry) -> Result<LedgerKey, ContractError> {
+fn ledger_entry_to_ledger_key(le: &LedgerEntry) -> Result<LedgerKey, CoreHostError> {
     match &le.data {
         LedgerEntryData::Account(a) => Ok(LedgerKey::Account(LedgerKeyAccount {
             account_id: a.account_id.clone(),
@@ -132,7 +132,7 @@ fn ledger_entry_to_ledger_key(le: &LedgerEntry) -> Result<LedgerKey, ContractErr
             contract_id: cd.contract_id.clone(),
             key: cd.key.clone(),
         })),
-        _ => Err(ContractError::General("unexpected ledger key")),
+        _ => Err(CoreHostError::General("unexpected ledger key")),
     }
 }
 
@@ -144,13 +144,13 @@ fn build_storage_map_from_xdr_ledger_entries(
     budget: Budget,
     footprint: &storage::Footprint,
     ledger_entries: &Vec<XDRBuf>,
-) -> Result<MeteredOrdMap<LedgerKey, Option<LedgerEntry>>, ContractError> {
+) -> Result<MeteredOrdMap<LedgerKey, Option<LedgerEntry>>, CoreHostError> {
     let mut map = MeteredOrdMap::new(budget)?;
     for buf in ledger_entries {
         let le = xdr_from_xdrbuf::<LedgerEntry>(buf)?;
         let key = ledger_entry_to_ledger_key(&le)?;
         if !footprint.0.contains_key(&key)? {
-            return Err(ContractError::General(
+            return Err(CoreHostError::General(
                 "ledger entry not found in footprint",
             ));
         }
@@ -169,7 +169,7 @@ fn build_storage_map_from_xdr_ledger_entries(
 fn build_xdr_ledger_entries_from_storage_map(
     footprint: &storage::Footprint,
     storage_map: &MeteredOrdMap<LedgerKey, Option<LedgerEntry>>,
-) -> Result<Vec<Bytes>, ContractError> {
+) -> Result<Vec<Bytes>, CoreHostError> {
     let mut res = Vec::new();
     for (lk, ole) in storage_map {
         match footprint.0.get(lk)? {
@@ -179,7 +179,7 @@ fn build_xdr_ledger_entries_from_storage_map(
                     res.push(xdr_to_bytes(le)?)
                 }
             }
-            None => return Err(ContractError::General("ledger entry not in footprint")),
+            None => return Err(CoreHostError::General("ledger entry not in footprint")),
         }
     }
     Ok(res)
@@ -190,12 +190,35 @@ fn build_xdr_ledger_entries_from_storage_map(
 /// the data the invocation intends to read. Then calls the host function with the specified
 /// arguments, discards the [`xdr::ScVal`] return value, and returns the [`ReadWrite`] ledger
 /// entries in serialized form. Ledger entries not returned have been deleted.
+
 pub(crate) fn invoke_host_function(
     hf_buf: &XDRBuf,
     args_buf: &XDRBuf,
     footprint_buf: &XDRBuf,
     source_account_buf: &XDRBuf,
     ledger_entries: &Vec<XDRBuf>,
+) -> Result<Vec<Bytes>, Box<dyn Error>> {
+    let res = panic::catch_unwind(panic::AssertUnwindSafe(|| {
+        invoke_host_function_or_maybe_panic(
+            hf_buf,
+            args_buf,
+            footprint_buf,
+            source_account_buf,
+            ledger_entries,
+        )
+    }));
+    match res {
+        Err(_) => Err(CoreHostError::General("contract host panicked").into()),
+        Ok(r) => r,
+    }
+}
+
+fn invoke_host_function_or_maybe_panic(
+    hf_buf: &XDRBuf,
+    args_buf: &XDRBuf,
+    footprint_buf: &XDRBuf,
+    source_account_buf: &XDRBuf,
+    ledger_entries: &Vec<XDRBuf>,
 ) -> Result<Vec<Bytes>, Box<dyn Error>> {
     let budget = Budget::default();
     let hf = xdr_from_xdrbuf::<HostFunction>(&hf_buf)?;
@@ -215,7 +238,7 @@ pub(crate) fn invoke_host_function(
 
     let (storage, _budget, _events) = host
         .try_finish()
-        .map_err(|_h| ContractError::General("could not get storage from host"))?;
+        .map_err(|_h| CoreHostError::General("could not get storage from host"))?;
     Ok(build_xdr_ledger_entries_from_storage_map(
         &storage.footprint,
         &storage.map,
@@ -281,6 +304,20 @@ pub(crate) fn preflight_host_function(
     hf_buf: &CxxVector<u8>,
     args_buf: &CxxVector<u8>,
     cb: UniquePtr<PreflightCallbacks>,
+) -> Result<(), Box<dyn Error>> {
+    let res = panic::catch_unwind(panic::AssertUnwindSafe(|| {
+        preflight_host_function_or_maybe_panic(hf_buf, args_buf, cb)
+    }));
+    match res {
+        Err(_) => Err(CoreHostError::General("contract host panicked").into()),
+        Ok(r) => r,
+    }
+}
+
+fn preflight_host_function_or_maybe_panic(
+    hf_buf: &CxxVector<u8>,
+    args_buf: &CxxVector<u8>,
+    cb: UniquePtr<PreflightCallbacks>,
 ) -> Result<(), Box<dyn Error>> {
     let hf = xdr_from_slice::<HostFunction>(hf_buf.as_slice())?;
     let args = xdr_from_slice::<ScVec>(args_buf.as_slice())?;
@@ -294,7 +331,7 @@ pub(crate) fn preflight_host_function(
     // Recover, convert and return the storage footprint and other values to C++.
     let (storage, budget, _events) = host
         .try_finish()
-        .map_err(|_| ContractError::General("could not get storage from host"))?;
+        .map_err(|_| CoreHostError::General("could not get storage from host"))?;
     let (cpu_insns, mem_bytes) = (budget.get_cpu_insns_count(), budget.get_mem_bytes_count());
     let val_vec = xdr_to_vec_u8(&val)?;
     let foot_vec = xdr_to_vec_u8(&storage_footprint_to_ledger_footprint(&storage.footprint)?)?;
```
