### Title
Quadratic-cost GRANDPA ancestry traversal in `verify_justification` is not captured by the linear `submit_finality_proof` weight formula - (File: bridges/primitives/header-chain/src/justification/verification/mod.rs, bridges/modules/grandpa/src/lib.rs)

### Summary
`submit_finality_proof_ex` charges pre-dispatch weight as a linear function of `precommits.len()` (`p`) and `votes_ancestries.len()` (`v`), but the actual verification loop in `JustificationVerifier::verify_justification` can perform `O(p*v)` work when an attacker crafts a justification whose `votes_ancestries` form multiple disjoint branches that each precommit must fully traverse. The optional economic penalty for oversized `votes_ancestries` is a flat "charge full call weight" rule that is itself derived from the same linear formula, so it does not account for the quadratic blow-up.

### Finding Description
`submit_finality_proof_ex` computes its dispatch weight straight from the caller-supplied vector lengths: [1](#0-0) 

`verify_justification::<T, I>` internally calls into `JustificationVerifier::verify_justification`, which iterates once over `precommits` (bounded by `p`), and for every precommit calls `chain.ancestry(...)` to walk backward through the `votes_ancestries` parent map until it reaches the base header or a node marked "visited": [2](#0-1) [3](#0-2) 

The "already visited" short-circuit (`is_visited_before`) only helps when precommit routes overlap on a common suffix. An attacker who builds `votes_ancestries` as several disjoint branches (a tree rather than a single chain) and points each of the `p` precommits at a distinct branch forces `ancestry()` to walk close to the full branch length (`~v/branch_count`) for every precommit, giving total traversal work close to `O(p * v)` rather than the `O(p + v)` implicitly assumed by the benchmark model: [4](#0-3) 

The weight formula only has independent linear terms in `p` and `v` (`Weight::from_parts(...).saturating_mul(p.into())` plus a separate term for `v`), with no `p*v` cross term, so it structurally cannot express super-linear cost.

There is also no hard, in-pallet cap on `votes_ancestries.len()`. The only mitigation is `submit_finality_proof_limits_extras`, which merely flags `is_weight_limit_exceeded` when `votes_ancestries_len > REASONABLE_HEADERS_IN_JUSTIFICATION_ANCESTRY` and, if so, charges the *entire* (still linearly computed) call weight as "extra" via an optional transaction extension registered at the runtime level: [5](#0-4) [6](#0-5) 

This extension is a signed extension that a runtime may or may not wire in; even when present, it does not change the underlying linear weight formula used to price the call - it just avoids a partial refund. It does not reject the call for having an adversarial branching ancestry structure, nor does it scale the charged fee/weight quadratically to match worst-case traversal cost.

### Impact Explanation
Because dispatch weight is priced linearly in `p` and `v` while actual worst-case verification cost can be quadratic (`p*v`), a relayer/attacker can submit a `submit_finality_proof_ex` call whose real CPU cost during block execution substantially exceeds the weight it was charged for. If crafted aggressively enough (large validator set count `p` combined with a maximally-sized, deeply branched `votes_ancestries` vector, up to whatever the block/extrinsic length limit allows), this can push actual execution time beyond the block's allotted time budget, risking a block-production/import stall (bridge or parachain-level DoS) - matching the "Bridge halt / chain halt" impact category.

### Likelihood Explanation
- The call is fully public/unprivileged (`ensure_signed(origin)?` only) — any signed account can submit it.
- The justification's `commit.precommits` and `votes_ancestries` are entirely attacker-controlled bytes/data before verification runs; the only precondition is producing a syntactically valid `GrandpaJustification` (the signature checks on precommits will still run at O(p) cost regardless of whether the votes ultimately count, and the ancestry traversal cost is incurred before/at the point where a route is proven or rejected).
- Building a large, deliberately-branched `votes_ancestries` structure that still validates (or fails only after full traversal) requires knowledge of `finality-grandpa` mechanics but no privileged access.
- Repeatability is straightforward: the same shape of justification can be resubmitted with different `finality_target`/`current_set_id` values as long as it beats `check_obsolete`.

### Recommendation
- Change the `votes_ancestries` traversal to a strictly bounded-cost algorithm, e.g., pre-compute a single ancestor-depth map / topologically bound the number of hash lookups so total cost is provably `O(p + v)` regardless of branch structure (e.g., cap traversal per precommit or memoize depth from a single pass instead of restarting `ancestry()` per precommit).
- Add a hard, non-refundable cap on `votes_ancestries.len()` in-pallet (enforced before verification, not just economically discouraged via an optional runtime-level extension), rejecting the call outright if exceeded rather than merely charging extra fee.
- If quadratic cost cannot be eliminated, update the weight formula in `bridges/modules/grandpa/src/weights.rs`/benchmarking to include a `p * v` term so pre-dispatch weight actually bounds worst-case execution time.

### Proof of Concept
Rust integration test plan (in `bridges/primitives/header-chain` or `bridges/modules/grandpa` test suite):
1. Build a `GrandpaJustification` where `votes_ancestries` forms `k` disjoint branches, each of length `v/k`, rooted at `finality_target`.
2. Construct `commit.precommits` with `p` (~`MAX_AUTHORITIES_COUNT`) valid signed precommits, each one targeting the tip of a distinct branch (round-robin across the `k` branches) so that `ancestry()` cannot short-circuit via the `is_visited_before` check for most precommits.
3. Measure actual instruction/time cost of `verify_and_optimize_justification`/`verify_justification` for this input versus a "chain-shaped" justification with identical `p`/`v` (single branch, precommits reusing the same route).
4. Assert that the branched-structure justification's measured execution time/instruction count is asymptotically larger (approaching `O(p*v)`) than the chain-shaped one, while `T::WeightInfo::submit_finality_proof(p, v)` returns the *same* weight for both (since it is purely a function of `p` and `v`), demonstrating the charged weight does not reflect actual worst-case cost.

### Citations

**File:** bridges/modules/grandpa/src/lib.rs (L279-283)
```rust
		#[pallet::call_index(4)]
		#[pallet::weight(T::WeightInfo::submit_finality_proof_weight(
			justification.commit.precommits.len().saturated_into(),
			justification.votes_ancestries.len().saturated_into(),
		))]
```

**File:** bridges/primitives/header-chain/src/justification/verification/mod.rs (L92-131)
```rust
	pub fn ancestry(
		&self,
		precommit_target_hash: &Header::Hash,
		precommit_target_number: &Header::Number,
	) -> Option<Vec<Header::Hash>> {
		if precommit_target_number < &self.base.number() {
			return None;
		}

		let mut route = vec![];
		let mut current_hash = *precommit_target_hash;
		loop {
			if current_hash == self.base.hash() {
				break;
			}

			current_hash = match self.parent_hash_of(&current_hash) {
				Some(parent_hash) => {
					let is_visited_before = self.unvisited.get(&current_hash).is_none();
					if is_visited_before {
						// If the current header has been visited in a previous call, it is a
						// descendent of `base` (we assume that the previous call was successful).
						return Some(route);
					}
					route.push(current_hash);

					*parent_hash
				},
				None => return None,
			};
		}

		Some(route)
	}

	fn mark_route_as_visited(&mut self, route: Vec<Header::Hash>) {
		for hash in route {
			self.unvisited.remove(&hash);
		}
	}
```

**File:** bridges/primitives/header-chain/src/justification/verification/mod.rs (L260-322)
```rust
		for (precommit_idx, signed) in justification.commit.precommits.iter().enumerate() {
			if cumulative_weight >= threshold {
				let action =
					self.process_redundant_vote(precommit_idx).map_err(Error::Precommit)?;
				if matches!(action, IterationFlow::Skip) {
					continue;
				}
			}

			// authority must be in the set
			let authority_info = match context.voter_set.get(&signed.id) {
				Some(authority_info) => {
					// The implementer may want to do extra checks here.
					// For example to see if the authority has already voted in the same round.
					let action = self
						.process_known_authority_vote(precommit_idx, signed)
						.map_err(Error::Precommit)?;
					if matches!(action, IterationFlow::Skip) {
						continue;
					}

					authority_info
				},
				None => {
					self.process_unknown_authority_vote(precommit_idx).map_err(Error::Precommit)?;
					continue;
				},
			};

			// all precommits must be descendants of the target block
			let maybe_route =
				chain.ancestry(&signed.precommit.target_hash, &signed.precommit.target_number);
			if maybe_route.is_none() {
				let action = self
					.process_unrelated_ancestry_vote(precommit_idx)
					.map_err(Error::Precommit)?;
				if matches!(action, IterationFlow::Skip) {
					continue;
				}
			}

			// verify authority signature
			if !sp_consensus_grandpa::check_message_signature_with_buffer(
				&finality_grandpa::Message::Precommit(signed.precommit.clone()),
				&signed.id,
				&signed.signature,
				justification.round,
				context.authority_set_id,
				&mut signature_buffer,
			)
			.is_valid()
			{
				self.process_invalid_signature_vote(precommit_idx).map_err(Error::Precommit)?;
				continue;
			}

			// now we can count the vote since we know that it is valid
			self.process_valid_vote(signed);
			if let Some(route) = maybe_route {
				chain.mark_route_as_visited(route);
				cumulative_weight = cumulative_weight.saturating_add(authority_info.weight().get());
			}
		}
```

**File:** bridges/modules/grandpa/src/weights.rs (L100-112)
```rust
	fn submit_finality_proof(p: u32, v: u32) -> Weight {
		// Proof Size summary in bytes:
		//  Measured:  `394 + p * (60 ±0)`
		//  Estimated: `4745`
		// Minimum execution time: 228_072 nanoseconds.
		Weight::from_parts(57_853_228, 4745)
			// Standard Error: 149_421
			.saturating_add(Weight::from_parts(36_708_702, 0).saturating_mul(p.into()))
			// Standard Error: 10_625
			.saturating_add(Weight::from_parts(1_469_032, 0).saturating_mul(v.into()))
			.saturating_add(T::DbWeight::get().reads(6_u64))
			.saturating_add(T::DbWeight::get().writes(6_u64))
	}
```

**File:** bridges/primitives/header-chain/src/lib.rs (L336-372)
```rust
pub fn submit_finality_proof_limits_extras<C: ChainWithGrandpa>(
	header: &C::Header,
	proof: &justification::GrandpaJustification<C::Header>,
) -> SubmitFinalityProofCallExtras {
	// the `submit_finality_proof` call will reject justifications with invalid, duplicate,
	// unknown and extra signatures. It'll also reject justifications with less than necessary
	// signatures. So we do not care about extra weight because of additional signatures here.
	let precommits_len = proof.commit.precommits.len().saturated_into();
	let required_precommits = precommits_len;

	// the weight check is simple - we assume that there are no more than the `limit`
	// headers in the ancestry proof
	let votes_ancestries_len: u32 = proof.votes_ancestries.len().saturated_into();
	let is_weight_limit_exceeded =
		votes_ancestries_len > C::REASONABLE_HEADERS_IN_JUSTIFICATION_ANCESTRY;

	// check if the `finality_target` is a mandatory header. If so, we are ready to refund larger
	// size
	let is_mandatory_finality_target =
		GrandpaConsensusLogReader::<BlockNumberOf<C>>::find_scheduled_change(header.digest())
			.is_some();

	// we can estimate extra call size easily, without any additional significant overhead
	let actual_call_size: u32 =
		header.encoded_size().saturating_add(proof.encoded_size()).saturated_into();
	let max_expected_call_size = max_expected_submit_finality_proof_arguments_size::<C>(
		is_mandatory_finality_target,
		required_precommits,
	);
	let extra_size = actual_call_size.saturating_sub(max_expected_call_size);

	SubmitFinalityProofCallExtras {
		is_weight_limit_exceeded,
		extra_size,
		is_mandatory_finality_target,
	}
}
```

**File:** bridges/modules/grandpa/src/call_ext.rs (L272-298)
```rust
	// check if call exceeds limits. In other words - whether some size or weight is included
	// in the call
	let extras =
		submit_finality_proof_limits_extras::<T::BridgedChain>(finality_target, justification);

	// We do care about extra weight because of more-than-expected headers in the votes
	// ancestries. But we have problems computing extra weight for additional headers (weight of
	// additional header is too small, so that our benchmarks aren't detecting that). So if there
	// are more than expected headers in votes ancestries, we will treat the whole call weight
	// as an extra weight.
	let extra_weight = if extras.is_weight_limit_exceeded {
		let precommits_len = justification.commit.precommits.len().saturated_into();
		let votes_ancestries_len = justification.votes_ancestries.len().saturated_into();
		T::WeightInfo::submit_finality_proof(precommits_len, votes_ancestries_len)
	} else {
		Weight::zero()
	};

	SubmitFinalityProofInfo {
		block_number: *finality_target.number(),
		current_set_id,
		is_mandatory: extras.is_mandatory_finality_target,
		is_free_execution_expected,
		extra_weight,
		extra_size: extras.extra_size,
	}
}
```
