This confirms the max-based (overlay) semantics is the documented, intended design for freezes across the entire fungible/fungibles framework, not a bug specific to `assets-freezer`.

### Title
No vulnerability found

### Summary
The `max()`-based aggregation in `Pallet::<T,I>::update_freezes` at `substrate/frame/assets-freezer/src/lib.rs` mirrors the exact same design used by `pallet-balances`' `update_freezes`/`update_locks`, and is explicitly documented as the intended semantic for freezes across the whole `fungible`/`fungibles` trait framework.

### Finding Description
`Pallet::<T,I>::update_freezes` computes `after_frozen` as `freezes.into_iter().map(|f| f.amount).max().unwrap_or_else(Zero::zero)` [1](#0-0) , and this is exactly mirrored by `pallet_balances::Pallet::<T,I>::update_freezes`, which also takes the max over all locks and freezes rather than summing them [2](#0-1) . This is not a pallet-specific quirk; it's the documented, canonical semantic of "Freeze" throughout `frame_support`'s tokens framework: `frame_support::traits::tokens::fungible` module docs explicitly state "Multiple freezes always operate over the same funds, so they 'overlay' rather than 'stack'... if an account has 3 freezes for 100 units, the account can spend its funds for any reason down to 100 units" [3](#0-2) . This is contrasted explicitly with Holds, which are documented as cumulative/additive: "Holds are cumulative (do not overlap) and are distinct from the free balance - Freezes are not cumulative, and can overlap with each other or with holds" [4](#0-3) . A unit test in `pallet-balances` (`locks_and_freezes`) confirms the overlay behavior as intentional: "Frozen takes the max of lock (40) and freeze (70)" [5](#0-4) . Additionally, the `try_state` invariant checks in both `assets-freezer` (`do_try_state`) and `pallet-balances` (`account_frozen_greater_than_freezes`) explicitly assert that the frozen balance equals the max of freezes, confirming this is the enforced/expected invariant, not an accounting bug [6](#0-5) [7](#0-6) .

Any FRAME pallet that wants additive reservation semantics is expected to use the separate `Hold`/`MutateHold` trait family (which is cumulative, as documented), not `Freeze`. There is no known consumer pallet in the tree that mistakenly relies on freezes being additive; the framework's design intentionally separates "additive" (Hold) from "overlay" (Freeze) semantics so that different pallets (e.g., staking and governance) can each independently freeze funds for their own purpose without needing to coordinate amounts, while still allowing the user to spend down to the largest single freeze requirement.

### Impact Explanation
Not applicable — the behavior matches the intended, documented design across the entire fungible token framework (`pallet-balances` and `assets-freezer` alike), so there is no over-withdrawal bug relative to the actual protocol semantics that consumer pallets are supposed to rely on.

### Likelihood Explanation
Not applicable.

### Recommendation
No fix needed. If a specific consumer pallet is suspected of incorrectly assuming freezes stack additively, that would need to be identified and reviewed against this documented Freeze semantic — but no such pallet was found in this codebase.

### Proof of Concept
Not applicable; the `max()` behavior is by design and already covered by existing tests (`locks_and_freezes` in `pallet-balances` and the `try_state` invariant checks in both pallets).

### Citations

**File:** substrate/frame/assets-freezer/src/lib.rs (L151-153)
```rust
		let prev_frozen = FrozenBalances::<T, I>::get(asset.clone(), who).unwrap_or_default();
		let after_frozen = freezes.into_iter().map(|f| f.amount).max().unwrap_or_else(Zero::zero);
		FrozenBalances::<T, I>::set(asset.clone(), who, Some(after_frozen));
```

**File:** substrate/frame/assets-freezer/src/lib.rs (L170-183)
```rust
	#[cfg(feature = "try-runtime")]
	fn do_try_state() -> Result<(), TryRuntimeError> {
		for (asset, who, _) in FrozenBalances::<T, I>::iter() {
			let max_frozen_amount =
				Freezes::<T, I>::get(asset.clone(), who.clone()).iter().map(|l| l.amount).max();

			ensure!(
				FrozenBalances::<T, I>::get(asset, who) == max_frozen_amount,
				"The `FrozenAmount` is not equal to the maximum amount in `Freezes` for (`asset`, `who`)"
			);
		}

		Ok(())
	}
```

**File:** substrate/frame/balances/src/lib.rs (L1216-1231)
```rust
		pub(crate) fn update_freezes(
			who: &T::AccountId,
			freezes: BoundedSlice<IdAmount<T::FreezeIdentifier, T::Balance>, T::MaxFreezes>,
		) -> DispatchResult {
			let mut prev_frozen = Zero::zero();
			let mut after_frozen = Zero::zero();
			let (_, maybe_dust) = Self::mutate_account(who, false, |b| {
				prev_frozen = b.frozen;
				b.frozen = Zero::zero();
				for l in Locks::<T, I>::get(who).iter() {
					b.frozen = b.frozen.max(l.amount);
				}
				for l in freezes.iter() {
					b.frozen = b.frozen.max(l.amount);
				}
				after_frozen = b.frozen;
```

**File:** substrate/frame/balances/src/lib.rs (L1415-1432)
```rust
		fn account_frozen_greater_than_freezes() -> Result<(), sp_runtime::TryRuntimeError> {
			Freezes::<T, I>::iter().try_for_each(|(who, freezes)| {
				let max_locks = freezes.iter().map(|l| l.amount).max().unwrap_or_default();
				let frozen = T::AccountStore::get(&who).frozen;
				if max_locks > frozen {
					log::warn!(
						target: crate::LOG_TARGET,
						"Maximum freeze of {:?} ({:?}) is greater than the frozen balance {:?}",
						who,
						max_locks,
						frozen
					);
					Err("bad freezes".into())
				} else {
					Ok(())
				}
			})
		}
```

**File:** substrate/frame/support/src/traits/tokens/fungible/mod.rs (L65-71)
```rust
//! - **Frozen Balance**: A freeze on a specified amount of an account's balance. Tokens that are
//!   frozen cannot be transferred.
//!
//!   Multiple freezes always operate over the same funds, so they "overlay" rather than
//!   "stack". This means that if an account has 3 freezes for 100 units, the account can spend its
//!   funds for any reason down to 100 units, at which point the freezes will start to come into
//!   play.
```

**File:** substrate/frame/support/src/traits/tokens/fungible/mod.rs (L113-126)
```rust
//!
//! The primary distinction between the two are that:
//! - Holds are cumulative (do not overlap) and are distinct from the free balance
//! - Freezes are not cumulative, and can overlap with each other or with holds
//!
//! ```ignore
//! |__total_____________________________|
//! |__hold_a__|__hold_b__|_____free_____|
//! |__on_hold____________|     // <- the sum of all holds
//! |__freeze_a_______________|
//! |__freeze_b____|
//! |__freeze_c________|
//! |__frozen_________________| // <- the max of all freezes
//! ```
```

**File:** substrate/frame/balances/src/tests/fungible_and_currency.rs (L160-163)
```rust
			// Freeze 70 tokens
			assert_ok!(<Balances as MutateFreeze<_>>::set_freeze(&TestId::Foo, &who, 70));
			// Frozen takes the max of lock (40) and freeze (70)
			assert_eq!(b(who), (100, 0, 70));
```
