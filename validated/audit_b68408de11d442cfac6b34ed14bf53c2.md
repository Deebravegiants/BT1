Given the search results, the closest reachable analog to the css-what "non-linear complexity in attribute parsing" bug class is in the GRANDPA justification verifier, where an unbounded, attacker-supplied `votes_ancestries`/`precommits` list drives per-precommit ancestry walks — a quadratic-time proof-verification cost triggerable via the permissionless `pallet-ismp::handle_unsigned` extrinsic.

### Title
Unbounded GRANDPA justification precommits/ancestries enable O(n·m) verification cost DoS - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`GrandpaJustification::verify_with_voter_set` iterates every precommit in `self.commit.precommits` and, for each one that doesn't already sit at the `base_hash`, calls `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)`, which itself walks parent-hash pointers one step at a time through `self.ancestry` (built from the attacker-supplied `votes_ancestries` header list) until it reaches `base`. [1](#0-0)  Neither `precommits.len()` nor `votes_ancestries.len()` nor the depth of any single ancestry walk is bounded before this loop runs; `grep_search` for `MAX_VOTES`/`MAX_PRECOMMITS` found no such constant defined anywhere in the crate. This mirrors the css-what class of bug: the parser (proof verifier) does not guarantee linear-time complexity relative to the size of attacker-controlled input, so a crafted, large-but-otherwise-well-formed structure can force disproportionate CPU work.

### Finding Description
`AncestryChain::ancestry` performs a linear walk of up to `votes_ancestries.len()` steps per call. [2](#0-1)  `verify_with_voter_set` invokes this walk once per precommit whose target differs from `base_hash`. [3](#0-2)  Both `precommits` and `votes_ancestries` are fields of the SCALE-decoded, attacker-supplied `GrandpaJustification<H>` with no declared size cap, so the total verification cost for a single justification is `O(precommits × ancestry_length)`, i.e. quadratic in the size of the submitted proof rather than linear.

This justification reaches on-chain execution through the permissionless `pallet_ismp::Call::handle_unsigned` extrinsic, which anyone can submit unsigned and which is validated then executed via `Self::execute(messages.clone())` before block inclusion. [4](#0-3)  `IsmpCallFilter` on the nexus runtime explicitly permits BEEFY exclusion but does not filter GRANDPA-tagged consensus messages, and `grandpa-verifier`'s `verify_grandpa_finality_proof` calls `justification.verify(...)` unconditionally on the submitted bytes. [5](#0-4) 

Because `handle_unsigned` is validated via `ValidateUnsigned::validate_unsigned`, which itself calls `Self::execute` to determine transaction validity, the expensive verification work is performed during transaction-pool validation (potentially repeatedly, on every peer/collator that receives the gossiped extrinsic) even before block inclusion is guaranteed. [6](#0-5) 

### Impact Explanation
A single unsigned extrinsic carrying a crafted GRANDPA consensus message can force disproportionate CPU consumption during proof verification on every node that validates/executes it (block-builders, RPC nodes servicing `handle_unsigned` validation, and relayer nodes). Because message weight/fees for `handle_unsigned` are unsigned/free by design (documented as such for pallet-ismp) the attacker pays little to nothing to trigger this cost repeatedly, which can degrade block production or relayer throughput — a route-unable-to-deliver-messages / availability impact against the message dispatch pipeline.

### Likelihood Explanation
Reachable from a single relayed/dispatched message: any unprivileged actor able to submit a `pallet_ismp::handle_unsigned` extrinsic (the primary permissionless entrypoint for delivering ISMP messages) can embed a GRANDPA `ConsensusMessage` with an oversized `votes_ancestries`/`precommits` pair. No signature or fee gating on `handle_unsigned` itself increases likelihood; the only gate is the extrinsic's own proof/format validity, which the crafted values can still satisfy while being large.

### Recommendation
Bound `votes_ancestries.len()` and `commit.precommits.len()` (and/or overall justification encoded size) to protocol-appropriate maxima before performing per-precommit ancestry walks, rejecting oversized justifications early — analogous to the fix pattern already applied elsewhere in this codebase for `MAX_PROOF_DEPTH`/`MAX_VALIDATORS` bounds checks (e.g. `modules/consensus/pharos/primitives/src/spv.rs`, `modules/consensus/pharos/verifier/src/state_proof.rs`). Consider also capping the per-call ancestry walk length independent of the overall list size.

### Proof of Concept
1. Construct a `GrandpaJustification` whose `commit.precommits` contains many distinct valid signed precommits targeting many distinct block hashes, and whose `votes_ancestries` contains a long, valid parent-hash chain connecting all of them back to a common base.
2. Wrap it in a `ConsensusMessage`/`FinalityProof` and submit via `pallet_ismp::Call::handle_unsigned` as an unsigned extrinsic.
3. Observe that `verify_with_voter_set` performs `precommits.len() * average_ancestry_depth` linear scans over `votes_ancestries`, scaling quadratically with submitted proof size, with no size cap rejecting the submission beforehand.

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L90-93)
```rust
	// 2. verify justification.
	justification
		.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
		.map_err(|e| Error::JustificationVerify(e.to_string()))?;
```
