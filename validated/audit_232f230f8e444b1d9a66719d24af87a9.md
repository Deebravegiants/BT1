### Title
Static, size-independent extrinsic weight lets an unprivileged caller trigger unbounded computation via `handle_unsigned` - (File: modules/pallets/ismp/src/lib.rs)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is unsigned/permissionless and is charged a fixed weight of `300_000_000` regardless of the number or size of `Message`s in the submitted `Vec<Message>` batch. Because this same batch is fully executed (proof verification, consensus/state-trie checks, request/response handling) inside `ValidateUnsigned::validate_unsigned` on every full node's mempool validation pass *before* any fee or weight accounting kicks in, an attacker can submit arbitrarily large batches, up to the block/extrinsic length limit, of cheap-to-construct-but-expensive-to-verify messages for free, repeatedly, to burn CPU on every node that validates the transaction pool — analogous to the HTTP/2 rapid-reset class of bug where inexpensive requests trigger disproportionate server-side work.

### Finding Description
`handle_unsigned` is declared as an unsigned call (`ensure_none(origin)`), reachable by anyone, and its declared weight ignores the actual size of its `messages` argument: [1](#0-0) 

The weight function used for this call is a hard-coded constant that does not scale with `messages.len()` or the number/size of proofs each message carries: [2](#0-1) 

`validate_unsigned`, which every node must run on every unsigned extrinsic received (whether or not it is ultimately included in a block), performs the **full** execution of the batch — proof verification, consensus checks, request/response handling — via `Self::execute(messages.clone())`: [3](#0-2) 

`Self::execute` iterates over every message in the batch, invoking `handle_incoming_message` per-message (consensus verification, MMR/merkle-trie non/membership proofs, module dispatch) with no per-batch or per-message cap: [4](#0-3) 

The `Message`/`ConsensusMessage`/proof fields are unbounded `Vec<u8>`/`Vec<Message>` types with no `BoundedVec` or explicit max-item constraints at the type level: [5](#0-4) 

Because the only constraint is the runtime's generic maximum extrinsic/block length (not a message-count or verification-cost cap), an attacker can pack many post/get/timeout messages — or messages that force expensive cryptographic proof verification paths (BEEFY/SP1/GRANDPA/state-trie proofs) — into one unsigned extrinsic near the length limit, submit it repeatedly, and force every full node in the network to redo this expensive verification during mempool validation for free (no fee is charged and the transaction may still be rejected/dropped after validation). The declared, fixed weight of `300_000_000` also decouples on-chain weight accounting from the true computational cost, meaning weight-based inclusion limits inside a block can undercount work actually performed, risking block time overruns.

### Impact Explanation
This is a denial-of-service vector reachable from a single, unauthenticated, gas-free extrinsic submission — no privileged role, governance, or specific admin/collator/relayer role is required; anyone able to submit unsigned transactions can exploit it. Repeated submission of maximal-size or verification-heavy batches can degrade or stall block production and mempool responsiveness network-wide (a route unable to deliver messages / halted message processing), which the "Validate" criteria explicitly list as an acceptable impact category. It does not directly cause theft of funds, but it can deny the relayer/consensus pipeline that message delivery depends on. This is rated Medium in line with the reported CVE-2023-39325 (HTTP/2 DoS) severity, matching the network-wide-but-not-fund-theft nature of the bug class.

### Likelihood Explanation
Likelihood is high: the call requires no signature, no fee, no special account, and no state precondition beyond constructing a syntactically valid (but not necessarily "successful") `Vec<Message>` payload. The docs even acknowledge the free-execution design ("all cross-chain messages received are executed for free as unsigned transactions") but rely on validity checks alone to prevent spam, without bounding the cost of those very validity checks themselves. Any node with network connectivity can submit an extrinsic sized up to the maximum block/extrinsic length repeatedly.

### Recommendation
- Scale the declared weight of `handle_unsigned` with the actual size/complexity of `messages` (e.g., `messages.len()`, aggregate proof byte length, and message type) rather than using a flat constant, so weight-based limits reflect real cost.
- Impose an explicit maximum message count and/or proof size per `handle_unsigned` batch (e.g., a `MaxMessagesPerBatch` config bound) enforced both in `validate_unsigned` and in `execute`.
- Consider cheap, coarse pre-filters in `validate_unsigned` (e.g., cap total proof bytes, message count) before running the expensive `Self::execute` path, so obviously oversized/abusive batches are rejected without doing full cryptographic verification.
- Add rate limiting/priority decay for repeated failed unsigned submissions from the same source where feasible at the node/transaction-pool level.

### Proof of Concept
1. Construct a `pallet_ismp::Call::handle_unsigned { messages }` where `messages` is a `Vec<Message>` filled with the maximum number of `Message::Request` (or `Message::Consensus`) entries that fit under the runtime's max extrinsic/block length (each carrying a maximal proof payload, e.g. large MMR/state-trie proofs or `GetRequest.keys` arrays as seen in `modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs:33-95`, which already demonstrates 100+ requests with 256 keys each being accepted as valid message shapes).
2. Submit this unsigned extrinsic to the network via RPC repeatedly from many source nodes/IPs (no fee, no nonce, no signature required).
3. Observe that each node's `validate_unsigned` (modules/pallets/ismp/src/lib.rs:614-625) fully executes `Self::execute(messages.clone())`, doing full consensus/state proof verification for the entire batch, at zero cost to the attacker, regardless of whether the extrinsic is ultimately included or rejected — this can be repeated indefinitely to consume node CPU.

Note: I was not able to execute this against a live node or benchmark the actual weight-vs-compute-time discrepancy since I only have read access to the repository index; a Devin session with build/test tooling would be needed to empirically measure the CPU cost per validate_unsigned call versus the declared `300_000_000` weight and confirm the magnitude of the discrepancy.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L604-625)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
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

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L40-57)
```rust
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;

		let messages_with_weights = message_results
			.iter()
			.zip(messages)
			.map(|(result, message)| MessageWithWeight { message, weight: result.weight() })
			.collect::<Vec<_>>();
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
