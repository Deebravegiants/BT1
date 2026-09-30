# [?] Count gasless tx for DoS protection (#25866)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-03-30
Source: https://github.com/MystenLabs/sui/commit/54e640f65d70ba7f1fa280c458671b381d687ec7
Type: security-commit

## Details
Count gasless tx for DoS protection (#25866)

## Description 

Gasless tx should be counted in traffic controller since they have no
cost to sender.

## Test plan 

Added test

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:
- [ ] Indexing Framework:

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### crates/sui-core/src/authority_server.rs
```diff
@@ -706,6 +706,8 @@ impl ValidatorService {
         let mut results: Vec<Option<SubmitTxResult>> = vec![None; request.transactions.len()];
         // Total size of all transactions in the request.
         let mut total_size_bytes = 0;
+        // Traffic control spam weight to use for the transaction.
+        let mut spam_weight = Weight::zero();
 
         let req_type = if is_ping_request {
             "ping"
@@ -737,6 +739,15 @@ impl ValidatorService {
             // Ok to fail the request when any transaction is invalid.
             let tx_size = transaction.validity_check(&epoch_store.tx_validity_check_context())?;
 
+            if transaction
+                .data()
+                .transaction_data()
+                .is_gasless_transaction()
+            {
+                // Gasless transactions count for traffic control, since they have no economic cost.
+                spam_weight = Weight::one();
+            }
+
             let overload_check_res = state.check_system_overload(
                 consensus_adapter,
                 transaction.data(),
@@ -912,7 +923,7 @@ impl ValidatorService {
         }
 
         if consensus_transactions.is_empty() && !is_ping_request {
-            return Ok((Self::try_from_submit_tx_response(results)?, Weight::zero()));
+            return Ok((Self::try_from_submit_tx_response(results)?, spam_weight));
         }
 
         // Set the max bytes size of the soft bundle to be half of the consensus max transactions in block size.
@@ -1016,7 +1027,7 @@ impl ValidatorService {
             }
         }
 
-        Ok((Self::try_from_submit_tx_response(results)?, Weight::zero()))
+        Ok((Self::try_from_submit_tx_response(results)?, spam_weight))
     }
 
     fn try_from_submit_tx_response(
```

### crates/sui-e2e-tests/tests/traffic_control_tests.rs
```diff
@@ -9,6 +9,7 @@
 use core::panic;
 use fastcrypto::encoding::Base64;
 use jsonrpsee::{core::client::ClientT, rpc_params};
+use move_core_types::identifier::Identifier;
 use std::fs::File;
 use std::num::NonZeroUsize;
 use std::time::Duration;
@@ -22,16 +23,24 @@ use sui_json_rpc_types::{
 };
 use sui_macros::sim_test;
 use sui_network::default_mysten_network_config;
+use sui_protocol_config::ProtocolConfig;
 use sui_swarm_config::network_config_builder::ConfigBuilder;
 use sui_test_transaction_builder::batch_make_transfer_transactions;
+use sui_types::gas_coin::GAS;
 use sui_types::traffic_control::TrafficControlReconfigParams;
 use sui_types::{
+    SUI_FRAMEWORK_PACKAGE_ID,
     crypto::Ed25519SuiSignature,
     messages_grpc::SubmitTxRequest,
+    programmable_transaction_builder::ProgrammableTransactionBuilder,
     signature::GenericSignature,
     traffic_control::{
         FreqThresholdConfig, PolicyConfig, PolicyType, RemoteFirewallConfig, Weight,
     },
+    transaction::{
+        FundsWithdrawalArg, GasData, TransactionData, TransactionDataV1, TransactionExpiration,
+        TransactionKind, add_gasless_token_for_testing,
+    },
     transaction_driver_types::ExecuteTransactionRequestType,
 };
 use test_cluster::{TestCluster, TestClusterBuilder};
@@ -976,3 +985,95 @@ async fn assert_validator_traffic_control_dry_run(
     }
     Ok(())
 }
+
+#[tokio::test]
+async fn test_validator_traffic_control_gasless_spam_blocked() -> Result<(), anyhow::Error> {
+    telemetry_subscribers::init_for_testing();
+    let n = 5;
+    let _guard = ProtocolConfig::apply_overrides_for_testing(|_, mut cfg| {
+        cfg.enable_gasless_for_testing();
+        cfg
+    });
+    let policy_config = PolicyConfig {
+        connection_blocklist_ttl_sec: 1,
+        proxy_blocklist_ttl_sec: 5,
+        spam_policy_type: PolicyType::TestNConnIP(n - 1),
+        spam_sample_rate: Weight::one(),
+        error_policy_type: PolicyType::TestPanicOnInvocation,
+        dry_run: false,
+        ..Default::default()
+    };
+    let network_config = ConfigBuilder::new_with_temp_dir()
+        .committee_size(NonZeroUsize::new(4).unwrap())
+        .with_policy_config(Some(policy_config))
+        .build();
+    let committee = network_config.committee_with_network();
+    let test_cluster = TestClusterBuilder::new()
+        .set_network_config(network_config)
+        .build()
+        .await;
+    let local_clients = make_network_authority_clients_with_network_config(
+        &committee,
+        &default_mysten_network_config(),
+    );
+    let (_, auth_client) = local_clients.first_key_value().unwrap();
+
+    let chain_id = test_cluster.get_chain_identifier();
+    let sender = test_cluster.wallet.get_addresses()[0];
+    let recipient = test_cluster.wallet.get_addresses()[1];
+
+    // Register SUI as an allowed gasless token type for this test.
+    add_gasless_token_for_testing(GAS::type_tag().to_canonical_string(true));
+
+    // Build a gasless transaction with a valid balance::send_funds MoveCall.
+    let mut builder = ProgrammableTransactionBuilder::new();
+    let withdraw_arg = FundsWithdrawalArg::balance_from_sender(1000, GAS::type_tag());
+    let withdraw_arg = builder.funds_withdrawal(withdraw_arg).unwrap();
+    let balance = builder.programmable_move_call(
+        SUI_FRAMEWORK_PACKAGE_ID,
+        Identifier::new("balance").unwrap(),
+        Identifier::new("redeem_funds").unwrap(),
+        vec![GAS::type_tag()],
+        vec![withdraw_arg],
+    );
+    let recipient_arg = builder.pure(recipient).unwrap();
+    builder.programmable_move_call(
+        SUI_FRAMEWORK_PACKAGE_ID,
+        Identifier::new("balance").unwrap(),
+        Identifier::new("send_funds").unwrap(),
+        vec![GAS::type_tag()],
+        vec![balance, recipient_arg],
+    );
+    let tx_kind = TransactionKind::ProgrammableTransaction(builder.finish());
+    let tx_data = TransactionData::V1(TransactionDataV1 {
+        kind: tx_kind,
+        sender,
+        gas_data: GasData {
+            payment: vec![],
+            owner: sender,
+            price: 0,
+            budget: 0,
+        },
+        expiration: TransactionExpiration::ValidDuring {
+            min_epoch: Some(0),
+            max_epoch: Some(0),
+            min_timestamp: None,
+            max_timestamp: None,
+            chain: chain_id,
+            nonce: 0,
+        },
+    });
+    let tx = test_cluster.wallet.sign_transaction(&tx_data).await;
+
+    for _ in 0..n {
+        let response = auth_client
+            .submit_transaction(SubmitTxRequest::new_transaction(tx.clone()), None)
+            .await;
+        if let Err(err) = response
+            && err.to_string().contains("Too many requests")
+        {
+            return Ok(());
+        }
+    }
+    panic!("Expected spam policy to trigger within {n} requests for gasless transactions");
+}
```
