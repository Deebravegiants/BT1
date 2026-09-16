### Title
GRANDPA `AncestryChain::ancestry` has an unbounded parent-hash walk that a crafted justification can drive into an infinite loop - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
The wolfSSL CVE is a DoS caused by a message-processing state machine that never terminates when fed a crafted, out-of-order sequence of protocol messages. Hyperbridge's GRANDPA light-client verifier contains an analogous unbounded loop: `AncestryChain::ancestry` walks parent hashes from a target block back to a base block using attacker-supplied header data, with no cycle detection and no iteration bound.

### Finding Description
`AncestryChain::ancestry` walks backwards via `parent_hash()` until it reaches `base`: [1](#0-0) 

The `ancestry` map is built directly from `votes_ancestries`, a `Vec<H>` fully controlled by whoever submits the GRANDPA justification (the header hash keys are derived from each header's own encoding, but each header's `parent_hash` field is an arbitrary attacker-chosen value): [2](#0-1) 

An attacker can craft two (or more) headers `A` and `B` where `A.parent_hash = hash(B)` and `B.parent_hash = hash(A)`, forming a 2-cycle that never resolves to `base`. When `GrandpaJustification::verify_with_voter_set` calls `ancestry_chain.ancestry(base_hash, target_hash)` for a precommit whose target is part of this cycle, the `while current_hash != base` loop bounces between `A` and `B` forever, pushing to `route` on every iteration with no termination condition: [3](#0-2) 

The same unbounded `ancestry()` call is also used directly in the consensus-state-update path, `verify_grandpa_finality_proof`, reachable via the light client's `verify_consensus`/fraud-proof entry points: [4](#0-3) [5](#0-4) 

Unlike Substrate contract execution, native runtime dispatch (pallet-ismp `update_client`) has no gas metering to interrupt an unbounded native loop — the extrinsic will simply run until it hangs (or exhausts memory from the ever-growing `route` vector), matching the wolfSSL `ProcessReply()` DoS pattern of a message-processing loop with no exit condition on adversarial input.

### Impact Explanation
Any relayer/unprivileged submitter can submit a `ConsensusMessage` carrying a GRANDPA justification whose `votes_ancestries` contains a cyclic parent-hash chain. Processing this message inside `update_client` (`modules/ismp/core/src/handlers/consensus.rs`) or the GRANDPA fraud-proof path never returns, blocking block production/finalization on the collator processing it — a chain-halting availability failure, i.e. "a route unable to deliver messages" for as long as the malicious message keeps being included/retried.

### Likelihood Explanation
I could not fully confirm within the available tool calls whether pallet-ismp's dispatch path (`handle_unsigned`/signed extrinsic weight limits) or any upstream size/length bound on `votes_ancestries` prevents this cycle from being constructed and reaching `AncestryChain::ancestry` unfiltered. I was unable to load `modules/pallets/ismp/src/lib.rs` to verify the exact dispatch entry point and whether any pre-validation rejects malformed/cyclic ancestries before `verify_with_voter_set`/`verify_grandpa_finality_proof` is invoked. This is a material gap — please treat likelihood as unconfirmed until that dispatch path and any bounding on `votes_ancestries` length/well-formedness is reviewed directly in a full session.

### Recommendation
Bound `AncestryChain::ancestry` with a maximum number of iterations (e.g., ≤ `votes_ancestries.len() + 1`) and return `Error::NotDescendent` if exceeded, and/or track visited hashes in the walk to detect and reject cycles before they can loop, mirroring the loop-termination fixes already present elsewhere in the codebase (e.g., `MAX_PROOF_DEPTH` bounding in the Pharos SPV verifier).

### Proof of Concept
1. Construct header `A` with an arbitrary body such that `hash(A) = hA`, and set `A.parent_hash = hB` (a not-yet-computed placeholder).
2. Construct header `B` with `hash(B) = hB` and `B.parent_hash = hA`.
3. Include both `A` and `B` in `votes_ancestries` of a `GrandpaJustification`, and craft a precommit whose `target_hash` is `hA` (or `hB`), while `base_hash` (the lowest-numbered precommit target) is neither `hA` nor `hB`.
4. Submit this justification as a `ConsensusMessage` via the standard consensus-update path; `GrandpaJustification::verify` → `verify_with_voter_set` invokes `ancestry_chain.ancestry(base_hash, target_hash)`, which loops indefinitely bouncing between `hA` and `hB` since neither ever equals `base`.

Note: this PoC path assumes no upstream check rejects duplicate/cyclic `parent_hash` linkage in `votes_ancestries` before reaching this function — that assumption could not be fully verified in this session.

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L157-167)
```rust
pub struct AncestryChain<H: HeaderT> {
	ancestry: BTreeMap<H::Hash, H>,
}

impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
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
