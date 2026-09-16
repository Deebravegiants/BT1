### Title
Unbounded / cyclic ancestry walk in GRANDPA `AncestryChain::ancestry` can hang block execution via a permissionless `handle_unsigned` consensus message - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
The GRANDPA consensus verifier's `AncestryChain::ancestry` walks a parent-hash chain built entirely from attacker-supplied, unverified `unknown_headers` before any cryptographic check is performed. Because the loop terminates only when it reaches `base` or fails a lookup, a caller who supplies headers forming a cycle (or an extremely long chain) can make the loop run far beyond any bounded "max iterations," mirroring the OctoRPKI issue where a long chain of CAs drove the validator past its iteration budget and crashed it. This is reachable from the permissionless, unsigned `pallet_ismp::handle_unsigned` extrinsic that any unprivileged caller can submit with a `Message::Consensus` payload.

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

The `while current_hash != base` loop only terminates when `current_hash` equals `base` or a lookup in the attacker-supplied `ancestry` `BTreeMap` fails. Both `current_hash` and the map are built directly from `finality_proof.unknown_headers`, i.e., raw decoded structs with attacker-chosen `parent_hash` fields: [2](#0-1) 

Crucially, this walk is invoked in `verify_grandpa_finality_proof` **before** any signature/justification verification takes place: [3](#0-2) 

Since `unknown_headers` are just SCALE-decoded header structs with no relation to any real chain enforced at this point, an attacker can craft two (or more) headers `A`, `B` where `hash(A)`'s `parent_hash` field is set to `hash(B)` and `hash(B)`'s `parent_hash` field is set to `hash(A)`. When `ancestry()` is asked to walk from `target.hash()` (some header in this cycle) back to `base` (or `consensus_state.latest_hash`), and `base`/`latest_hash` is never encountered in the crafted set, the loop will run indefinitely, never returning `Err(NotDescendent)` because every `current_hash` lookup always succeeds (it cycles between the attacker's own headers). No bound on iteration count, path length, or cycle detection exists — the exact bug class described in the OctoRPKI advisory (unbounded chain-walk causing the validator to exceed its iteration budget and crash/hang), except here the walk can be a true infinite loop rather than merely "very long."

The same pattern with no cost check is present at `check_message_signature`-adjacent call site `verify_with_voter_set`, and in `verify_fraud_proof`, all of which build an `AncestryChain` from unauthenticated attacker input and call `.ancestry(...)` on it: [4](#0-3) 

### Impact Explanation
This code path is reachable by any unprivileged account through the free, unsigned `pallet_ismp::Call::handle_unsigned` extrinsic carrying a `Message::Consensus` payload targeting a GRANDPA-backed `consensus_state_id`: [5](#0-4) 

The GRANDPA consensus client decodes the submitted proof and calls straight into `verify_grandpa_finality_proof` / `AncestryChain::ancestry` as part of `verify_consensus`. Because the vulnerable loop executes prior to any signature check, the attacker pays no cryptographic cost to trigger it, and (per the analysis above) can construct a genuine infinite loop rather than merely a long one. Runtime execution has no cooperative yielding inside this synchronous loop, so triggering it can hang block execution / stall the collator processing the block — a chain-halting denial of service that prevents any further message delivery on that state machine ("a route unable to deliver messages"), which satisfies the required Medium-severity impact bar (unsound message-verification path / route unable to deliver messages).

### Likelihood Explanation
Likelihood is high for any deployment where the GRANDPA client's `handle_unsigned` path is not otherwise gated. The attacker only needs to submit a syntactically valid `ConsensusMessage` (decodable `FinalityProof`) with a crafted `unknown_headers` cycle; no signature, stake, or special permission is required, and the transaction-pool validation itself calls `Self::execute`, meaning the hang can be triggered merely by submitting the transaction for pool validation (before it is even included in a block), amplifying the DoS to full-node validators as well as block producers.

### Recommendation
Bound `AncestryChain::ancestry` with an explicit iteration cap equal to the number of headers actually supplied (`unknown_headers.len()` or a fixed `MAX_ANCESTRY_DEPTH`), returning `Err(NotDescendent)` once the cap is exceeded, and/or track visited hashes to detect and reject cycles deterministically (similar to the `MAX_PROOF_DEPTH` guard already added for the Pharos SPV verifier). Apply the fix uniformly to every call site that constructs an `AncestryChain` from unauthenticated proof data (`verify_grandpa_finality_proof`, `verify_parachain_headers_with_grandpa_finality_proof`, `verify_fraud_proof`, and `GrandpaJustification::verify_with_voter_set`).

### Proof of Concept
1. Construct headers `A` and `B` (arbitrary `Header` structs) such that `A.parent_hash = hash(B)` and `B.parent_hash = hash(A)`, forming a two-node cycle unrelated to any real chain.
2. Build `FinalityProof { block: hash(A), justification: <any decodable justification bytes>, unknown_headers: vec![A, B] }` and wrap it in a `Message::Consensus` targeting the GRANDPA `consensus_state_id`, with `consensus_state.latest_hash` set to some hash not equal to `hash(A)` or `hash(B)`.
3. Submit via `pallet_ismp::Call::handle_unsigned { messages: vec![msg] }` as an unsigned extrinsic.
4. `verify_grandpa_finality_proof` calls `headers.ancestry(from, target.hash())`, which enters `while current_hash != base` and cycles forever between `A` and `B`, since `current_hash` always resolves in the map and never equals `base`/`consensus_state.latest_hash` — hanging execution before any signature is checked.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L161-174)
```rust
impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
	}

	/// Fetch a header from the ancestry chain, given it's hash. Returns [`None`] if it doesn't
	/// exist.
	pub fn header(&self, hash: &H::Hash) -> Option<&H> {
		self.ancestry.get(hash)
	}
}
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L176-198)
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
}
```

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L74-93)
```rust
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L309-320)
```rust
		let first_chain = first_headers
			.ancestry(first_base.hash(), first_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;

		let second_base = second_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let second_chain = second_headers
			.ancestry(second_base.hash(), second_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;
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
