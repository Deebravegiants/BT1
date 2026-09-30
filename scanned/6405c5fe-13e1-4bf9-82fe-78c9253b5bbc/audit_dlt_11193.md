# [?] apollo_gateway: bound concurrent declare compilations to mitigate ingestion DoS (#14552)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-06-21
Source: https://github.com/starkware-libs/sequencer/commit/45b80db43a59ef1cdf893062b65715777678e83c
Type: security-commit

## Details
apollo_gateway: bound concurrent declare compilations to mitigate ingestion DoS (#14552)

Declare transactions trigger CPU- and memory-intensive Sierra-to-CASM
compilation during ingestion, before the transaction's signature and balance
are verified. An unauthenticated attacker could flood the gateway with declares
carrying arbitrary contract classes to exhaust the node's resources.

Bound the number of compilations running concurrently with a process-global
semaphore (configurable via max_concurrent_declare_compilations, default 40).
Declares arriving while the limit is reached are rejected immediately with
TRANSACTION_LIMIT_EXCEEDED rather than queued. The permit is held only across
compilation and released before stateful validation; non-declares are
unaffected.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### crates/apollo_deployments/resources/app_configs/gateway_config.json
```diff
@@ -12,6 +12,7 @@
   "gateway_config.static_config.contract_class_manager_config.native_compiler_config.max_file_size.#is_none": false,
   "gateway_config.static_config.contract_class_manager_config.native_compiler_config.max_memory_usage": 16106127360,
   "gateway_config.static_config.contract_class_manager_config.native_compiler_config.optimization_level": 2,
+  "gateway_config.static_config.max_concurrent_declare_compilations": 40,
   "gateway_config.static_config.proof_archive_writer_config.bucket_name": "",
   "gateway_config.static_config.stateful_tx_validator_config.max_allowed_nonce_gap": 200,
   "gateway_config.static_config.stateful_tx_validator_config.max_nonce_for_validation_skip": "0x1",
```

### crates/apollo_deployments/resources/app_configs/replacer_gateway_config.json
```diff
@@ -12,6 +12,7 @@
   "gateway_config.static_config.contract_class_manager_config.native_compiler_config.max_file_size.#is_none": false,
   "gateway_config.static_config.contract_class_manager_config.native_compiler_config.max_memory_usage": 16106127360,
   "gateway_config.static_config.contract_class_manager_config.native_compiler_config.optimization_level": 2,
+  "gateway_config.static_config.max_concurrent_declare_compilations": 40,
   "gateway_config.static_config.proof_archive_writer_config.bucket_name": "$$$_GATEWAY_CONFIG-STATIC_CONFIG-PROOF_ARCHIVE_WRITER_CONFIG-BUCKET_NAME_$$$",
   "gateway_config.static_config.stateful_tx_validator_config.max_allowed_nonce_gap": "$$$_GATEWAY_CONFIG-STATIC_CONFIG-STATEFUL_TX_VALIDATOR_CONFIG-MAX_ALLOWED_NONCE_GAP_$$$",
   "gateway_config.static_config.stateful_tx_validator_config.max_nonce_for_validation_skip": "0x1",
```

### crates/apollo_gateway/src/gateway.rs
```diff
@@ -40,6 +40,7 @@ use starknet_api::rpc_transaction::{
 use starknet_api::transaction::fields::{Proof, ProofFacts, TransactionSignature};
 use starknet_api::transaction::TransactionHash;
 use starknet_types_core::felt::Felt;
+use tokio::sync::Semaphore;
 use tokio::task::JoinHandle;
 use tokio::time::timeout;
 use tracing::{debug, info, warn};
@@ -132,6 +133,9 @@ pub struct GenericGateway<
     mempool_client: SharedMempoolClient,
     transaction_converter: Arc<TTransactionConverter>,
     proof_archive_writer: Arc<dyn ProofArchiveWriterTrait>,
+    // Bounds the number of concurrent Sierra-to-CASM compilations triggered by declare
+    // transactions. Shared across all clones of the gateway so the limit is process-global.
+    declare_compilation_semaphore: Arc<Semaphore>,
 }
 
 impl<
@@ -153,6 +157,8 @@ impl<
         stateless_tx_validator: Arc<TStatelessValidator>,
         proof_archive_writer: Arc<dyn ProofArchiveWriterTrait>,
     ) -> Self {
+        let declare_compilation_semaphore =
+            Arc::new(Semaphore::new(config.static_config.max_concurrent_declare_compilations));
         Self {
             config: Arc::new(config.clone()),
             stateless_tx_validator,
@@ -167,6 +173,7 @@ impl<
             mempool_client,
             transaction_converter,
             proof_archive_writer,
+            declare_compilation_semaphore,
         }
     }
 }
@@ -229,8 +236,23 @@ impl<
         self.stateless_tx_validator.validate(&tx)?;
 
         let tx_signature = tx.signature().clone();
+
+        // Declare conversions overload the compiler component's CPU and memory. Reject declares if
+        // there are too many declares compiling in parallel. The permit is held only across
+        // compilation and released before stateful validation.
+        let compilation_permit = if matches!(tx, RpcTransaction::Declare(_)) {
+            Some(self.declare_compilation_semaphore.try_acquire().map_err(|_| {
+                let error = StarknetError::too_many_concurrent_declare_compilations();
+                metric_counters.record_add_tx_failure(&error);
+                error
+            })?)
+        } else {
+            None
+        };
+
         let (internal_tx, executable_tx, proof_data) =
             self.convert_rpc_tx_to_internal_and_executable_txs(tx, &tx_signature).await?;
+        drop(compilation_permit);
 
         let mut stateful_transaction_validator = self
             .stateful_tx_validator_factory
```

### crates/apollo_gateway/src/gateway_test.rs
```diff
@@ -140,6 +140,7 @@ fn mock_dependencies() -> MockDependencies {
             chain_info: ChainInfo::create_for_testing(),
             block_declare: false,
             authorized_declarer_accounts: None,
+            max_concurrent_declare_compilations: 5,
             proof_archive_writer_config: ProofArchiveWriterConfig::default(),
         },
         ..Default::default()
@@ -707,6 +708,56 @@ async fn test_block_declare_config(mut mock_dependencies: MockDependencies) {
     assert_eq!(result.unwrap_err().code, expected_code);
 }
 
+#[rstest]
+#[tokio::test(flavor = "multi_thread")]
+async fn test_declare_compilation_concurrency_limit(mut mock_dependencies: MockDependencies) {
+    mock_dependencies.config.static_config.max_concurrent_declare_compilations = 1;
+
+    // Both declares run stateless validation, so replace the fixture's single-call mock with one
+    // that accepts repeated calls.
+    let mut mock_stateless_transaction_validator = MockStatelessTransactionValidatorTrait::new();
+    mock_stateless_transaction_validator.expect_validate().returning(|_| Ok(()));
+    mock_dependencies.mock_stateless_transaction_validator = mock_stateless_transaction_validator;
+
+    // The first declare's conversion performs the Sierra-to-CASM compilation while holding the
+    // single permit. Make that conversion block so the second declare arrives while the permit is
+    // still held: `compilation_started_sender` signals that the permit is held, and the conversion
+    // then parks on `release_compilation_receiver` until the test lets it finish.
+    let (compilation_started_sender, compilation_started_receiver) =
+        tokio::sync::oneshot::channel();
+    let (release_compilation_sender, release_compilation_receiver) = std::sync::mpsc::channel();
+    mock_dependencies
+        .mock_transaction_converter
+        .expect_convert_rpc_tx_to_internal_rpc_tx()
+        .return_once(move |_| {
+            compilation_started_sender.send(()).unwrap();
+            release_compilation_receiver.recv().unwrap();
+            // Fail the conversion so the first declare short-circuits here instead of running the
+            // full admission path; its outcome is irrelevant, so the specific error is arbitrary.
+            Err(TransactionConverterError::ClassNotFound { class_hash: ClassHash::default() })
+        });
+
+    let gateway = Arc::new(mock_dependencies.gateway());
+
+    // Spawn the first declare and wait until it holds the permit inside compilation.
+    let first_declare_task = {
+        let gateway = gateway.clone();
+        tokio::spawn(async move { gateway.add_tx(declare_tx(), None).await })
+    };
+    compilation_started_receiver.await.unwrap();
+
+    // The second declare cannot acquire a permit and must be rejected immediately.
+    let second_declare_error = gateway.add_tx(declare_tx(), None).await.unwrap_err();
+    assert_eq!(
+        second_declare_error.code,
+        StarknetErrorCode::KnownErrorCode(KnownStarknetErrorCode::TransactionLimitExceeded)
+    );
+
+    // Release the first declare so its task and the blocked worker thread can wind down.
+    release_compilation_sender.send(()).unwrap();
+    let _ = first_declare_task.await;
+}
+
 #[test]
 fn test_register_metrics() {
     let recorder = PrometheusBuilder::new().build_recorder();
@@ -851,6 +902,7 @@ async fn add_tx_returns_error_when_extract_state_nonce_and_run_validations_fails
         mempool_client: Arc::new(mock_dependencies.mock_mempool_client),
         transaction_converter: Arc::new(mock_dependencies.mock_transaction_converter),
         proof_archive_writer: Arc::new(mock_dependencies.mock_proof_archive_writer),
+        declare_compilation_semaphore: Arc::new(tokio::sync::Semaphore::new(5)),
     };
 
     let result = gateway.add_tx(tx_args.get_rpc_tx(), None).await;
@@ -908,6 +960,7 @@ async fn add_tx_returns_error_when_instantiating_validator_fails(
         mempool_client: Arc::new(mock_dependencies.mock_mempool_client),
         transaction_converter: Arc::new(mock_dependencies.mock_transaction_converter),
         proof_archive_writer: Arc::new(mock_dependencies.mock_proof_archive_writer),
+        declare_compilation_semaphore: Arc::new(tokio::sync::Semaphore::new(5)),
     };
 
     let result = gateway.add_tx(tx_args.get_rpc_tx(), None).await;
```

### crates/apollo_gateway_config/src/config.rs
```diff
@@ -24,6 +24,19 @@ use crate::compiler_version::VersionId;
 
 const DEFAULT_BUCKET_NAME: &str = "proof-archive";
 
+// Compiling a declared Sierra class to CASM is CPU- and memory-intensive, and it happens during
+// transaction ingestion before the transaction's signature and balance are verified. Bound the
+// number of compilations running concurrently to protect the node from resource exhaustion.
+//
+// Derivation: compilations are served by the sierracompiler instances, so the safe per-gateway
+// bound is the sierracompiler fleet's headroom divided across the gateway fleet, i.e.
+// `per_instance_capacity * num_sierracompiler_instances / num_gateway_instances`. Observed
+// sierracompiler usage per compilation is small (memory spike ~0.75% of an instance), so a single
+// instance can absorb many concurrent compilations. 40 stays well within that envelope while still
+// capping the blast radius of a declare flood; retune via the formula above if the
+// sierracompiler/gateway instance ratio or per-instance capacity changes.
+const DEFAULT_MAX_CONCURRENT_DECLARE_COMPILATIONS: usize = 40;
+
 #[derive(Clone, Debug, Deserialize, PartialEq, Serialize, Validate)]
 pub struct GatewayStaticConfig {
     #[validate(nested)]
@@ -36,6 +49,11 @@ pub struct GatewayStaticConfig {
     pub block_declare: bool,
     #[serde(default, deserialize_with = "deserialize_comma_separated_str")]
     pub authorized_declarer_accounts: Option<Vec<ContractAddress>>,
+    /// Maximum number of Sierra-to-CASM compilations (triggered by declare transactions) allowed
+    /// to run concurrently. Declares that arrive while this limit is reached are rejected
+    /// immediately rather than queued.
+    #[validate(range(min = 1))]
+    pub max_concurrent_declare_compilations: usize,
     pub proof_archive_writer_config: ProofArchiveWriterConfig,
 }
 
@@ -51,6 +69,7 @@ impl Default for GatewayStaticConfig {
             chain_info: ChainInfo::default(),
             block_declare: false,
             authorized_declarer_accounts: None,
+            max_concurrent_declare_compilations: DEFAULT_MAX_CONCURRENT_DECLARE_COMPILATIONS,
             proof_archive_writer_config: ProofArchiveWriterConfig::default(),
         }
     }
@@ -85,6 +104,14 @@ impl SerializeConfig for GatewayStaticConfig {
              Addresses are in hex format and separated by a comma with no space.",
             ParamPrivacyInput::Public,
         ));
+        dump.extend([ser_param(
+            "max_concurrent_declare_compilations",
+            &self.max_concurrent_declare_compilations,
+            "Maximum number of Sierra-to-CASM compilations (triggered by declare transactions) \
+             allowed to run concurrently. Declares arriving while this limit is reached are \
+             rejected immediately.",
+            ParamPrivacyInput::Public,
+        )]);
         dump.extend(prepend_sub_config_name(
             self.proof_archive_writer_config.dump(),
             "proof_archive_writer_config",
```

### crates/apollo_gateway_types/src/deprecated_gateway_error.rs
```diff
@@ -91,6 +91,19 @@ impl StarknetError {
         self.code == Self::internal_error_code()
     }
 
+    /// Returned when the gateway is already running its maximum number of concurrent declare
+    /// compilations and rejects an additional declare rather than queueing it.
+    pub fn too_many_concurrent_declare_compilations() -> Self {
+        Self {
+            code: StarknetErrorCode::KnownErrorCode(
+                KnownStarknetErrorCode::TransactionLimitExceeded,
+            ),
+            message: "Too many declare transactions are being compiled concurrently. Please retry \
+                      later."
+                .to_string(),
+        }
+    }
+
     fn internal_error_code() -> StarknetErrorCode {
         StarknetErrorCode::UnknownErrorCode("StarknetErrorCode.InternalError".to_string())
     }
```

### crates/apollo_integration_tests/src/utils.rs
```diff
@@ -849,6 +849,7 @@ pub fn create_gateway_config(
             chain_info,
             block_declare: false,
             authorized_declarer_accounts: None,
+            max_concurrent_declare_compilations: 5,
             proof_archive_writer_config,
         },
         ..Default::default()
```

### crates/apollo_node/resources/config_schema.json
```diff
@@ -3049,6 +3049,11 @@
     "privacy": "Public",
     "value": 2
   },
+  "gateway_config.static_config.max_concurrent_declare_compilations": {
+    "description": "Maximum number of Sierra-to-CASM compilations (triggered by declare transactions) allowed to run concurrently. Declares arriving while this limit is reached are rejected immediately.",
+    "privacy": "Public",
+    "value": 40
+  },
   "gateway_config.static_config.proof_archive_writer_config.bucket_name": {
     "description": "The name of the bucket to write proofs to. An empty string indicates a test environment that does not connect to GCS.",
     "privacy": "Public",
```
