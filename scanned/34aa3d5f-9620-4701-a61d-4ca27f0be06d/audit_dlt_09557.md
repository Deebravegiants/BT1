# [?] add intrinsic gas check before transact to avoid arithmetic operation overflow

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2025-04-18
Source: https://github.com/Conflux-Chain/conflux-rust/commit/82500ade686e39211a10820ca15da04ba3d38cc4
Type: security-commit

## Details
add intrinsic gas check before transact to avoid arithmetic operation overflow

## Patch
### bins/conflux/src/command/evm/statetest/mod.rs
```diff
@@ -3,16 +3,16 @@ mod utils;
 
 use cfx_executor::{
     executive::{
-        ChargeCollateral, ExecutionOutcome, ExecutiveContext, TransactOptions,
-        TransactSettings,
+        gas_required_for, ChargeCollateral, ExecutionOutcome, ExecutiveContext,
+        TransactOptions, TransactSettings,
     },
     machine::{Machine, VmFactory},
     state::State,
 };
 use cfx_rpc_eth_types::{
     AccountOverride, AccountStateOverrideMode, StateOverride,
 };
-use cfx_statedb::{Result as DbResult, StateDb};
+use cfx_statedb::{Error as DbError, Result as DbResult, StateDb};
 use cfx_types::{
     u256_to_h256_be, AddressWithSpace, Space, SpaceMap, H256, U256, U64,
 };
@@ -224,13 +224,6 @@ impl StateTestCmd {
                 // spec_name.
 
                 for (index, test) in tests.into_iter().enumerate() {
-                    if Some(
-                        "TransactionException.INTRINSIC_GAS_TOO_LOW"
-                            .to_string(),
-                    ) == test.expect_exception
-                    {
-                        continue;
-                    }
                     let _ = index;
                     let tx = self.make_tx(
                         &unit.transaction,
@@ -563,6 +556,21 @@ impl StateTestCmd {
     ) -> DbResult<ExecutionOutcome> {
         let machine = self.make_machine();
         let spec = machine.spec(env.number, env.epoch_height);
+
+        // intrinsic gas check
+        let tx_intrinsic_gas = gas_required_for(
+            transaction.action() == Action::Create,
+            &transaction.data(),
+            transaction.access_list(),
+            transaction.authorization_len(),
+            &spec,
+        );
+        if transaction.gas_limit().as_u64() < tx_intrinsic_gas {
+            return Err(DbError::Msg(
+                "TransactionException.INTRINSIC_GAS_TOO_LOW".into(),
+            ));
+        }
+
         let evm = ExecutiveContext::new(state, env, &machine, &spec);
         evm.transact(transaction, options)
     }
```
