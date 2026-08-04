### Title
`trigger_onboard` can force a parathread into parachain status using a stale/foreign `Leases` entry, without verifying the lease belongs to the para's current manager - ([File: polkadot/runtime/common/src/slots/mod.rs])

### Summary
`Pallet::trigger_onboard` only checks whether `Leases::<T>::get(para).first()` is `Some(Some(_))` before calling `T::Registrar::make_parachain(para)`; it never validates that the leaser recorded in that entry corresponds to the para's *current* manager. [1](#0-0)  Because `Leases<T>` entries are not automatically cleared on `swap`/`deregister`/re-`register` (only the root-only `clear_all_leases` clears them) [2](#0-1) , and `OnSwap::on_swap` merely swaps the raw `Leases` vectors between two `ParaId`s without checking manager identity [3](#0-2) , a stale lease entry can persist after a para changes managers and be exploited by any signed account.

### Finding Description
`trigger_onboard` is explicitly documented as callable "by anyone" as long as the origin is signed: [4](#0-3) . Its entire authorization logic is:

```
let leases = Leases::<T>::get(para);
match leases.first() {
    Some(Some(_lease_info)) => T::Registrar::make_parachain(para)?,
    Some(None) | None => return Err(Error::<T>::ParaNotOnboarding.into()),
};
``` [5](#0-4) 

This binds `_lease_info` but discards it — the account stored in the lease tuple (`(leaser, amount)`) is never compared against the para's current `ParaInfo.manager` in `pallet_registrar`. The only invariant enforced is "some deposit entry exists for the current period," which was designed to detect legitimate but un-onboarded leases (e.g., after a failed on-chain onboarding), not to authorize state transitions on behalf of arbitrary managers.

`Leases<T>` is keyed purely by `ParaId` and is populated by `Leaser::lease_out` [6](#0-5) , independent of the registrar's manager/lock state. Nothing ties a `Leases` entry's lifetime to a specific manager epoch of the para. Clearing is only done by `clear_all_leases`, a root-only (`ForceOrigin`) call [7](#0-6) , and by `manage_lease_period_start` naturally expiring entries at lease-period boundaries (`lease_periods.len() == 1` branch removes the entry) [8](#0-7) . Neither `swap` (`OnSwap::on_swap`, which just moves the vector between two `ParaId` keys) nor deregister/register flows in `paras_registrar` clear or re-key `Leases` based on new manager identity.

Given the described precondition — a para that had a lease under `old_leaser`, later transferred to a new manager via `swap`/`deregister`+`reserve`+`register` without an intervening `clear_all_leases`, and whose lease entry's first slot still reflects the yet-unexpired lease period — any signed account can call `trigger_onboard(para)`. The pallet only checks the lease presence, not leaser identity, so `T::Registrar::make_parachain(para)` executes and moves the para from `Parathread` to `Parachain` lifecycle state regardless of the new manager's consent.

### Impact Explanation
This produces an unauthorized parathread→parachain state transition triggered by an unprivileged third party, consuming a scarce parachain slot resource without the current manager's action or governance approval. This matches the stated scoped impact directly.

### Likelihood Explanation
The precondition requires a specific sequence: a lease must exist and not yet be expired/cleared (`clear_all_leases` is root-only and there is no automatic clearing tied to manager changes), and the para's manager must have changed in the interim (via `swap` or full deregister/re-register) while a lease entry for a still-current or future period remains in storage. This is a non-trivial but plausible sequence in production given crowdloan/slots-auction usage patterns where leases span many blocks/lease periods and manager changes (`swap`, `deregister`, re-`register`) can legitimately occur in that window. The call itself (`trigger_onboard`) requires only a signed origin — no fee/weight/proxy/multisig barrier prevents it once the state is reached.

### Recommendation
`trigger_onboard` (and/or the underlying `Leases` bookkeeping in `swap`/`deregister`) should validate that the stored leaser in the first `Leases` entry still corresponds to the para's current manager (via `T::Registrar`'s manager lookup) before calling `make_parachain`, or `Leases` entries should be forcibly cleared/rebated whenever the para's manager changes (in `on_swap`, `deregister`, and any manager-transfer flow), not only via the root-only `clear_all_leases`.

### Proof of Concept
Rust unit test extending the existing `trigger_onboard_works`/`lease_out_current_lease_period` tests in `polkadot/runtime/common/src/slots/mod.rs`:
1. Register para `1` under manager `A`; call `Slots::lease_out(1.into(), &A, amount, current_period, 1)` so `Leases::<Test>::get(1)` has `Some((A, amount))` in slot 0.
2. Simulate manager change without clearing leases: either call `Pallet::<Test>::on_swap(1.into(), 2.into())` (para-registrar swap hook) to move para 1's lease to para 2 while para 2 is registered/manager by `B`, or directly deregister/re-register para `1` under manager `B` via the registrar pallet's real extrinsics (`deregister` then `reserve`+`register`) without calling `clear_all_leases`.
3. Assert `TestRegistrar::<Test>::manager(para) == B` (new manager, unrelated to `A`).
4. Call `Slots::trigger_onboard(RuntimeOrigin::signed(C), para)` from an unrelated account `C`.
5. Assert `Ok(())` is returned and `TestRegistrar::<Test>::operations()` contains a `(para, _, true)` make_parachain entry — i.e., the parachain was onboarded despite the lease belonging to a stale account `A`, not to current manager `B`, and despite the caller `C` having no relationship to the para at all.

### Citations

**File:** polkadot/runtime/common/src/slots/mod.rs (L184-201)
```rust
		/// Clear all leases for a Para Id, refunding any deposits back to the original owners.
		///
		/// The dispatch origin for this call must match `T::ForceOrigin`.
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::clear_all_leases())]
		pub fn clear_all_leases(origin: OriginFor<T>, para: ParaId) -> DispatchResult {
			T::ForceOrigin::ensure_origin(origin)?;
			let deposits = Self::all_deposits_held(para);

			// Refund any deposits for these leases
			for (who, deposit) in deposits {
				let err_amount = T::Currency::unreserve(&who, deposit);
				debug_assert!(err_amount.is_zero());
			}

			Leases::<T>::remove(para);
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L203-223)
```rust
		/// Try to onboard a parachain that has a lease for the current lease period.
		///
		/// This function can be useful if there was some state issue with a para that should
		/// have onboarded, but was unable to. As long as they have a lease period, we can
		/// let them onboard from here.
		///
		/// Origin must be signed, but can be called by anyone.
		#[pallet::call_index(2)]
		#[pallet::weight(T::WeightInfo::trigger_onboard())]
		pub fn trigger_onboard(origin: OriginFor<T>, para: ParaId) -> DispatchResult {
			ensure_signed(origin)?;
			let leases = Leases::<T>::get(para);
			match leases.first() {
				// If the first element in leases is present, then it has a lease!
				// We can try to onboard it.
				Some(Some(_lease_info)) => T::Registrar::make_parachain(para)?,
				// Otherwise, it does not have a lease.
				Some(None) | None => return Err(Error::<T>::ParaNotOnboarding.into()),
			};
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L245-256)
```rust
			if lease_periods.len() == 1 {
				// Just one entry, which corresponds to the now-ended lease period.
				//
				// `para` is now just an on-demand parachain.
				//
				// Unreserve whatever is left.
				if let Some((who, value)) = &lease_periods[0] {
					T::Currency::unreserve(&who, *value);
				}

				// Remove the now-empty lease list.
				Leases::<T>::remove(para);
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L332-336)
```rust
impl<T: Config> crate::traits::OnSwap for Pallet<T> {
	fn on_swap(one: ParaId, other: ParaId) {
		Leases::<T>::mutate(one, |x| Leases::<T>::mutate(other, |y| core::mem::swap(x, y)))
	}
}
```

**File:** polkadot/runtime/common/src/slots/mod.rs (L343-426)
```rust
	fn lease_out(
		para: ParaId,
		leaser: &Self::AccountId,
		amount: <Self::Currency as Currency<Self::AccountId>>::Balance,
		period_begin: Self::LeasePeriod,
		period_count: Self::LeasePeriod,
	) -> Result<(), LeaseError> {
		let now = frame_system::Pallet::<T>::block_number();
		let (current_lease_period, _) =
			Self::lease_period_index(now).ok_or(LeaseError::NoLeasePeriod)?;
		// Finally, we update the deposit held so it is `amount` for the new lease period
		// indices that were won in the auction.
		let offset = period_begin
			.checked_sub(&current_lease_period)
			.and_then(|x| x.checked_into::<usize>())
			.ok_or(LeaseError::AlreadyEnded)?;

		// offset is the amount into the `Deposits` items list that our lease begins. `period_count`
		// is the number of items that it lasts for.

		// The lease period index range (begin, end) that newly belongs to this parachain
		// ID. We need to ensure that it features in `Deposits` to prevent it from being
		// reaped too early (any managed parachain whose `Deposits` set runs low will be
		// removed).
		Leases::<T>::try_mutate(para, |d| {
			// Left-pad with `None`s as necessary.
			if d.len() < offset {
				d.resize_with(offset, || None);
			}
			let period_count_usize =
				period_count.checked_into::<usize>().ok_or(LeaseError::AlreadyEnded)?;
			// Then place the deposit values for as long as the chain should exist.
			for i in offset..(offset + period_count_usize) {
				if d.len() > i {
					// Already exists but it's `None`. That means a later slot was already leased.
					// No problem.
					if d[i] == None {
						d[i] = Some((leaser.clone(), amount));
					} else {
						// The chain tried to lease the same period twice. This might be a griefing
						// attempt.
						//
						// We bail, not giving any lease and leave it for governance to sort out.
						return Err(LeaseError::AlreadyLeased);
					}
				} else if d.len() == i {
					// Doesn't exist. This is usual.
					d.push(Some((leaser.clone(), amount)));
				} else {
					// earlier resize means it must be >= i; qed
					// defensive code though since we really don't want to panic here.
				}
			}

			// Figure out whether we already have some funds of `leaser` held in reserve for
			// `para_id`.  If so, then we can deduct those from the amount that we need to reserve.
			let maybe_additional = amount.checked_sub(&Self::deposit_held(para, &leaser));
			if let Some(ref additional) = maybe_additional {
				T::Currency::reserve(&leaser, *additional)
					.map_err(|_| LeaseError::ReserveFailed)?;
			}

			let reserved = maybe_additional.unwrap_or_default();

			// Check if current lease period is same as period begin, and onboard them directly.
			// This will allow us to support onboarding new parachains in the middle of a lease
			// period.
			if current_lease_period == period_begin {
				// Best effort. Not much we can do if this fails.
				let _ = T::Registrar::make_parachain(para);
			}

			Self::deposit_event(Event::<T>::Leased {
				para_id: para,
				leaser: leaser.clone(),
				period_begin,
				period_count,
				extra_reserved: reserved,
				total_amount: amount,
			});

			Ok(())
		})
	}
```
