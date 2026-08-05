The code confirms the claim exactly as described: `retract_tip` at lines 311-324 only checks `tip.finder == who` with no check on `tip.closes` or `Tippers` membership, and `tip_new` at lines 366-375 sets `finder: tipper` with `finders_fee: false`, allowing any account that called `tip_new` to later retract a tip that has already reached quorum (`tip.closes.is_some()` via `insert_tip_and_check_closing` at lines 522-539). The doc comment at lines 297-299 explicitly states this should only apply to `report_awesome`-created tips, but no such restriction is enforced in code.

Audit Report

## Title
`retract_tip` lacks lifecycle/state checks, allowing a stale finder to unilaterally cancel an already-closing tip - (File: substrate/frame/tips/src/lib.rs)

## Summary
`retract_tip` only verifies `tip.finder == who` before deleting the `Tips`/`Reasons` entries and refunding the deposit; it never checks whether the tip has already reached quorum and entered its countdown (`tip.closes.is_some()`), nor whether the caller is still an active `Tippers` member. Because `tip_new` also sets `finder: tipper` for the calling tipper, this lets any account that originated a tip via `tip_new` unilaterally erase a tip that has already been approved by a majority of tippers and is waiting to be paid out via `close_tip`.

## Finding Description
`retract_tip` [1](#0-0)  performs only `ensure!(tip.finder == who, Error::<T, I>::NotFinder);` before removing the `Tips` and `Reasons` entries and unreserving the deposit. There is no check of `tip.closes`, the field set by `insert_tip_and_check_closing` once the tip crosses the tipper quorum threshold [2](#0-1) , and no re-validation of `T::Tippers::contains(&who)`.

Critically, `tip_new`, callable by any `Tippers` member, creates an `OpenTip` with `finder: tipper` (the calling tipper), `deposit: Zero::zero()`, `finders_fee: false` [3](#0-2) . The doc comment for `retract_tip` explicitly states the tip "must have been reported by the signing account through `report_awesome` (and not through `tip_new`)" [4](#0-3) , but the code enforces no such restriction — any tip, regardless of origin call or lifecycle stage, can be retracted by the recorded `finder` as long as it still exists in storage.

Exploit flow: a `Tippers` member calls `tip_new`, becoming `tip.finder`; other tippers call `tip` via [5](#0-4) , pushing the tip past the majority threshold so `tip.closes` becomes `Some(...)`, emitting `TipClosing`; the original finder then calls `retract_tip` before `close_tip` fires, deleting the tip and its `Reasons` entry and unreserving the (zero) deposit, bypassing the privileged `slash_tip`/`RejectOrigin` path [6](#0-5)  that is the only intended way to cancel an accepted tip.

## Impact Explanation
An account that acted as finder via `tip_new` can unilaterally cancel a treasury tip that has already achieved the required tipper quorum and entered its payout countdown, bypassing the governance decision made by the `Tippers` set and the privileged `slash_tip`/`RejectOrigin` path meant to override an approved tip. This subverts the intended tipping governance outcome and can censor or deny legitimate payouts approved by the community. Since `tip_new`-derived tips have a zero deposit, no funds are drained to the attacker directly; the impact is denial/griefing of governance outcomes rather than fund theft, which is a real but moderate-severity defect.

## Likelihood Explanation
Fully reachable from unprivileged, signed extrinsics via the call chain `tip_new` → `tip` (by other tippers) → `retract_tip`, requiring only that the caller was a `Tippers` member at tip-creation time (membership is not re-checked at retract time). No special timing beyond acting before `close_tip` is dispatched, which is within the finder's control since the countdown block is public and predictable. The action is repeatable for any tip the account originated as finder.

## Recommendation
- In `retract_tip`, reject retraction once `tip.closes.is_some()` (i.e., once quorum/countdown has begun), directing cancellation of closing tips exclusively through `slash_tip` (privileged `RejectOrigin`).
- Additionally, restrict `retract_tip` to tips created via `report_awesome` only (e.g., by checking `tip.finders_fee` is true, matching the doc comment's intent), so `tip_new`-originated tips cannot be retracted by the finder at all.

## Proof of Concept
Integration test in `substrate/frame/tips/src/tests.rs`:
1. A `Tippers` member calls `tip_new(reason, who, tip_value)`, becoming `tip.finder`, with `deposit = 0`.
2. Other tippers call `tip(hash, tip_value)` enough times to reach `threshold = T::Tippers::count().div_ceil(2)`, causing `tip.closes` to become `Some(...)` and `TipClosing` to be emitted (verified via `Tips::tips(hash).unwrap().closes.is_some()`).
3. The original finder calls `retract_tip(hash)`.
4. Currently this succeeds: `Tips::tips(hash)` becomes `None` and `TipRetracted` fires, even though the tip had already reached quorum — demonstrating that a majority-approved tip can be erased outside the `slash_tip`/`RejectOrigin` path. After applying the recommended fix (checking `tip.closes.is_none()` and/or `tip.finders_fee`), this call should instead return an error and leave the tip intact.

### Citations

**File:** substrate/frame/tips/src/lib.rs (L297-299)
```rust
		/// The dispatch origin for this call must be _Signed_ and the tip identified by `hash`
		/// must have been reported by the signing account through `report_awesome` (and not
		/// through `tip_new`).
```

**File:** substrate/frame/tips/src/lib.rs (L311-324)
```rust
		pub fn retract_tip(origin: OriginFor<T>, hash: T::Hash) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let tip = Tips::<T, I>::get(&hash).ok_or(Error::<T, I>::UnknownTip)?;
			ensure!(tip.finder == who, Error::<T, I>::NotFinder);

			Reasons::<T, I>::remove(&tip.reason);
			Tips::<T, I>::remove(&hash);
			if !tip.deposit.is_zero() {
				let err_amount = T::Currency::unreserve(&who, tip.deposit);
				debug_assert!(err_amount.is_zero());
			}
			Self::deposit_event(Event::TipRetracted { tip_hash: hash });
			Ok(())
		}
```

**File:** substrate/frame/tips/src/lib.rs (L362-376)
```rust
			let hash = T::Hashing::hash_of(&(&reason_hash, &who));
			Reasons::<T, I>::insert(&reason_hash, &reason);
			Self::deposit_event(Event::NewTip { tip_hash: hash });
			let tips = vec![(tipper.clone(), tip_value)];
			let tip = OpenTip {
				reason: reason_hash,
				who,
				finder: tipper,
				deposit: Zero::zero(),
				closes: None,
				tips,
				finders_fee: false,
			};
			Tips::<T, I>::insert(&hash, tip);
			Ok(())
```

**File:** substrate/frame/tips/src/lib.rs (L402-419)
```rust
		pub fn tip(
			origin: OriginFor<T>,
			hash: T::Hash,
			#[pallet::compact] tip_value: BalanceOf<T, I>,
		) -> DispatchResult {
			let tipper = ensure_signed(origin)?;
			ensure!(T::Tippers::contains(&tipper), BadOrigin);

			ensure!(T::MaxTipAmount::get() >= tip_value, Error::<T, I>::MaxTipAmountExceeded);

			let mut tip = Tips::<T, I>::get(hash).ok_or(Error::<T, I>::UnknownTip)?;

			if Self::insert_tip_and_check_closing(&mut tip, tipper, tip_value) {
				Self::deposit_event(Event::TipClosing { tip_hash: hash });
			}
			Tips::<T, I>::insert(&hash, tip);
			Ok(())
		}
```

**File:** substrate/frame/tips/src/lib.rs (L460-476)
```rust
		pub fn slash_tip(origin: OriginFor<T>, hash: T::Hash) -> DispatchResult {
			T::RejectOrigin::ensure_origin(origin)?;

			let tip = Tips::<T, I>::take(hash).ok_or(Error::<T, I>::UnknownTip)?;

			if !tip.deposit.is_zero() {
				let imbalance = T::Currency::slash_reserved(&tip.finder, tip.deposit).0;
				T::OnSlash::on_unbalanced(imbalance);
			}
			Reasons::<T, I>::remove(&tip.reason);
			Self::deposit_event(Event::TipSlashed {
				tip_hash: hash,
				finder: tip.finder,
				deposit: tip.deposit,
			});
			Ok(())
		}
```

**File:** substrate/frame/tips/src/lib.rs (L522-539)
```rust
	fn insert_tip_and_check_closing(
		tip: &mut OpenTip<T::AccountId, BalanceOf<T, I>, BlockNumberFor<T>, T::Hash>,
		tipper: T::AccountId,
		tip_value: BalanceOf<T, I>,
	) -> bool {
		match tip.tips.binary_search_by_key(&&tipper, |x| &x.0) {
			Ok(pos) => tip.tips[pos] = (tipper, tip_value),
			Err(pos) => tip.tips.insert(pos, (tipper, tip_value)),
		}
		Self::retain_active_tips(&mut tip.tips);
		let threshold = T::Tippers::count().div_ceil(2);
		if tip.tips.len() >= threshold && tip.closes.is_none() {
			tip.closes = Some(frame_system::Pallet::<T>::block_number() + T::TipCountdown::get());
			true
		} else {
			false
		}
	}
```
