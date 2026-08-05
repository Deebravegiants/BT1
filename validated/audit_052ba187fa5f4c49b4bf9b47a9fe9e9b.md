Audit Report

## Title
Non-atomic legacy `StatusFor` → `RequestStatusFor` migration can permanently orphan `PreimageFor` bytes with lost deposit accounting - (File: substrate/frame/preimage/src/lib.rs)

## Summary
`Pallet::do_ensure_updated` unconditionally takes and discards the legacy `StatusFor` entry and unreserves the associated deposit via `T::Currency::unreserve` before attempting to place a new `Consideration`/hold for the same account and amount. If the new hold fails (e.g., because the account's frozen/locked balance increased since the deposit was originally reserved), the function silently returns `true` without writing to `RequestStatusFor`, permanently orphaning the corresponding `PreimageFor` bytes with no backing deposit and no way to reprocess the hash.

## Finding Description
`do_ensure_updated` at `substrate/frame/preimage/src/lib.rs` performs, in order: `StatusFor::<T>::take(h)` (irreversibly removing the legacy record), `T::Currency::unreserve(&who, amount)` (restoring the deposit to free balance), and then `T::Consideration::new(&who, ...)` to place a new hold. [1](#0-0) . If `Consideration::new` fails, the failure is only logged via `.defensive_proof(...)` — which in production builds emits a `log::error!` and only triggers a `debug_assert!` (a no-op unless `debug_assertions` is enabled) — and the function returns `true` without ever calling `RequestStatusFor::<T>::insert`. [2](#0-1) 

The hold-placement path (`HoldConsideration::new` → `F::hold`) is checked against the account's current reducible/frozen balance, not merely against the just-restored free balance. `pallet_balances`'s `can_withdraw`/`reducible_balance` explicitly account for `account.frozen` (driven by locks/freezes such as vesting or staking) when determining whether a hold/withdrawal can succeed. [3](#0-2)  This confirms the claimed mechanism: an amount that was safely reserved earlier can fail to be re-held after `unreserve` if the account's frozen balance grew in the interim (e.g., a new vesting schedule or larger staking bond), independent of the preimage logic itself. [4](#0-3) 

Once this occurs: `StatusFor` is gone, `RequestStatusFor` was never populated, and `PreimageFor::<T>` for `(hash, len)` remains stored, since `PreimageFor` removal only occurs via `Self::remove` inside `do_unnote_preimage`/`do_unrequest_preimage`, both of which require a `RequestStatusFor` entry. Any retry hits `StatusFor::<T>::take(h) => None => return false` at the top of `do_ensure_updated`, so the hash can never be reprocessed through `note_preimage`, `unnote_preimage`, `request_preimage`, `unrequest_preimage`, or `ensure_updated` — all of which route through `do_ensure_updated`/`RequestStatusFor`. [5](#0-4) 

## Impact Explanation
This produces state-bloat with no deposit backing: the account's funds are fully released to spendable balance while the on-chain `PreimageFor` bytes it was paying for remain stored indefinitely, unreachable by any dispatchable including privileged `ManagerOrigin`-gated calls (`unrequest_preimage`), since those also key off `RequestStatusFor`. This matches an in-scope "unbacked storage / permanent inability to reclaim" impact rather than direct fund theft.

## Likelihood Explanation
Exploitation requires two conditions: (1) an existing legacy `StatusFor` (`OldRequestStatus::Unrequested`) entry for a hash the caller controls — realistic on any chain that adopted the `Consideration`-based accounting but still has un-migrated legacy preimages, since migration here is lazy (triggered per-hash on `note_preimage`/`request_preimage`/`ensure_updated`) rather than a one-shot runtime upgrade; and (2) the account's frozen/locked balance having grown since the original deposit was reserved (e.g., a new vesting schedule or increased staking bond) such that `unreserve` followed by `hold` for the identical nominal amount now fails. Both conditions are attacker-controlled and plausible pre-migration, though contingent on pre-existing legacy state that shrinks over time as lazy migration touches more hashes.

## Recommendation
Make the migration atomic: attempt to acquire the new `Consideration`/hold before calling `StatusFor::<T>::take`/`unreserve`, or roll back (re-insert `StatusFor`, or insert an appropriate unbacked/no-ticket entry into `RequestStatusFor`) if `Consideration::new` fails, so `PreimageFor` remains reachable and the legacy record is only discarded once the new hold is confirmed.

## Proof of Concept
1. In a mock runtime with `Currency = pallet_balances` and `Consideration = HoldConsideration<..., Balances, PreimageHoldReason, ...>`, seed legacy state: `StatusFor::<Test>::insert(hash, OldRequestStatus::Unrequested{ deposit: (who, amount), len })` and `PreimageFor::<Test>::insert((hash, len), bytes)`, mirroring genuine pre-migration on-chain state.
2. Apply a lock on `who` (e.g., `Balances::set_lock(VESTING_ID, &who, big_amount, WithdrawReasons::all())`) such that `free_balance(who) - amount < frozen_balance(who)`.
3. Trigger `do_ensure_updated` via `Preimage::note_preimage`/`ensure_updated`.
4. Assert `RequestStatusFor::<Test>::get(hash).is_none()`, `PreimageFor::<Test>::contains_key((hash, len))` remains `true`, and `Balances::balance_on_hold(&HoldReason::Preimage.into(), &who) == 0` while the deposit amount is now free/spendable.

### Citations

**File:** substrate/frame/preimage/src/lib.rs (L219-242)
```rust
		pub fn unnote_preimage(origin: OriginFor<T>, hash: T::Hash) -> DispatchResult {
			let maybe_sender = Self::ensure_signed_or_manager(origin)?;
			Self::do_unnote_preimage(&hash, maybe_sender)
		}

		/// Request a preimage be uploaded to the chain without paying any fees or deposits.
		///
		/// If the preimage requests has already been provided on-chain, we unreserve any deposit
		/// a user may have paid, and take the control of the preimage out of their hands.
		#[pallet::call_index(2)]
		pub fn request_preimage(origin: OriginFor<T>, hash: T::Hash) -> DispatchResult {
			T::ManagerOrigin::ensure_origin(origin)?;
			Self::do_request_preimage(&hash);
			Ok(())
		}

		/// Clear a previously made request for a preimage.
		///
		/// NOTE: THIS MUST NOT BE CALLED ON `hash` MORE TIMES THAN `request_preimage`.
		#[pallet::call_index(3)]
		pub fn unrequest_preimage(origin: OriginFor<T>, hash: T::Hash) -> DispatchResult {
			T::ManagerOrigin::ensure_origin(origin)?;
			Self::do_unrequest_preimage(&hash)
		}
```

**File:** substrate/frame/preimage/src/lib.rs (L267-285)
```rust
	fn do_ensure_updated(h: &T::Hash) -> bool {
		#[allow(deprecated)]
		let r = match StatusFor::<T>::take(h) {
			Some(r) => r,
			None => return false,
		};
		let n = match r {
			OldRequestStatus::Unrequested { deposit: (who, amount), len } => {
				// unreserve deposit
				T::Currency::unreserve(&who, amount);
				// take consideration
				let Ok(ticket) =
					T::Consideration::new(&who, Footprint::from_parts(1, len as usize))
						.defensive_proof("Unexpected inability to take deposit after unreserved")
				else {
					return true;
				};
				RequestStatus::Unrequested { ticket: (who, ticket), len }
			},
```

**File:** substrate/frame/support/src/traits/misc.rs (L69-97)
```rust
#[macro_export]
macro_rules! defensive {
	() => {
		$crate::__private::log::error!(
			target: "runtime::defensive",
			"{}",
			$crate::traits::DEFENSIVE_OP_PUBLIC_ERROR
		);
		debug_assert!(false, "{}", $crate::traits::DEFENSIVE_OP_INTERNAL_ERROR);
	};
	($error:expr $(,)?) => {
		$crate::__private::log::error!(
			target: "runtime::defensive",
			"{}: {:?}",
			$crate::traits::DEFENSIVE_OP_PUBLIC_ERROR,
			$error
		);
		debug_assert!(false, "{}: {:?}", $crate::traits::DEFENSIVE_OP_INTERNAL_ERROR, $error);
	};
	($error:expr, $proof:expr $(,)?) => {
		$crate::__private::log::error!(
			target: "runtime::defensive",
			"{}: {:?}: {:?}",
			$crate::traits::DEFENSIVE_OP_PUBLIC_ERROR,
			$error,
			$proof,
		);
		debug_assert!(false, "{}: {:?}: {:?}", $crate::traits::DEFENSIVE_OP_INTERNAL_ERROR, $error, $proof);
	}
```

**File:** substrate/frame/balances/src/impl_fungible.rs (L104-150)
```rust
	fn can_withdraw(
		who: &T::AccountId,
		amount: Self::Balance,
	) -> WithdrawConsequence<Self::Balance> {
		if amount.is_zero() {
			return WithdrawConsequence::Success;
		}

		if TotalIssuance::<T, I>::get().checked_sub(&amount).is_none() {
			return WithdrawConsequence::Underflow;
		}

		let account = Self::account(who);
		let new_free_balance = match account.free.checked_sub(&amount) {
			Some(x) => x,
			None => return WithdrawConsequence::BalanceLow,
		};

		let liquid = Self::reducible_balance(who, Expendable, Polite);
		if amount > liquid {
			return WithdrawConsequence::Frozen;
		}

		// Provider restriction - total account balance cannot be reduced to zero if it cannot
		// sustain the loss of a provider reference.
		// NOTE: This assumes that the pallet is a provider (which is true). Is this ever changes,
		// then this will need to adapt accordingly.
		let ed = T::ExistentialDeposit::get();
		let success = if new_free_balance < ed {
			if frame_system::Pallet::<T>::can_dec_provider(who) {
				WithdrawConsequence::ReducedToZero(new_free_balance)
			} else {
				return WithdrawConsequence::WouldDie;
			}
		} else {
			WithdrawConsequence::Success
		};

		let new_total_balance = new_free_balance.saturating_add(account.reserved);

		// Eventual free funds must be no less than the frozen balance.
		if new_total_balance < account.frozen {
			return WithdrawConsequence::Frozen;
		}

		success
	}
```

**File:** substrate/frame/balances/src/tests/fungible_tests.rs (L244-253)
```rust
#[test]
fn frozen_hold_balance_cannot_be_moved_without_force() {
	ExtBuilder::default()
		.existential_deposit(1)
		.monied(true)
		.build_and_execute_with(|| {
			assert_ok!(Balances::set_freeze(&TestId::Foo, &1, 10));
			assert_ok!(Balances::hold(&TestId::Foo, &1, 9));
			assert_eq!(Balances::reducible_total_balance_on_hold(&1, Force), 9);
			assert_eq!(Balances::reducible_total_balance_on_hold(&1, Polite), 0);
```
