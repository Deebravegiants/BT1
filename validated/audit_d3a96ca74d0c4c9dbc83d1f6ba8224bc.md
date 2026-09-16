## Title
Quadratic-complexity GRANDPA ancestry verification lets an unsigned, zero-weight consensus message DoS `pallet-ismp` nodes - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`GrandpaJustification::verify_with_voter_set` re-walks the submitted header chain from scratch for every precommit in a justification, giving the verification step `O(precommits × unknown_headers)` cost. Because `ConsensusMessage`s are billed `Weight::zero()` and are executed via the free, unsigned `handle_unsigned` extrinsic (validated by every node that receives the gossiped transaction), an attacker can submit a single GRANDPA consensus update whose `FinalityProof.unknown_headers` and `commit.precommits` are both maximized to force every relaying node to perform a large, unbilled `O(n²)`-style computation — the same "linear-per-item re-scan repeated across many items" bug class as the Suricata http1 header-parsing quadratic-complexity CVE.

### Finding Description
`AncestryChain::ancestry` performs a linear walk of the header map from a target hash back to a base hash: [1](#0-0) 

`GrandpaJustification::verify_with_voter_set` calls this `ancestry()` walk **once per precommit** in the justification's commit: [2](#0-1) 

`self.commit.precommits` is sized by the number of voting GRANDPA authorities (can be hundreds), and each call to `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)` walks up to the full length of `finality_proof.unknown_headers` (an attacker-supplied `Vec<H>`, bounded only by block/extrinsic size limits, not by any dedicated cap). The result is `O(precommits × unknown_headers.len())` work for a single proof — structurally identical to the Suricata bug class where a per-unit (per-packet / per-precommit) operation re-scans an accumulated, attacker-growable structure instead of amortizing the cost.

This routine is reached from `verify_grandpa_finality_proof`, the entry point used for both standalone-chain and relaychain GRANDPA consensus updates: [3](#0-2) 

Critically, `ConsensusMessage` handling is priced at **zero weight**: [4](#0-3) 

and it is dispatched through `pallet_ismp::Call::handle_unsigned`, an unsigned, permissionless extrinsic that is fully executed once during `validate_unsigned` (run by every node that receives the gossiped transaction, before it is even included in a block) and again during actual dispatch: [5](#0-4) [6](#0-5) 

### Impact Explanation
Since `handle_unsigned` is free (unsigned, `Weight::zero()` for consensus messages) and validated by every peer node on gossip, an attacker can craft a single GRANDPA `FinalityProof` maximizing both `unknown_headers` length and the number of `precommits`, causing disproportionate CPU consumption on every node that validates the transaction pool candidate — a network-wide compute amplification triggered by one submitted extrinsic. This matches the "route unable to deliver messages" / DoS class called out as acceptable impact: sustained submission of such proofs can stall block production or consensus-client updates on affected chains, since the relaychain/standalone GRANDPA client is a prerequisite for delivering all ISMP messages routed through it.

### Likelihood Explanation
Reachability requires no privilege: `handle_unsigned` is explicitly documented as permissionless/unsigned and is the standard path relayers use to submit GRANDPA consensus updates. `FinalityProof.unknown_headers` and the justification's `commit.precommits` are both attacker-controlled inputs from the wire proof, decoded with no dedicated per-request cap tied to authority-set size, so the quadratic blow-up is directly triggerable by any party able to submit a transaction/extrinsic to a node's pool.

### Recommendation
Compute the ancestry route once (e.g., build a single parent-hash walk from the highest target down to `base_hash`, or memoize visited nodes across precommits) instead of re-invoking `ancestry_chain.ancestry()` per precommit. Additionally, weight/fee `ConsensusMessage` proportional to `unknown_headers.len()` and `precommits.len()` (or enforce explicit caps matching the known authority-set size and epoch length) so verification cost is bounded and priced rather than free and unbounded.

### Proof of Concept
1. Construct a `FinalityProof<H>` with `unknown_headers` containing `N` chained headers (attacker-controlled, bounded only by extrinsic size limits).
2. Construct a `GrandpaJustification` whose `commit.precommits` contains `V` precommits (up to the authority-set size) each targeting the highest header in `unknown_headers`.
3. Wrap it in a `ConsensusMessage` and submit via `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(msg)] }` as an unsigned extrinsic.
4. `validate_unsigned` (run by every receiving node, for free) calls `Self::execute` → `handle_incoming_message` → `verify_grandpa_finality_proof` → `GrandpaJustification::verify` → `verify_with_voter_set`, performing `O(V×N)` map walks with `Weight::zero()` accounted cost, before the signature check even fully rejects an otherwise-invalid vote set — repeat submission amplifies load across the network's tx-pool validators.

### Citations

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L180-197)
```rust
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L42-93)
```rust
/// This function verifies the GRANDPA finality proof for both standalone chain and parachain
/// headers.
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

	if justification.commit.target_hash != finality_proof.block {
		Err(Error::JustificationTargetMismatch)?;
	}

	let from = consensus_state.latest_hash;

	let base = finality_proof
		.unknown_headers
		.iter()
		.min_by_key(|h| *h.number())
		.ok_or(Error::UnknownHeadersEmpty)?;

	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;

	// 2. verify justification.
	justification
		.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
		.map_err(|e| Error::JustificationVerify(e.to_string()))?;
```

**File:** modules/ismp/core/src/handlers.rs (L73-82)
```rust
impl MessageResult {
	/// Returns the total weight consumed by this message
	pub fn weight(&self) -> Weight {
		match self {
			MessageResult::Request { weight, .. } => *weight,
			MessageResult::Response { weight, .. } => *weight,
			MessageResult::Timeout { weight, .. } => *weight,
			MessageResult::ConsensusMessage(_) | MessageResult::FrozenClient(_) => Weight::zero(),
		}
	}
```

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
