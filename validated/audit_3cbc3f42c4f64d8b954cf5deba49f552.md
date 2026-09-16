### Title
`pallet-ismp`'s `handle_unsigned` charges a static, batch-size-independent weight, letting an unsigned message batch consume unbounded computation for free - (File: modules/pallets/ismp/src/lib.rs)

### Summary
`pallet_ismp::Pallet::handle_unsigned` is a permissionless, fee-less (`ensure_none`) extrinsic that executes an arbitrary `Vec<Message>` batch, where a `Message::Request` variant itself wraps a `Vec<PostRequest>` with a single merkle multi-proof. The extrinsic's declared weight is a hard-coded constant, independent of the number of messages or the number of requests/leaves inside each message, unlike the EIP-2930 intrinsic-gas gap described in the referenced minievm finding, where the accesslist's true cost (unbounded state loads) was never charged against the payer.

### Finding Description
The dispatchable is declared with a fixed weight: [1](#0-0) 

That constant is defined as: [2](#0-1) 

`Weight::from_parts(300_000_000, 0)` is returned unconditionally by `weight()`, regardless of how many `Message`s are in the `messages: Vec<Message>` argument, and regardless of how many `PostRequest`s a single `Message::Request(RequestMessage)` carries. `RequestMessage.requests` is an unbounded `Vec<PostRequest>`: [3](#0-2) 

Both `validate_unsigned` and the dispatch body call `Self::execute(messages.clone())`, which performs a full merkle multi-proof `verify_membership` over all requests, then loops over every request to look up its target module and invoke `IsmpModule::on_accept` (a per-module, potentially expensive callback), storing a receipt for each: [4](#0-3) 

This means the actual computational cost of a `handle_unsigned` call scales with `O(number_of_messages × number_of_requests_per_message × per-module callback cost × proof-verification cost)`, but the weight charged against the block's weight budget (via `frame_system::CheckWeight`) is always the same fixed `300_000_000`. There is no code path found that scales `weight()` by `messages.len()`, by `RequestMessage.requests.len()`, or by proof size — the documentation itself explicitly notes: "Static weights because these should get overridden by the FeeHandler," but the `FeeHandler` (`fee_handler.rs`) only converts *post-dispatch* weight into a *balance fee for a paying account* — it does not, and cannot, retroactively increase the weight already consumed against the block's `MAXIMUM_BLOCK_WEIGHT`/`BlockLength` limits before dispatch, since these unsigned calls have no signer to charge and no pre-dispatch bound tied to array length.

This is structurally the same bug class as the minievm report: a permissionless entry point performs work whose cost is driven by an attacker-controlled array (accesslist in minievm; `Vec<Message>`/`Vec<PostRequest>` here), but the fee/weight model charges a value that does not scale with that array's size, so the actual computational resources consumed are not properly compensated/bounded.

### Impact Explanation
Because `handle_unsigned` is unsigned and "free" by design (this is explicitly documented behavior for legitimate relayers), the transaction-pool validity check is the only gate — and that check itself runs the full `execute()` (including proof verification and all `on_accept` callbacks) to determine validity. An attacker who can produce (or reuse already-finalized/valid) large batches of legitimately provable requests, or messages targeting `IsmpModule`s with expensive `on_accept` handlers, can submit a single `handle_unsigned` extrinsic whose declared weight is only `300_000_000` but whose actual block-execution time is far larger. Because block-import/production reasons about resource consumption in terms of declared weight, this allows an attacker to consistently under-report the true cost of blocks they cause to be produced, creating a computational-resource DoS risk to collators/validators (block production/import stalls, potential missed slots) without paying commensurate weight/fees — directly mirroring the "abuse of the accesslist to consume computational resources without proper compensation" pattern in the reference finding.

### Likelihood Explanation
`handle_unsigned` is explicitly permissionless by design (`Unsigned` origin, "anyone execute ISMP messages for free, provided they have valid proofs"), so no privileged access is required — only the ability to construct or replay a `RequestMessage`/other `Message` with a large batch and a valid state/membership proof, which any relayer or user with access to a finalized-but-unprocessed batch of requests can do. The core weight function contains no per-item scaling factor at all, so the gap is deterministic and not dependent on a rare edge case.

### Recommendation
Make the weight charged for `handle_unsigned` scale with the actual size/complexity of the batch before dispatch (e.g., a function of `messages.len()`, the aggregate `requests.len()` across all `Message::Request`/`Message::Response`/`Message::Timeout` variants, and the destination module's benchmarked `IsmpModuleWeight` costs), and enforce a maximum batch size (e.g. a `BoundedVec` cap on `messages` and on `RequestMessage.requests`) so that no single unsigned extrinsic can force execution cost far in excess of its declared weight. This mirrors the minievm fix of properly charging "intrinsic" cost for the accesslist-equivalent array before allowing execution to proceed.

### Proof of Concept
1. Construct (or observe on-chain) a `RequestMessage` whose `proof` is a valid MMR/state multi-proof for `N` legitimate `PostRequest`s destined for a module with a non-trivial `on_accept` implementation (e.g. N = several thousand), all of which have not yet been delivered.
2. Submit `Ismp::handle_unsigned(messages: vec![Message::Request(msg)])` as an unsigned extrinsic.
3. `validate_unsigned` in [5](#0-4)  runs `Self::execute(messages.clone())` in full to validate — the pool accepts it because the proof and receipts are all legitimately valid, at real computational cost proportional to `N`.
4. On inclusion, `handle_unsigned` at [6](#0-5)  re-executes the same `O(N)` work, but the block only accounts `300_000_000` weight for it (per `weight()` at [7](#0-6) ), letting the attacker force disproportionate, unpriced computation onto every collator that must import/produce that block.

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

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
```rust
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

**File:** docs/content/protocol/ismp/requests.mdx (L85-93)
```text
/// A request message holds a batch of incoming requests and their proofs.
pub struct RequestMessage {
    /// POST requests from a source chain
    pub requests: Vec<PostRequest>,
    /// Membership batch proof for these requests
    pub proof: Proof,
    /// Signer information. Ideally should be their account identifier.
    pub signer: Vec<u8>,
}
```

**File:** modules/ismp/core/src/handlers/request.rs (L86-133)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;

	let mut total_weights = Weight::zero();
	let result = msg
		.requests
		.into_iter()
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
			};

			let res = lambda().and_then(|res| res);
			res
		})
		.collect::<Vec<_>>();

```
