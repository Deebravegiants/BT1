### Title
Unbounded, fee-free `handle_unsigned` batches let an unpriced submitter force full ISMP message execution (including expensive consensus/state-proof verification) inside transaction-pool validation on every node — analogous to HTTP/2 Rapid Reset resource exhaustion (CVE-2023-44487) - (File: modules/pallets/ismp/src/lib.rs)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is validated via `ValidateUnsigned::validate_unsigned`, which does not perform a cheap, bounded pre-check — it calls `Self::execute(messages.clone())`, i.e. it **runs the full message-handling pipeline** (proof/consensus verification, state commitment lookups, MMR/child-trie work) just to decide whether the transaction is admissible to the pool.

### Finding Description
`handle_unsigned` is declared as an unsigned, permissionless, fee-free call: [1](#0-0) 

Its `ValidateUnsigned` implementation performs the entire message execution — not a lightweight structural/format check — before the transaction is even queued or gossiped: [2](#0-1) 

`Self::execute` in turn maps `handle_incoming_message` over every message in the batch, which performs full request/response/timeout/consensus handling including cryptographic proof verification: [3](#0-2) [4](#0-3) 

There is no visible bound on the size of `messages: Vec<Message>` accepted by `handle_unsigned` (no `MaxMessages`/`BoundedVec` constant found in `pallet-ismp`), and the transaction carries `longevity: 25` and `propagate: true`, meaning it will be re-validated (re-executing the same expensive work) across the pool's lifetime and gossiped to every peer node that must itself re-run `validate_unsigned` to decide whether to accept and propagate it: [5](#0-4) 

This is structurally analogous to the HTTP/2 Rapid Reset bug class: a client (here, any unprivileged network participant who can gossip an extrinsic) can cause the server (here, every full/collator node) to perform disproportionately expensive work (full ISMP message + consensus/state-proof verification) for a payload that costs the attacker nothing and never needs to be included in a block ("cancelled" the same way an HTTP/2 stream is reset before completion — the transaction can simply be invalid/never mined, yet the expensive validation work has already been paid for by the network). Because it's unsigned and fee-free by design ("all cross-chain messages received are executed for free as unsigned transactions"), the normal weight-fee/anti-spam economics that would throttle a signed extrinsic do not apply to the validation-time cost.

### Impact Explanation
An attacker can flood the network with a stream of `handle_unsigned` extrinsics carrying large batches of syntactically well-formed but computationally heavy messages (e.g. many `Response`/`Request`/consensus messages requiring proof verification against arbitrary heights/keys). Each node that receives the gossiped extrinsic must run `validate_unsigned`, which fully executes the batch (proof verification, storage reads, MMR/child-trie computation) before it can even determine the transaction is invalid or a duplicate. Because this cost is paid by every node on every (re-)validation, and the attacker pays nothing and needs no proof to eventually succeed, this can degrade block production / transaction pool throughput network-wide — a resource-consumption denial-of-service directly reachable from a single unprivileged, unsigned submission, matching the CVE-2023-44487 bug class ("many stream resets/cheap requests causing disproportionate server work").

### Likelihood Explanation
The docs explicitly acknowledge the intended trust model relies on "the transaction pool will check if the submitted extrinsics are valid before they are included in the pool," assuming this check is cheap — but the actual implementation performs the full execution pipeline as the check itself, inverting the expected cost asymmetry. Since `handle_unsigned` is permissionless by design (Unsigned origin, no signature/fee required) and message batch size appears unbounded in the pallet definition reviewed, the attack requires no privileged access, no valid proofs, and no economic cost beyond bandwidth to construct and gossip malformed/heavy message batches.

### Recommendation
- Add a `MaxMessages`/`BoundedVec` cap on `handle_unsigned`'s `messages` parameter, scaled to a safe validation-time budget.
- Perform a cheap, structural pre-validation in `validate_unsigned` (e.g., message well-formedness, proof-height sanity, and per-message caps) before invoking `Self::execute`, deferring full cryptographic verification to `pre_dispatch`/actual execution rather than mempool admission.
- Consider charging a small bond or rate-limiting per-peer/per-account submissions of unsigned ISMP messages to restore cost symmetry between attacker and validating nodes.

### Proof of Concept
1. An attacker crafts a `pallet_ismp::Call::handle_unsigned { messages }` extrinsic containing a large `Vec<Message>` (e.g., hundreds of `RequestMessage`/`TimeoutMessage`/consensus entries) with syntactically valid but ultimately-failing proofs (as already exercised by the compression test harness with 100–1000 dummy requests, showing such batches are freely constructible): [6](#0-5) 
2. Submit repeated variants of this unsigned extrinsic via RPC/gossip to the network without signing and without any fee.
3. Each receiving node calls `ValidateUnsigned::validate_unsigned`, which calls `Self::execute(messages.clone())`, forcing full traversal of `handle_incoming_message` for every message (proof verification, consensus checks) purely to determine mempool validity: [2](#0-1) 
4. Repeat rapidly and in parallel from multiple peers; because the extrinsics are free and can be malformed/never finalized (analogous to a "reset" before completion), the attacker incurs negligible cost while every node incurs the full execution cost repeatedly, degrading network-wide validation throughput.

Note: I was unable to fully confirm within the indexed portion of the codebase whether any additional runtime-level extrinsic size/weight limit (outside `pallet-ismp` itself, e.g. a `BaseCallFilter` or `system::MaximumExtrinsicWeight`) effectively bounds batch size before it reaches `handle_unsigned`; this would need confirmation in a full checkout, since the index may not include every runtime configuration file.

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

**File:** modules/pallets/ismp/src/lib.rs (L638-645)
```rust
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
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

**File:** modules/ismp/core/src/handlers.rs (L86-100)
```rust
pub fn handle_incoming_message<H>(
	host: &H,
	message: Message,
) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	match message {
		Message::Consensus(consensus_message) => consensus::update_client(host, consensus_message),
		Message::FraudProof(fraud_proof) => consensus::freeze_client(host, fraud_proof),
		Message::Request(req) => request::handle(host, req),
		Message::Response(resp) => response::handle(host, resp),
		Message::Timeout(timeout) => timeout::handle(host, timeout),
	}
}
```

**File:** modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs (L148-188)
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

		let msg = RequestMessage {
			requests,
			proof: Proof {
				height: StateMachineHeight {
					id: StateMachineId {
						state_id: StateMachine::Evm(1),
						consensus_state_id: MOCK_CONSENSUS_STATE_ID,
					},
					height: 3,
				},
				proof: H512::random().0.to_vec(),
			},
			signer: H512::random().0.to_vec(),
		};

		let call = RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned {
			messages: vec![Message::Request(msg)],
		})
		.encode();
```
