# [?] fix ccc panic CodeNotFound (#958)

## Summary
Severity: Unknown
Chain: ZK
Component: scroll-tech/zkevm-circuits
Published: 2023-09-19
Source: https://github.com/scroll-tech/zkevm-circuits/commit/2723b82fb5d538d6fcc7b2dd0d84d3df8818499f
Type: security-commit

## Details
fix ccc panic CodeNotFound (#958)

## Patch
### bus-mapping/src/circuit_input_builder/input_state_ref.rs
```diff
@@ -90,15 +90,20 @@ impl<'a> CircuitInputStateRef<'a> {
                 let mut gas_left = prev_step.gas_left.0 - prev_step.gas_cost.0;
                 // handling for contract creation tx
                 let call = self.tx.calls()[0].clone();
-                if call.is_create() {
+                if call.is_create()
+                    && call.is_success()
+                    && prev_step.exec_state == ExecState::Op(OpcodeId::RETURN)
+                {
                     let code_hash = self.sdb.get_account(&call.address).1.code_hash;
-                    let bytecode_len = self.code(code_hash).unwrap().len() as u64;
-                    let deposit_cost = bytecode_len * GasCost::CODE_DEPOSIT_BYTE_COST.as_u64();
-                    assert!(
-                        gas_left >= deposit_cost,
-                        "gas left {gas_left} is not enough for deposit cost {deposit_cost}"
-                    );
-                    gas_left -= deposit_cost;
+                    if code_hash != CodeDB::empty_code_hash() {
+                        let bytecode_len = self.code(code_hash).unwrap().len() as u64;
+                        let deposit_cost = bytecode_len * GasCost::CODE_DEPOSIT_BYTE_COST.as_u64();
+                        assert!(
+                            gas_left >= deposit_cost,
+                            "gas left {gas_left} is not enough for deposit cost {deposit_cost}"
+                        );
+                        gas_left -= deposit_cost;
+                    }
                 }
 
                 Gas(gas_left)
```
