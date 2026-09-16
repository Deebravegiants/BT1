### Title
Transaction Congestion via Free, Fully-Executed `handle_unsigned` Validation Starves Legitimate Message Delivery - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is submitted as an **unsigned transaction and executed for free** — an unprivileged relayer or any actor with a network connection can flood every collator's transaction pool with `handle_unsigned` batches. Critically, `ValidateUnsigned::validate_unsigned` does not just cheaply check the message shape — it calls `Self::execute(messages.clone())`, running the **full** ISMP message pipeline (consensus/state proof verification, MMR/trie membership checks, module dispatch) during mempool validation, for every submission and on every re-validation while the transaction sits in the pool. This is directly analogous to the EOSVegas "transaction congestion attack," where an attacker floods a cheap/free interaction to monopolize processing capacity and profit from delayed/blocked legitimate transactions.

### Finding Description
`handle_unsigned` is declared with `ensure_none(origin)` and a fixed weight, meaning it can be submitted without a fee-paying signed account: [1](#0-0) 

The pallet's `ValidateUnsigned::validate_unsigned` implementation, run on every node before a transaction is admitted to (or retained in) the pool, does not perform a lightweight sanity check — it calls `Self::execute(messages.clone())`, i.e., the same code path used for real block execution, including full cryptographic proof verification (BEEFY/consensus, MMR non/membership, trie storage proofs): [2](#0-1) 

Because this execution happens inside `validate_unsigned` (which every full node/collator runs to admit or re-validate pool contents, with `longevity: 25` meaning re-validation across up to 25 blocks), an attacker can construct or replay many distinct message batches (varying nonces/heights/consensus proofs so each produces a unique `provides` tag, defeating de-duplication) and force full proof verification to be repeated across the network for free, on every block, for up to 25 blocks per submission: [3](#0-2) 

The docs confirm the design intent was that transaction-pool validation would filter spam cheaply, but the implementation actually performs the expensive work as part of that filter: [4](#0-3) 

This lets an attacker saturate collator CPU/block-building capacity with computationally expensive-but-free unsigned submissions, crowding out legitimate `Message::Request`, `Message::Response`, `Message::Timeout`, and `Message::Consensus` batches from being included before their respective `timeout_timestamp` or `challenge_period` windows elapse.

### Impact Explanation
If legitimate `PostRequest`/`GetRequest` delivery or `TimeoutMessage` processing is starved out of blocks by attacker-induced congestion:
- Requests that should be delivered in time are instead pushed past their `timeout_timestamp`, permanently rejected on the destination (per the timeout mechanics in `docs/content/protocol/ismp/timeouts.mdx`), and the relayer fee refund path (which itself requires another transaction to be included in time) can likewise be starved, freezing relayer fees and any application state pending the delivery/timeout callback.
- Consensus/fraud-proof messages needed to keep a connected state machine's light client advancing can be crowded out, temporarily creating "a route unable to deliver messages" for that state machine, per the impact classes explicitly in scope.
- Because the flood costs the attacker nothing (no signed fee, `Pays` not being enforced against an unsigned dispatch), the attack is essentially free to sustain, unlike the fee-priced EOSVegas congestion attack, making it cheaper and more durable.

This qualifies as Medium/High: no direct fund transfer to the attacker, but it can cause concrete freezing of relayer fees and message non-delivery across the bridge, matching the accepted "permanent freezing of funds" / "route unable to deliver messages" categories.

### Likelihood Explanation
Likelihood is high for the congestion effect itself: `handle_unsigned` is a public unsigned call reachable by anyone able to submit transactions or gossip them to a collator's pool, requiring only the ability to construct syntactically valid (but possibly stale/duplicate-content) `Message` batches with distinct hashes to avoid the `provides`-tag dedup, which is trivial (e.g., trivially varying `signer` bytes on `RequestMessage`/`ConsensusMessage`, or timeout messages for a large volume of already-known request commitments). The complexity is in reliably timing the congestion to coincide with a victim's narrow timeout window, which lowers the practical exploitation to Medium/High rather than Critical.

### Recommendation
- Avoid running the full `Self::execute()` pipeline inside `validate_unsigned`; instead perform a cheap, non-mutating structural/signature check sufficient to compute `provides`/`priority`, and defer expensive proof verification to actual block execution (or ensure duplicate/near-duplicate submissions cannot cheaply force repeated full verification).
- Introduce a per-submitter or per-block cap on the amount of proof-verification work admissible via unsigned `handle_unsigned` transactions (e.g., weight-based rate limiting analogous to the `pallet-bandwidth` byte-metering already used for inbound requests), so a flood of free-but-expensive submissions cannot monopolize collator block-building capacity.
- Reduce `longevity` for message batches with no `has_consensus` flag or otherwise ensure repeated re-validation of the same underlying proof does not repeat the expensive verification path.

### Proof of Concept
1. An attacker (no special privilege, no signed key required) repeatedly crafts `Message::Timeout` or `Message::Request` batches referencing many distinct — but individually cheap-to-obtain — proofs (e.g., resubmitting variations with different `signer` bytes as shown to be sufficient for unique `provides` tags in `modules/pallets/testsuite/src/tests/pallet_ismp.rs:558-606`).
2. Each submission triggers `validate_unsigned` → `Self::execute(messages.clone())` on every collator, performing full proof verification for free.
3. Attacker submits these in a sustained stream, exceeding normal message throughput; collators spend disproportionate CPU/time re-validating and building blocks around the flood.
4. A legitimate pending `PostRequest` nearing its `timeout_timestamp`, or a consensus update required to keep a state machine's client live, fails to be included in time, causing the destination to reject it as timed out (per `docs/content/protocol/ismp/timeouts.mdx:8-12`) and freezing the relayer fee/refund flow until a timeout message can itself be included — which is subject to the same congestion.

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

**File:** modules/pallets/ismp/src/lib.rs (L614-645)
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

			if let Some((state_machine_id, latest_height)) = events.iter().find_map(|event| {
				if let ismp::events::Event::StateMachineUpdated(state_machine_updated_event) = event
				{
					Some((
						state_machine_updated_event.state_machine_id.clone(),
						state_machine_updated_event.latest_height,
					))
				} else {
					None
				}
			}) {
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
			}
```

**File:** modules/pallets/ismp/src/lib.rs (L694-715)
```rust
			if tags.is_empty() {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&tags.encode()).to_vec();

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
		}
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-259)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.

```
