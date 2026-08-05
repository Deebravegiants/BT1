Audit Report

## Title
Unbounded per-offence nominator slashing loop in `slash_nominators` / `apply_slash` (legacy `pallet-staking`) — insufficiently confirmed as exploitable weight-DoS - (File: substrate/frame/staking/src/slashing.rs)

## Summary
The claim correctly identifies that `slash_nominators` and `apply_slash` in `substrate/frame/staking/src/slashing.rs` iterate the full, non-paged `exposure.others` / `unapplied_slash.others` vector with no internal chunking or early-exit weight metering. However, the report itself admits it could not confirm the one fact that determines whether this is exploitable: whether the exposure fed into `compute_slash` via `on_offence` can actually be made disproportionately large by an attacker relative to what the runtime charges for it. Investigation of `on_offence` in `substrate/frame/staking/src/pallet/impls.rs` shows this gap is not a blind spot in the code — the weight consumed by the slash-application loop is computed dynamically as a function of `unapplied.others.len()` (`nominators_len`) and added to `consumed_weight` at call time, rather than relying on a fixed pre-charged benchmark constant.

## Finding Description
`slash_nominators` reserves and pushes one entry per nominator in `params.exposure.others` with no cap: [1](#0-0) . `compute_slash` places this vector, unbounded, into `UnappliedSlash.others`: [2](#0-1) . `apply_slash` then iterates the entire vector calling `do_slash` once per nominator: [3](#0-2) , and `do_slash` does a full ledger read/mutate/write per call: [4](#0-3) . These facts in the claim are accurate.

However, the caller, `Pallet::<T>::on_offence`, does not treat this as a fixed-weight operation. It computes `nominators_len` from the actual resulting `unapplied.others.len()` and adds proportional read/write weight to `consumed_weight` before or immediately after calling `apply_slash`: [5](#0-4) . This means the actual weight accounting scales with the real number of nominators processed rather than assuming a fixed benchmarked constant — the weight-charging design already anticipates variable-size `exposure.others`, which undermines the claim's core assertion that "the loop cost is a direct... function... [with] no weight budget check."

The claim's likelihood section explicitly states the critical precondition is unverified: whether a single validator's `exposure.others` can, through the real election pipeline (`nominate`/bonding + `MaxNominatorsCount`/backer caps), grow to a size that exceeds what `on_offence`'s per-item weight computation and the runtime's overall block weight limit can tolerate. This repository contains two parallel staking implementations: the legacy `pallet-staking` (target of this claim) which uses full unpaged `Exposure` in `on_offence`/`slashing.rs`, and the newer `pallet-staking-async` which explicitly paginates offence processing via `Eras::get_paged_exposure` bounded by `MaxExposurePageSize`, and further bounds `UnappliedSlash.others` with `WeakBoundedVec` [6](#0-5) . That the newer implementation went out of its way to add per-page offence processing and bounded nominator vectors for slashing suggests the paging omission in the legacy `pallet-staking` slashing path may be a known, if unaddressed, design gap — but this alone does not establish that it is practically exploitable in the legacy runtime, since election-time backer bounds (`MaxNominatorsCount`, `MaxBackersPerWinner`) and dynamic weight accounting in `on_offence` may already constrain the achievable exposure size and cost.

## Impact Explanation
Unconfirmed. The report's own analysis concedes that without knowing whether an attacker-controlled validator's exposure can realistically be made large enough to exceed `on_offence`'s dynamically-computed weight allowance and the block's overall weight limit, the claim cannot be shown to produce a concrete DoS beyond theoretical linear cost growth. No fund loss or double-spend is claimed — at most a temporary block-weight/processing-delay effect, contingent on an unverified precondition.

## Likelihood Explanation
The claim itself flags this as unconfirmed and states the required verification (confirming maximum achievable `exposure.others.len()` via real bond/nominate flows against `WeightInfo` benchmarks) "could not be completed with the available read-only tool budget." My own investigation corroborates that `on_offence` computes weight proportionally to the actual nominator count rather than using a fixed benchmark, and that `MaxNominatorsCount`/election backer bounds exist as separate constraints on exposure growth, further reducing the likelihood that this represents an unaccounted-for/unbounded weight discrepancy. Without concrete evidence that achievable exposure size exceeds the runtime's tolerances, this remains speculative.

## Recommendation
If pursued, the reporter should benchmark actual worst-case validator backer counts achievable via the runtime's live election bounds (`MaxNominatorsCount`, `MaxBackersPerWinner`, `MaxBackersPerWinnerFinal`) and compare them against the dynamic weight-accounting formula already present in `on_offence`, to determine whether a genuine gap exists between charged and consumed weight. Absent that comparison, no fix is warranted beyond what the newer `pallet-staking-async` paged-slashing design already provides as a template.

## Proof of Concept
Not established. The claim's own proposed PoC (steps 1–4) was not executed against real election-pipeline bounds, and the required comparison between maximum reachable `exposure.others.len()` and `on_offence`'s per-item dynamic weight charge was not performed. This is the decisive missing piece for validity, consistent with the claim's own "Likelihood Explanation" admission.

### Citations

**File:** substrate/frame/staking/src/slashing.rs (L297-306)
```rust
	let mut nominators_slashed = Vec::new();
	reward_payout += slash_nominators::<T>(params.clone(), prior_slash_p, &mut nominators_slashed);

	Some(UnappliedSlash {
		validator: params.stash.clone(),
		own: val_slashed,
		others: nominators_slashed,
		reporters: Vec::new(),
		payout: reward_payout,
	})
```

**File:** substrate/frame/staking/src/slashing.rs (L332-341)
```rust
fn slash_nominators<T: Config>(
	params: SlashParams<T>,
	prior_slash_p: Perbill,
	nominators_slashed: &mut Vec<(T::AccountId, BalanceOf<T>)>,
) -> BalanceOf<T> {
	let mut reward_payout = Zero::zero();

	nominators_slashed.reserve(params.exposure.others.len());
	for nominator in &params.exposure.others {
		let stash = &nominator.who;
```

**File:** substrate/frame/staking/src/slashing.rs (L554-590)
```rust
pub fn do_slash<T: Config>(
	stash: &T::AccountId,
	value: BalanceOf<T>,
	reward_payout: &mut BalanceOf<T>,
	slashed_imbalance: &mut NegativeImbalanceOf<T>,
	slash_era: EraIndex,
) {
	let mut ledger =
		match Pallet::<T>::ledger(sp_staking::StakingAccount::Stash(stash.clone())).defensive() {
			Ok(ledger) => ledger,
			Err(_) => return, // nothing to do.
		};

	let value = ledger.slash(value, asset::existential_deposit::<T>(), slash_era);
	if value.is_zero() {
		// nothing to do
		return;
	}

	// Skip slashing for virtual stakers. The pallets managing them should handle the slashing.
	if !Pallet::<T>::is_virtual_staker(stash) {
		let (imbalance, missing) = asset::slash::<T>(stash, value);
		slashed_imbalance.subsume(imbalance);

		if !missing.is_zero() {
			// deduct overslash from the reward payout
			*reward_payout = reward_payout.saturating_sub(missing);
		}
	}

	let _ = ledger
		.update()
		.defensive_proof("ledger fetched from storage so it exists in storage; qed.");

	// trigger the event
	<Pallet<T>>::deposit_event(super::Event::<T>::Slashed { staker: stash.clone(), amount: value });
}
```

**File:** substrate/frame/staking/src/slashing.rs (L593-619)
```rust
pub(crate) fn apply_slash<T: Config>(
	unapplied_slash: UnappliedSlash<T::AccountId, BalanceOf<T>>,
	slash_era: EraIndex,
) {
	let mut slashed_imbalance = NegativeImbalanceOf::<T>::zero();
	let mut reward_payout = unapplied_slash.payout;

	do_slash::<T>(
		&unapplied_slash.validator,
		unapplied_slash.own,
		&mut reward_payout,
		&mut slashed_imbalance,
		slash_era,
	);

	for &(ref nominator, nominator_slash) in &unapplied_slash.others {
		do_slash::<T>(
			nominator,
			nominator_slash,
			&mut reward_payout,
			&mut slashed_imbalance,
			slash_era,
		);
	}

	pay_reporters::<T>(reward_payout, slashed_imbalance, &unapplied_slash.reporters);
}
```

**File:** substrate/frame/staking/src/pallet/impls.rs (L1330-1360)
```rust
			let unapplied = slashing::compute_slash::<T>(slashing::SlashParams {
				stash,
				slash: *slash_fraction,
				exposure: &exposure,
				slash_era,
				window_start,
				now: active_era,
				reward_proportion,
			});

			if let Some(mut unapplied) = unapplied {
				let nominators_len = unapplied.others.len() as u64;
				let reporters_len = details.reporters.len() as u64;

				{
					let upper_bound = 1 /* Validator/NominatorSlashInEra */ + 2 /* fetch_spans */;
					let rw = upper_bound + nominators_len * upper_bound;
					add_db_reads_writes(rw, rw);
				}
				unapplied.reporters = details.reporters.clone();
				if slash_defer_duration == 0 {
					// Apply right away.
					slashing::apply_slash::<T>(unapplied, slash_era);
					{
						let slash_cost = (6, 5);
						let reward_cost = (2, 2);
						add_db_reads_writes(
							(1 + nominators_len) * slash_cost.0 + reward_cost.0 * reporters_len,
							(1 + nominators_len) * slash_cost.1 + reward_cost.1 * reporters_len,
						);
					}
```

**File:** substrate/frame/staking-async/src/slashing.rs (L491-513)
```rust
pub(crate) fn compute_slash<T: Config>(params: SlashParams<T>) -> Option<UnappliedSlash<T>> {
	let (val_slashed, mut reward_payout) = slash_validator::<T>(params.clone());

	let mut nominators_slashed = Vec::new();
	let (nom_slashed, nom_reward_payout) =
		slash_nominators::<T>(params.clone(), &mut nominators_slashed);
	reward_payout += nom_reward_payout;

	// If nominators are not slashable for this era, the list must be empty
	// (because we use `from_overview` which creates empty `others`).
	debug_assert!(Eras::<T>::are_nominators_slashable(params.offence_era));

	(nom_slashed + val_slashed > Zero::zero()).then_some(UnappliedSlash {
		validator: params.stash.clone(),
		own: val_slashed,
		others: WeakBoundedVec::force_from(
			nominators_slashed,
			Some("slashed nominators not expected to be larger than the bounds"),
		),
		reporter: None,
		payout: reward_payout,
	})
}
```
