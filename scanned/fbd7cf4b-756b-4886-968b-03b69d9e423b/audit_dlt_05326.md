# [?] Fix for the race condition with tx status and receipts (#1658)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-02-12
Source: https://github.com/FuelLabs/fuel-core/commit/b7e1c6ece6cafb3c64ca41b6e0c966ee67bca46f
Type: security-commit

## Details
Fix for the race condition with tx status and receipts (#1658)

Example of the failed CI
https://github.com/FuelLabs/fuel-core/actions/runs/7865306004/job/21471566710?pr=1656

The change moves receipts into the `TransationStatus` to avoid requests
to the database. The `TxPool` directly listens for blocks and
transaction statuses to notify the user via subscription. But when it
notifies the users, the off-chain database can still be outdated,
leading to empty receipts.

This PR fixes the race condition for the receipts. However, the problem
still exists for the end user if they want to fetch some updated
information from the off-chain database. I created a separate issue to
track it: https://github.com/FuelLabs/fuel-core/issues/1659.

It is the fix for the https://github.com/FuelLabs/fuel-core/pull/1656

## Patch
### .github/workflows/ci.yml
```diff
@@ -16,7 +16,7 @@ concurrency:
 
 env:
   CARGO_TERM_COLOR: always
-  RUST_VERSION: 1.73.0
+  RUST_VERSION: 1.74.0
   NIGHTLY_RUST_VERSION: nightly-2023-10-29
   RUSTFLAGS: -D warnings
   REGISTRY: ghcr.io
```

### .github/workflows/dependencies.yml
```diff
@@ -16,7 +16,7 @@ defaults:
 env:
   # So cargo doesn't complain about unstable features
   RUSTC_BOOTSTRAP: 1
-  RUST_VERSION: 1.73.0
+  RUST_VERSION: 1.74.0
   PR_TITLE: Weekly `cargo update`
   PR_MESSAGE: |
     Automation to keep dependencies in `Cargo.lock` current.
```

### CHANGELOG.md
```diff
@@ -10,6 +10,7 @@ Description of the upcoming release here.
 
 ### Changed
 
+- [#1658](https://github.com/FuelLabs/fuel-core/pull/1658): Removed `Receipts` table. Instead, receipts are part of the `TransactionStatuses` table.
 - [#1650](https://github.com/FuelLabs/fuel-core/pull/1650): Add api endpoint for getting estimates for future gas prices
 - [#1649](https://github.com/FuelLabs/fuel-core/pull/1649): Add api endpoint for getting latest gas price
 - [#1600](https://github.com/FuelLabs/fuel-core/pull/1640): Upgrade to fuel-vm 0.45.0
@@ -29,6 +30,9 @@ Description of the upcoming release here.
 - [#1636](https://github.com/FuelLabs/fuel-core/pull/1636): Add more docs to GraphQL DAP API.
 
 #### Breaking
+- [#1658](https://github.com/FuelLabs/fuel-core/pull/1658): Receipts are part of the transaction status. 
+    Removed `reason` from the `TransactionExecutionResult::Failed`. It can be calculated based on the program state and receipts.
+    Also, it is not possible to fetch `receipts` from the `Transaction` directly anymore. Instead, you need to fetch `status` and its receipts.
 - [#1646](https://github.com/FuelLabs/fuel-core/pull/1646): Remove redundant receipts from queries.
 - [#1639](https://github.com/FuelLabs/fuel-core/pull/1639): Make Merkle metadata, i.e. `SparseMerkleMetadata` and `DenseMerkleMetadata` type version-able enums
 - [#1632](https://github.com/FuelLabs/fuel-core/pull/1632): Make `Message` type a version-able enum
```

### benches/benches/block_target_gas.rs
```diff
@@ -72,6 +72,7 @@ use fuel_core_types::{
         checked_transaction::EstimatePredicates,
         consts::WORD_SIZE,
     },
+    services::executor::TransactionExecutionResult,
 };
 use rand::SeedableRng;
 use utils::{
@@ -352,11 +353,9 @@ fn run_with_service_with_extra_inputs(
     extra_outputs: Vec<Output>,
 ) {
     group.bench_function(id, |b| {
-
         b.to_async(rt).iter(|| {
             let shared = service.shared.clone();
 
-
             let mut tx_builder = fuel_core_types::fuel_tx::TransactionBuilder::script(
                 script.clone().into_iter().collect(),
                 script_data.clone(),
@@ -382,7 +381,11 @@ fn run_with_service_with_extra_inputs(
                     TxPointer::default(),
                     *contract_id,
                 );
-                let contract_output = Output::contract(input_count as u8, Bytes32::zeroed(), Bytes32::zeroed());
+                let contract_output = Output::contract(
+                    input_count as u8,
+                    Bytes32::zeroed(),
+                    Bytes32::zeroed(),
+                );
 
                 tx_builder
                     .add_input(contract_input)
@@ -397,9 +400,13 @@ fn run_with_service_with_extra_inputs(
                 tx_builder.add_output(*output);
             }
             let mut tx = tx_builder.finalize_as_transaction();
-            tx.estimate_predicates(&shared.config.chain_conf.consensus_parameters.clone().into()).unwrap();
+            tx.estimate_predicates(
+                &shared.config.chain_conf.consensus_parameters.clone().into(),
+            )
+            .unwrap();
             async move {
-                let tx_id = tx.id(&shared.config.chain_conf.consensus_parameters.chain_id);
+                let tx_id =
+                    tx.id(&shared.config.chain_conf.consensus_parameters.chain_id);
 
                 let mut sub = shared.block_importer.block_importer.subscribe();
                 shared
@@ -415,13 +422,12 @@ fn run_with_service_with_extra_inputs(
                 assert_eq!(res.sealed_block.entity.transactions().len(), 2);
                 assert_eq!(res.tx_status[0].id, tx_id);
 
-                let fuel_core_types::services::executor::TransactionExecutionResult::Failed {
-                    reason,
-                    ..
-                } = &res.tx_status[0].result
-                    else {
-                        panic!("The execution should fails with out of gas")
-                    };
+                let TransactionExecutionResult::Failed { result, receipts } =
+                    &res.tx_status[0].result
+                else {
+                    panic!("The execution should fails with out of gas")
+                };
+                let reason = TransactionExecutionResult::reason(receipts, result);
                 if !reason.contains("OutOfGas") {
                     panic!("The test failed because of {}", reason);
                 }
```

### bin/e2e-test-client/src/tests/script.rs
```diff
@@ -179,7 +179,7 @@ async fn _dry_runs(
 
         let tx_statuses = query?;
         for (tx_status, tx) in tx_statuses.iter().zip(transactions.iter()) {
-            if tx_status.receipts.is_empty() {
+            if tx_status.result.receipts().is_empty() {
                 return Err(
                     format!("Receipts are empty for query_number {query_number}").into(),
                 )
@@ -189,10 +189,13 @@ async fn _dry_runs(
             if expect == DryRunResult::Successful {
                 assert!(matches!(
                     &tx_status.result,
-                    TransactionExecutionResult::Success { result: _result }
+                    TransactionExecutionResult::Success {
+                        result: _result,
+                        ..
+                    }
                 ));
                 assert!(matches!(
-                    tx_status.receipts.last(),
+                    tx_status.result.receipts().last(),
                     Some(Receipt::ScriptResult {
                         result: ScriptExecutionResult::Success,
                         ..
```

### ci_checks.sh
```diff
@@ -3,7 +3,7 @@
 # The script runs almost all CI checks locally.
 #
 # Requires installed:
-# - Rust `1.73.0`
+# - Rust `1.74.0`
 # - Nightly rust formatter
 # - `cargo install cargo-sort`
 
```

### crates/client/assets/schema.sdl
```diff
@@ -258,10 +258,12 @@ union DependentCost = LightOperation | HeavyOperation
 type DryRunFailureStatus {
 	programState: ProgramState
 	reason: String!
+	receipts: [Receipt!]!
 }
 
 type DryRunSuccessStatus {
 	programState: ProgramState
+	receipts: [Receipt!]!
 }
 
 type DryRunTransactionExecutionStatus {
@@ -973,7 +975,6 @@ type Transaction {
 	witnesses: [HexString!]
 	receiptsRoot: Bytes32
 	status: TransactionStatus
-	receipts: [Receipt!]
 	script: HexString
 	scriptData: HexString
 	bytecodeWitnessIndex: Int
```

### crates/client/src/client/schema/snapshots/fuel_core_client__client__schema__tx__tests__dry_run_tx_gql_output.snap
```diff
@@ -12,49 +12,82 @@ mutation($txs: [HexString!]!, $utxoValidation: Boolean) {
           returnType
           data
         }
+        receipts {
+          param1
+          param2
+          amount
+          assetId
+          gas
+          digest
+          contract {
+            id
+          }
+          is
+          pc
+          ptr
+          ra
+          rb
+          rc
+          rd
+          reason
+          receiptType
+          to {
+            id
+          }
+          toAddress
+          val
+          len
+          result
+          gasUsed
+          data
+          sender
+          recipient
+          nonce
+          contractId
+          subId
+        }
       }
       ... on DryRunFailureStatus {
-        reason
         programState {
           returnType
           data
         }
+        receipts {
+          param1
+          param2
+          amount
+          assetId
+          gas
+          digest
+          contract {
+            id
+          }
+          is
+          pc
+          ptr
+          ra
+          rb
+          rc
+          rd
+          reason
+          receiptType
+          to {
+            id
+          }
+          toAddress
+          val
+          len
+          result
+          gasUsed
+          data
+          sender
+          recipient
+          nonce
+          contractId
+          subId
+        }
       }
     }
-    receipts {
-      param1
-      param2
-      amount
-      assetId
-      gas
-      digest
-      contract {
-        id
-      }
-      is
-      pc
-      ptr
-      ra
-      rb
-      rc
-      rd
-      reason
-      receiptType
-      to {
-        id
-      }
-      toAddress
-      val
-      len
-      result
-      gasUsed
-      data
-      sender
-      recipient
-      nonce
-      contractId
-      subId
-    }
   }
 }
 
```

### crates/client/src/client/schema/snapshots/fuel_core_client__client__schema__tx__tests__transparent_transaction_by_id_query_gql_output.snap
```diff
@@ -196,40 +196,6 @@ query($id: TransactionId!) {
       }
     }
     witnesses
-    receipts {
-      param1
-      param2
-      amount
-      assetId
-      gas
-      digest
-      contract {
-        id
-      }
-      is
-      pc
-      ptr
-      ra
-      rb
-      rc
-      rd
-      reason
-      receiptType
-      to {
-        id
-      }
-      toAddress
-      val
-      len
-      result
-      gasUsed
-      data
-      sender
-      recipient
-      nonce
-      contractId
-      subId
-    }
     script
     scriptData
     policies {
```

### crates/client/src/client/schema/tx.rs
```diff
@@ -217,14 +217,25 @@ impl TryFrom<DryRunTransactionStatus> for TransactionExecutionResult {
     fn try_from(status: DryRunTransactionStatus) -> Result<Self, Self::Error> {
         Ok(match status {
             DryRunTransactionStatus::SuccessStatus(s) => {
+                let receipts = s
+                    .receipts
+                    .into_iter()
+                    .map(|receipt| receipt.try_into())
+                    .collect::<Result<Vec<fuel_tx::Receipt>, _>>()?;
                 TransactionExecutionResult::Success {
                     result: s.program_state.map(TryInto::try_into).transpose()?,
+                    receipts,
                 }
             }
             DryRunTransactionStatus::FailureStatus(s) => {
+                let receipts = s
+                    .receipts
+                    .into_iter()
+                    .map(|receipt| receipt.try_into())
+                    .collect::<Result<Vec<fuel_tx::Receipt>, _>>()?;
                 TransactionExecutionResult::Failed {
                     result: s.program_state.map(TryInto::try_into).transpose()?,
-                    reason: s.reason,
+                    receipts,
                 }
             }
             DryRunTransactionStatus::Unknown => {
@@ -238,21 +249,21 @@ impl TryFrom<DryRunTransactionStatus> for TransactionExecutionResult {
 #[cynic(schema_path = "./assets/schema.sdl")]
 pub struct DryRunSuccessStatus {
     pub program_state: Option<ProgramState>,
+    pub receipts: Vec<Receipt>,
 }
 
 #[derive(cynic::QueryFragment, Debug)]
 #[cynic(schema_path = "./assets/schema.sdl")]
 pub struct DryRunFailureStatus {
-    pub reason: String,
     pub program_state: Option<ProgramState>,
+    pub receipts: Vec<Receipt>,
 }
 
 #[derive(cynic::QueryFragment, Debug)]
 #[cynic(schema_path = "./assets/schema.sdl")]
 pub struct DryRunTransactionExecutionStatus {
     pub id: TransactionId,
     pub status: DryRunTransactionStatus,
-    pub receipts: Vec<Receipt>,
 }
 
 impl TryFrom<DryRunTransactionExecutionStatus> for TransactionExecutionStatus {
@@ -261,17 +272,8 @@ impl TryFrom<DryRunTransactionExecutionStatus> for TransactionExecutionStatus {
     fn try_from(schema: DryRunTransactionExecutionStatus) -> Result<Self, Self::Error> {
         let id = schema.id.into();
         let status = schema.status.try_into()?;
-        let receipts = schema
-            .receipts
-            .into_iter()
-            .map(|receipt| receipt.try_into())
-            .collect::<Result<Vec<fuel_tx::Receipt>, _>>()?;
-
-        Ok(TransactionExecutionStatus {
-            id,
-            result: status,
-            receipts,
-        })
+
+        Ok(TransactionExecutionStatus { id, result: status })
     }
 }
 
```

### crates/client/src/client/schema/tx/transparent_tx.rs
```diff
@@ -2,7 +2,6 @@ use crate::client::schema::{
     contract::ContractIdFragment,
     schema,
     tx::{
-        transparent_receipt::Receipt,
         TransactionStatus,
         TxIdArgs,
     },
@@ -130,8 +129,6 @@ pub struct Transaction {
     pub status: Option<TransactionStatus>,
     /// The field of the `Transaction::Script` and `Transaction::Create`.
     pub witnesses: Option<Vec<HexString>>,
-    /// The receipts produced during transaction execution. It is fetched from the database..
-    pub receipts: Option<Vec<Receipt>>,
     /// The field of the `Transaction::Script`.
     pub script: Option<HexString>,
     /// The field of the `Transaction::Script`.
```

### crates/fuel-core/src/database/storage.rs
```diff
@@ -6,12 +6,9 @@ use crate::{
         message::OwnedMessageIds,
         Database,
     },
-    fuel_core_graphql_api::storage::{
-        receipts::Receipts,
-        transactions::{
-            OwnedTransactions,
-            TransactionStatuses,
-        },
+    fuel_core_graphql_api::storage::transactions::{
+        OwnedTransactions,
+        TransactionStatuses,
     },
     state::DataSource,
 };
@@ -84,7 +81,6 @@ use_structured_implementation!(
     SealedBlockConsensus,
     Transactions,
     ProcessedTransactions,
-    Receipts,
     ContractsStateMerkleMetadata,
     ContractsStateMerkleData,
     ContractsAssetsMerkleMetadata,
```
