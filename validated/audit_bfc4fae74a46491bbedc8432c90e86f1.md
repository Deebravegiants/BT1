### Title
Unsigned `handle_unsigned` ISMP messages perform full, fee-free proof verification during `validate_unsigned`, enabling unmetered CPU exhaustion of every validating node - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp`'s `handle_unsigned` extrinsic is dispatched as `Unsigned` and executes cross-chain messages "for free," as the pallet's own docs state [1](#0-0) . Its `ValidateUnsigned::validate_unsigned` implementation calls `Self::execute(messages.clone())` directly, meaning full consensus/state-proof verification runs on every node's transaction-pool validation path with no fee and no weight-based cost accounting [2](#0-1) . This mirrors the H-15 pattern: computationally expensive verification logic is reachable by an unprivileged submitter without any gas/weight metering tied to the actual work performed.

### Finding Description
`validate_unsigned` for `pallet_ismp::Call::handle_unsigned` executes the entire message batch (including consensus and state-proof verification) before it decides whether the transaction is even valid to admit into the pool [3](#0-2) . Transaction-pool validation happens on every full node that receives the gossiped extrinsic, and — unlike block execution — is not subject to `frame_system::CheckWeight` block-weight accounting; it is purely a P2P/RPC-facing computation gate. The pallet's own dispatch weight for `handle_unsigned` is a hard-coded placeholder (`Weight::from_parts(300_000_000, 0)`) explicitly noted as a stand-in "because these should get overridden by the FeeHandler" [4](#0-3) , so there is no mechanism that ties verification cost (proof size, number of requests/consensus updates in a batch, Merkle-proof depth) to any metered/limited resource before the expensive `Self::execute` call runs.

An attacker can construct large batches of `Message::Request`/`Message::Consensus`/`Message::FraudProof` entries with maximal proof sizes and submit many distinct unsigned `handle_unsigned` transactions (varying content so each produces a unique `provides` tag, as the pool dedup logic requires [5](#0-4) ). Each submission forces every peer node to run full proof verification for free during pool validation, at essentially the attacker's bandwidth cost only, not any protocol-priced cost.

### Impact Explanation
Because this validation path runs on every full/validating node upon transaction propagation, an attacker flooding the network with such unsigned batches can drain CPU across the validator set, delaying block production or transaction propagation network-wide — the same "delay block building, possibly to the point of chain halt" impact described in the source report. This is reachable from a completely unprivileged actor (anyone who can submit an unsigned extrinsic/gossip a transaction), matching the required "unprivileged message dispatcher/relayer" reachability.

### Likelihood Explanation
Medium-High: submitting unsigned extrinsics requires no tokens, no signature, and no privileged role — only the ability to construct a syntactically valid `Message` batch with a proof blob (the proof does not need to be cryptographically valid to trigger the verification cost; it only needs to parse). The pool's `provides`/`priority`/`longevity` tags prevent trivial duplicate rejection from blocking distinct submissions, so an attacker can generate many unique-tag batches cheaply.

### Recommendation
Bound the computational cost admissible during `validate_unsigned` before invoking `Self::execute`: enforce hard caps on batch size, per-message proof length, and number of requests/consensus updates per unsigned submission, and/or introduce a lightweight, cheap pre-check (e.g., signature/structure sanity, size limits) that runs before the expensive proof-verification path, so unmetered CPU cost cannot scale with attacker-supplied batch size.

### Proof of Concept
Not executed; reasoning based on static code paths shown above. A concrete PoC would submit repeated unsigned `Ismp::handle_unsigned` extrinsics with large, distinct message batches (large proofs / many requests) via RPC and measure per-node CPU time consumed in `validate_transaction`/`Self::execute` versus the near-zero cost to the attacker.

### Citations

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L253-258)
```text
| `handle_unsigned` | Unsigned | Execute the provided batch of ISMP messages for free with valid proofs. This will short-circuit and revert if any of the provided messages are invalid. |
| `fund_message` | Signed | Increase the relayer fee for in-flight requests and responses to incentivize their delivery. Should not be called on a message that has been completed (delivered or timed-out) as those funds will be lost forever. |

## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
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

**File:** modules/pallets/ismp/src/lib.rs (L647-699)
```rust
			// No state machine was advanced by these messages. Build a content-unique
			// `provides` tag from the messages themselves so that distinct submissions
			// never collide in the transaction pool.
			//
			// A consensus message that doesn't advance a state machine (e.g. a
			// validator-set rotation during sync) previously mapped to an empty request
			// list via the catch-all arm. Every such message therefore produced an
			// identical `provides` tag and a fixed priority of 100, so the pool rejected
			// any two of them with "Priority is too low (100 vs 100)". Hashing the
			// consensus message (excluding the signer, so equivalent submissions from
			// different relayers dedupe) gives each update a unique tag.
			let mut has_consensus = false;
			let mut tags = messages
				.into_iter()
				.map(|message| match message {
					Message::Consensus(ConsensusMessage {
						consensus_proof,
						consensus_state_id,
						..
					}) => {
						has_consensus = true;
						vec![H256(sp_io::hashing::keccak_256(
							&(consensus_state_id, consensus_proof).encode(),
						))]
					},
					Message::FraudProof(FraudProofMessage { proof_1, proof_2, .. }) => vec![
						H256(sp_io::hashing::keccak_256(&proof_1)),
						H256(sp_io::hashing::keccak_256(&proof_2)),
					],
					Message::Request(RequestMessage { requests, .. }) => requests
						.into_iter()
						.map(|post| hash_request::<Pallet<T>>(&Request::Post(post.clone())))
						.collect::<Vec<_>>(),
					Message::Response(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
					Message::Timeout(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
				})
				.collect::<Vec<_>>();
			tags.sort();

			if tags.is_empty() {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&tags.encode()).to_vec();
```

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```
