Audit Report

## Title
Stale `PendingSwap` entry survives counterparty deregistration, allowing unauthorized swap with unrelated re-registered ParaId - ([File: polkadot/runtime/common/src/paras_registrar/mod.rs])

## Summary
`swap` implements a two-phase commit via the `PendingSwap` map: an initiator calling `swap(id, other)` inserts `PendingSwap[id] = other` when no reverse entry exists, and the swap only completes when the counterparty calls `swap(other, id)` and finds `PendingSwap::get(other) == Some(id)`. `do_deregister` clears only `PendingSwap::<T>::remove(id)` for the para being torn down, never scanning for or removing any other entry `X` such that `PendingSwap::get(X) == Some(id)`. This allows a stale, unconfirmed swap offer targeting a deregistered ParaId to be completed later by an unrelated party who re-registers that same ParaId.

## Finding Description
In `swap` [1](#0-0) , the initiator's authorization is checked only against `id` via `ensure_root_para_or_owner(origin, id)`, not against `other`. If no matching reverse entry `PendingSwap::get(other) == Some(id)` exists, the call simply stores `PendingSwap::<T>::insert(id, other)` as a pending, unconfirmed offer.

`do_deregister` [2](#0-1)  only removes `PendingSwap::<T>::remove(id)` — the entry keyed by the para being deregistered itself — but performs no reverse lookup/removal for any `X` whose pending swap target equals `id`. Consequently, if `A`'s owner calls `swap(A, B)` (storing `PendingSwap[A] = B`) and `B` is deregistered before confirming, `PendingSwap[A] = B` remains untouched.

`do_register`/`do_reserve` [3](#0-2)  allow any unprivileged signed account to reserve and register a fresh para at the same, now-vacant `ParaId` (e.g. `B`), since the only guard is that the id has no active lifecycle/registration — nothing checks for lingering `PendingSwap` references. The new owner of `B` can then call `swap(B, A)`; `ensure_root_para_or_owner` only validates control over `B` (which the new owner has), and the stale check `PendingSwap::get(A) == Some(B)` still evaluates true, so `do_thread_and_chain_swap` or `T::OnSwap::on_swap` [4](#0-3)  executes between `A` and the new unrelated `B`, without any consent from `A`'s owner for this specific counterparty.

## Impact Explanation
This lets an unprivileged new registrant of a reused `ParaId` force an unauthorized lifecycle/scheduling swap (and associated `OnSwap` hook effects such as lease/deposit record changes in downstream pallets like `slots`/`crowdloan`) with an unrelated existing parachain, violating the intended two-party-consent model of `swap`. The affected state (lease holding vs. on-demand status, deposits, auction data) is core parachain lifecycle state, so the impact is a legitimate protocol-state integrity issue rather than a cosmetic bug.

## Likelihood Explanation
The exploit path uses only standard signed extrinsics (`reserve`, `register`, `deregister`, `swap`) reachable by any account and requires no privileged access. It does depend on a timing window: an initiator must leave a swap unconfirmed, the counterparty ParaId must be deregistered before confirmation, and a third party must then re-register that same id and confirm. This is a realistic sequencing scenario given normal para lifecycle operations (deregistration and re-registration of on-demand parachains are routine), making the vulnerability practically triggerable rather than purely theoretical.

## Recommendation
In `do_deregister`, in addition to `PendingSwap::<T>::remove(id)`, also invalidate any pending swap that references the deregistered id as its target. Since only one outstanding pending swap can reference a given id at a time under current call semantics, this can be done by recording/looking up the reverse reference (e.g., maintaining a reverse index, or storing pending swaps symmetrically/bidirectionally) so that deregistering either side of an outstanding swap offer clears both entries.

## Proof of Concept
1. Register `para_1` (owner 1) and `para_2` (owner 2); elevate `para_1` to a lease-holding `Parachain`, leave `para_2` as `Parathread`.
2. Owner 1 calls `swap(para_1, para_2)` → `PendingSwap::<Test>::get(para_1) == Some(para_2)`.
3. Deregister `para_2` via `deregister`/`do_deregister`; advance to the session where cleanup completes.
4. Observe `PendingSwap::<Test>::get(para_1)` is still `Some(para_2)` (stale entry not cleared).
5. A new unrelated account (owner 3) calls `reserve` then `register` to re-register at the same `para_2` id.
6. Owner 3 calls `swap(para_2, para_1)`.
7. The call succeeds, emits `Swapped { para_id: para_2, other_id: para_1 }`, and executes `do_thread_and_chain_swap`/`T::OnSwap::on_swap` between `para_1` and owner 3's unrelated new registration — demonstrating the unauthorized cross-swap.

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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L702-710)
```rust
	/// Swap a lease holding parachain and parathread (on-demand parachain), which involves
	/// scheduling an appropriate lifecycle update.
	fn do_thread_and_chain_swap(to_downgrade: ParaId, to_upgrade: ParaId) {
		let res1 = polkadot_runtime_parachains::schedule_parachain_downgrade::<T>(to_downgrade);
		debug_assert!(res1.is_ok());
		let res2 = polkadot_runtime_parachains::schedule_parathread_upgrade::<T>(to_upgrade);
		debug_assert!(res2.is_ok());
		T::OnSwap::on_swap(to_upgrade, to_downgrade);
	}
```
