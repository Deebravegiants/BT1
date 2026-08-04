### Title
`submit` charges a fixed benchmarked weight regardless of attacker-controlled proof/vector sizes, allowing undercharged verification work - (File: bridges/snowbridge/pallets/inbound-queue/src/lib.rs)

### Summary
The `submit` extrinsic is weighted with a single constant, `T::WeightInfo::submit()`, that does not scale with the size of any attacker-supplied field inside `EventProof`. Because `Proof.receipt_proof: Vec<Vec<u8>>`, `ExecutionProof.execution_branch: Vec<H256>`, `AncestryProof.header_branch: Vec<H256>`, and `Log.topics/data` are unbounded (no `BoundedVec`/`MaxEncodedLen` enforcement specific to this pallet), an unprivileged signed account can submit a maximally-sized, garbage-filled proof that is decoded and partially processed by the verifier before it ultimately fails, at a cost far above the fixed charged weight.

### Finding Description
`submit` is declared with a fixed weight: [1](#0-0) 

This weight comes from a constant benchmark value (`Weight::from_parts(70_000_000, 0)` in the fallback, or similarly fixed values in the generated runtime weights), with no dependency on proof size, message count, or vector lengths: [2](#0-1) [3](#0-2) 

Contrast this with the bridge messages pallet's `receive_messages_proof`, which explicitly derives weight from `proof.size()`, `messages_count`, and `dispatch_weight` at dispatch time: [4](#0-3) 

In the Snowbridge inbound-queue's own `Proof`/`ExecutionProof`/`Log` types, none of the vector fields are size-bounded: [5](#0-4) [6](#0-5) 

The pallet's own `MaxMessageSize` config is explicitly documented as only used for fee *estimation*, not as an enforced bound on the actual submitted event: [7](#0-6) 

`T::Verifier::verify` then does real computational work over these unbounded fields before any rejection: it copies every `receipt_proof` node into a new `Bytes` vector, runs RLP/Merkle-Patricia-trie verification over it, and separately verifies the (attacker-supplied-length) `execution_branch`/`ancestry_proof.header_branch` merkle branches: [8](#0-7) [9](#0-8) 

Since the only real ceiling on these Vec sizes is the runtime's generic extrinsic/block length limit (megabytes), not a pallet-specific bound tied into the weight formula, an attacker can submit near-maximal garbage vectors that get fully SCALE-decoded and partially traversed by the verifier (RLP decode attempts, hash computations, copies) before failing with `InvalidProof`/`InvalidExecutionHeaderProof`/etc. All of this happens under the flat weight charged for `submit()`, which was benchmarked against small, realistic fixture proofs (`Measured: 309/586/657 bytes`), not against a maximal attacker-crafted payload.

Note that crafting a *cryptographically valid* deep/wide receipt-trie proof against the real receipts_root is infeasible without breaking hash preimage resistance, so the most damaging vector is the branch/vector fields that are checked by simple, length-driven loops (`ancestry_proof.header_branch`, `execution_branch`, and the raw byte-copy/RLP-decode-attempt phase over `receipt_proof`) — these can be padded arbitrarily and will be processed (decoded/copied/looped) in full before failing, independent of whether the padding is "valid."

### Impact Explanation
Because the weight charged for `submit` is a constant that ignores attacker-controlled vector sizes, a malicious signed account can repeatedly submit near-max-size garbage `EventProof`s that consume CPU time disproportionate to the weight budget consumed in the block. This can degrade block production performance/throughput on the bridge-hub parachain (computation DoS on the inbound-queue path), which maps to the scoped "Bridge halt, chain halt" impact category, without requiring any privileged access — only a signed account able to call the public `submit` extrinsic.

### Likelihood Explanation
This is straightforwardly and repeatably reachable: any signed account can call `submit` with a crafted `EventProof` at any time (no origin filter beyond `ensure_signed`, no rate limiting other than normal transaction fees/nonce). The only friction is the transaction fee paid, but the fee model (`calculate_delivery_cost`) is based on the fixed `WeightInfo::submit()` value plus a length-fee term configured via `T::LengthToFee`, not on the actual computational cost of verification triggered by the padded proof fields — so the fee does not necessarily track the true worst-case execution cost, especially for the `ref_time` weight metric used for block-filling, which is what is under threat here (not just the fee amount).

### Recommendation
- Bound the proof-related vector fields (`Proof.receipt_proof`, `ExecutionProof.execution_branch`, `AncestryProof.header_branch`, and `Log.topics`/`Log.data`) with `BoundedVec<_, MaxX>` types tied into `Config`, similar to how `polkadot/node/primitives` bounds its own `Proof` type with `MERKLE_PROOF_MAX_DEPTH`/`MERKLE_NODE_MAX_SIZE`.
- Make `submit`'s declared weight a function of the actual size/length of the supplied `EventProof` (similar to `receive_messages_proof_weight` in `bridges/modules/messages`), so the charged weight scales with proof size rather than being a single constant benchmarked against small fixtures.
- Enforce `MaxMessageSize` (or an equivalent) as an actual runtime check on the incoming `event: EventProof` length before any decoding/verification work is performed, rejecting oversized submissions early with `ensure!`.

### Proof of Concept
Rust unit test plan (in `bridges/snowbridge/pallets/inbound-queue/src/test.rs` or `ethereum-client`'s test module):
1. Build a valid base fixture (`mock_event_log()`, `mock_execution_proof()`).
2. Construct a "worst-case" `EventProof` where `proof.receipt_proof` contains many large `Vec<u8>` entries (e.g., up to the runtime's `BlockLength`/`MaximumExtrinsicWeight` allowance) and `execution_proof.ancestry_proof.header_branch`/`execution_branch` are padded with thousands of `H256` entries.
3. Call `InboundQueue::submit(origin, event)` inside `execute_with` while wrapping the call with a wall-clock/weight-metering harness (e.g., using `frame_support::weights::WeightMeter` or measuring `Instant::now()` around the call in a `#[test]`).
4. Assert that:
   - The call still returns `Err(Error::Verification(...))` (no state corruption), confirming there is no correctness bug, but
   - The measured execution time/instructions for the padded proof significantly exceeds the execution time for the base fixture-sized proof, while the declared `T::WeightInfo::submit()` weight charged is identical in both cases — demonstrating the charged weight does not reflect the real work performed.
5. Optionally add a `#[bench]`/criterion benchmark comparing `submit()` cost at `receipt_proof`/`header_branch` sizes of 1x vs. 100x vs. max-allowed to quantify the discrepancy against the fixed benchmarked weight constant.

### Citations

**File:** bridges/snowbridge/pallets/inbound-queue/src/lib.rs (L138-139)
```rust
		/// The upper limit here only used to estimate delivery cost
		type MaxMessageSize: Get<u32>;
```

**File:** bridges/snowbridge/pallets/inbound-queue/src/lib.rs (L235-243)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::submit())]
		pub fn submit(origin: OriginFor<T>, event: EventProof) -> DispatchResult {
			let who = ensure_signed(origin)?;
			ensure!(!Self::operating_mode().is_halted(), Error::<T>::Halted);

			// submit message to verifier for verification
			T::Verifier::verify(&event.event_log, &event.proof)
				.map_err(|e| Error::<T>::Verification(e))?;
```

**File:** bridges/snowbridge/pallets/inbound-queue/src/weights.rs (L18-31)
```rust
/// Weight functions needed for ethereum_beacon_client.
pub trait WeightInfo {
    fn submit() -> Weight;
}

// For backwards compatibility and tests
impl WeightInfo for () {
    fn submit() -> Weight {
        Weight::from_parts(70_000_000, 0)
            .saturating_add(Weight::from_parts(0, 3601))
            .saturating_add(RocksDbWeight::get().reads(2))
            .saturating_add(RocksDbWeight::get().writes(2))
    }
}
```

**File:** cumulus/parachains/runtimes/bridge-hubs/bridge-hub-rococo/src/weights/snowbridge_pallet_inbound_queue.rs (L69-78)
```rust
	fn submit() -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `586`
		//  Estimated: `4051`
		// Minimum execution time: 165_953_000 picoseconds.
		Weight::from_parts(171_518_000, 0)
			.saturating_add(Weight::from_parts(0, 4051))
			.saturating_add(T::DbWeight::get().reads(8))
			.saturating_add(T::DbWeight::get().writes(2))
	}
```

**File:** bridges/modules/messages/src/lib.rs (L212-245)
```rust
		#[pallet::call_index(2)]
		#[pallet::weight(T::WeightInfo::receive_messages_proof_weight(&**proof, *messages_count, *dispatch_weight))]
		pub fn receive_messages_proof(
			origin: OriginFor<T>,
			relayer_id_at_bridged_chain: AccountIdOf<BridgedChainOf<T, I>>,
			proof: Box<FromBridgedChainMessagesProof<HashOf<BridgedChainOf<T, I>>, T::LaneId>>,
			messages_count: u32,
			dispatch_weight: Weight,
		) -> DispatchResultWithPostInfo {
			Self::ensure_not_halted().map_err(Error::<T, I>::BridgeModule)?;
			let relayer_id_at_this_chain = ensure_signed(origin)?;

			// reject transactions that are declaring too many messages
			ensure!(
				MessageNonce::from(messages_count) <=
					BridgedChainOf::<T, I>::MAX_UNCONFIRMED_MESSAGES_IN_CONFIRMATION_TX,
				Error::<T, I>::TooManyMessagesInTheProof
			);

			// why do we need to know the weight of this (`receive_messages_proof`) call? Because
			// we may want to return some funds for not-dispatching (or partially dispatching) some
			// messages to the call origin (relayer). And this is done by returning actual weight
			// from the call. But we only know dispatch weight of every message. So to refund
			// relayer because we have not dispatched message, we need to:
			//
			// ActualWeight = DeclaredWeight - Message.DispatchWeight
			//
			// The DeclaredWeight is exactly what's computed here. Unfortunately it is impossible
			// to get pre-computed value (and it has been already computed by the executive).
			let declared_weight = T::WeightInfo::receive_messages_proof_weight(
				&*proof,
				messages_count,
				dispatch_weight,
			);
```

**File:** bridges/snowbridge/primitives/verification/src/lib.rs (L37-62)
```rust
/// A bridge message from the Gateway contract on Ethereum
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Debug, TypeInfo)]
pub struct EventProof {
	/// Event log emitted by Gateway contract
	pub event_log: Log,
	/// Inclusion proof for a transaction receipt containing the event log
	pub proof: Proof,
}

/// Event log
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Debug, TypeInfo)]
pub struct Log {
	pub address: H160,
	pub topics: Vec<H256>,
	pub data: Vec<u8>,
	pub tx_index: u64,
}

/// Inclusion proof for a transaction receipt
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Debug, TypeInfo)]
pub struct Proof {
	// Proof values from receipts tree
	pub receipt_proof: Vec<Vec<u8>>,
	// Proof that an execution header was finalized by the beacon chain
	pub execution_proof: ExecutionProof,
}
```

**File:** bridges/snowbridge/primitives/beacon/src/types.rs (L450-474)
```rust
pub struct ExecutionProof {
	/// Header for the beacon block containing the execution payload
	pub header: BeaconHeader,
	/// Proof that `header` is an ancestor of a finalized header
	pub ancestry_proof: Option<AncestryProof>,
	/// The execution header to be verified
	pub execution_header: VersionedExecutionPayloadHeader,
	/// Merkle proof that execution payload is contained within `header`
	pub execution_branch: Vec<H256>,
}

#[derive(
	Encode, Decode, DecodeWithMemTracking, CloneNoBound, PartialEqNoBound, DebugNoBound, TypeInfo,
)]
#[cfg_attr(
	feature = "std",
	derive(serde::Deserialize),
	serde(deny_unknown_fields, bound(serialize = ""), bound(deserialize = ""))
)]
pub struct AncestryProof {
	/// Merkle proof that `header` is an ancestor of `finalized_header`
	pub header_branch: Vec<H256>,
	/// Root of a finalized block that has already been imported into the light client
	pub finalized_block_root: H256,
}
```

**File:** bridges/snowbridge/pallets/ethereum-client/src/impls.rs (L21-41)
```rust
	fn verify(event_log: &Log, proof: &Proof) -> Result<(), VerificationError> {
		// Refuse to verify any Ethereum-side proof while the beacon light client is halted.
		// Governance halts the light client when it suspects a compromise (e.g. sync committee
		// takeover), at which point any signed headers/receipts must be treated as untrusted.
		// Covers every Verifier consumer, including `inbound_queue_v2::submit` and
		// `outbound_queue_v2::submit_delivery_receipt` (which would otherwise still drain
		// pending relayer rewards while the bridge is halted).
		ensure!(!Self::operating_mode().is_halted(), VerificationError::Halted);

		Self::verify_execution_proof(&proof.execution_proof)
			.map_err(|e| InvalidExecutionProof(e.into()))?;

		Self::verify_receipt_inclusion(
			proof.execution_proof.execution_header.receipts_root(),
			event_log.tx_index,
			&proof.receipt_proof,
			event_log,
		)?;

		Ok(())
	}
```

**File:** bridges/snowbridge/primitives/verification/src/receipt.rs (L13-36)
```rust
pub fn verify_receipt_proof(
	receipts_root: H256,
	tx_index: u64,
	proof: &[Vec<u8>],
) -> Option<ReceiptEnvelope> {
	let key = receipt_trie_key(tx_index);
	let root = B256::from_slice(receipts_root.as_bytes());
	let proof_nodes: Vec<Bytes> = proof.iter().map(|node| Bytes::copy_from_slice(node)).collect();

	// Call verify_proof with None to extract the value from an inclusion proof. For inclusion
	// proofs, alloy_trie returns ValueMismatch with the extracted value in `got`. The proof is
	// already cryptographically verified during this traversal.
	let value = match verify_proof(root, key, None, proof_nodes.iter()) {
		Ok(()) => return None, // Exclusion proof - key does not exist
		Err(ProofVerificationError::ValueMismatch { path, got: Some(v), expected: None })
			if path == key =>
		{
			v.to_vec()
		},
		Err(_) => return None,
	};

	ReceiptEnvelope::decode(&mut value.as_slice()).ok()
}
```
