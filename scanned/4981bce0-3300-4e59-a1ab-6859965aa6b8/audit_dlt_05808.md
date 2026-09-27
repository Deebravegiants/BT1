# [?] Fix resource exhaustion when replaying finalized-block transactions (#12374)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-08-03
Source: https://github.com/paritytech/polkadot-sdk/commit/1407d3feba9d3fc95e20823cd0b74acbe1ca24ee
Type: security-commit

## Details
Fix resource exhaustion when replaying finalized-block transactions (#12374)

## Description

Re-applying a finalized block's transactions can reject with
`ExhaustsResources` some that
originally succeeded, so runtime APIs that replay a block
(`pallet-revive`'s `trace_block` /
`trace_tx`) drop the rejected tail transactions' traces.

**Cause.** Each extrinsic is charged its worst-case `proof_size`;
`StorageWeightReclaim` refunds
the difference down to the actual size read from a proof-size recorder.
Authoring has a recorder
registered, so the over-charge is reclaimed; the replay has none, so
reclaim is skipped,
`proof_size` accumulates past the block limit, and `CheckWeight` rejects
the tail.

**Fix.** Replay the block through the runtime API with a proof-size
recorder registered.

## Integration

- New **unsafe-gated** RPC `state_callRecorded(name, bytes, block)` on
`StateApi`, the recorded
sibling of `state_call`: runs the call re-enacting `block` at its parent
state with a
proof-size recorder, replaying `block`'s stored recording when available
(fresh recorder
otherwise). `bytes` is the opaque SCALE-encoded args — the node doesn't
inspect them, so
versioned payloads work; `block` only locates the parent state and the
recording.
- New `TracingExecuteBlock::call_recorded(block, method, call_data)`
trait method (default impl
errors, non-breaking; implemented for parachains in
`cumulus-client-service`).
- New `sc-rpc-api` state errors with stable wire codes clients match on
to fall back:
`CallRecordedUnsupported` (node has no recorder) and
`CallRecordedDenied` (unsafe RPCs
disabled), both scoped to `state_callRecorded`; the shared
`UnsafeRpcCalled` code is unchanged.
- `pallet-revive-types` trace types now deserialize the JSON they
serialize
  (`skip_serializing_if` fields also carry `#[serde(default)]`).

## Review Notes

**Why a new RPC.** eth-rpc talks to the node remotely, so its typed
`runtime_api.trace_block()`
already crosses the wire as a `state_call`, and the recorder can only be
registered node-side.
Recording on every `state_call` would add overhead to all hot paths; the
scoped method gives
per-call consent.

**Faithful under bundling.** eth-rpc passes the block's on-chain hash;
the node replays `block`'s
stored recording, matching `execute_block`. A fresh recorder would
re-count already-proven nodes,
so a bundle-tail replay could spuriously hit `ExhaustsResources`; nodes
without a recording (dev
nodes, non-bundling collators) fall back to a fresh recorder.

**Client fallback.** When a node cannot service `state_callRecorded`,
eth-rpc falls back to the
plain trace APIs (version-skew and unsafe-disabled warn; the expected
recorder-less case is
debug) and marks the result degraded: `debug_traceBlock*` returns
dropped transactions as
geth-style `{txHash, error}` entries, `debug_traceTransaction` returns
trace-unavailable rather
than "not found".

**Tests.** An Asset Hub Westend integration test reproduces the bug and
confirms the fix through
the versioned trace APIs; a new `repeated_storage_read` fixture creates
the `proof_size`
over-charge (a distinct cold storage key per round).
`pallet-revive-eth-rpc` unit tests cover the
fallback classification; `sc-rpc` tests pin the unsafe-denied wire
contract.

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>

### Cargo.lock
```diff
@@ -1844,6 +1844,7 @@ dependencies = [
  "sp-storage 19.0.0",
  "sp-tracing 16.0.0",
  "sp-transaction-pool",
+ "sp-trie 29.0.0",
  "sp-version 29.0.0",
  "staging-parachain-info",
  "staging-xcm",
@@ -4992,6 +4993,7 @@ dependencies = [
  "sp-crypto-ec-utils",
  "sp-io 30.0.0",
  "sp-runtime 31.0.1",
+ "sp-state-machine 0.35.0",
  "sp-transaction-pool",
  "sp-trie 29.0.0",
 ]
```

### cumulus/client/service/Cargo.toml
```diff
@@ -37,6 +37,7 @@ sp-core = { workspace = true, default-features = true }
 sp-crypto-ec-utils = { workspace = true, default-features = true, features = ["rfc163"] }
 sp-io = { workspace = true, default-features = true }
 sp-runtime = { workspace = true, default-features = true }
+sp-state-machine = { workspace = true, default-features = true }
 sp-transaction-pool = { workspace = true, default-features = true }
 sp-trie = { workspace = true, default-features = true }
 
```

### cumulus/client/service/src/lib.rs
```diff
@@ -32,8 +32,8 @@ use futures::{channel::mpsc, StreamExt};
 use polkadot_primitives::{CandidateEvent, CollatorPair, OccupiedCoreAssumption};
 use prometheus::{Histogram, HistogramOpts, Registry};
 use sc_client_api::{
-	AuxStore, Backend as BackendT, BlockBackend, BlockchainEvents, Finalizer, ProofProvider,
-	UsageProvider,
+	AuxStore, Backend as BackendT, BlockBackend, BlockchainEvents, CallExecutor, ExecutorProvider,
+	Finalizer, ProofProvider, UsageProvider,
 };
 use sc_consensus::{
 	import_queue::{ImportQueue, ImportQueueService},
@@ -53,13 +53,15 @@ use sc_tracing::block::TracingExecuteBlock;
 use sc_utils::mpsc::TracingUnboundedSender;
 use sp_api::{ApiExt, Core, ProofRecorder, ProvideRuntimeApi};
 use sp_blockchain::{HeaderBackend, HeaderMetadata};
-use sp_core::Decode;
+use sp_core::{traits::CallContext, Decode};
 use sp_runtime::{
-	traits::{Block as BlockT, BlockIdTo, Header},
+	traits::{Block as BlockT, BlockIdTo, HashingFor, Header},
 	SaturatedConversion, Saturating,
 };
+use sp_state_machine::OverlayedChanges;
 use sp_trie::proof_size_extension::{ProofSizeExt, ReplayProofSizeProvider};
 use std::{
+	cell::RefCell,
 	sync::Arc,
 	time::{Duration, Instant},
 };
@@ -621,20 +623,40 @@ impl<Client> ParachainTracingExecuteBlock<Client> {
 	}
 }
 
+/// Proof-size extension for re-enacting `hash`: replay its stored recording if present, else
+/// measure with `recorder`.
+fn recorded_proof_size_ext<Block, Client>(
+	client: &Client,
+	hash: Block::Hash,
+	recorder: &ProofRecorder<Block>,
+) -> sp_blockchain::Result<ProofSizeExt>
+where
+	Block: BlockT,
+	Client: AuxStore,
+{
+	Ok(load_proof_size_recording(client, hash)?.map_or_else(
+		|| ProofSizeExt::new(recorder.clone()),
+		|recordings| ProofSizeExt::new(ReplayProofSizeProvider::from(recordings)),
+	))
+}
+
 impl<Block, Client> TracingExecuteBlock<Block> for ParachainTracingExecuteBlock<Client>
 where
 	Block: BlockT,
-	Client: ProvideRuntimeApi<Block> + AuxStore + Send + Sync,
+	Client: ProvideRuntimeApi<Block>
+		+ ExecutorProvider<Block>
+		+ HeaderBackend<Block>
+		+ AuxStore
+		+ Send
+		+ Sync,
 	Client::Api: Core<Block>,
 {
 	fn execute_block(&self, orig_hash: Block::Hash, block: Block) -> sp_blockchain::Result<()> {
 		let mut runtime_api = self.client.runtime_api();
 		let storage_proof_recorder = ProofRecorder::<Block>::default();
 
-		let proof_size_ext = load_proof_size_recording(&*self.client, orig_hash)?.map_or_else(
-			|| ProofSizeExt::new(storage_proof_recorder.clone()),
-			|recordings| ProofSizeExt::new(ReplayProofSizeProvider::from(recordings)),
-		);
+		let proof_size_ext =
+			recorded_proof_size_ext::<Block, _>(&*self.client, orig_hash, &storage_proof_recorder)?;
 		runtime_api.register_extension(proof_size_ext);
 
 		runtime_api.record_proof_with_recorder(storage_proof_recorder);
@@ -643,4 +665,37 @@ where
 			.execute_block(*block.header().parent_hash(), block.into())
 			.map_err(Into::into)
 	}
+
+	fn call_recorded(
+		&self,
+		block: Block::Hash,
+		method: &str,
+		call_data: &[u8],
+	) -> sp_blockchain::Result<Vec<u8>> {
+		let header = self
+			.client
+			.header(block)?
+			.ok_or_else(|| sp_blockchain::Error::UnknownBlock(format!("{block:?}")))?;
+		let at = *header.parent_hash();
+		let number = self
+			.client
+			.number(at)?
+			.ok_or_else(|| sp_blockchain::Error::UnknownBlock(format!("{at:?}")))?;
+		let storage_proof_recorder = ProofRecorder::<Block>::default();
+
+		let proof_size_ext =
+			recorded_proof_size_ext::<Block, _>(&*self.client, block, &storage_proof_recorder)?;
+		let mut extensions = self.client.execution_extensions().extensions(at, number);
+		extensions.register(proof_size_ext);
+
+		self.client.executor().contextual_call(
+			at,
+			method,
+			call_data,
+			&RefCell::new(OverlayedChanges::<HashingFor<Block>>::default()),
+			&Some(storage_proof_recorder),
+			CallContext::Offchain,
+			&RefCell::new(extensions),
+		)
+	}
 }
```

### cumulus/parachains/runtimes/assets/asset-hub-westend/Cargo.toml
```diff
@@ -162,6 +162,7 @@ pallet-revive-fixtures = { workspace = true, default-features = true }
 parachains-runtimes-test-utils = { workspace = true, default-features = true }
 remote-externalities = { workspace = true, default-features = true }
 sp-tracing = { workspace = true, default-features = true }
+sp-trie = { workspace = true, default-features = true }
 tokio = { workspace = true, features = ["macros"] }
 westend-runtime = { workspace = true, default-features = true }
 
```

### cumulus/parachains/runtimes/assets/asset-hub-westend/tests/tests.rs
```diff
@@ -140,6 +140,15 @@ fn bare_instantiate(origin: &AccountId, code: Vec<u8>) -> BareInstantiateBuilder
 }
 
 fn construct_extrinsic(sender: Sr25519Keyring, call: RuntimeCall) -> UncheckedExtrinsic {
+	let nonce = frame_system::Pallet::<Runtime>::account(&AccountId::from(sender.public())).nonce;
+	construct_extrinsic_with_nonce(sender, call, nonce)
+}
+
+fn construct_extrinsic_with_nonce(
+	sender: Sr25519Keyring,
+	call: RuntimeCall,
+	nonce: u32,
+) -> UncheckedExtrinsic {
 	let account_id = AccountId::from(sender.public());
 	let tx_ext: TxExtension = (
 		frame_system::AuthorizeCall::<Runtime>::new(),
@@ -148,9 +157,7 @@ fn construct_extrinsic(sender: Sr25519Keyring, call: RuntimeCall) -> UncheckedEx
 		frame_system::CheckTxVersion::<Runtime>::new(),
 		frame_system::CheckGenesis::<Runtime>::new(),
 		frame_system::CheckEra::<Runtime>::from(Era::immortal()),
-		frame_system::CheckNonce::<Runtime>::from(
-			frame_system::Pallet::<Runtime>::account(&account_id).nonce,
-		),
+		frame_system::CheckNonce::<Runtime>::from(nonce),
 		frame_system::CheckWeight::<Runtime>::new(),
 		pallet_pgas_allowance::ChargePGAS::<
 			Runtime,
@@ -2858,3 +2865,150 @@ mod pgas_allowance {
 		});
 	}
 }
+
+// Regression tests for the revive trace-replay proof-size reclaim fix: replaying a block via
+// `trace_block`/`trace_tx` registers a proof recorder so the accumulated worst-case `proof_size` is
+// reclaimed instead of tripping `ExhaustsResources` and dropping the tail's traces.
+mod revive_trace_reclaim {
+	use super::*;
+	use frame_support::dispatch::DispatchClass;
+	use frame_system::pallet_prelude::HeaderFor;
+	use pallet_revive::{
+		pallet_revive_types::runtime_api::{
+			TraceBlockInputPayloadV1, TraceBlockVersionedInputPayload,
+			TraceBlockVersionedOutputPayload, TraceTxInputPayloadV1, TraceTxVersionedInputPayload,
+			TraceTxVersionedOutputPayload, TraceV1, TracerTypeV1,
+		},
+		runtime_decl_for_revive_api::ReviveApiV2,
+	};
+	use pallet_revive_fixtures::compile_module;
+	use sp_core::H160;
+	use sp_runtime::{traits::Header as _, BuildStorage};
+	use sp_trie::{proof_size_extension::ProofSizeExt, ProofSizeProvider};
+
+	const SENDER: Sr25519Keyring = Sr25519Keyring::Bob;
+	// Enough reads that each call meters ~the per-call proof_size limit.
+	const ROUNDS: u32 = 100_000;
+
+	// Reports a constant size, so the per-extrinsic proof diff is zero: models a recorder being
+	// present, letting reclaim refund the full over-charge.
+	struct ConstantRecorder;
+	impl ProofSizeProvider for ConstantRecorder {
+		fn estimate_encoded_size(&self) -> usize {
+			0
+		}
+	}
+
+	fn setup_ext() -> sp_io::TestExternalities {
+		let mut t = frame_system::GenesisConfig::<Runtime>::default().build_storage().unwrap();
+		pallet_balances::GenesisConfig::<Runtime> {
+			balances: vec![
+				(SENDER.to_account_id(), 1_000_000_000 * UNITS),
+				(pallet_revive::Pallet::<Runtime>::account_id(), 1_000_000 * UNITS),
+			],
+			..Default::default()
+		}
+		.assimilate_storage(&mut t)
+		.unwrap();
+		let mut ext: sp_io::TestExternalities = t.into();
+		ext.execute_with(|| System::set_block_number(1));
+		ext
+	}
+
+	fn signed_revive_call(addr: H160, nonce: u32, weight_limit: Weight) -> UncheckedExtrinsic {
+		let call = RuntimeCall::Revive(pallet_revive::Call::call {
+			dest: addr,
+			value: 0,
+			weight_limit,
+			storage_deposit_limit: 0,
+			data: ROUNDS.to_le_bytes().to_vec(),
+		});
+		construct_extrinsic_with_nonce(SENDER, call, nonce)
+	}
+
+	// Deploy the repeated-read contract, build a block of two calls, and replay it through `f`
+	// (`trace_block` or `trace_tx`), registering the proof recorder when `with_recorder`.
+	fn with_block<R>(with_recorder: bool, f: impl FnOnce(Block) -> R) -> R {
+		let code = compile_module("repeated_storage_read").unwrap().0;
+		let mut ext = setup_ext();
+		if with_recorder {
+			ext.register_extension(ProofSizeExt::new(ConstantRecorder));
+		}
+		ext.execute_with(|| {
+			let budget = <Runtime as frame_system::Config>::BlockWeights::get()
+				.get(DispatchClass::Normal)
+				.max_total
+				.expect("normal class has a max_total; qed")
+				.proof_size();
+			// ~60% of the budget each, so the two calls only both fit when reclaim is in effect.
+			let weight_limit = Weight::from_parts(500_000_000_000, budget * 3 / 5);
+
+			let contract = bare_instantiate(&SENDER.to_account_id(), code)
+				.transaction_limits(TransactionLimits::WeightAndDeposit {
+					weight_limit: Weight::from_parts(500_000_000_000, 10 * 1024 * 1024),
+					deposit_limit: Balance::MAX,
+				})
+				.build_and_unwrap_contract();
+
+			// deploying bumped the sender's nonce
+			let base = frame_system::Pallet::<Runtime>::account(&SENDER.to_account_id()).nonce;
+			let extrinsics = vec![
+				signed_revive_call(contract.addr, base, weight_limit),
+				signed_revive_call(contract.addr, base + 1, weight_limit),
+			];
+			let header = <HeaderFor<Runtime>>::new(
+				frame_system::Pallet::<Runtime>::block_number() + 1,
+				Default::default(),
+				Default::default(),
+				Default::default(),
+				Default::default(),
+			);
+
+			f(Block { header, extrinsics })
+		})
+	}
+
+	fn tracer() -> TracerTypeV1 {
+		TracerTypeV1::CallTracer(None)
+	}
+
+	fn trace_block(block: Block) -> usize {
+		let input = TraceBlockVersionedInputPayload::V1(TraceBlockInputPayloadV1 {
+			block,
+			config: tracer(),
+		});
+		let TraceBlockVersionedOutputPayload::V1(output) = Runtime::trace_block_versioned(input)
+		else {
+			panic!("v1 input must produce v1 output");
+		};
+		output.traces.len()
+	}
+
+	fn trace_tx(block: Block, tx_index: u32) -> Option<TraceV1> {
+		let input = TraceTxVersionedInputPayload::V1(TraceTxInputPayloadV1 {
+			block,
+			tx_index,
+			config: tracer(),
+		});
+		let TraceTxVersionedOutputPayload::V1(output) = Runtime::trace_tx_versioned(input) else {
+			panic!("v1 input must produce v1 output");
+		};
+		output.trace
+	}
+
+	#[test]
+	fn trace_block_drops_tail_trace_without_proof_recorder() {
+		let with_recorder = with_block(true, trace_block);
+		let without = with_block(false, trace_block);
+		assert_eq!(with_recorder, 2, "both calls traced with a recorder");
+		assert!(without < with_recorder, "tail trace dropped without a recorder");
+	}
+
+	#[test]
+	fn trace_tx_drops_tail_trace_without_proof_recorder() {
+		let with_recorder = with_block(true, |b| trace_tx(b, 1));
+		let without = with_block(false, |b| trace_tx(b, 1));
+		assert!(with_recorder.is_some(), "tail tx traced with a recorder");
+		assert!(without.is_none(), "tail tx trace dropped without a recorder");
+	}
+}
```

### prdoc/pr_12374.prdoc
```diff
@@ -0,0 +1,75 @@
+title: Fix resource exhaustion when replaying finalized-block transactions
+doc:
+- audience:
+  - Node Dev
+  - Runtime Dev
+  description: |-
+    # Description
+
+    Re-applying a finalized block's transactions can reject with `ExhaustsResources` some that
+    originally succeeded, so runtime APIs that replay a block (`pallet-revive`'s `trace_block` /
+    `trace_tx`) drop the rejected tail transactions' traces.
+
+    **Cause.** Each extrinsic is charged its worst-case `proof_size`; `StorageWeightReclaim` refunds
+    the difference down to the actual size read from a proof-size recorder. Authoring has a recorder
+    registered, so the over-charge is reclaimed; the replay has none, so reclaim is skipped,
+    `proof_size` accumulates past the block limit, and `CheckWeight` rejects the tail.
+
+    **Fix.** Replay the block through the runtime API with a proof-size recorder registered.
+
+    # Integration
+
+    - New **unsafe-gated** RPC `state_callRecorded(name, bytes, block)` on `StateApi`, the recorded
+      sibling of `state_call`: runs the call re-enacting `block` at its parent state with a
+      proof-size recorder, replaying `block`'s stored recording when available (fresh recorder
+      otherwise). `bytes` is the opaque SCALE-encoded args — the node doesn't inspect them, so
+      versioned payloads work; `block` only locates the parent state and the recording.
+    - New `TracingExecuteBlock::call_recorded(block, method, call_data)` trait method (default impl
+      errors, non-breaking; implemented for parachains in `cumulus-client-service`).
+    - New `sc-rpc-api` state errors with stable wire codes clients match on to fall back:
+      `CallRecordedUnsupported` (node has no recorder) and `CallRecordedDenied` (unsafe RPCs
+      disabled), both scoped to `state_callRecorded`; the shared `UnsafeRpcCalled` code is unchanged.
+    - `pallet-revive-types` trace types now deserialize the JSON they serialize
+      (`skip_serializing_if` fields also carry `#[serde(default)]`).
+
+    # Review Notes
+
+    **Why a new RPC.** eth-rpc talks to the node remotely, so its typed `runtime_api.trace_block()`
+    already crosses the wire as a `state_call`, and the recorder can only be registered node-side.
+    Recording on every `state_call` would add overhead to all hot paths; the scoped method gives
+    per-call consent.
+
+    **Faithful under bundling.** eth-rpc passes the block's on-chain hash; the node replays `block`'s
+    stored recording, matching `execute_block`. A fresh recorder would re-count already-proven nodes,
+    so a bundle-tail replay could spuriously hit `ExhaustsResources`; nodes without a recording (dev
+    nodes, non-bundling collators) fall back to a fresh recorder.
+
+    **Client fallback.** When a node cannot service `state_callRecorded`, eth-rpc falls back to the
+    plain trace APIs (version-skew and unsafe-disabled warn; the expected recorder-less case is
+    debug) and marks the result degraded: `debug_traceBlock*` returns dropped transactions as
+    geth-style `{txHash, error}` entries, `debug_traceTransaction` returns trace-unavailable rather
+    than "not found".
+
+    **Tests.** An Asset Hub Westend integration test reproduces the bug and confirms the fix through
+    the versioned trace APIs; a new `repeated_storage_read` fixture creates the `proof_size`
+    over-charge (a distinct cold storage key per round). `pallet-revive-eth-rpc` unit tests cover the
+    fallback classification; `sc-rpc` tests pin the unsafe-denied wire contract.
+crates:
+- name: sc-tracing
+  bump: minor
+- name: cumulus-client-service
+  bump: minor
+- name: sc-rpc-api
+  bump: major
+- name: sc-rpc
+  bump: major
+- name: pallet-revive-eth-rpc
+  bump: patch
+- name: pallet-revive
+  bump: patch
+- name: asset-hub-westend-runtime
+  bump: patch
+- name: pallet-revive-fixtures
+  bump: patch
+- name: pallet-revive-types
+  bump: patch
```

### substrate/client/rpc-api/src/state/error.rs
```diff
@@ -50,11 +50,25 @@ pub enum Error {
 	/// Call to an unsafe RPC was denied.
 	#[error(transparent)]
 	UnsafeRpcCalled(#[from] crate::policy::UnsafeRpcError),
+	/// The node registers no proof-size recorder and so cannot service a recorded runtime call.
+	#[error("Recorded runtime calls are not supported by this node")]
+	CallRecordedUnsupported,
+	/// A recorded runtime call was denied because unsafe RPC methods are disabled on this node.
+	#[error("Recorded runtime calls are unsafe and disabled on this node")]
+	CallRecordedDenied,
 }
 
 /// Base code for all state errors.
 const BASE_ERROR: i32 = crate::error::base::STATE;
 
+/// Error code for [`Error::CallRecordedUnsupported`]. Stable wire contract matched by clients to
+/// decide fallback; do not renumber.
+pub const CALL_RECORDED_UNSUPPORTED_ERROR_CODE: i32 = BASE_ERROR + 4;
+
+/// Error code for [`Error::CallRecordedDenied`]. Stable wire contract matched by clients to decide
+/// fallback; do not renumber.
+pub const CALL_RECORDED_DENIED_ERROR_CODE: i32 = BASE_ERROR + 5;
+
 impl From<Error> for ErrorObjectOwned {
 	fn from(e: Error) -> ErrorObjectOwned {
 		match e {
@@ -64,6 +78,12 @@ impl From<Error> for ErrorObjectOwned {
 			Error::InvalidCount { .. } => {
 				ErrorObject::owned(BASE_ERROR + 2, e.to_string(), None::<()>)
 			},
+			Error::CallRecordedUnsupported => {
+				ErrorObject::owned(CALL_RECORDED_UNSUPPORTED_ERROR_CODE, e.to_string(), None::<()>)
+			},
+			Error::CallRecordedDenied => {
+				ErrorObject::owned(CALL_RECORDED_DENIED_ERROR_CODE, e.to_string(), None::<()>)
+			},
 			e => ErrorObject::owned(BASE_ERROR + 3, e.to_string(), None::<()>),
 		}
 	}
```

### substrate/client/rpc-api/src/state/mod.rs
```diff
@@ -300,4 +300,15 @@ pub trait StateApi<Hash> {
 		storage_keys: Option<String>,
 		methods: Option<String>,
 	) -> Result<sp_rpc::tracing::TraceBlockResponse, Error>;
+
+	/// Recorded sibling of [`Self::call`]: runs `name` re-enacting `block` at its parent state
+	/// with a proof-size recorder, replaying `block`'s stored recording when available. `bytes` is
+	/// the complete SCALE-encoded args, opaque to the node as in [`Self::call`]. Only nodes with a
+	/// proof-recording hook (parachains) can service it; others report
+	/// [`Error::CallRecordedUnsupported`].
+	///
+	/// **Unsafe** (a call replays up to a whole block); denied calls report
+	/// [`Error::CallRecordedDenied`].
+	#[method(name = "state_callRecorded", blocking, with_extensions)]
+	fn call_recorded(&self, name: String, bytes: Bytes, block: Hash) -> Result<Bytes, Error>;
 }
```

### substrate/client/rpc/src/state/mod.rs
```diff
@@ -149,6 +149,15 @@ where
 		methods: Option<String>,
 	) -> Result<sp_rpc::tracing::TraceBlockResponse, Error>;
 
+	/// Run `method` re-enacting `block` at its parent state with a proof-size recorder, replaying
+	/// `block`'s stored recording when available.
+	fn call_recorded(
+		&self,
+		block: Block::Hash,
+		method: String,
+		call_data: Bytes,
+	) -> Result<Bytes, Error>;
+
 	/// New runtime version subscription
 	fn subscribe_runtime_version(&self, pending: PendingSubscriptionSink);
 
@@ -162,6 +171,10 @@ where
 }
 
 /// Create new state API that works on full node.
+///
+/// `execute_block` is the optional proof-size-recording block executor (`Some` on parachains).
+/// When `None`, `state_traceBlock` runs without recording and `state_callRecorded` reports
+/// `CallRecordedUnsupported`.
 pub fn new_full<BE, Block: BlockT, Client>(
 	client: Arc<Client>,
 	executor: SubscriptionTaskExecutor,
@@ -331,6 +344,17 @@ where
 			.map_err(Into::into)
 	}
 
+	fn call_recorded(
+		&self,
+		ext: &Extensions,
+		method: String,
+		data: Bytes,
+		block: Block::Hash,
+	) -> Result<Bytes, Error> {
+		check_if_safe(ext).map_err(|_| Error::CallRecordedDenied)?;
+		self.backend.call_recorded(block, method, data).map_err(Into::into)
+	}
+
 	fn subscribe_runtime_version(&self, pending: PendingSubscriptionSink) {
 		self.backend.subscribe_runtime_version(pending)
 	}
```

### substrate/client/rpc/src/state/state_full.rs
```diff
@@ -66,6 +66,7 @@ struct QueryStorageRange<Block: BlockT> {
 pub struct FullState<BE, Block: BlockT, Client> {
 	client: Arc<Client>,
 	executor: SubscriptionTaskExecutor,
+	/// Proof-size-recording block executor; `None` on nodes that do not record proof size.
 	execute_block: Option<Arc<dyn TracingExecuteBlock<Block>>>,
 	_phantom: PhantomData<BE>,
 }
@@ -495,6 +496,28 @@ where
 		.trace_block()
 		.map_err(|e| invalid_block::<Block>(block, None, e.to_string()))
 	}
+
+	fn call_recorded(
+		&self,
+		block: Block::Hash,
+		method: String,
+		call_data: Bytes,
+	) -> std::result::Result<Bytes, Error> {
+		let execute_block = self.execute_block.as_ref().ok_or(Error::CallRecordedUnsupported)?;
+		execute_block
+			.call_recorded(block, &method, &call_data.0)
+			.map(Into::into)
+			.map_err(|e| match e {
+				sp_blockchain::Error::Application(ref inner)
+					if inner
+						.downcast_ref::<sc_tracing::block::CallRecordedUnsupported>()
+						.is_some() =>
+				{
+					Error::CallRecordedUnsupported
+				},
+				e => Error::Client(Box::new(e)),
+			})
+	}
 }
 
 impl<BE, Block, Client> ChildStateBackend<Block, Client> for FullState<BE, Block, Client>
```

### substrate/client/rpc/src/state/tests.rs
```diff
@@ -18,7 +18,7 @@
 
 use self::error::Error;
 use super::*;
-use crate::testing::{allow_unsafe, test_executor, timeout_secs};
+use crate::testing::{allow_unsafe, deny_unsafe, test_executor, timeout_secs};
 use assert_matches::assert_matches;
 use futures::executor;
 use jsonrpsee::{core::EmptyServerParams as EmptyParams, MethodsError as RpcError};
@@ -207,6 +207,64 @@ async fn should_call_contract() {
 	)
 }
 
+#[tokio::test]
+async fn call_recorded_is_unsupported_without_recorder() {
+	let client = Arc::new(substrate_test_runtime_client::new());
+	let block_hash = client.chain_info().best_hash;
+	let (state, _child) = new_full(client, test_executor(), None);
+
+	let err = state
+		.call_recorded(&allow_unsafe(), "Core_version".into(), Bytes(vec![]), block_hash)
+		.unwrap_err();
+
+	assert_matches!(err, Error::CallRecordedUnsupported);
+	let object = jsonrpsee::types::ErrorObjectOwned::from(err);
+	assert_eq!(object.code(), error::CALL_RECORDED_UNSUPPORTED_ERROR_CODE);
+}
+
+#[tokio::test]
+async fn call_recorded_denied_when_unsafe() {
+	let client = Arc::new(substrate_test_runtime_client::new());
+	let block_hash = client.chain_info().best_hash;
+	let (state, _child) = new_full(client, test_executor(), None);
+
+	let err = state
+		.call_recorded(&deny_unsafe(), "Core_version".into(), Bytes(vec![]), block_hash)
+		.unwrap_err();
+
+	assert_matches!(err, Error::CallRecordedDenied);
+	let object = jsonrpsee::types::ErrorObjectOwned::from(err);
+	assert_eq!(object.code(), error::CALL_RECORDED_DENIED_ERROR_CODE);
+}
+
+#[tokio::test]
+async fn call_recorded_reports_dispatch_failures_as_client_errors() {
+	struct FailingExecuteBlock;
+	impl<Block: BlockT> sc_tracing::block::TracingExecuteBlock<Block> for FailingExecuteBlock {
+		fn execute_block(&self, _: Block::Hash, _: Block) -> sp_blockchain::Result<()> {
+			unreachable!("not exercised by this test")
+		}
+
+		fn call_recorded(
+			&self,
+			_: Block::Hash,
+			_: &str,
+			_: &[u8],
+		) -> sp_blockchain::Result<Vec<u8>> {
+			Err(sp_blockchain::Error::Backend("dispatch failed".into()))
+		}
+	}
+
+	let client = Arc::new(substrate_test_runtime_client::new());
+	let block_hash = client.chain_info().best_hash;
+	let (state, _child) = new_full(client, test_executor(), Some(Arc::new(FailingExecuteBlock)));
+
+	assert_matches!(
+		state.call_recorded(&allow_unsafe(), "Core_version".into(), Bytes(vec![]), block_hash),
+		Err(Error::Client(e)) if e.to_string().contains("dispatch failed")
+	);
+}
+
 #[tokio::test]
 async fn should_notify_about_storage_changes() {
 	let mut sub = {
```

### substrate/client/tracing/src/block/mod.rs
```diff
@@ -63,6 +63,20 @@ pub trait TracingExecuteBlock<Block: BlockT>: Send + Sync {
 	/// The execution should be done sync on the same thread, because the caller will register
 	/// special tracing collectors.
 	fn execute_block(&self, orig_hash: Block::Hash, block: Block) -> sp_blockchain::Result<()>;
+
+	/// Run `method` re-enacting `block` at its parent state, with a proof-size recorder registered
+	/// and `block`'s stored recording replayed when available; returns the SCALE-encoded result.
+	/// `call_data` is the complete SCALE-encoded argument list, passed through verbatim.
+	///
+	/// The default implementation errors: nodes that do not record proof size do not need it.
+	fn call_recorded(
+		&self,
+		_block: Block::Hash,
+		_method: &str,
+		_call_data: &[u8],
+	) -> sp_blockchain::Result<Vec<u8>> {
+		Err(sp_blockchain::Error::Application(Box::new(CallRecordedUnsupported)))
+	}
 }
 
 /// Default implementation of [`ExecuteBlock`].
@@ -96,6 +110,12 @@ where
 /// Tracing Block Result type alias
 pub type TraceBlockResult<T> = Result<T, Error>;
 
+/// Typed marker returned by the default [`TracingExecuteBlock::call_recorded`], letting callers
+/// recognise "this node has no proof-recording hook" by downcast and map it to their own error.
+#[derive(Debug, thiserror::Error)]
+#[error("Recorded runtime calls are not supported by this node")]
+pub struct CallRecordedUnsupported;
+
 /// Tracing Block error
 #[derive(Debug, thiserror::Error)]
 #[allow(missing_docs)]
@@ -244,12 +264,7 @@ where
 		}
 	}
 
-	/// Execute block, record all spans and events belonging to `Self::targets`
-	/// and filter out events which do not have keys starting with one of the
-	/// prefixes in `Self::storage_keys`.
-	pub fn trace_block(&self) -> TraceBlockResult<TraceBlockResponse> {
-		tracing::debug!(target: "state_tracing", "Tracing block: {}", self.block);
-		// Prepare the block
+	fn prepared_block(&self) -> TraceBlockResult<Block> {
 		let mut header = self
 			.client
 			.header(self.block)
@@ -261,11 +276,18 @@ where
 			.map_err(Error::InvalidBlockId)?
 			.ok_or_else(|| Error::MissingBlockComponent("Extrinsics not found".to_string()))?;
 		tracing::debug!(target: "state_tracing", "Found {} extrinsics", extrinsics.len());
-		let parent_hash = *header.parent_hash();
-		// Remove all `Seal`s as they are added by the consensus engines after building the block.
-		// On import they are normally removed by the consensus engine.
+
 		header.digest_mut().logs.retain(|d| d.as_seal().is_none());
-		let block = Block::new(header, extrinsics);
+		Ok(Block::new(header, extrinsics))
+	}
+
+	/// Execute block, record all spans and events belonging to `Self::targets`
+	/// and filter out events which do not have keys starting with one of the
+	/// prefixes in `Self::storage_keys`.
+	pub fn trace_block(&self) -> TraceBlockResult<TraceBlockResponse> {
+		tracing::debug!(target: "state_tracing", "Tracing block: {}", self.block);
+		let block = self.prepared_block()?;
+		let parent_hash = *block.header().parent_hash();
 
 		let targets = if let Some(t) = &self.targets { t } else { DEFAULT_TARGETS };
 		let block_subscriber = BlockSubscriber::new(targets);
```
