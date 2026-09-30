# [?] fix: exceeding MAX gas DOS vector

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2025-02-13
Source: https://github.com/software-mansion/pathfinder/commit/4d6c666524751047f7807dca99a44b7f4ebd3fb8
Type: security-commit

## Details
fix: exceeding MAX gas DOS vector

## Patch
### crates/executor/src/estimate.rs
```diff
@@ -92,7 +92,9 @@ where
             return Err(error);
         }
         Err(TransactionSimulationError::OutOfGas) => {
-            unreachable!("Transaction should not run out of gas with MAX gas limit")
+            return Err(
+                anyhow::anyhow!("Fee estimation failed, maximum gas limit exceeded").into(),
+            );
         }
     };
 
```

### crates/rpc/src/method/estimate_fee.rs
```diff
@@ -193,8 +193,8 @@ impl crate::dto::SerializeForVersion for Output {
 mod tests {
     use pathfinder_common::macro_prelude::*;
     use pathfinder_common::prelude::*;
-    use pathfinder_common::transaction::{DataAvailabilityMode, ResourceBounds};
-    use pathfinder_common::{felt, BlockId, Tip};
+    use pathfinder_common::transaction::{DataAvailabilityMode, ResourceBound, ResourceBounds};
+    use pathfinder_common::{felt, BlockId, ResourceAmount, ResourcePricePerUnit, Tip};
     use pathfinder_executor::types::{FeeEstimate, PriceUnit};
     use pretty_assertions_sorted::assert_eq;
 
@@ -742,9 +742,9 @@ mod tests {
         );
         let sierra_hash =
             class_hash!("0x04468CD91AB8BD74957307632CFC13C48B7B51C741B1BD3069796F3268A5F3D1");
-        // TODO:
+
         let casm_hash =
-            casm_hash!("0x069032ff71f77284e1a0864a573007108ca5cc08089416af50f03260f5d6d4d8");
+            casm_hash!("0x00D15DFCE490CB17D5E4102813BC0BD9362CB371C92AC0AD1E891E0863248CA6");
 
         let contract_class: SierraContractClass =
             ContractClass::from_definition_bytes(sierra_definition)
@@ -830,15 +830,74 @@ mod tests {
                     // AccountCallArray::data_len
                     call_param!("1"),
                     // Depth
-                    call_param!("100"),
+                    call_param!("0x7"),
                 ],
                 nonce: transaction_nonce!("0x2"),
-                resource_bounds: ResourceBounds::default(),
+                resource_bounds: ResourceBounds {
+                    l1_gas: ResourceBound {
+                        max_amount: ResourceAmount(50),
+                        max_price_per_unit: ResourcePricePerUnit(1000),
+                    },
+                    l1_data_gas: Some(ResourceBound {
+                        max_amount: ResourceAmount(100),
+                        max_price_per_unit: ResourcePricePerUnit(1000),
+                    }),
+                    l2_gas: ResourceBound {
+                        max_amount: ResourceAmount(800_000),
+                        max_price_per_unit: ResourcePricePerUnit(1000),
+                    },
+                },
                 tip: Tip(0),
                 paymaster_data: vec![],
                 account_deployment_data: vec![],
-                nonce_data_availability_mode: DataAvailabilityMode::L1,
-                fee_data_availability_mode: DataAvailabilityMode::L1,
+                nonce_data_availability_mode: DataAvailabilityMode::L2,
+                fee_data_availability_mode: DataAvailabilityMode::L2,
+            },
+        ))
+    }
+
+    fn invoke_v3_transaction_max_gas_exceeded(
+        account_contract_address: ContractAddress,
+    ) -> BroadcastedTransaction {
+        BroadcastedTransaction::Invoke(BroadcastedInvokeTransaction::V3(
+            BroadcastedInvokeTransactionV3 {
+                version: TransactionVersion::THREE,
+                signature: vec![],
+                sender_address: account_contract_address,
+                calldata: vec![
+                    // address of the deployed test contract
+                    CallParam(felt!(
+                        "0x0439479402A760C7368249703758241828EB7C838B536195079907F02D8CB838"
+                    )),
+                    // Entry point selector for the called contract, i.e.
+                    // AccountCallArray::selector
+                    CallParam(EntryPoint::hashed(b"test_redeposits").0),
+                    // Length of the call data for the called contract, i.e.
+                    // AccountCallArray::data_len
+                    call_param!("1"),
+                    // Depth
+                    call_param!("100000"),
+                ],
+                nonce: transaction_nonce!("0x2"),
+                resource_bounds: ResourceBounds {
+                    l1_gas: ResourceBound {
+                        max_amount: ResourceAmount(50),
+                        max_price_per_unit: ResourcePricePerUnit(1000),
+                    },
+                    l1_data_gas: Some(ResourceBound {
+                        max_amount: ResourceAmount(100),
+                        max_price_per_unit: ResourcePricePerUnit(1000),
+                    }),
+                    l2_gas: ResourceBound {
+                        max_amount: ResourceAmount(800_000),
+                        max_price_per_unit: ResourcePricePerUnit(1000),
+                    },
+                },
+                tip: Tip(0),
+                paymaster_data: vec![],
+                account_deployment_data: vec![],
+                nonce_data_availability_mode: DataAvailabilityMode::L2,
+                fee_data_availability_mode: DataAvailabilityMode::L2,
             },
         ))
     }
@@ -886,18 +945,45 @@ mod tests {
             unit: PriceUnit::Fri,
         };
         let invoke_expected = FeeEstimate {
-            l1_gas_consumed: 134.into(),
+            l1_gas_consumed: 0.into(),
             l1_gas_price: 2.into(),
             l1_data_gas_consumed: 128.into(),
             l1_data_gas_price: 2.into(),
-            l2_gas_consumed: 0.into(),
+            l2_gas_consumed: 700511.into(),
             l2_gas_price: 1.into(),
-            overall_fee: 524.into(),
+            overall_fee: 700767.into(),
             unit: PriceUnit::Fri,
         };
         self::assert_eq!(
             result,
             Output(vec![declare_expected, deploy_expected, invoke_expected,])
         );
     }
+
+    #[tokio::test]
+    async fn starknet_0_13_4_max_gas_exceeded() {
+        let (context, last_block_header, account_contract_address, universal_deployer_address) =
+            crate::test_setup::test_context_with_starknet_version(StarknetVersion::new(
+                0, 13, 4, 0,
+            ))
+            .await;
+
+        // declare test class
+        let declare_transaction = declare_v3_transaction(account_contract_address);
+        // deploy with universal deployer contract
+        let deploy_transaction =
+            deploy_v3_transaction(account_contract_address, universal_deployer_address);
+
+        // invoke deployed contract
+        let invoke_transaction = invoke_v3_transaction_max_gas_exceeded(account_contract_address);
+
+        let input = Input {
+            request: vec![declare_transaction, deploy_transaction, invoke_transaction],
+            simulation_flags: vec![],
+            block_id: BlockId::Number(last_block_header.number),
+        };
+        let result = super::estimate_fee(context, input).await;
+        let expected_err = anyhow::anyhow!("Fee estimation failed, maximum gas limit exceeded");
+        assert_matches::assert_matches!(result, Err(EstimateFeeError::Internal(err)) if err.to_string() == expected_err.to_string());
+    }
 }
```
