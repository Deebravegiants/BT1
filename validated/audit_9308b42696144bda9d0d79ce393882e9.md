### Title
Unbounded proof/body sizes in `pallet-ismp`'s `handle_unsigned` allow free, unbounded-cost message processing DoS - (File: modules/pallets/ismp/src/lib.rs)

### Summary
The external report describes a WASM-store DoS where large files are accepted without an enforced size ceiling, causing expensive processing before any rejection. The closest reachable analog in Hyperbridge is `pallet_ismp::Call::handle_unsigned`, the permissionless entry point relayers use to submit ISMP `Message`s (requests, responses, consensus updates). Unlike sibling pallets in this same codebase — `pallet-call-decompressor` (`MaxCallSize` gate enforced in `decompress` before any expansion) and `pallet-beefy-consensus-proofs` (`BoundedVec<u8, T::MaxProofSize>` on `submit_proof`) — `handle_unsigned` takes a completely unbounded `Vec<Message>` whose nested fields (`ConsensusMessage.consensus_proof: Vec<u8>`, `RequestMessage.proof.proof: Vec<u8>`, `PostRequest.body: Vec<u8>`, `GetRequest.keys: Vec<Vec<u8>>`, `FraudProofMessage.proof_1/proof_2: Vec<u8>`) carry no `MaxEncodedLen`/`BoundedVec` constraint at the pallet level.

### Finding Description
`handle_unsigned` is declared with an unsigned origin and is explicitly documented as allowing "anyone execute ISMP messages for free": [1](#0-0) 

Its `ValidateUnsigned::validate_unsigned` implementation calls `Self::execute(messages.clone())` directly inside transaction-pool validation, i.e. before any fee is charged and before the extrinsic is even included in a block: [2](#0-1) 

`Self::execute` routes into consensus-proof verification (`update_client`) and request/response verification, all of which decode and cryptographically process attacker-supplied `Vec<u8>` proof/body payloads with no size gate: [3](#0-2) [4](#0-3) 

Contrast with the two pallets in this same repository that were already hardened against exactly this class of bug:
- `pallet-call-decompressor` bounds the claimed decompressed size before doing any expansion, explicitly citing the zstd-bomb DoS risk of unbounded claims reaching `validate_unsigned` for free: [5](#0-4) 
- `pallet-beefy-consensus-proofs` bounds its proof parameter with `BoundedVec<u8, T::MaxProofSize>` so oversized payloads are rejected at SCALE-decode time, before dispatch or verification, and ships a runtime constant (`MaxBeefyProofSize = 1 MiB`) for it: [6](#0-5) [7](#0-6) 

`pallet_ismp::Call::handle_unsigned` has no equivalent bound on its `messages: Vec<Message>` parameter or on the nested proof/body fields. The only implicit ceiling is the runtime's overall `RuntimeBlockLength` (5 MiB, `NORMAL_DISPATCH_RATIO` applied): [8](#0-7) 
That figure is a block-level constraint, not a per-message/per-proof gate, and it still permits multi-megabyte unsigned extrinsics whose consensus-proof/state-proof verification cost (BEEFY MMR verification, EVM/Substrate storage-proof trie walks, sync-committee BLS verification, etc.) scales with the attacker-chosen payload size, invoked repeatedly and for free during mempool `validate_unsigned` gossip/re-validation, unlike the two sibling pallets that were deliberately fixed to close this exact gap.

### Impact Explanation
An unprivileged relayer (or anyone able to construct a syntactically valid `Message`) can submit `handle_unsigned` extrinsics with maximally-sized proof/body blobs (up to the block-length ceiling) repeatedly and for free — the call bypasses normal transaction fees under `ensure_none`. Because `validate_unsigned` performs full cryptographic/state verification synchronously during mempool validation, this can be used to inflate CPU and memory cost on every full node re-validating the transaction pool, degrading throughput and potentially stalling block production/relaying for legitimate cross-chain messages (a route unable to deliver messages), which is the class of impact this program treats as Medium/High.

### Likelihood Explanation
Likelihood is high for the specific mechanism (crafting oversized-but-decodable `Message` payloads requires no privilege and no stake), though the practical severity is bounded by the block-length limit and by other pallets' independent fee/anti-spam mechanisms (e.g. `messaging-incentives`, per-request commitment checks) which may reduce — but do not eliminate — the free, pre-fee verification cost incurred in `validate_unsigned`.

### Recommendation
Add an explicit, pallet-level maximum size/config bound on `handle_unsigned`'s inputs, mirroring the fixes already applied to `pallet-call-decompressor` and `pallet-beefy-consensus-proofs`:
- Introduce a `T::MaxProofSize`/`T::MaxMessageBodySize`-style `Get<u32>` bound and validate proof/body/key lengths as the very first step of `validate_unsigned` and `execute`, rejecting oversized messages with `InvalidTransaction` before any decoding/verification work is performed.
- Consider converting the hottest nested fields (`consensus_proof`, `proof.proof`, `body`) to `BoundedVec` so the size limit is enforced at SCALE-decode time (as done for `BeefyConsensusProofs::submit_proof`), rather than only after decoding into `Vec<u8>`.

### Proof of Concept
1. Construct an unsigned `pallet_ismp::Call::handle_unsigned` extrinsic carrying a single `Message::Request(RequestMessage { requests, proof: Proof { proof: <several-MB filler bytes>, .. }, signer })`, sized up to the ~5 MiB `RuntimeBlockLength` ceiling.
2. Submit repeatedly via RPC (as an unsigned transaction, no signature/fee required) — see the pattern already used in tests: [9](#0-8) 
3. Each submission triggers `ValidateUnsigned::validate_unsigned` → `Self::execute` → full consensus-client/state-proof verification against the oversized `proof` bytes, for free, with no size gate rejecting it up front — unlike the guarded `decompress_call`/`submit_proof` paths in sibling pallets.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L605-626)
```rust
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;

```

**File:** modules/ismp/core/src/handlers/consensus.rs (L29-47)
```rust
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
```

**File:** modules/ismp/core/src/messaging.rs (L41-48)
```rust
pub struct ConsensusMessage {
	/// Scale Encoded Consensus Proof
	pub consensus_proof: Vec<u8>,
	/// The consensus state Id
	pub consensus_state_id: ConsensusStateId,
	/// Public key of the sender
	pub signer: Vec<u8>,
}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-231)
```rust
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L127-135)
```rust
		/// Maximum size in bytes of a single proof payload.
		#[pallet::constant]
		type MaxProofSize: Get<u32>;

		/// Per-bucket cap on the `MessagingProofs` and `RotationProofs` on-chain ring
		/// buffers (and, transitively, on the number of offchain proof blobs retained
		/// per kind).
		#[pallet::constant]
		type MaxStoredProofs: Get<u32>;
```

**File:** parachain/runtimes/nexus/src/lib.rs (L314-316)
```rust
	pub RuntimeBlockLength: BlockLength =
		BlockLength::max_with_normal_ratio(5 * 1024 * 1024, NORMAL_DISPATCH_RATIO);
	pub RuntimeBlockWeights: BlockWeights = BlockWeights::builder()
```

**File:** parachain/runtimes/nexus/src/lib.rs (L1007-1008)
```rust
	/// Maximum size in bytes of a single proof passed to `submit_proof`.
	pub const MaxBeefyProofSize: u32 = 1_048_576;
```

**File:** parachain/simtests/src/pallet_ismp.rs (L281-293)
```rust
	// 3. next send the requests
	let tx = subxt::dynamic::tx(
		"Ismp",
		"handle_unsigned",
		vec![messages_to_value(vec![Message::Request(RequestMessage {
			requests: vec![post.clone().into()],
			proof: proof.clone(),
			signer: signature.encode(),
		})])],
	);

	// send once
	let progress = client.tx().create_unsigned(&tx)?.submit_and_watch().await?;
```
