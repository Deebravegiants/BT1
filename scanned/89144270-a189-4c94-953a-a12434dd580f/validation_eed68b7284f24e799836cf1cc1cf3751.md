Based on my analysis of the FRAME equivocation-reporting pathway, a structurally analogous vulnerability exists.

### Title
Equivocation Report Front-Running Allows Theft of Slashing Report Rewards - (File: `substrate/frame/grandpa/src/lib.rs`, `substrate/frame/babe/src/lib.rs`, `substrate/frame/beefy/src/lib.rs`)

### Summary
The GRANDPA, BABE, and BEEFY pallets expose signed extrinsics (`report_equivocation`, `report_fork_voting`, `report_future_block_voting`) that reward whichever account happens to be `ensure_signed(origin)` at dispatch time, while the equivocation evidence itself (`equivocation_proof` + `key_owner_proof`) is fully public data containing no binding to the discovering account, mirroring the Mantle TSS `msg.sender`-based reward bug.

### Finding Description
`pallet_grandpa::Pallet::report_equivocation` derives the reward recipient purely from the transaction signer: `let reporter = ensure_signed(origin)?;` and forwards it into `T::EquivocationReportSystem::process_evidence(Some(reporter), ...)`. [1](#0-0) 
The identical pattern exists in BABE's `report_equivocation`. [2](#0-1) 
and in BEEFY's `report_fork_voting` / `report_future_block_voting`. [3](#0-2) [4](#0-3) 

The `equivocation_proof` and `key_owner_proof` arguments are self-verifying, publicly derivable data (the misbehaving validator's own conflicting signed votes plus a Merkle-style membership proof) — nothing in the payload is bound to the original discoverer's identity. `process_evidence` simply forwards the `reporter` option down to `ReportOffence::report_offence`, which slashes the offender and eventually calls `pay_reporters`, crediting the reward directly to whichever account was recorded as `reporter`. [5](#0-4) [6](#0-5) 

Because the transaction is signed (not the unsigned/local-only variant) and the evidence is copyable byte-for-byte, any observer of the pending transaction in the transaction pool/mempool can extract `equivocation_proof` and `key_owner_proof` and resubmit them in their own signed transaction. If that copy is prioritized ahead of the original (e.g., via a higher tip, since transaction pool ordering in the signed-extrinsic path is priority/tip-based rather than FIFO), the copier's transaction is included first. The original report then fails duplicate-offence validation (`R::is_known_offence` / `DuplicateOffenceReport`) inside `report_offence`'s triage logic. [7](#0-6) 
Only the successful report gets its transaction fee waived via `Ok(Pays::No.into())`; a failed/duplicate report pays normal fees while receiving no reward — an outcome directly analogous to Mantle's `msg.sender`-front-run scenario, where the reward described in documentation as belonging to "the TSS-node that submits the slashing message" is instead captured by an unrelated copier.

### Impact Explanation
The original discoverer of a validator equivocation can be deprived of the reward and additionally charged a transaction fee for a rejected duplicate report, while an unrelated account that merely observed and resubmitted the public proof collects the reward instead. This does not compromise consensus safety (the offender is still correctly slashed), but it breaks the intended incentive alignment for equivocation reporting and can discourage honest reporting behavior, similar to the concern raised in the referenced Mantle report.

### Likelihood Explanation
Exploitation requires only observing a pending `report_equivocation`/`report_fork_voting`/`report_future_block_voting` extrinsic in the transaction pool and resubmitting the same public proof with a higher tip — no privileged role or special access is required, making this reachable by any unprivileged network participant running a full/light node with pool visibility. The main mitigating factors are that the unsigned variant (author-only, `ensure_none`) removes attribution race concerns for validator-authored reports, and the fee-waiver design (`Pays::No`) only benefits the fee cost, not the reward itself.

### Recommendation
Where reward attribution matters, prefer the existing unsigned `report_equivocation_unsigned` path (which attributes the reporter via `pallet_authorship::Pallet::<T>::author()` rather than an easily copyable signed origin) for automated/off-chain-worker submission, or bind reporter identity into evidence validation so that a re-submission by a different signer is rejected/ignored rather than treated as a valid duplicate that displaces the original claim.

### Proof of Concept
1. Node A's off-chain worker constructs an equivocation report and submits `report_equivocation(origin=A, equivocation_proof, key_owner_proof)` as a signed extrinsic into the transaction pool.
2. Attacker B observes this pending extrinsic, extracts `equivocation_proof` and `key_owner_proof` (public data, no signature over B's identity required), and submits `report_equivocation(origin=B, equivocation_proof, key_owner_proof)` with a higher tip/priority.
3. B's extrinsic is included first; `process_evidence(Some(B), ...)` succeeds, slashing the offender and paying the reporter reward to B via `pay_reporters`.
4. A's extrinsic is later included, triggers `R::is_known_offence` → `DuplicateOffenceReport`, fails, and A pays a normal transaction fee for a losing report while receiving no reward.

### Citations

**File:** substrate/frame/grandpa/src/lib.rs (L200-213)
```rust
		pub fn report_equivocation(
			origin: OriginFor<T>,
			equivocation_proof: Box<EquivocationProof<T::Hash, BlockNumberFor<T>>>,
			key_owner_proof: T::KeyOwnerProof,
		) -> DispatchResultWithPostInfo {
			let reporter = ensure_signed(origin)?;

			T::EquivocationReportSystem::process_evidence(
				Some(reporter),
				(*equivocation_proof, key_owner_proof),
			)?;
			// Waive the fee since the report is valid and beneficial
			Ok(Pays::No.into())
		}
```

**File:** substrate/frame/babe/src/lib.rs (L415-427)
```rust
		pub fn report_equivocation(
			origin: OriginFor<T>,
			equivocation_proof: Box<EquivocationProof<HeaderFor<T>>>,
			key_owner_proof: T::KeyOwnerProof,
		) -> DispatchResultWithPostInfo {
			let reporter = ensure_signed(origin)?;
			T::EquivocationReportSystem::process_evidence(
				Some(reporter),
				(*equivocation_proof, key_owner_proof),
			)?;
			// Waive the fee since the report is valid and beneficial
			Ok(Pays::No.into())
		}
```

**File:** substrate/frame/beefy/src/lib.rs (L303-322)
```rust
		pub fn report_fork_voting(
			origin: OriginFor<T>,
			equivocation_proof: Box<
				ForkVotingProof<
					HeaderFor<T>,
					T::BeefyId,
					<T::AncestryHelper as AncestryHelper<HeaderFor<T>>>::Proof,
				>,
			>,
			key_owner_proof: T::KeyOwnerProof,
		) -> DispatchResultWithPostInfo {
			let reporter = ensure_signed(origin)?;

			T::EquivocationReportSystem::process_evidence(
				Some(reporter),
				EquivocationEvidenceFor::ForkVotingProof(*equivocation_proof, key_owner_proof),
			)?;
			// Waive the fee since the report is valid and beneficial
			Ok(Pays::No.into())
		}
```

**File:** substrate/frame/beefy/src/lib.rs (L367-383)
```rust
		pub fn report_future_block_voting(
			origin: OriginFor<T>,
			equivocation_proof: Box<FutureBlockVotingProof<BlockNumberFor<T>, T::BeefyId>>,
			key_owner_proof: T::KeyOwnerProof,
		) -> DispatchResultWithPostInfo {
			let reporter = ensure_signed(origin)?;

			T::EquivocationReportSystem::process_evidence(
				Some(reporter),
				EquivocationEvidenceFor::FutureBlockVotingProof(
					*equivocation_proof,
					key_owner_proof,
				),
			)?;
			// Waive the fee since the report is valid and beneficial
			Ok(Pays::No.into())
		}
```

**File:** substrate/frame/grandpa/src/equivocation.rs (L175-235)
```rust
	fn process_evidence(
		reporter: Option<T::AccountId>,
		evidence: (EquivocationProof<T::Hash, BlockNumberFor<T>>, T::KeyOwnerProof),
	) -> Result<(), DispatchError> {
		let (equivocation_proof, key_owner_proof) = evidence;
		let reporter = reporter.or_else(|| pallet_authorship::Pallet::<T>::author());
		let offender = equivocation_proof.offender().clone();

		// We check the equivocation within the context of its set id (and
		// associated session) and round. We also need to know the validator
		// set count when the offence since it is required to calculate the
		// slash amount.
		let set_id = equivocation_proof.set_id();
		let round = equivocation_proof.round();
		let session_index = key_owner_proof.session();
		let validator_set_count = key_owner_proof.validator_count();

		// Validate equivocation proof (check votes are different and signatures are valid).
		if !sp_consensus_grandpa::check_equivocation_proof(equivocation_proof) {
			return Err(Error::<T>::InvalidEquivocationProof.into());
		}

		// Validate the key ownership proof extracting the id of the offender.
		let offender = P::check_proof((KEY_TYPE, offender), key_owner_proof)
			.ok_or(Error::<T>::InvalidKeyOwnershipProof)?;

		// Fetch the current and previous sets last session index.
		// For genesis set there's no previous set.
		let previous_set_id_session_index = if set_id != 0 {
			let idx = crate::SetIdSession::<T>::get(set_id - 1)
				.ok_or(Error::<T>::InvalidEquivocationProof)?;
			Some(idx)
		} else {
			None
		};

		let set_id_session_index =
			crate::SetIdSession::<T>::get(set_id).ok_or(Error::<T>::InvalidEquivocationProof)?;

		// Check that the session id for the membership proof is within the
		// bounds of the set id reported in the equivocation.
		if session_index > set_id_session_index ||
			previous_set_id_session_index
				.map(|previous_index| session_index <= previous_index)
				.unwrap_or(false)
		{
			return Err(Error::<T>::InvalidEquivocationProof.into());
		}

		let offence = EquivocationOffence {
			time_slot: TimeSlot { set_id, round },
			session_index,
			offender,
			validator_set_count,
		};

		R::report_offence(reporter.into_iter().collect(), offence)
			.map_err(|_| Error::<T>::DuplicateOffenceReport)?;

		Ok(())
	}
```

**File:** substrate/frame/staking/src/slashing.rs (L621-651)
```rust
/// Apply a reward payout to some reporters, paying the rewards out of the slashed imbalance.
fn pay_reporters<T: Config>(
	reward_payout: BalanceOf<T>,
	slashed_imbalance: NegativeImbalanceOf<T>,
	reporters: &[T::AccountId],
) {
	if reward_payout.is_zero() || reporters.is_empty() {
		// nobody to pay out to or nothing to pay;
		// just treat the whole value as slashed.
		T::Slash::on_unbalanced(slashed_imbalance);
		return;
	}

	// take rewards out of the slashed imbalance.
	let reward_payout = reward_payout.min(slashed_imbalance.peek());
	let (mut reward_payout, mut value_slashed) = slashed_imbalance.split(reward_payout);

	let per_reporter = reward_payout.peek() / (reporters.len() as u32).into();
	for reporter in reporters {
		let (reporter_reward, rest) = reward_payout.split(per_reporter);
		reward_payout = rest;

		// this cancels out the reporter reward imbalance internally, leading
		// to no change in total issuance.
		asset::deposit_slashed::<T>(reporter, reporter_reward);
	}

	// the rest goes to the on-slash imbalance handler (e.g. treasury)
	value_slashed.subsume(reward_payout); // remainder of reward division remains.
	T::Slash::on_unbalanced(value_slashed);
}
```

**File:** substrate/frame/offences/src/lib.rs (L107-123)
```rust
impl<T, O> ReportOffence<T::AccountId, T::IdentificationTuple, O> for Pallet<T>
where
	T: Config,
	O: Offence<T::IdentificationTuple>,
{
	fn report_offence(reporters: Vec<T::AccountId>, offence: O) -> Result<(), OffenceError> {
		let offenders = offence.offenders();
		let slot = offence.slot();

		// Go through all offenders in the offence report and find all offenders that were spotted
		// in unique reports.
		let TriageOutcome { concurrent_offenders } =
			match Self::triage_offence_report::<O>(reporters, &slot, offenders) {
				Some(triage) => triage,
				// The report contained only duplicates, so there is no need to slash again.
				None => return Err(OffenceError::DuplicateReport),
			};
```
