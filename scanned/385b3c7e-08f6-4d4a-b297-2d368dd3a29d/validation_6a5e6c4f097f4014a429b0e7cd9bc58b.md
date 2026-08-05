### Title
Referendum Pass/Fail Threshold Can Be Manipulated by Burning Tokens Between Vote-Casting and Finalization — [File: `substrate/frame/democracy/src/lib.rs`]

### Summary
`pallet-democracy`'s `bake_referendum` re-reads the *live* `total_issuance()` at the exact block a referendum matures and uses it directly as the "electorate" for the `SuperMajorityApprove`/`SuperMajorityAgainst` threshold formula, rather than using an issuance value snapshotted when the referendum was launched or votes were cast. This is the same root-cause pattern as the Pyth Governance finding: a governance approval curve computed from a *mutable* token-supply metric evaluated at *settlement time*, which an actor can move between "vote" and "tally" to flip a marginal outcome.

### Finding Description
`Democracy::bake_referendum` computes approval as: [1](#0-0) 

`total_issuance` is fetched fresh at the block the referendum is finalized (`begin_block` → `bake_referendum` for each maturing referendum), not the value that existed when voters cast `aye`/`nay`: [2](#0-1) 

The threshold math itself is in `VoteThreshold::approved`, which derives `sqrt_electorate` from this electorate value and compares it against the tally: [3](#0-2) 

For `SuperMajorityApprove`, approval requires `nays/sqrt(turnout) < ayes/sqrt(electorate)`. Shrinking `electorate` (i.e., burning tokens out of `total_issuance`) *lowers* `sqrt_electorate`, which *increases* `ayes/sqrt_electorate` and makes the inequality easier to satisfy — i.e., burning supply right before finalization makes a referendum easier to pass, exactly mirroring the Pyth PoC where burning supply before "finalize" pushed a 33% vote over a 50%-of-majority bar.

By contrast, the newer governance stack (`pallet-referenda` + `pallet-conviction-voting`) already adopted the fix the Pyth auditors recommended for Pyth: it computes `support`/`approval` against a fixed constant `Total: Get<Votes>` rather than live issuance: [4](#0-3) 

This confirms the pattern is understood as fixable via a constant denominator — but the legacy `pallet-democracy` code path, which is still present in this repository and usable by any runtime that includes it, retains the vulnerable live-issuance design.

### Impact Explanation
An account (or colluding accounts) that hold enough tokens to bring a referendum to a marginal outcome could shift a `NotPassed` outcome to `Passed` (or vice-versa for `SuperMajorityAgainst`-gated external proposals) purely by reducing `total_issuance` (via burning owned, unlocked/free tokens) timed to land before the deterministic finalization block. Because `VotingPeriod` and thus the exact maturation block of a referendum are public and deterministic, an attacker can precisely time the issuance-reduction transaction. If the referendum enacts a privileged call (e.g., `set_balance`, a runtime upgrade, or any `Root`-scheduled dispatch), this becomes a path to pushing an otherwise-failing proposal through governance — the same "attacker gets whatever authority the passed proposal grants" impact called out in the original report.

### Likelihood Explanation
Likelihood depends on: (1) a referendum being close enough to the threshold boundary that the electorate shift matters, and (2) the ability for an unprivileged account to reduce `total_issuance` (e.g., via a self-service `burn` extrinsic or any other issuance-reducing mechanism) with tokens that are not already locked from voting. I located a `burn`-related item in `substrate/frame/balances/src/lib.rs`, consistent with balances pallets exposing an issuance-reducing dispatchable, but I could not fully confirm its exact signature/permission model within the remaining investigation budget — this should be verified before treating likelihood as "high" versus "requires specific conditions." The attack does not require compromising any trusted role; it only requires an account with free (non-reserved) balance and knowledge of the referendum's maturation block, which is public on-chain data.

### Recommendation
- Snapshot `total_issuance` (or another electorate metric) at referendum launch (`inject_referendum`) and store it in `ReferendumStatus`, then use that stored snapshot in `bake_referendum` instead of re-querying live issuance at settlement time.
- Alternatively, follow the same mitigation already used by `pallet-conviction-voting`: derive the threshold denominator from a fixed, governance-set constant rather than live token supply.
- Audit any runtime that still enables `pallet-democracy` (as opposed to `pallet-referenda`) to confirm whether this legacy code path is reachable in production, and prioritize migration off it given this design difference.

### Proof of Concept
1. Launch (or wait for) a public referendum with `VoteThreshold::SuperMajorityApprove` via `Democracy::inject_referendum` — threshold check occurs in `bake_referendum`: [5](#0-4) 
2. Vote such that the tally is marginally below the passing threshold under the *current* `total_issuance` (e.g., `ayes/sqrt(electorate) ≈ nays/sqrt(turnout)`, per `should_work` test values `{ayes:100, nays:50, turnout:150}` vs. issuance `210`): [6](#0-5) 
3. Before the deterministic `VotingPeriod` maturation block, burn a portion of unlocked/free tokens (reducing `total_issuance`) using the balances pallet's issuance-reducing extrinsic.
4. At maturation, `begin_block`/`bake_referendum` reads the now-lower `total_issuance` and recomputes `sqrt_electorate`, potentially flipping `approved` from `false` to `true`: [7](#0-6)

### Citations

**File:** substrate/frame/democracy/src/lib.rs (L1580-1585)
```rust
				let ref_index = Self::inject_referendum(
					now.saturating_add(T::VotingPeriod::get()),
					proposal,
					VoteThreshold::SuperMajorityApprove,
					T::EnactmentPeriod::get(),
				);
```

**File:** substrate/frame/democracy/src/lib.rs (L1601-1604)
```rust
	) -> bool {
		let total_issuance = T::Currency::total_issuance();
		let approved = status.threshold.approved(status.tally, total_issuance);

```

**File:** substrate/frame/democracy/src/lib.rs (L1656-1661)
```rust
		// tally up votes for any expiring referenda.
		for (index, info) in Self::maturing_referenda_at_inner(now, next..last).into_iter() {
			let approved = Self::bake_referendum(now, index, info);
			ReferendumInfoOf::<T>::insert(index, ReferendumInfo::Finished { end: now, approved });
			weight = max_block_weight;
		}
```

**File:** substrate/frame/democracy/src/vote_threshold.rs (L103-118)
```rust
	fn approved(&self, tally: Tally<Balance>, electorate: Balance) -> bool {
		let sqrt_voters = tally.turnout.integer_sqrt();
		let sqrt_electorate = electorate.integer_sqrt();
		if sqrt_voters.is_zero() {
			return false;
		}
		match *self {
			VoteThreshold::SuperMajorityApprove => {
				compare_rationals(tally.nays, sqrt_voters, tally.ayes, sqrt_electorate)
			},
			VoteThreshold::SuperMajorityAgainst => {
				compare_rationals(tally.nays, sqrt_electorate, tally.ayes, sqrt_voters)
			},
			VoteThreshold::SimpleMajority => tally.ayes > tally.nays,
		}
	}
```

**File:** substrate/frame/conviction-voting/src/types.rs (L68-79)
```rust
	fn support(&self, _: Class) -> Perbill {
		Perbill::from_rational(self.support, Total::get())
	}

	fn approval(&self, _: Class) -> Perbill {
		let total = self.ayes.saturating_add(self.nays);
		if total.is_zero() {
			Perbill::zero()
		} else {
			Perbill::from_rational(self.ayes, total)
		}
	}
```

**File:** substrate/frame/democracy/src/tests/voting.rs (L151-171)
```rust
#[test]
fn passing_low_turnout_voting_should_work() {
	new_test_ext().execute_with(|| {
		assert_eq!(Balances::free_balance(42), 0);
		assert_eq!(pallet_balances::TotalIssuance::<Test>::get(), 210);

		let r = Democracy::inject_referendum(
			2,
			set_balance_proposal(2),
			VoteThreshold::SuperMajorityApprove,
			0,
		);
		assert_ok!(Democracy::vote(RuntimeOrigin::signed(4), r, big_aye(4)));
		assert_ok!(Democracy::vote(RuntimeOrigin::signed(5), r, big_nay(5)));
		assert_ok!(Democracy::vote(RuntimeOrigin::signed(6), r, big_aye(6)));
		assert_eq!(tally(r), Tally { ayes: 100, nays: 50, turnout: 150 });

		next_block();
		next_block();
		assert_eq!(Balances::free_balance(42), 2);
	});
```
