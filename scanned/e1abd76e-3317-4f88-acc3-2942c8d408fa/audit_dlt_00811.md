# [?] Enforce `DepthLimiter` in the `Host` to avoid stack overflow (#904)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-07-14
Source: https://github.com/stellar/rs-soroban-env/commit/63e8430b0efd6c8a96134f2d6dc22d615e05bbc0
Type: security-commit

## Details
Enforce `DepthLimiter` in the `Host` to avoid stack overflow (#904)

* Enforce `DepthLimiter` on `Env` to avoid stack overflow

* fixup! Enforce `DepthLimiter` on `Env` to avoid stack overflow

* Remove `DepthGuard`; Remove `EnvBase` dependency on `DepthLimiter`; clean-ups

* Revert unintentional touch

* Refresh xdr

## Patch
### Cargo.lock
```diff
@@ -1456,7 +1456,7 @@ dependencies = [
 [[package]]
 name = "stellar-xdr"
 version = "0.0.17"
-source = "git+https://github.com/stellar/rs-stellar-xdr?rev=a49a739d2af0d75814b62004a5c301ac2fd77036#a49a739d2af0d75814b62004a5c301ac2fd77036"
+source = "git+https://github.com/stellar/rs-stellar-xdr?rev=54c183e91573d8a5882ff1dda21d444ef42cc426#54c183e91573d8a5882ff1dda21d444ef42cc426"
 dependencies = [
  "arbitrary",
  "base64 0.13.1",
```

### Cargo.toml
```diff
@@ -27,7 +27,7 @@ soroban-native-sdk-macros = { version = "0.0.17", path = "soroban-native-sdk-mac
 [workspace.dependencies.stellar-xdr]
 version = "0.0.17"
 git = "https://github.com/stellar/rs-stellar-xdr"
-rev = "a49a739d2af0d75814b62004a5c301ac2fd77036"
+rev = "54c183e91573d8a5882ff1dda21d444ef42cc426"
 default-features = false
 
 [workspace.dependencies.wasmi]
```

### soroban-env-common/src/error.rs
```diff
@@ -136,8 +136,13 @@ impl From<ConversionError> for Error {
 }
 
 impl From<stellar_xdr::Error> for Error {
-    fn from(_: stellar_xdr::Error) -> Self {
-        Error::from_type_and_code(ScErrorType::Value, ScErrorCode::InvalidInput)
+    fn from(e: stellar_xdr::Error) -> Self {
+        match e {
+            stellar_xdr::Error::DepthLimitExceeded => {
+                Error::from_type_and_code(ScErrorType::Context, ScErrorCode::ExceededLimit)
+            }
+            _ => Error::from_type_and_code(ScErrorType::Value, ScErrorCode::InvalidInput),
+        }
     }
 }
 
```

### soroban-env-host/src/budget.rs
```diff
@@ -4,12 +4,13 @@ use std::{
     rc::Rc,
 };
 
-use soroban_env_common::xdr::{ScErrorCode, ScErrorType};
-
 use crate::{
     host::error::TryBorrowOrErr,
-    xdr::{ContractCostParamEntry, ContractCostParams, ContractCostType, ExtensionPoint},
-    Host, HostError,
+    xdr::{
+        ContractCostParamEntry, ContractCostParams, ContractCostType, DepthLimiter, ExtensionPoint,
+        ScErrorCode, ScErrorType,
+    },
+    Error, Host, HostError, DEFAULT_HOST_DEPTH_LIMIT,
 };
 
 use wasmi::FuelCosts;
@@ -249,7 +250,7 @@ impl FuelConfig {
     }
 }
 
-#[derive(Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
+#[derive(Clone, PartialEq, Eq, PartialOrd, Ord)]
 pub(crate) struct BudgetImpl {
     pub cpu_insns: BudgetDimension,
     pub mem_bytes: BudgetDimension,
@@ -258,6 +259,7 @@ pub(crate) struct BudgetImpl {
     tracker: Vec<(u64, Option<u64>)>,
     enabled: bool,
     fuel_config: FuelConfig,
+    depth_limit: u32,
 }
 
 impl BudgetImpl {
@@ -274,6 +276,7 @@ impl BudgetImpl {
             tracker: vec![(0, None); ContractCostType::variants().len()],
             enabled: true,
             fuel_config: Default::default(),
+            depth_limit: DEFAULT_HOST_DEPTH_LIMIT,
         };
 
         b.init_tracker();
@@ -408,6 +411,30 @@ impl Display for BudgetImpl {
     }
 }
 
+impl DepthLimiter for BudgetImpl {
+    type DepthLimiterError = HostError;
+
+    fn enter(&mut self) -> Result<(), HostError> {
+        if let Some(depth) = self.depth_limit.checked_sub(1) {
+            self.depth_limit = depth;
+        } else {
+            return Err(Error::from_type_and_code(
+                ScErrorType::Context,
+                ScErrorCode::ExceededLimit,
+            )
+            .into());
+        }
+        Ok(())
+    }
+
+    // `leave` should be called in tandem with `enter` such that the depth
+    // doesn't exceed the initial depth limit.
+    fn leave(&mut self) -> Result<(), HostError> {
+        self.depth_limit = self.depth_limit.saturating_add(1);
+        Ok(())
+    }
+}
+
 #[derive(Default, Clone, PartialEq, Eq, PartialOrd, Ord)]
 pub struct Budget(pub(crate) Rc<RefCell<BudgetImpl>>);
 
@@ -445,6 +472,18 @@ impl AsBudget for &Host {
     }
 }
 
+impl DepthLimiter for Budget {
+    type DepthLimiterError = HostError;
+
+    fn enter(&mut self) -> Result<(), HostError> {
+        self.0.try_borrow_mut_or_err()?.enter()
+    }
+
+    fn leave(&mut self) -> Result<(), HostError> {
+        self.0.try_borrow_mut_or_err()?.leave()
+    }
+}
+
 impl Budget {
     /// Initializes the budget from network configuration settings.
     pub fn from_configs(
@@ -721,6 +760,7 @@ impl Default for BudgetImpl {
             tracker: vec![(0, None); ContractCostType::variants().len()],
             enabled: true,
             fuel_config: Default::default(),
+            depth_limit: DEFAULT_HOST_DEPTH_LIMIT,
         };
 
         for ct in ContractCostType::variants() {
```

### soroban-env-host/src/host.rs
```diff
@@ -69,6 +69,20 @@ pub(crate) use frame::Frame;
 #[cfg(any(test, feature = "testutils"))]
 use soroban_env_common::xdr::SorobanAuthorizedInvocation;
 
+/// Defines the maximum depth for recursive calls in the host, i.e. `Val` conversion, comparison,
+/// and deep clone, to prevent stack overflow.
+///
+/// Similar to the `xdr::DEFAULT_XDR_RW_DEPTH_LIMIT`, `DEFAULT_HOST_DEPTH_LIMIT` is also a proxy
+/// to the stack depth limit, and its purpose is to prevent the program from
+/// hitting the maximum stack size allowed by Rust, which would result in an unrecoverable `SIGABRT`.
+///
+/// The difference is the `DEFAULT_HOST_DEPTH_LIMIT`guards the recursion paths via the `Env` and
+/// the `Budget`, i.e., conversion, comparison and deep clone. The limit is checked at specific
+/// points of the recursion path, e.g. when `Val` is encountered, to minimize noise. So the
+/// "actual stack depth"/"host depth" factor will typically be larger, and thus the
+/// `DEFAULT_HOST_DEPTH_LIMIT` here is set to a smaller value.
+pub const DEFAULT_HOST_DEPTH_LIMIT: u32 = 100;
+
 /// Temporary helper for denoting a slice of guest memory, as formed by
 /// various bytes operations.
 pub(crate) struct VmSlice {
```

### soroban-env-host/src/host/comparison.rs
```diff
@@ -4,8 +4,8 @@ use soroban_env_common::{
     xdr::{
         AccountEntry, AccountId, ClaimableBalanceEntry, ConfigSettingEntry, ContractCodeEntryBody,
         ContractCostType, ContractDataDurability, ContractDataEntryBody, ContractDataEntryData,
-        ContractEntryBodyType, ContractExecutable, CreateContractArgs, DataEntry, Duration,
-        ExtensionPoint, Hash, LedgerEntry, LedgerEntryData, LedgerEntryExt, LedgerKey,
+        ContractEntryBodyType, ContractExecutable, CreateContractArgs, DataEntry, DepthLimiter,
+        Duration, ExtensionPoint, Hash, LedgerEntry, LedgerEntryData, LedgerEntryExt, LedgerKey,
         LedgerKeyAccount, LedgerKeyClaimableBalance, LedgerKeyConfigSetting, LedgerKeyContractCode,
         LedgerKeyData, LedgerKeyLiquidityPool, LedgerKeyOffer, LedgerKeyTrustLine,
         LiquidityPoolEntry, OfferEntry, PublicKey, ScAddress, ScErrorCode, ScErrorType, ScMap,
@@ -52,44 +52,47 @@ impl Compare<HostObject> for Host {
 
     fn compare(&self, a: &HostObject, b: &HostObject) -> Result<Ordering, Self::Error> {
         use HostObject::*;
-        match (a, b) {
-            (U64(a), U64(b)) => self.as_budget().compare(a, b),
-            (I64(a), I64(b)) => self.as_budget().compare(a, b),
-            (TimePoint(a), TimePoint(b)) => self.as_budget().compare(a, b),
-            (Duration(a), Duration(b)) => self.as_budget().compare(a, b),
-            (U128(a), U128(b)) => self.as_budget().compare(a, b),
-            (I128(a), I128(b)) => self.as_budget().compare(a, b),
-            (U256(a), U256(b)) => self.as_budget().compare(a, b),
-            (I256(a), I256(b)) => self.as_budget().compare(a, b),
-            (Vec(a), Vec(b)) => self.compare(a, b),
-            (Map(a), Map(b)) => self.compare(a, b),
-            (Bytes(a), Bytes(b)) => self.as_budget().compare(&a.as_slice(), &b.as_slice()),
-            (String(a), String(b)) => self.as_budget().compare(&a.as_slice(), &b.as_slice()),
-            (Symbol(a), Symbol(b)) => self.as_budget().compare(&a.as_slice(), &b.as_slice()),
-            (Address(a), Address(b)) => self.as_budget().compare(a, b),
-
-            // List out at least one side of all the remaining cases here so
-            // we don't accidentally forget to update this when/if a new
-            // HostObject type is added.
-            (U64(_), _)
-            | (TimePoint(_), _)
-            | (Duration(_), _)
-            | (I64(_), _)
-            | (U128(_), _)
-            | (I128(_), _)
-            | (U256(_), _)
-            | (I256(_), _)
-            | (Vec(_), _)
-            | (Map(_), _)
-            | (Bytes(_), _)
-            | (String(_), _)
-            | (Symbol(_), _)
-            | (Address(_), _) => {
-                let a = host_obj_discriminant(a);
-                let b = host_obj_discriminant(b);
-                Ok(a.cmp(&b))
+        // This is the depth limit checkpoint for `Val` comparison.
+        self.budget_cloned().with_limited_depth(|_| {
+            match (a, b) {
+                (U64(a), U64(b)) => self.as_budget().compare(a, b),
+                (I64(a), I64(b)) => self.as_budget().compare(a, b),
+                (TimePoint(a), TimePoint(b)) => self.as_budget().compare(a, b),
+                (Duration(a), Duration(b)) => self.as_budget().compare(a, b),
+                (U128(a), U128(b)) => self.as_budget().compare(a, b),
+                (I128(a), I128(b)) => self.as_budget().compare(a, b),
+                (U256(a), U256(b)) => self.as_budget().compare(a, b),
+                (I256(a), I256(b)) => self.as_budget().compare(a, b),
+                (Vec(a), Vec(b)) => self.compare(a, b),
+                (Map(a), Map(b)) => self.compare(a, b),
+                (Bytes(a), Bytes(b)) => self.as_budget().compare(&a.as_slice(), &b.as_slice()),
+                (String(a), String(b)) => self.as_budget().compare(&a.as_slice(), &b.as_slice()),
+                (Symbol(a), Symbol(b)) => self.as_budget().compare(&a.as_slice(), &b.as_slice()),
+                (Address(a), Address(b)) => self.as_budget().compare(a, b),
+
+                // List out at least one side of all the remaining cases here so
+                // we don't accidentally forget to update this when/if a new
+                // HostObject type is added.
+                (U64(_), _)
+                | (TimePoint(_), _)
+                | (Duration(_), _)
+                | (I64(_), _)
+                | (U128(_), _)
+                | (I128(_), _)
+                | (U256(_), _)
+                | (I256(_), _)
+                | (Vec(_), _)
+                | (Map(_), _)
+                | (Bytes(_), _)
+                | (String(_), _)
+                | (Symbol(_), _)
+                | (Address(_), _) => {
+                    let a = host_obj_discriminant(a);
+                    let b = host_obj_discriminant(b);
+                    Ok(a.cmp(&b))
+                }
             }
-        }
+        })
     }
 }
 
@@ -258,7 +261,8 @@ impl Compare<ScVal> for Budget {
 
     fn compare(&self, a: &ScVal, b: &ScVal) -> Result<Ordering, Self::Error> {
         use ScVal::*;
-        match (a, b) {
+        // This is the depth limit checkpoint for `ScVal` comparison.
+        self.clone().with_limited_depth(|_| match (a, b) {
             (Vec(Some(a)), Vec(Some(b))) => self.compare(a, b),
             (Map(Some(a)), Map(Some(b))) => self.compare(a, b),
 
@@ -309,7 +313,7 @@ impl Compare<ScVal> for Budget {
             | (LedgerKeyContractInstance, _)
             | (LedgerKeyNonce(_), _)
             | (ContractInstance(_), _) => Ok(a.cmp(b)),
-        }
+        })
     }
 }
 
```

### soroban-env-host/src/host/conversion.rs
```diff
@@ -10,9 +10,9 @@ use soroban_env_common::num::{
     i256_from_pieces, i256_into_pieces, u256_from_pieces, u256_into_pieces,
 };
 use soroban_env_common::xdr::{
-    self, int128_helpers, AccountId, ContractDataDurability, ContractEntryBodyType, Int128Parts,
-    Int256Parts, ScAddress, ScBytes, ScErrorCode, ScErrorType, ScMap, ScMapEntry, UInt128Parts,
-    UInt256Parts,
+    self, int128_helpers, AccountId, ContractDataDurability, ContractEntryBodyType, DepthLimiter,
+    Int128Parts, Int256Parts, ScAddress, ScBytes, ScErrorCode, ScErrorType, ScMap, ScMapEntry,
+    UInt128Parts, UInt256Parts,
 };
 use soroban_env_common::{
     AddressObject, BytesObject, Convert, Object, ScValObjRef, ScValObject, TryFromVal, TryIntoVal,
@@ -369,27 +369,32 @@ impl Host {
         // translates a u64 into another form defined by the xdr.
         // For an `Object`, the actual structural conversion (such as byte
         // cloning) occurs in `from_host_obj` and is metered there.
-        self.charge_budget(ContractCostType::ValXdrConv, None)?;
-        ScVal::try_from_val(self, &val).map_err(|_| {
-            self.err(
-                ScErrorType::Value,
-                ScErrorCode::InvalidInput,
-                "failed to convert host value to ScVal",
-                &[val],
-            )
+        // This is the depth limit checkpoint for `Val`->`ScVal` conversion.
+        self.budget_cloned().with_limited_depth(|_| {
+            self.charge_budget(ContractCostType::ValXdrConv, None)?;
+            ScVal::try_from_val(self, &val).map_err(|_| {
+                self.err(
+                    ScErrorType::Value,
+                    ScErrorCode::InvalidInput,
+                    "failed to convert host value to ScVal",
+                    &[val],
+                )
+            })
         })
     }
 
     pub(crate) fn to_host_val(&self, v: &ScVal) -> Result<Val, HostError> {
-        // `ValXdrConv` is const cost in both cpu and mem. The input=0 will be ignored.
-        self.charge_budget(ContractCostType::ValXdrConv, None)?;
-        v.try_into_val(self).map_err(|_| {
-            self.err(
-                ScErrorType::Value,
-                ScErrorCode::InternalError,
-                "failed to convert ScVal to host value",
-                &[],
-            )
+        // This is the depth limit checkpoint for `ScVal`->`Val` conversion.
+        self.budget_cloned().with_limited_depth(|_| {
+            self.charge_budget(ContractCostType::ValXdrConv, None)?;
+            v.try_into_val(self).map_err(|_| {
+                self.err(
+                    ScErrorType::Value,
+                    ScErrorCode::InternalError,
+                    "failed to convert ScVal to host value",
+                    &[],
+                )
+            })
         })
     }
 
```

### soroban-env-host/src/host/metered_clone.rs
```diff
@@ -1,6 +1,6 @@
 use std::{mem, rc::Rc};
 
-use soroban_env_common::xdr::ScContractInstance;
+use soroban_env_common::xdr::DepthLimiter;
 
 use crate::{
     budget::Budget,
@@ -17,9 +17,9 @@ use crate::{
         LedgerEntryData, LedgerEntryExt, LedgerKey, LedgerKeyAccount, LedgerKeyClaimableBalance,
         LedgerKeyConfigSetting, LedgerKeyContractCode, LedgerKeyData, LedgerKeyLiquidityPool,
         LedgerKeyOffer, LedgerKeyTrustLine, LiquidityPoolEntry, OfferEntry, PublicKey, ScAddress,
-        ScBytes, ScErrorCode, ScErrorType, ScMap, ScMapEntry, ScNonceKey, ScString, ScSymbol,
-        ScVal, ScVec, SorobanAuthorizedInvocation, StringM, TimePoint, TrustLineAsset,
-        TrustLineEntry, Uint256,
+        ScBytes, ScContractInstance, ScErrorCode, ScErrorType, ScMap, ScMapEntry, ScNonceKey,
+        ScString, ScSymbol, ScVal, ScVec, SorobanAuthorizedInvocation, StringM, TimePoint,
+        TrustLineAsset, TrustLineEntry, Uint256,
     },
     AddressObject, Bool, BytesObject, DurationObject, DurationSmall, DurationVal, Error, HostError,
     I128Object, I128Small, I128Val, I256Object, I256Small, I256Val, I32Val, I64Object, I64Small,
@@ -251,34 +251,39 @@ impl MeteredClone for ScVal {
     const IS_SHALLOW: bool = false;
 
     fn charge_for_substructure(&self, budget: &Budget) -> Result<(), HostError> {
-        match self {
-            ScVal::Vec(Some(v)) => ScVec::charge_for_substructure(v, budget),
-            ScVal::Map(Some(m)) => ScMap::charge_for_substructure(m, budget),
-            ScVal::Vec(None) | ScVal::Map(None) => {
-                Err((ScErrorType::Value, ScErrorCode::MissingValue).into())
+        // This is the depth limit checkpoint for `ScVal` cloning.
+        budget.clone().with_limited_depth(|_| {
+            match self {
+                ScVal::Vec(Some(v)) => ScVec::charge_for_substructure(v, budget),
+                ScVal::Map(Some(m)) => ScMap::charge_for_substructure(m, budget),
+                ScVal::Vec(None) | ScVal::Map(None) => {
+                    Err((ScErrorType::Value, ScErrorCode::MissingValue).into())
+                }
+                ScVal::Bytes(b) => BytesM::charge_for_substructure(b, budget),
+                ScVal::String(s) => StringM::charge_for_substructure(s, budget),
+                ScVal::Symbol(s) => StringM::charge_for_substructure(s, budget),
+                ScVal::ContractInstance(i) => {
+                    ScContractInstance::charge_for_substructure(i, budget)
+                }
+                // Everything else was handled by the memcpy above.
+                ScVal::U64(_)
+                | ScVal::I64(_)
+                | ScVal::U128(_)
+                | ScVal::I128(_)
+                | ScVal::Address(_)
+                | ScVal::U32(_)
+                | ScVal::I32(_)
+                | ScVal::Error(_)
+                | ScVal::Bool(_)
+                | ScVal::Void
+                | ScVal::Timepoint(_)
+                | ScVal::Duration(_)
+                | ScVal::U256(_)
+                | ScVal::I256(_)
+                | ScVal::LedgerKeyContractInstance
+                | ScVal::LedgerKeyNonce(_) => Ok(()),
             }
-            ScVal::Bytes(b) => BytesM::charge_for_substructure(b, budget),
-            ScVal::String(s) => StringM::charge_for_substructure(s, budget),
-            ScVal::Symbol(s) => StringM::charge_for_substructure(s, budget),
-            ScVal::ContractInstance(i) => ScContractInstance::charge_for_substructure(i, budget),
-            // Everything else was handled by the memcpy above.
-            ScVal::U64(_)
-            | ScVal::I64(_)
-            | ScVal::U128(_)
-            | ScVal::I128(_)
-            | ScVal::Address(_)
-            | ScVal::U32(_)
-            | ScVal::I32(_)
-            | ScVal::Error(_)
-            | ScVal::Bool(_)
-            | ScVal::Void
-            | ScVal::Timepoint(_)
-            | ScVal::Duration(_)
-            | ScVal::U256(_)
-            | ScVal::I256(_)
-            | ScVal::LedgerKeyContractInstance
-            | ScVal::LedgerKeyNonce(_) => Ok(()),
-        }
+        })
     }
 }
 
```

### soroban-env-host/src/host/metered_xdr.rs
```diff
@@ -6,7 +6,9 @@ use crate::{
 use std::io::Write;
 
 use sha2::{Digest, Sha256};
-use soroban_env_common::xdr::{ScErrorCode, ScErrorType};
+use soroban_env_common::xdr::{
+    DepthLimitedWrite, ScErrorCode, ScErrorType, DEFAULT_XDR_RW_DEPTH_LIMIT,
+};
 
 struct MeteredWrite<'a, W: Write> {
     host: &'a Host,
@@ -35,7 +37,8 @@ impl Host {
         obj: &impl WriteXdr,
         w: &mut Vec<u8>,
     ) -> Result<(), HostError> {
-        let mut w = MeteredWrite { host: self, w };
+        let mw = MeteredWrite { host: self, w };
+        let mut w = DepthLimitedWrite::new(mw, DEFAULT_XDR_RW_DEPTH_LIMIT);
         // MeteredWrite above turned any budget failure into an IO error; we turn it
         // back to a budget failure here, since there's really no "IO error" that can
         // occur when writing to a Vec<u8>.
```

### soroban-env-host/src/lib.rs
```diff
@@ -48,7 +48,7 @@ pub use host::testutils::call_with_suppressed_panic_hook;
 pub use host::ContractFunctionSet;
 pub use host::{
     metered_map::MeteredOrdMap, metered_vector::MeteredVector, Host, HostError, LedgerInfo, Seed,
-    SEED_BYTES,
+    DEFAULT_HOST_DEPTH_LIMIT, SEED_BYTES,
 };
 pub use soroban_env_common::*;
 
```

### soroban-env-host/src/native_contract/token/test_token.rs
```diff
@@ -7,7 +7,7 @@ use crate::{
     Host, HostError,
 };
 use soroban_env_common::{
-    xdr::{Asset, WriteXdr},
+    xdr::{Asset, DepthLimitedWrite, WriteXdr, DEFAULT_XDR_RW_DEPTH_LIMIT},
     Env,
 };
 use soroban_env_common::{Symbol, TryFromVal, TryIntoVal};
@@ -21,11 +21,11 @@ pub(crate) struct TestToken<'a> {
 
 impl<'a> TestToken<'a> {
     pub(crate) fn new_from_asset(host: &'a Host, asset: Asset) -> Self {
-        let mut asset_bytes_vec = vec![];
+        let mut asset_bytes_vec = DepthLimitedWrite::new(vec![], DEFAULT_XDR_RW_DEPTH_LIMIT);
         asset.write_xdr(&mut asset_bytes_vec).unwrap();
         let address_obj = host
             .create_asset_contract(
-                Bytes::from_slice(host, &asset_bytes_vec.as_slice())
+                Bytes::from_slice(host, &asset_bytes_vec.inner.as_slice())
                     .unwrap()
                     .into(),
             )
```

### soroban-env-host/src/test.rs
```diff
@@ -1,24 +1,24 @@
 pub(crate) mod util;
 
 mod address;
+mod auth;
 mod basic;
+mod budget_metering;
 mod bytes;
+mod complex;
 mod crypto;
+mod depth_limit;
+mod event;
+mod hostile;
+mod invocation;
 mod ledger;
+mod lifecycle;
 mod map;
 mod num;
+mod prng;
 mod storage;
 mod str;
 mod symbol;
-mod vec;
-
-mod auth;
-mod budget_metering;
-mod complex;
-mod event;
-mod hostile;
-mod invocation;
-mod lifecycle;
-mod prng;
 mod token;
 mod tuple;
+mod vec;
```
