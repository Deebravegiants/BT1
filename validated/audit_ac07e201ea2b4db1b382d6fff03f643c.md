### Title
Free, unsigned `handle_unsigned` fully executes attacker-supplied consensus messages during mempool validation, enabling unbounded computational resource consumption — (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet_ismp::Pallet::handle_unsigned` is a permissionless, unsigned, fee-free extrinsic [1](#0-0)  whose `ValidateUnsigned::validate_unsigned` implementation does not perform any cheap pre-check before running the full message-processing pipeline: it calls `Self::execute(messages.clone())`, which decodes and verifies every submitted `Message` — including consensus proofs — inside mempool validation, on every full node in the network, for free [2](#0-1) . This mirrors the OPC UA Legacy Java Stack bug class (CVE-2023-32787): a single, cheaply crafted message triggers disproportionate resource consumption on every server (node) that has to validate it, without the sender bearing a comparable cost.

### Finding Description
`execute()` iterates every `Message` and calls `handle_incoming_message`, invoking consensus-client verification for `Message::Consensus` payloads [3](#0-2) . For the GRANDPA consensus client, this reaches `verify_grandpa_finality_proof`, which SCALE-decodes an attacker-controlled `justification` and an attacker-controlled `unknown_headers: Vec<H>` with no size bound enforced by the verifier itself [4](#0-3) . It then calls `justification.verify()`, which performs an ED25519 `check_message_signature` for every precommit and, for each precommit, walks `AncestryChain::ancestry()` — a loop that follows parent hashes through a `BTreeMap` until it reaches the base hash [5](#0-4) [6](#0-5) .

Unlike the BEEFY proof path, which is gated behind a `BoundedVec<u8, MaxProofSize>` at the extrinsic decode stage before any verification work happens [7](#0-6) , `pallet_ismp::Call::handle_unsigned` takes an unbounded `messages: Vec<Message>` [8](#0-7) , and its `validate_unsigned` runs the entire `execute()` pipeline — full signature checks and ancestry walks over attacker-supplied precommits/headers — before rejecting an invalid submission [2](#0-1) . Because the call is unsigned (`ensure_none`) and explicitly documented as "free" [9](#0-8) , an attacker pays nothing to force this work, and every node that receives the transaction over the p2p gossip layer independently re-runs the same expensive validation in its own transaction-pool `validate_unsigned` call, before the extrinsic can ever be included in a block.

### Impact Explanation
An attacker can craft consensus messages with large numbers of bogus precommits/headers (bounded only by block-length/extrinsic-size limits, not by any semantic limit in the GRANDPA verifier or `pallet_ismp`), and gossip them repeatedly to the network. Each copy forces every full/collator node to perform costly SCALE decoding, N signature verifications, and N ancestry walks in `validate_unsigned` before rejecting the transaction — at zero cost to the submitter (unsigned, no fee) and with the transaction pool's only counter-measure being a fixed `longevity: 25` / dedup by content hash, which an attacker can trivially defeat by varying the payload bytes. This can degrade or block honest relayers' consensus updates and request/response delivery, i.e., a route unable to deliver messages, matching the CVSS 7.5 (availability-only) profile of CVE-2023-32787.

### Likelihood Explanation
High. `handle_unsigned` is intentionally permissionless and unsigned by design so that relaying is fee-free for legitimate relayers [10](#0-9) , meaning any network participant that can submit a transaction to the p2p network can reach this path with no economic barrier. Crafting a `ConsensusMessage` containing many precommits/unknown headers requires no special privilege or valid cryptographic material other than syntactically valid SCALE encoding.

### Recommendation
Add cheap, size-bounded pre-checks in `validate_unsigned` (and ideally at the type level, similar to BEEFY's `BoundedVec<u8, MaxProofSize>`) before any consensus-proof verification is attempted — e.g., bound the number of `unknown_headers` and `precommits`/signatures per `Message::Consensus` submission, and reject oversized batches immediately without decoding/verifying their cryptographic contents. Consider also charging a minimal computational cost or requiring a bond for consensus messages that fail validation repeatedly, to disincentivize resource-exhaustion spam via unsigned transactions.

### Proof of Concept
1. Construct a `GrandpaJustification` whose `commit.precommits` vector contains a very large number of syntactically valid (but for unrelated/bogus) `SignedPrecommit` entries, and a `FinalityProof.unknown_headers` containing a long, deep chain of headers.
2. Wrap it in `Message::Consensus(ConsensusMessage { consensus_proof: encoded_justification_and_headers, .. })` and submit as `pallet_ismp::Call::handle_unsigned { messages: vec![msg] }` via `submit_and_watch` as an unsigned extrinsic, per the pattern used in `parachain/simtests/src/pallet_ismp.rs` [11](#0-10) .
3. Observe that `validate_unsigned` executes `Self::execute(messages.clone())` fully, running `verify_grandpa_finality_proof` → `justification.verify()`, performing signature checks and `AncestryChain::ancestry()` walks proportional to the crafted precommit/header count, on every node validating the gossiped transaction — before ultimately rejecting it as invalid, at no cost to the submitter.

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

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
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

**File:** modules/pallets/ismp/src/impls.rs (L37-51)
```rust
impl<T: Config> Pallet<T> {
	/// Execute the provided ISMP datagrams, this will short circuit if any messages are invalid.
	/// This also charges fee on valid message delivery
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L44-68)
```rust
pub fn verify_grandpa_finality_proof<H>(
	mut consensus_state: ConsensusState,
	finality_proof: FinalityProof<H>,
) -> Result<(ConsensusState, H, Vec<H256>, AncestryChain<H>), Error>
where
	H: Header<Hash = H256, Number = u32>,
	H::Number: finality_grandpa::BlockNumberOps + Into<u32>,
{
	// First validate unknown headers.
	let headers = AncestryChain::<H>::new(&finality_proof.unknown_headers);

	let target = finality_proof
		.unknown_headers
		.iter()
		.max_by_key(|h| *h.number())
		.ok_or(Error::UnknownHeadersEmpty)?;

	// this is illegal
	if target.hash() != finality_proof.block {
		Err(Error::LatestBlockMismatch)?;
	}

	let justification =
		GrandpaJustification::<H>::decode_all(&mut &finality_proof.justification[..])
			.map_err(|e| Error::DecodeJustification(alloc::format!("{e:?}")))?;
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L109-134)
```rust
		let mut visited_hashes = BTreeSet::new();
		for signed in self.commit.precommits.iter() {
			let message = finality_grandpa::Message::Precommit(signed.precommit.clone());

			check_message_signature::<_, _>(
				&message,
				&signed.id,
				&signed.signature,
				self.round,
				set_id,
			)?;

			if base_hash == signed.precommit.target_hash {
				continue;
			}

			let route = ancestry_chain
				.ancestry(base_hash, signed.precommit.target_hash)
				.map_err(|_| anyhow!("[verify_with_voter_set] Invalid ancestry!"))?;
			// ancestry starts from parent hash but the precommit target hash has been
			// visited
			visited_hashes.insert(signed.precommit.target_hash);
			for hash in route {
				visited_hashes.insert(hash);
			}
		}
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L176-197)
```rust
impl<H: HeaderT> finality_grandpa::Chain<H::Hash, H::Number> for AncestryChain<H>
where
	H::Number: finality_grandpa::BlockNumberOps,
{
	fn ancestry(
		&self,
		base: H::Hash,
		block: H::Hash,
	) -> Result<Vec<H::Hash>, finality_grandpa::Error> {
		let mut route = vec![block];
		let mut current_hash = block;
		while current_hash != base {
			match self.ancestry.get(&current_hash) {
				Some(current_header) => {
					current_hash = *current_header.parent_hash();
					route.push(current_hash);
				},
				_ => return Err(finality_grandpa::Error::NotDescendent),
			};
		}
		Ok(route)
	}
```

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L355-366)
```rust
	// 6. submit_proof oversized payload — `proof: BoundedVec<u8, MaxProofSize>` rejects at the
	//    txpool decode stage, before dispatch. We send `MaxProofSize + 1` bytes prefixed with
	//    `PROOF_TYPE_NAIVE`.
	let mut oversized_proof = vec![PROOF_TYPE_NAIVE; MAX_PROOF_SIZE + 1];
	oversized_proof[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&oversized_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "oversized submit_proof must be rejected by the BoundedVec decode",);
```

**File:** modules/pallets/ismp/README.md (L34-35)
```markdown
- `handle` - Handles incoming ISMP messages.
- `handle_unsigned` Unsigned variant for handling incoming messages, enabled by `feature = ["unsigned"]`
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L253-258)
```text
| `handle_unsigned` | Unsigned | Execute the provided batch of ISMP messages for free with valid proofs. This will short-circuit and revert if any of the provided messages are invalid. |
| `fund_message` | Signed | Increase the relayer fee for in-flight requests and responses to incentivize their delivery. Should not be called on a message that has been completed (delivered or timed-out) as those funds will be lost forever. |

## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** parachain/simtests/src/pallet_ismp.rs (L282-293)
```rust
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
