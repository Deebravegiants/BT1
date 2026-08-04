### Title
`submit_finality_proof` charges linear O(p+v) weight for a justification-verification loop whose worst-case cost is O(p×v) - (File: bridges/modules/grandpa/src/lib.rs)

### Summary
The `submit_finality_proof`/`submit_finality_proof_ex` extrinsics charge weight as `T::WeightInfo::submit_finality_proof(precommits_len, votes_ancestries_len)`, which is linear in the number of precommits `p` and vote-ancestries `v`. The actual verification routine in `verify_justification` (via `AncestryChain::ancestry`) can be forced to re-traverse the whole `votes_ancestries` chain for every precommit whose signature check fails, because nodes are only marked "visited" (and thus excluded from future traversals) after a *successful* signature check. This makes the worst-case verification cost O(p×v), not O(p+v), letting an attacker submit a call that consumes far more execution time than the weight system charges for.

### Finding Description
`submit_finality_proof_ex` is weighed purely from the declared vector lengths of the submitted `justification`: [1](#0-0) 

That weight function is linear in `p` (precommits) and `v` (votes_ancestries): [2](#0-1) 

The actual verification, `JustificationVerifier::verify_justification`, iterates over every precommit and for each one calls `chain.ancestry(...)` **before** checking the precommit's signature. Only on a *successful* signature check is `chain.mark_route_as_visited(route)` invoked, which removes the traversed nodes from the `unvisited` set so future calls short-circuit: [3](#0-2) 

`AncestryChain::ancestry` walks the `parents` map from the precommit's target hash back toward the base header, and only stops early if a node was previously *visited* (i.e., previously included in a route that was later marked visited by a successful vote): [4](#0-3) 

Because `mark_route_as_visited` is skipped whenever `process_invalid_signature_vote` triggers a `continue` (invalid signature) or `process_unrelated_ancestry_vote` triggers `continue`/`Run` without success, the traversed `unvisited` nodes are never consumed. An attacker who controls the encoded `justification` can craft `p` precommits, each:
- referencing a `signed.id` present in the current `voter_set` (so it passes the "known authority" check and is not skipped before the ancestry walk),
- carrying a deliberately invalid signature,
- targeting a hash that requires walking through most/all of the `v` headers in `votes_ancestries`,

so that each of the `p` precommits independently re-walks up to `v` unvisited ancestry nodes, yielding O(p×v) BTreeMap lookups/traversal work, while the charged weight remains O(p+v).

The declared-vs-actual size/weight mismatch is explicitly acknowledged as non-strict in the codebase: [5](#0-4) 
and the compensating fee mechanism (`submit_finality_proof_limits_extras`/`is_weight_limit_exceeded`) simply charges the *whole linear* weight as an extra fee when `votes_ancestries_len` exceeds `REASONABLE_HEADERS_IN_JUSTIFICATION_ANCESTRY` — it does not account for the quadratic blow-up, and is not even enforced as a hard cap unless `is_free_execution_expected` is set: [6](#0-5) [7](#0-6) 

Thus there is no check anywhere — not in `#[pallet::weight]`, not in the transaction extension, not in the verifier itself — that bounds the true O(p×v) worst-case cost, only linear bounds on `p` and `v` individually (themselves only soft/non-strict limits, bounded in practice by block/extrinsic length).

### Impact Explanation
An unprivileged relayer (any signed account, since `submit_finality_proof`/`_ex` only requires `ensure_signed`) can submit a single crafted call whose actual execution time is quadratic in attacker-chosen `p` and `v`, while the weight meter only accounts for a linear amount. With `p` and `v` each in the hundreds to low thousands (bounded only by the block's max extrinsic length, not by any dispatch-time cap), this can produce a verification loop with far more hashing/lookups than the block's weight budget assumes, risking block-production overruns / chain stalls on the importing chain (bridge/relay-chain halt due to weight-vs-actual-time divergence), matching the "Bridge halt / chain halt" impact class.

### Likelihood Explanation
- Preconditions: pallet must be initialized (`BestFinalized` set) and not halted; attacker needs a `finality_target` header number greater than the current best (trivial, e.g. one block ahead) and a set id matching the current one (public storage, easily read).
- Feasibility: crafting `p` precommits with valid-looking `AuthorityId`s (drawn from the known `voter_set`, which is public on-chain state) but garbage/invalid signatures, plus `v` chained ancestor headers, is a pure off-chain construction, requiring no privileged access, race conditions, or third-party cooperation.
- Repeatability: the attack can be repeated every time the attacker can submit a signed extrinsic; each call independently exploits the O(p×v) blow-up since the underlying issue (marking-on-success rather than marking-on-visit) is not a one-time-fixable state, it's a code path.

### Recommendation
Mark ancestry nodes as visited (or at least as "traversed", to guarantee amortized O(v) total traversal cost) as soon as they are visited during `AncestryChain::ancestry`, independent of whether the owning precommit's signature later validates — i.e., perform the visited-bookkeeping inside/alongside the traversal itself rather than gating it on `process_valid_vote` succeeding. Alternatively, change the weight function to include a term proportional to `p * v` (or a conservative upper bound) to correctly charge for the worst-case verification cost, and/or enforce a hard (not merely fee-adjusted) cap on `votes_ancestries_len` and `precommits_len` at dispatch time regardless of `is_free_execution_expected`.

### Proof of Concept
Rust integration test plan (in `bridges/primitives/header-chain/tests/justification/`):
1. Build a `GrandpaJustification` with a `voter_set` of `N` known authorities and `votes_ancestries` containing `V` chained headers (long single fork from `base` to a `head`).
2. Add `P` precommits, each with `signed.id` equal to a distinct known authority (so `process_known_authority_vote` succeeds) but with `signed.signature` corrupted (e.g., all-zero/invalid bytes), each precommit's `target_hash` set to `head` (forcing a full walk of the `V`-length ancestry chain on every iteration since none of these routes get marked visited on failure).
3. Instrument/time (or count `BTreeMap` lookups via a wrapped counter) `verify_justification` and assert that the number of `parent_hash_of` calls scales as `O(P * V)` rather than `O(P + V)` by varying `P` and `V` independently and checking the call-count ratio.
4. Compare the measured operation count/time against `T::WeightInfo::submit_finality_proof(P, V)` (linear formula) and assert the actual cost exceeds the charged weight's assumed budget by a growing multiplicative factor as `P` and `V` increase — demonstrating the charged weight underestimates true verification cost.

### Citations

**File:** bridges/modules/grandpa/src/lib.rs (L279-290)
```rust
		#[pallet::call_index(4)]
		#[pallet::weight(T::WeightInfo::submit_finality_proof_weight(
			justification.commit.precommits.len().saturated_into(),
			justification.votes_ancestries.len().saturated_into(),
		))]
		pub fn submit_finality_proof_ex(
			origin: OriginFor<T>,
			finality_target: Box<BridgedHeader<T, I>>,
			justification: GrandpaJustification<BridgedHeader<T, I>>,
			current_set_id: sp_consensus_grandpa::SetId,
			_is_free_execution_expected: bool,
		) -> DispatchResultWithPostInfo {
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

**File:** bridges/primitives/header-chain/src/justification/verification/mod.rs (L91-125)
```rust
	/// Returns a route if the precommit target block is a descendant of the `base` block.
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
```

**File:** bridges/primitives/header-chain/src/justification/verification/mod.rs (L288-322)
```rust

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

**File:** bridges/primitives/header-chain/src/lib.rs (L265-271)
```rust
	/// Max reasonable number of headers in `votes_ancestries` vector of the GRANDPA justification.
	///
	/// This isn't a strict limit. The relay may submit justifications with more headers in its
	/// ancestry and the pallet will accept such justification. The limit is only used to compute
	/// maximal refund amount and submitting justifications which exceed the limit, may be costly
	/// to submitter.
	const REASONABLE_HEADERS_IN_JUSTIFICATION_ANCESTRY: u32;
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

**File:** bridges/modules/grandpa/src/call_ext.rs (L98-122)
```rust
		// ensure that the `improved_by` is larger than the configured free interval
		if !call_info.is_mandatory {
			if let Some(free_headers_interval) = T::FreeHeadersInterval::get() {
				if improved_by < free_headers_interval.into() {
					tracing::trace!(
						target: crate::LOG_TARGET,
						chain_id=?T::BridgedChain::ID,
						block_number=?call_info.block_number,
						?improved_by,
						%free_headers_interval,
						"Cannot accept free header. Too small difference between submitted headers"
					);

					return Err(Error::<T, I>::BelowFreeHeaderInterval);
				}
			}
		}

		// let's also check whether the header submission fits the hardcoded limits. A normal
		// relayer would check that before submitting a transaction (since limits are constants
		// and do not depend on a volatile runtime state), but the ckeck itself is cheap, so
		// let's do it here too
		if !call_info.fits_limits() {
			return Err(Error::<T, I>::HeaderOverflowLimits);
		}
```
