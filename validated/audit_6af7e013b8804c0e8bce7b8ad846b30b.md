Confirmed: this vulnerability class exists in this repo's legacy `pallet-staking`, and there is direct evidence it was already identified and fixed in the newer `pallet-staking-async` fork but the fix was never backported to `pallet-staking`.

### Title
`Staking::nominate` fails to check that a target validator exists, allowing nomination of unregistered/removed validators - (File: `substrate/frame/staking/src/pallet/mod.rs`)

### Summary
The `_incrementGaugeWeight` bug pattern (checking a "negative" membership condition instead of the required "positive" membership condition) has a direct analog in `pallet-staking`'s `nominate` extrinsic, where the target-validity check only tests `!blocked` and never confirms the target is actually a registered validator.

### Finding Description
In `Pallet::nominate`, each target is validated with:
```rust
if old.contains(&n) || !Validators::<T>::get(&n).blocked {
    Ok(n)
} else {
    Err(Error::<T>::BadTarget.into())
}
``` [1](#0-0) 

`Validators<T>` is a `StorageMap` from account to `ValidatorPrefs`. For any account that is *not* a registered validator, `Validators::<T>::get(&n)` returns the type's default value, `ValidatorPrefs::default()`, whose `blocked` field defaults to `false`. Consequently `!Validators::<T>::get(&n).blocked` evaluates to `true` for accounts that were never registered as validators (or that have `chill`ed/been removed), exactly mirroring the ERC20Gauges bug where the code checked "not deprecated" instead of "is an active gauge." The check never calls `Validators::<T>::contains_key(&n)`.

This is confirmed by comparison with the sibling pallet `pallet-staking-async`, which already fixed this exact issue:
```rust
if old.contains(&n) ||
    (Validators::<T>::contains_key(&n) && !Validators::<T>::get(&n).blocked)
``` [2](#0-1) 

The corresponding prdoc explicitly documents this as a bug fix, applied only to `pallet-staking-async`:
```
title: 'Fix calling nominate on a validator that doesn't exist silently succeeds'
...
crates:
  - name: pallet-staking-async
    bump: major
``` [3](#0-2) 

The legacy `pallet-staking` test suite also lacks the corresponding regression test — `nominating_non_validators_is_not_ok` exists only in `substrate/frame/staking-async/src/tests/bonding.rs`, not in `substrate/frame/staking/src/tests.rs`, confirming the fix (and its test coverage) never reached the older pallet. [4](#0-3) 

### Impact Explanation
A nominator can call `nominate` with an account that is not (or is no longer) a validator, and the extrinsic succeeds instead of returning `Error::BadTarget`. The bogus target gets stored in `Nominators<T>` and included as one of the nominator's stake targets. Depending on how downstream election/reward logic (`electing_voters`, exposure calculation) treats such an entry, the nominator's stake weight can be diluted across invalid targets, causing them to earn less than expected reward, or their vote to simply be wasted on an entity that can never be elected — an analog to "user may lose rewards" from the source report. It also pollutes on-chain state with stale/incorrect nomination targets which complicates governance/validator-set bookkeeping.

### Likelihood Explanation
This requires no privileged role — any signed account bonded with sufficient stake and calling the public `nominate` extrinsic with a mistaken/removed/never-registered validator account can trigger it. The most direct realistic trigger: nominate a validator that later chills/removes itself (`do_remove_validator`), or a typo'd/former stash address — a plausible unprivileged user error that the intended `BadTarget` guard exists specifically to prevent, but currently fails to catch for the "never registered" case.

### Recommendation
Mirror the fix already applied in `pallet-staking-async`: require both that the target is a currently known validator and not blocked:
```rust
if old.contains(&n) ||
    (Validators::<T>::contains_key(&n) && !Validators::<T>::get(&n).blocked)
{
    Ok(n)
} else {
    Err(Error::<T>::BadTarget.into())
}
```
Apply the same change to `substrate/frame/staking/src/pallet/mod.rs::nominate`, and add the equivalent `nominating_non_validators_is_not_ok`-style regression test to `substrate/frame/staking/src/tests.rs`.

### Proof of Concept
1. Deploy/genesis a chain using `pallet-staking` (non-async) with validators `{11, 21, 31}` and a bonded, unbonded account `1`.
2. Call `Staking::bond(1, 1000, ...)`.
3. Call `Staking::nominate(1, vec![41])` where `41` was never registered via `Staking::validate`.
4. Observe that this succeeds (returns `Ok`) instead of returning `Error::BadTarget`, because `Validators::<T>::get(&41)` returns `ValidatorPrefs::default()` (`blocked: false`).
   This is the exact scenario blocked (and tested) in `pallet-staking-async`'s `nominating_non_validators_is_not_ok` test at `substrate/frame/staking-async/src/tests/bonding.rs` lines 1684-1708, which has no equivalent passing check in `pallet-staking`.

### Citations

**File:** substrate/frame/staking/src/pallet/mod.rs (L1406-1420)
```rust
			let targets: BoundedVec<_, _> = targets
				.into_iter()
				.map(|t| T::Lookup::lookup(t).map_err(DispatchError::from))
				.map(|n| {
					n.and_then(|n| {
						if old.contains(&n) || !Validators::<T>::get(&n).blocked {
							Ok(n)
						} else {
							Err(Error::<T>::BadTarget.into())
						}
					})
				})
				.collect::<Result<Vec<_>, _>>()?
				.try_into()
				.map_err(|_| Error::<T>::TooManyNominators)?;
```

**File:** substrate/frame/staking-async/src/pallet/mod.rs (L2163-2178)
```rust
			let old = Nominators::<T>::get(stash).map_or_else(Vec::new, |x| x.targets.into_inner());

			let targets: BoundedVec<_, _> = targets
				.into_iter()
				.map(|n| {
					if old.contains(&n) ||
						(Validators::<T>::contains_key(&n) && !Validators::<T>::get(&n).blocked)
					{
						Ok(n)
					} else {
						Err(Error::<T>::BadTarget.into())
					}
				})
				.collect::<Result<Vec<_>, DispatchError>>()?
				.try_into()
				.map_err(|_| Error::<T>::TooManyNominators)?;
```

**File:** prdoc/stable2509/pr_8436.prdoc (L1-11)
```text
title: 'Fix calling nominate on a validator that doesn’t exist silently succeeds'

doc:
  - audience: Runtime Dev
    description: |
      This PR fixes a bug where calling nominate on a validator that doesn’t exist silently succeeds.
      It also updates all the tests that had an incorrect setup - they were simulating elections with unregistered validators.

crates:
  - name: pallet-staking-async
    bump: major
```

**File:** substrate/frame/staking-async/src/tests/bonding.rs (L1684-1708)
```rust
	#[test]
	fn nominating_non_validators_is_not_ok() {
		ExtBuilder::default().nominate(false).build_and_execute(|| {
			// given existing validators
			assert_eq!(
				<Validators<Test>>::iter().map(|(v, _)| v).collect::<Vec<_>>(),
				vec![31, 21, 11,],
			);

			// .. and no existing nominators
			assert!(<Nominators<T>>::iter().count() == 0);
			// and 1 bonded.
			assert_ok!(Staking::bond(RuntimeOrigin::signed(1), 1000, RewardDestination::Stash));

			// then
			assert_noop!(
				Staking::nominate(RuntimeOrigin::signed(1), vec![41]),
				Error::<Test>::BadTarget
			);
			assert_noop!(
				Staking::nominate(RuntimeOrigin::signed(1), vec![31, 21, 11, 41]),
				Error::<Test>::BadTarget
			);
		});
	}
```
