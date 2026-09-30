# [?] Close anti-reentrancy mechanism

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-09-10
Source: https://github.com/Conflux-Chain/conflux-rust/commit/6e9b18290d74c616ab092da41ffcf0b4dca3056c
Type: security-commit

## Details
Close anti-reentrancy mechanism

## Patch
### client/src/configuration.rs
```diff
@@ -1060,14 +1060,10 @@ impl Configuration {
             .raw_conf
             .unnamed_21autumn_transition_number
             .unwrap_or(default_transition_time);
-        params.transition_numbers.cip71a = self
+        params.transition_numbers.cip71 = self
             .raw_conf
             .unnamed_21autumn_transition_number
             .unwrap_or(default_transition_time);
-        params.transition_numbers.cip71b = self
-            .raw_conf
-            .unnamed_21autumn_cip71_deferred_transition
-            .unwrap_or(default_transition_time);
         params.transition_numbers.cip72b = self
             .raw_conf
             .unnamed_21autumn_transition_number
```

### core/src/executive/executive.rs
```diff
@@ -10,7 +10,6 @@ use crate::{
     executive::{
         context::LocalContext,
         executed::{ExecutionOutcome, ToRepackError},
-        internal_contract::get_reentrancy_allowance,
         vm_exec::{BuiltinExec, InternalContractExec, NoopExec},
         CollateralCheckResultToVmResult, InternalContractTrait, TxDropError,
     },
@@ -504,16 +503,7 @@ impl<'a, Substate: SubstateMngTrait> CallCreateExecutive<'a, Substate> {
         state.checkpoint();
 
         let contract_address = self.get_recipient().clone();
-        let allow_reentrancy = if self.context.spec.cip71a {
-            get_reentrancy_allowance(
-                &contract_address,
-                state,
-                &mut self.context.substate,
-            )?
-        } else {
-            false
-        };
-        callstack.push(contract_address, is_create, allow_reentrancy);
+        callstack.push(contract_address, is_create);
 
         // Pre execution: transfer value and init contract.
         let spec = self.context.spec;
```

### core/src/executive/internal_contract/contracts/future.rs
```diff
@@ -9,3 +9,6 @@ use cfx_types::Address;
 make_solidity_contract! {
     pub(super) struct PoS(POS_REGISTER_CONTRACT_ADDRESS, "placeholder");
 }
+make_solidity_contract! {
+    pub(super) struct AntiReentrancyConfig(ANTI_REENTRANCY_CONTRACT_ADDRESS, "placeholder");
+}
```

### core/src/executive/internal_contract/contracts/mod.rs
```diff
@@ -5,7 +5,6 @@
 mod admin;
 mod context;
 mod future;
-mod reentrancy;
 mod sponsor;
 mod staking;
 
@@ -37,8 +36,8 @@ mod macros {
 }
 
 pub use self::{
-    admin::AdminControl, context::Context, reentrancy::AntiReentrancyConfig,
-    sponsor::SponsorWhitelistControl, staking::Staking,
+    admin::AdminControl, context::Context, sponsor::SponsorWhitelistControl,
+    staking::Staking,
 };
 
 use super::{
@@ -185,13 +184,14 @@ impl InternalContractMap {
     }
 }
 
-/// All Built-in contracts.
+/// All Built-in contracts. All these addresses will be initialized as an
+/// internal contract in the genesis block of test mode.
 pub fn all_internal_contracts() -> Vec<Box<dyn InternalContractTrait>> {
     vec![
         Box::new(AdminControl::instance()),
         Box::new(Staking::instance()),
         Box::new(SponsorWhitelistControl::instance()),
-        Box::new(AntiReentrancyConfig::instance()),
+        Box::new(future::AntiReentrancyConfig::instance()),
         Box::new(Context::instance()),
         Box::new(future::PoS::instance()),
     ]
```

### core/src/executive/internal_contract/contracts/reentrancy.rs
```diff
@@ -1,119 +0,0 @@
-// Copyright 2020 Conflux Foundation. All rights reserved.
-// Conflux is free software and distributed under GNU General Public License.
-// See http://www.gnu.org/licenses/
-
-use super::{
-    super::impls::reentrancy::*, macros::*, ExecutionTrait, SolFnTable,
-};
-use crate::{
-    evm::{ActionParams, Spec},
-    executive::InternalRefContext,
-    spec::CommonParams,
-    trace::{trace::ExecTrace, Tracer},
-    vm,
-};
-use cfx_parameters::internal_contract_addresses::ANTI_REENTRANCY_CONTRACT_ADDRESS;
-use cfx_state::state_trait::StateOpsTrait;
-use cfx_types::{Address, U256};
-
-make_solidity_contract! {
-    pub struct AntiReentrancyConfig(ANTI_REENTRANCY_CONTRACT_ADDRESS,
-        generate_fn_table,
-        initialize: |params: &CommonParams| params.transition_numbers.cip71a,
-        is_active: |spec: &Spec| spec.cip71a);
-}
-fn generate_fn_table() -> SolFnTable {
-    make_function_table!(
-        AllowReentrancy,
-        AllowReentrancyByAdmin,
-        IsReentrancyAllowed
-    )
-}
-group_impl_is_active!(
-    |spec: &Spec| spec.cip71a,
-    AllowReentrancy,
-    AllowReentrancyByAdmin,
-    IsReentrancyAllowed
-);
-
-make_solidity_function! {
-    struct AllowReentrancy(bool, "allowReentrancy(bool)");
-}
-impl_function_type!(AllowReentrancy, "non_payable_write", gas: |spec: &Spec| spec.sstore_reset_gas);
-
-impl ExecutionTrait for AllowReentrancy {
-    fn execute_inner(
-        &self, input: bool, params: &ActionParams,
-        context: &mut InternalRefContext,
-        _tracer: &mut dyn Tracer<Output = ExecTrace>,
-    ) -> vm::Result<()>
-    {
-        if context.is_contract_address(&params.sender)? {
-            let storage_owner = params.storage_owner;
-            let contract_address = params.sender;
-            set_reentrancy_allowance(
-                &contract_address,
-                input,
-                context.state,
-                context.substate,
-                storage_owner,
-            )?
-        }
-        Ok(())
-    }
-}
-
-make_solidity_function! {
-    struct AllowReentrancyByAdmin((Address,bool), "allowReentrancyByAdmin(address,bool)");
-}
-impl_function_type!(AllowReentrancyByAdmin, "non_payable_write", gas: |spec: &Spec| spec.sstore_reset_gas);
-
-impl ExecutionTrait for AllowReentrancyByAdmin {
-    fn execute_inner(
-        &self, input: (Address, bool), params: &ActionParams,
-        context: &mut InternalRefContext,
-        _tracer: &mut dyn Tracer<Output = ExecTrace>,
-    ) -> vm::Result<()>
-    {
-        let (contract, allowance) = input;
-        if context.is_contract_address(&contract)?
-            && &params.sender == &context.state.admin(&contract)?
-        {
-            let storage_owner = params.storage_owner;
-            set_reentrancy_allowance(
-                &contract,
-                allowance,
-                context.state,
-                context.substate,
-                storage_owner,
-            )?
-        }
-        Ok(())
-    }
-}
-
-make_solidity_function! {
-    struct IsReentrancyAllowed(Address, "isReentrancyAllowed(address)", bool);
-}
-impl_function_type!(IsReentrancyAllowed, "query_with_default_gas");
-
-impl ExecutionTrait for IsReentrancyAllowed {
-    fn execute_inner(
-        &self, input: Address, _params: &ActionParams,
-        context: &mut InternalRefContext,
-        _tracer: &mut dyn Tracer<Output = ExecTrace>,
-    ) -> vm::Result<bool>
-    {
-        get_reentrancy_allowance(&input, context.state, context.substate)
-            .map_err(|err| err.into())
-    }
-}
-
-#[test]
-fn test_reentrancy_contract_sig() {
-    // Check the consistency between signature generated by rust code and
-    // js-conflux-sdk.
-    check_signature!(AllowReentrancy, "838d377c");
-    check_signature!(AllowReentrancyByAdmin, "8fef6c39");
-    check_signature!(IsReentrancyAllowed, "e2adea25");
-}
```

### core/src/executive/internal_contract/impls/mod.rs
```diff
@@ -3,8 +3,7 @@
 // See http://www.gnu.org/licenses/
 
 pub(super) mod admin;
-pub(super) mod reentrancy;
 pub(super) mod sponsor;
 pub(super) mod staking;
 
-pub use self::{admin::suicide, reentrancy::get_reentrancy_allowance};
+pub use self::admin::suicide;
```

### core/src/executive/internal_contract/impls/reentrancy.rs
```diff
@@ -1,31 +0,0 @@
-use cfx_parameters::internal_contract_addresses::ANTI_REENTRANCY_CONTRACT_ADDRESS;
-use cfx_state::{state_trait::StateOpsTrait, SubstateTrait};
-use cfx_statedb::Result as DbResult;
-use cfx_types::Address;
-
-pub fn set_reentrancy_allowance(
-    contract_address: &Address, allowance: bool, state: &mut dyn StateOpsTrait,
-    substate: &mut dyn SubstateTrait, storage_owner: Address,
-) -> DbResult<()>
-{
-    substate.set_storage(
-        state,
-        &ANTI_REENTRANCY_CONTRACT_ADDRESS,
-        contract_address.to_fixed_bytes().into(),
-        (allowance as u8).into(),
-        storage_owner,
-    )
-}
-
-pub fn get_reentrancy_allowance(
-    contract_address: &Address, state: &mut dyn StateOpsTrait,
-    substate: &mut dyn SubstateTrait,
-) -> DbResult<bool>
-{
-    let value = substate.storage_at(
-        state,
-        &ANTI_REENTRANCY_CONTRACT_ADDRESS,
-        contract_address.as_bytes(),
-    )?;
-    Ok(!value.is_zero())
-}
```

### core/src/executive/internal_contract/mod.rs
```diff
@@ -9,8 +9,7 @@ mod impls;
 mod internal_context;
 
 pub use self::{
-    contracts::InternalContractMap,
-    impls::{get_reentrancy_allowance, suicide},
+    contracts::InternalContractMap, impls::suicide,
     internal_context::InternalRefContext,
 };
 pub use solidity_abi::ABIDecodeError;
```

### core/src/spec/spec.rs
```diff
@@ -85,8 +85,7 @@ pub struct TransitionsBlockNumber {
     /// CIP64: Get current epoch number through internal contract
     pub cip64: BlockNumber,
     /// CIP71: Configurable anti-reentrancy
-    pub cip71a: BlockNumber,
-    pub cip71b: BlockNumber,
+    pub cip71: BlockNumber,
     /// CIP72: Accept Ethereum transaction signature
     pub cip72b: BlockNumber,
     /// CIP78: Correct `is_sponsored` fields in receipt
```

### core/src/state/substate.rs
```diff
@@ -29,15 +29,10 @@ impl CallStackInfo {
         }
     }
 
-    pub fn push(
-        &mut self, address: Address, is_create: bool, allow_reentrancy: bool,
-    ) {
+    pub fn push(&mut self, address: Address, is_create: bool) {
         // We should still use the correct behaviour to check if reentrancy
         // happens.
-        if !allow_reentrancy
-            && self.last() != Some(&address)
-            && self.contains_key(&address)
-        {
+        if self.last() != Some(&address) && self.contains_key(&address) {
             self.first_reentrancy_depth
                 .get_or_insert(self.call_stack_recipient_addresses.len());
         }
@@ -78,9 +73,9 @@ impl CallStackInfo {
     }
 
     pub fn in_reentrancy(&self, spec: &Spec) -> bool {
-        if spec.cip71b {
-            // Expected behaviour
-            self.first_reentrancy_depth.is_some()
+        if spec.cip71 {
+            // After CIP-71, anti-reentrancy will closed.
+            false
         } else {
             // Consistent with old behaviour
             // The old (unexpected) behaviour is equivalent to the top element
@@ -279,14 +274,14 @@ mod tests {
     #[test]
     fn test_callstack_info() {
         let mut call_stack = CallStackInfo::new();
-        call_stack.push(get_test_address(1), false, false);
-        call_stack.push(get_test_address(2), false, false);
+        call_stack.push(get_test_address(1), false);
+        call_stack.push(get_test_address(2), false);
         assert_eq!(call_stack.pop(), Some((get_test_address(2), false)));
         assert_eq!(call_stack.contains_key(&get_test_address(2)), false);
 
-        call_stack.push(get_test_address(3), true, false);
-        call_stack.push(get_test_address(4), false, false);
-        call_stack.push(get_test_address(3), false, false);
+        call_stack.push(get_test_address(3), true);
+        call_stack.push(get_test_address(4), false);
+        call_stack.push(get_test_address(3), false);
         assert_eq!(call_stack.last().unwrap().clone(), get_test_address(3));
 
         assert_eq!(call_stack.pop(), Some((get_test_address(3), false)));
@@ -301,9 +296,9 @@ mod tests {
         assert_eq!(call_stack.contains_key(&get_test_address(3)), false);
         assert_eq!(call_stack.last().unwrap().clone(), get_test_address(1));
 
-        call_stack.push(get_test_address(3), true, false);
-        call_stack.push(get_test_address(4), false, false);
-        call_stack.push(get_test_address(3), false, false);
+        call_stack.push(get_test_address(3), true);
+        call_stack.push(get_test_address(4), false);
+        call_stack.push(get_test_address(3), false);
         assert_eq!(call_stack.last().unwrap().clone(), get_test_address(3));
 
         assert_eq!(call_stack.pop(), Some((get_test_address(3), false)));
```

### core/src/vm/spec.rs
```diff
@@ -133,9 +133,7 @@ pub struct Spec {
     /// CIP-64: Get current epoch number through internal contract
     pub cip64: bool,
     /// CIP-71: Configurable anti-reentrancy: if configuration enabled
-    pub cip71a: bool,
-    /// CIP-71: Configurable anti-reentrancy: existing bug fixed
-    pub cip71b: bool,
+    pub cip71: bool,
     /// CIP-72: Accept Ethereum transaction signature
     pub cip72: bool,
     /// CIP-78: Correct `is_sponsored` fields in receipt
@@ -267,8 +265,7 @@ impl Spec {
             wasm: None,
             cip62: false,
             cip64: false,
-            cip71a: false,
-            cip71b: false,
+            cip71: false,
             cip72: false,
             cip78: false,
             cip80: false,
@@ -281,8 +278,7 @@ impl Spec {
         let mut spec = Self::genesis_spec();
         spec.cip62 = number >= params.transition_numbers.cip62;
         spec.cip64 = number >= params.transition_numbers.cip64;
-        spec.cip71a = number >= params.transition_numbers.cip71a;
-        spec.cip71b = number >= params.transition_numbers.cip71b;
+        spec.cip71 = number >= params.transition_numbers.cip71;
         spec.cip72 = number >= params.transition_numbers.cip72b;
         spec.cip78 = number >= params.transition_numbers.cip78;
         spec.cip80 = number >= params.transition_numbers.cip80;
```

### tests/reentrancy_no_protect_test.py
```diff
@@ -1,4 +0,0 @@
-from reentrancy_test_template import ReentrancyTest, NO_PROTECTION
-
-if __name__ == '__main__':
-    ReentrancyTest(NO_PROTECTION).main()
```
