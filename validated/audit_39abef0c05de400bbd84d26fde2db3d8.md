### Title
Unbounded `messages: Vec<Message>` in `pallet_ismp::handle_unsigned` is fully executed during unsigned-transaction validation, enabling free memory/CPU exhaustion — (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic accepts an unbounded `Vec<Message>`, where each `Message::Request`/`Response`/`Timeout` itself wraps an unbounded `Vec<PostRequest>`/`Vec<GetRequest>`. `ValidateUnsigned::validate_unsigned` for this call unconditionally clones and fully executes the entire batch (`Self::execute(messages.clone())`) before any size, count, or fee check is applied. This runs on every node that receives the gossiped unsigned extrinsic, for free, with no `BoundedVec` cap analogous to `pallet-call-decompressor`'s `MaxCallSize` gate.

### Finding Description
`handle_unsigned` is declared as:
```rust
pub fn handle_unsigned(origin: OriginFor<T>, messages: Vec<Message>) -> DispatchResultWithPostInfo {
    ensure_none(origin)?;
    Self::execute(messages.clone())?;
    Ok(().into())
}
``` [1](#0-0) 

`messages` is a plain `Vec<Message>`, not a `BoundedVec`. There is no configured maximum on the number of messages or on the number of requests/responses nested inside each message (`RequestMessage.requests: Vec<PostRequest>`, `ResponseMessage.requests`, `TimeoutMessage::Post/Get { requests }`).

The `ValidateUnsigned` impl, which fires whenever an unsigned transaction is gossiped to a node's transaction pool (i.e., before block inclusion, on every full node), does:
```rust
fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
    let messages = match call { Call::handle_unsigned { messages } => messages, ... };
    let events = Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
    ...
}
``` [2](#0-1) 

`execute` dispatches into the ISMP handlers (`modules/ismp/core/src/handlers/{request,response,timeout}.rs`), which for every request in the batch: clones it into a `Request` wrapper, computes its commitment hash, and pushes it into a `Vec` for membership/non-membership proof verification, e.g.:
```rust
let commitments = msg.requests.iter().map(|post| hash_request::<H>(&Request::Post(post.clone()))).collect();
state_machine.verify_membership(host, commitments, state, &msg.proof)?;
``` [3](#0-2) 

All of this cloning, hashing, and Vec construction happens **before** the proof is checked, and the proof check itself is the only thing that can reject the batch — cheap constant-size garbage bytes for `msg.proof` will fail late, only after the full batch has already been allocated and hashed. This is directly analogous to `SimpleDirectoryReader`'s `num_files_limit` being enforced only after all files were loaded: the resource-bounding check (proof validity / any size cap) is applied only after the unbounded input has already been fully materialized and processed.

Unlike `pallet-ismp-relayer`'s `pallet-call-decompressor`, which explicitly notes and fixes this exact class of bug (`ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, ...)` — "a fee-less attacker could claim `encoded_call_size = u32::MAX` and have a tiny zstd bomb expanded to gigabytes during transaction-pool validation, before any size check" — [4](#0-3) ), `pallet_ismp::handle_unsigned` has no equivalent bound on `messages` or the nested request vectors. Since `handle_unsigned` is reachable directly (not only via the decompressor), the fix applied to one path was never applied to the other, more direct, path.

### Impact Explanation
`handle_unsigned` is an unsigned extrinsic ("free" per the pallet's own documentation: *"This means all cross-chain messages received are executed for free as unsigned transactions"* [5](#0-4) ). Any unprivileged relayer/network peer can construct and gossip a `handle_unsigned` call containing an extremely large `Vec<Message>` (or one message with an extremely large `Vec<PostRequest>`/`Vec<GetRequest>`), each carrying attacker-controlled `from`/`to`/`body`/`keys` bytes and a garbage proof. Every node that receives this gossiped transaction will run `validate_unsigned`, which fully clones and executes the batch — allocating large `Vec`s, hashing every request, and doing per-request duplicate/timeout checks — before the (invalid) proof is ever checked. Repeated submissions from multiple peers/connections can degrade or crash relayer/collator nodes (CPU and memory exhaustion), impairing message delivery for the whole route — matching the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
High reachability: no signature, no fee, no special permission is required — only that the extrinsic be well-formed enough to decode as `Call::handle_unsigned` and pass SCALE decoding (bounded only by the node's general extrinsic-size/block-length limits, which are typically several MB — enough to carry tens of thousands of small `PostRequest`/`GetRequest` entries). It is triggered automatically by transaction-pool gossip validation on every full node, so a single submission is amplified across the whole network topology.

### Recommendation
Bound `handle_unsigned`'s input the same way `pallet-call-decompressor` bounds `decompress`: introduce a `T::MaxMessagesPerBatch` (and/or `T::MaxRequestsPerMessage`) configuration, and reject in `validate_unsigned`/`pre_dispatch` (before calling `Self::execute`) any call whose `messages.len()` or nested request/response/timeout vector lengths exceed the configured cap — mirroring the existing guard comment in `call-decompressor` about enforcing bounds "at the single choke point every caller flows through" before any expensive work is performed.

### Proof of Concept
1. Construct `Call::Ismp(pallet_ismp::Call::handle_unsigned { messages })` where `messages` is a `Vec<Message::Request(RequestMessage { requests, proof, signer })>` with `requests` containing e.g. 50,000–100,000 `PostRequest` entries (as already demonstrated feasible for 1,000 entries in the existing test `should_decompress_and_execute_pallet_ismp_post_request_calls_correctly`, [6](#0-5) ), and an arbitrary/invalid `proof` bytes blob.
2. Submit this as an unsigned extrinsic directly to `Ismp::handle_unsigned` (not via the decompressor, which is bound) via `create_unsigned`/RPC, as shown in the test harness pattern `client.tx().create_unsigned(&tx)?.submit_and_watch()` [7](#0-6) .
3. Every node that receives the gossiped transaction executes `validate_unsigned`, which calls `Self::execute(messages.clone())`, cloning and hashing all 50,000–100,000 requests and performing per-request duplicate/timeout checks, before ultimately failing at `verify_membership` due to the bogus proof — meaning the entire allocation/hash cost is paid on every receiving node for a transaction that costs the attacker nothing.

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

**File:** modules/ismp/core/src/handlers/request.rs (L88-93)
```rust
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L224-231)
```rust
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs (L148-168)
```rust
#[test]
fn should_decompress_and_execute_pallet_ismp_post_request_calls_correctly() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let requests = (0..1000)
			.into_iter()
			.map(|i| {
				let post = ismp::router::PostRequest {
					source: host.host_state_machine(),
					dest: StateMachine::Evm(1),
					nonce: i,
					from: H256::random().0.to_vec(),
					to: H256::random().0.to_vec(),
					timeout_timestamp: Duration::from_millis(Timestamp::now()).as_secs() +
						2_000_000_000,
					body: H512::random().0.to_vec(),
				};
				post
			})
			.collect::<Vec<_>>();
```

**File:** parachain/simtests/src/pallet_ismp.rs (L292-293)
```rust
	// send once
	let progress = client.tx().create_unsigned(&tx)?.submit_and_watch().await?;
```
