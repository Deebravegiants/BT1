This confirms a critical detail: the `#[pallet::weight(weight())]` annotation for `handle_unsigned` is a **fixed static weight** of `300_000_000` regardless of how many messages are in the `Vec<Message>` batch [1](#0-0) , and the weight/fee limits enforced at block-inclusion have no bearing on the `validate_unsigned` path anyway — that path unconditionally calls `Self::execute(messages.clone())`, fully running proof verification (MMR membership, state-trie non-membership, consensus checks) for every message in the batch, before any weight or fee accounting happens [2](#0-1) .

### Title
Unbounded `handle_unsigned` message batch causes network-wide Denial of Service during transaction-pool validation - (File: modules/pallets/ismp/src/lib.rs)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an unbounded `Vec<Message>` and is validated via `ValidateUnsigned::validate_unsigned`, which fully executes every message in the batch (`Self::execute(messages.clone())`) — including cryptographic proof verification for each request/response/consensus update — before the transaction is even admitted to the pool [3](#0-2) . Because this is an **unsigned, feeless** transaction that is gossiped to every node on the network, an attacker can submit a single large batch to force every full node to perform the full, expensive proof-verification workload for free, with no economic disincentive and no batch-size bound enforced anywhere before the expensive work occurs.

### Finding Description
`handle_unsigned` is explicitly documented as permissionless: "This allows users execute ISMP datagrams for free. Use with caution." [4](#0-3) . The dispatchable itself takes an arbitrary-length `Vec<Message>` [5](#0-4) , and its `validate_unsigned` implementation immediately calls `Self::execute(messages.clone())` to determine transaction validity [6](#0-5) . `execute()` iterates every message and runs `handle_incoming_message`, which performs full membership/non-membership proof verification (e.g. `MerkleMountainRange.VerifyProof`, `PolkadotTrie::VerifyProof`, or the state-machine's `verify_membership`) for each request/response in the batch [7](#0-6) [8](#0-7) .

Critically, this full re-execution happens as part of **transaction-pool admission**, which every peer node performs upon receiving the gossiped extrinsic — this is not gated by the weight limit assigned to the call. The `#[pallet::weight(weight())]` annotation only returns a static placeholder (`300_000_000`) regardless of batch size, described in comments as a value meant to be overridden post-hoc by the `FeeHandler` [1](#0-0) , so it provides no meaningful pre-execution size/cost bound during `validate_unsigned`. Because these are unsigned transactions there is also no fee charged to the submitter for the verification work forced onto every receiving node, and `propagate: true` in the returned `ValidTransaction` means valid-looking submissions continue to be relayed across the network [9](#0-8) .

This is directly analogous to the vLLM `best_of` issue: an unauthenticated, unprivileged caller controls an amount-of-work parameter (batch size / proof complexity) with no resource/timeout bound, and the receiving system (each ISMP-enabled parachain node) performs the resulting expensive work unconditionally before rejecting invalid input, exhausting CPU across the network.

### Impact Explanation
Any relayer, message dispatcher, or unprivileged actor able to submit gossiped unsigned extrinsics can craft `handle_unsigned` calls containing large numbers of `PostRequest`/`GetResponse`/timeout messages (bounded only by the runtime's max extrinsic/block length, which can still be megabytes) requiring expensive cryptographic verification per entry. Every full node that receives this extrinsict via gossip must perform this full verification work during mempool validation, for free, repeatedly for the transaction's `longevity` window (up to 25 blocks) if resubmitted. This can degrade or stall block production and increase p2p processing load network-wide — a resource-exhaustion Denial of Service against the parachain, potentially delaying legitimate ISMP message and relayer processing (route unable to deliver messages in a timely fashion).

### Likelihood Explanation
Medium. `handle_unsigned` is explicitly permissionless and designed to accept externally supplied proofs; crafting a batch with many entries (each carrying syntactically valid but ultimately-invalid proof data that still forces full verification attempts) requires no special privileges, funds, or governance access — only network connectivity to gossip the extrinsic. However, invalid entries do get rejected by `execute()` (short-circuiting on the first invalid message via `.collect::<Result<Vec<_>,_>>()`), so the attack is bounded by the batch size the attacker can fit into a single extrinsic and the cost of preparing that many plausible-but-invalid proofs; this is a per-transaction resource cost multiplier rather than infinite work.

### Recommendation
Enforce an explicit, small maximum on `messages.len()` (and on nested collection sizes such as `requests`/`timeouts` within each `Message` variant) before any proof verification is attempted in `validate_unsigned`, rejecting oversized batches immediately with `InvalidTransaction::Call`. Additionally, make the `#[pallet::weight(weight())]` value scale with the actual batch size/complexity so the runtime's `CheckWeight` extension can reject oversized batches cheaply, and consider validating cheap invariants (e.g., basic structural sanity, destination match, timeout) before running full cryptographic proof verification inside `validate_unsigned`.

### Proof of Concept
1. An attacker constructs a `pallet_ismp::Call::handle_unsigned { messages }` where `messages` is a `Vec<Message::Request(RequestMessage)>` containing an intentionally large `requests: Vec<PostRequest>` (e.g., thousands of synthetic entries) and a fabricated-but-parseable multiproof.
2. The attacker gossips this unsigned extrinsic to the network. Every receiving full node's `validate_unsigned` immediately calls `Self::execute(messages.clone())` [6](#0-5) , which iterates the full request list and performs full proof/membership verification per entry via `state_machine.verify_membership` [8](#0-7)  before ultimately failing on invalid proof data.
3. Because no bound on `messages.len()`/`requests.len()` is checked prior to this verification work, and the call carries no transaction fee, the attacker imposes the full verification cost on every peer node for free, repeatable across the transaction's longevity and re-submittable with new content.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L604-604)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
```

**File:** modules/pallets/ismp/src/lib.rs (L605-625)
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

**File:** modules/pallets/ismp/src/lib.rs (L701-714)
```rust
			Ok(ValidTransaction {
				// consensus messages unblock everything else, so they are included ahead
				// of request batches; identical submissions still share a priority so the
				// pool can dedupe them
				priority: if has_consensus { 200 } else { 100 },
				// they are all self-contained batches that have no dependencies
				requires: vec![],
				// provides this unique hash of transactions
				provides: vec![msg_hash],
				// should only live for at most 10 blocks
				longevity: 25,
				// always propagate
				propagate: true,
			})
```

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L40-51)
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
```

**File:** modules/ismp/core/src/handlers/request.rs (L86-93)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```
