### Title
Unbounded `Vec<Message>` in `pallet_ismp::handle_unsigned` allows resource-exhaustion during free unsigned-extrinsic validation - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an unbounded `Vec<Message>` and, critically, `ValidateUnsigned::validate_unsigned` fully executes the entire batch (`Self::execute(messages.clone())`) for *every* node during transaction-pool validation, before any fee or weight is charged. There is no cap on the number of messages (or on nested collections such as `GetRequest.keys`) that a single unsigned submission can carry, mirroring the wasmd `ValidateBasic` issue (GHSA-m3rh-cvr5-x6q4) where large, attacker-controlled address/array counts caused unbounded resource consumption in a validation routine that runs ahead of normal fee/weight gating.

### Finding Description
`handle_unsigned` is declared as an unsigned, fee-free call specifically so that valid ISMP messages can be relayed for free: [1](#0-0) 

Its `ValidateUnsigned::validate_unsigned` implementation runs `Self::execute(messages.clone())` directly, which fully processes and verifies every message in the batch (proof/signature verification, commitment lookups, router dispatch) before the transaction is even admitted to the pool: [2](#0-1) 

`Pallet::<T>::execute` iterates unconditionally over the full `messages` vector with `handle_incoming_message` for each entry: [3](#0-2) 

No length check exists on `messages: Vec<Message>` anywhere in the call signature, the `#[pallet::call]` handler, or `validate_unsigned` before this expensive execution begins — the only bound found in the request/timeout handlers is a check that the batch is non-empty (`EmptyBatch`), not that it is capped: [4](#0-3) 

Likewise, per-request fields such as `GetRequest.keys: Vec<Vec<u8>>` (storage keys to query) have no enforced upper bound at the message-validation layer, so a single `Message::Request` or `Message::Timeout` entry can itself carry an arbitrarily large array that must be hashed and proof-verified.

Because unsigned extrinsics bypass normal transaction fees and weight-based rejection at the mempool-admission stage (that is the entire design point — "execute ISMP datagrams for free"), the cost of running `validate_unsigned` on a maliciously large batch is not paid for by the submitter. Every full node that receives the extrinsic over the network (before block inclusion) must run this same expensive validation to decide whether to propagate/include it, which is the class of unbounded-resource-consumption issue CWE-400 describes.

### Impact Explanation
This is a pool-validation resource-consumption issue reachable by any relayer/peer submitting an unsigned extrinsic: an attacker can construct a `handle_unsigned` call with a very large `Vec<Message>` (or with a `GetRequest` containing a huge `keys` array), and every node validating the transaction (via `validate_unsigned`) executes the full processing pipeline — hashing, merkle/state proof verification, router dispatch attempts — for the whole batch. Because this runs during transaction-pool validation, not after weight/fee gating, it can consume disproportionate CPU/time relative to the (zero) cost paid by the attacker, an availability/DoS-class impact matching the referenced CWE-400 classification and matching the Medium severity of the analog advisory (no direct fund loss, but relayer/node-level resource strain and potential block-production delay under repeated submission).

### Likelihood Explanation
Likelihood is bounded by block/extrinsic length limits (Substrate's `BlockLength`/`BlockWeights` still cap the raw byte size of an extrinsic), so a batch cannot be truly infinite; however, because `Message`/`Request`/`GetRequest` structures use unbounded `Vec<u8>`/`Vec<Vec<u8>>` fields rather than `BoundedVec`, an attacker can still pack many small, syntactically-valid but semantically-inert messages (e.g., malformed/invalid proofs that still require processing to reject) into one submission, up to the byte-size ceiling, and pay nothing since the call is unsigned/free. This requires no privileged access — any peer/relayer capable of submitting the unsigned extrinsic can attempt it — but the actual severity depends on how expensive `handle_incoming_message` is per rejected message, which was not exhaustively benchmarked in this review.

### Recommendation
- Enforce an explicit, low upper bound on `messages.len()` in `handle_unsigned` and reject batches above it before any processing occurs (both in the `#[pallet::call]` body and in `validate_unsigned`, mirroring the `EmptyBatch` check but for a maximum, not just non-empty).
- Convert unbounded `Vec` fields inside `Message`/`Request`/`GetRequest` (e.g. `GetRequest.keys`, `from`/`to`/`body`) to `BoundedVec`s with protocol-appropriate maximums, consistent with the wasmd fix (CWA-2024-003) of capping address/array counts in `ValidateBasic`-equivalent logic.
- Consider doing a cheap, bounded pre-check (count/size only) in `validate_unsigned` prior to invoking the full `execute` pipeline, so obviously oversized batches are rejected without the expensive proof-verification work being performed by every validating node.

### Proof of Concept
Not independently verified by benchmark; the code path is as follows: a relayer submits `Ismp::handle_unsigned(messages: Vec<Message>)` as an unsigned extrinsic with a large number of entries (each a minimal `Message::Timeout`/`Message::Request` with an inert/invalid proof, or a single `GetRequest` with a very large `keys` array), sized up to the chain's max extrinsic/block length. On receipt, every node's `ValidateUnsigned::validate_unsigned` for `pallet_ismp::Call::handle_unsigned` calls `Self::execute(messages.clone())` (`modules/pallets/ismp/src/lib.rs:619-625` → `modules/pallets/ismp/src/impls.rs:40-51`), which iterates the full vector and invokes `handle_incoming_message` per entry — consuming CPU proportional to the attacker-chosen array size — before the extrinsic is even admitted to the pool, at zero cost to the submitter.

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

**File:** modules/ismp/core/src/handlers/request.rs (L30-36)
```rust
pub fn handle<H>(host: &H, msg: RequestMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	if msg.requests.is_empty() {
		Err(Error::EmptyBatch)?
	}
```
