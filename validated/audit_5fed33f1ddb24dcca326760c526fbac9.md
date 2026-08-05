Audit Report

## Title
Stale `PendingSwap` entry survives counterparty deregistration, allowing unauthorized swap with unrelated re-registered ParaId - ([File: polkadot/runtime/common/src/paras_registrar/mod.rs])

## Summary
`swap` implements a two-phase commit via the `PendingSwap` map: an initiator calling `swap(id, other)` inserts `PendingSwap[id] = other` if no matching reverse entry exists; the swap completes only when a later call finds `PendingSwap::get(other) == Some(id)`. `do_deregister` clears only `PendingSwap::<T>::remove(id)` for the para being torn down, but never removes any entry where a different para's pending-swap target equals the deregistered id, allowing a stale unconfirmed swap offer to be completed against an unrelated future registrant of the reused ParaId.

## Finding Description
In the `swap` extrinsic [1](#0-0) , `ensure_root_para_or_owner` only authorizes the caller over `id`, not `other` [2](#0-1) . When no reverse pending swap exists yet, the call simply stores `PendingSwap::<T>::insert(id, other)` [3](#0-2) .

`do_deregister` only removes the entry keyed by the para being deregistered, `PendingSwap::<T>::remove(id)` [4](#0-3) . It performs no scan/removal for any `X` such that `PendingSwap::get(X) == Some(id)`. Thus if `A`'s owner previously called `swap(A, B)` producing `PendingSwap[A] = B` (unconfirmed), and `B` is later deregistered, the stale entry `PendingSwap[A] = B` is left intact.

Since `do_register`/`do_reserve` allow any unprivileged account to reserve and register a previously deregistered/freed ParaId (`Paras::<T>::contains_key` and `lifecycle(id).is_none()` checks only look at current state, not history) [5](#0-4) , a new unrelated owner can register at id `B` and then call `swap(B, A)`. `ensure_root_para_or_owner` succeeds because the new owner controls `B`. The check `PendingSwap::get(A) == Some(B)` still evaluates true because of the stale entry, so the lifecycle-compatible branch executes (`do_thread_and_chain_swap` or `T::OnSwap::on_swap`) [6](#0-5) , swapping state between `A` and the new unrelated `B` without `A`'s owner's consent for this specific counterparty. The `PendingSwap` map is keyed only by `ParaId`, with no generation counter or manager-identity binding tying the pending offer to the specific registration that existed when it was created, so a re-registered id inherits any dangling offer.

## Impact Explanation
This allows an unprivileged new registrant of a reused `ParaId` to force an unauthorized swap of parachain lifecycle/scheduling state (lease-holding vs. on-demand status) and trigger `T::OnSwap::on_swap` hook effects (e.g., lease/deposit record swaps in downstream pallets such as `slots`/`crowdloan`) against an unrelated existing para whose owner never consented to a swap with this new entity. This is a real logic bug in an in-scope runtime pallet (`paras_registrar`) with a concrete state-integrity impact rather than a purely theoretical issue.

## Likelihood Explanation
The exploit requires only standard, permissionless extrinsics: `swap` (initiator, unconfirmed), `deregister` (either by the counterparty's owner or governance) of the counterparty id, and `reserve`+`register` by any new unprivileged account at the freed id, followed by `swap` from the new owner. All lifecycle preconditions (`Parachain`/`Parathread` combinations accepted by `swap`) are ordinary reachable states. The only constraint is a timing window where the initiator's original swap offer is never confirmed before the counterparty is deregistered and reused — a realistic scenario since `deregister` and re-registration of freed ids are normal permissionless operations, and there is no expiry or invalidation on unconfirmed `PendingSwap` entries besides the flawed `do_deregister` cleanup.

## Recommendation
When deregistering a para in `do_deregister`, also invalidate any pending swap that references it as a target: before removing `PendingSwap::<T>::remove(id)`, look up whether some other id `X` has `PendingSwap::<T>::get(X) == Some(id)` and remove that entry too (or maintain a reverse index / symmetric bidirectional storage so a single removal invalidates both sides of an unconfirmed swap offer). Alternatively, bind pending swap entries to a registration generation/manager identity so a re-registered id cannot satisfy a stale offer.

## Proof of Concept
1. Register `para_1` (owner 1) as a lease-holding `Parachain`; register `para_2` (owner 2) as a `Parathread`.
2. Owner 1 calls `swap(para_1, para_2)` → `PendingSwap::<Test>::get(para_1) == Some(para_2)`.
3. Deregister `para_2` via `deregister`/`do_deregister`, run to cleanup completion.
4. Confirm `PendingSwap::<Test>::get(para_1)` is still `Some(para_2)` (the dangling entry).
5. A new unrelated account (owner 3) `reserve`s and `register`s a fresh para at the same `para_2` id (defaults to `Parathread`).
6. Owner 3 calls `swap(para_2, para_1)`.
7. Observe the call succeeds, `Swapped { para_id: para_2, other_id: para_1 }` is emitted, and `do_thread_and_chain_swap`/`T::OnSwap::on_swap` executes between `para_1` and owner 3's unrelated new registration — demonstrating the unauthorized swap. A fixed implementation should either clear the stale entry at step 3 (making step 6 fail with `NotRegistered`/`CannotSwap`, since no matching pending entry would exist) or otherwise prevent the swap from completing.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L326-367)
```rust
		pub fn swap(origin: OriginFor<T>, id: ParaId, other: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;

			// If `id` and `other` is the same id, we treat this as a "clear" function, and exit
			// early, since swapping the same id would otherwise be a noop.
			if id == other {
				PendingSwap::<T>::remove(id);
				return Ok(());
			}

			// Sanity check that `id` is even a para.
			let id_lifecycle =
				paras::Pallet::<T>::lifecycle(id).ok_or(Error::<T>::NotRegistered)?;

			if PendingSwap::<T>::get(other) == Some(id) {
				let other_lifecycle =
					paras::Pallet::<T>::lifecycle(other).ok_or(Error::<T>::NotRegistered)?;
				// identify which is a lease holding parachain and which is a parathread (on-demand
				// parachain)
				if id_lifecycle == ParaLifecycle::Parachain &&
					other_lifecycle == ParaLifecycle::Parathread
				{
					Self::do_thread_and_chain_swap(id, other);
				} else if id_lifecycle == ParaLifecycle::Parathread &&
					other_lifecycle == ParaLifecycle::Parachain
				{
					Self::do_thread_and_chain_swap(other, id);
				} else if id_lifecycle == ParaLifecycle::Parachain &&
					other_lifecycle == ParaLifecycle::Parachain
				{
					// If both chains are currently parachains, there is nothing funny we
					// need to do for their lifecycle management, just swap the underlying
					// data.
					T::OnSwap::on_swap(id, other);
				} else {
					return Err(Error::<T>::CannotSwap.into());
				}
				Self::deposit_event(Event::<T>::Swapped { para_id: id, other_id: other });
				PendingSwap::<T>::remove(other);
			} else {
				PendingSwap::<T>::insert(id, other);
			}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L572-586)
```rust
	fn ensure_root_para_or_owner(
		origin: <T as frame_system::Config>::RuntimeOrigin,
		id: ParaId,
	) -> DispatchResult {
		if let Ok(who) = ensure_signed(origin.clone()) {
			let para_info = Paras::<T>::get(id).ok_or(Error::<T>::NotRegistered)?;

			if para_info.manager == who {
				ensure!(!para_info.is_locked(), Error::<T>::ParaLocked);
				return Ok(());
			}
		}

		Self::ensure_root_or_para(origin, id)
	}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L604-657)
```rust
	fn do_reserve(
		who: T::AccountId,
		deposit_override: Option<BalanceOf<T>>,
		id: ParaId,
	) -> DispatchResult {
		ensure!(!Paras::<T>::contains_key(id), Error::<T>::AlreadyRegistered);
		ensure!(paras::Pallet::<T>::lifecycle(id).is_none(), Error::<T>::AlreadyRegistered);

		let deposit = deposit_override.unwrap_or_else(T::ParaDeposit::get);
		<T as Config>::Currency::reserve(&who, deposit)?;
		let info = ParaInfo { manager: who.clone(), deposit, locked: None };

		Paras::<T>::insert(id, info);
		Self::deposit_event(Event::<T>::Reserved { para_id: id, who });
		Ok(())
	}

	/// Attempt to register a new Para Id under management of `who` in the
	/// system with the given information.
	fn do_register(
		who: T::AccountId,
		deposit_override: Option<BalanceOf<T>>,
		id: ParaId,
		genesis_head: HeadData,
		validation_code: ValidationCode,
		ensure_reserved: bool,
	) -> DispatchResult {
		let deposited = if let Some(para_data) = Paras::<T>::get(id) {
			ensure!(para_data.manager == who, Error::<T>::NotOwner);
			ensure!(!para_data.is_locked(), Error::<T>::ParaLocked);
			para_data.deposit
		} else {
			ensure!(!ensure_reserved, Error::<T>::NotReserved);
			Default::default()
		};
		ensure!(paras::Pallet::<T>::lifecycle(id).is_none(), Error::<T>::AlreadyRegistered);
		let (genesis, deposit) =
			Self::validate_onboarding_data(genesis_head, validation_code, ParaKind::Parathread)?;
		let deposit = deposit_override.unwrap_or(deposit);

		if let Some(additional) = deposit.checked_sub(&deposited) {
			<T as Config>::Currency::reserve(&who, additional)?;
		} else if let Some(rebate) = deposited.checked_sub(&deposit) {
			<T as Config>::Currency::unreserve(&who, rebate);
		};
		let info = ParaInfo { manager: who.clone(), deposit, locked: None };

		Paras::<T>::insert(id, info);
		// We check above that para has no lifecycle, so this should not fail.
		let res = polkadot_runtime_parachains::schedule_para_initialize::<T>(id, genesis);
		debug_assert!(res.is_ok());
		Self::deposit_event(Event::<T>::Registered { para_id: id, manager: who });
		Ok(())
	}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L660-676)
```rust
	fn do_deregister(id: ParaId) -> DispatchResult {
		match paras::Pallet::<T>::lifecycle(id) {
			// Para must be a parathread (on-demand parachain), or not exist at all.
			Some(ParaLifecycle::Parathread) | None => {},
			_ => return Err(Error::<T>::NotParathread.into()),
		}
		polkadot_runtime_parachains::schedule_para_cleanup::<T>(id)
			.map_err(|_| Error::<T>::CannotDeregister)?;

		if let Some(info) = Paras::<T>::take(&id) {
			<T as Config>::Currency::unreserve(&info.manager, info.deposit);
		}

		PendingSwap::<T>::remove(id);
		Self::deposit_event(Event::<T>::Deregistered { para_id: id });
		Ok(())
	}
```
