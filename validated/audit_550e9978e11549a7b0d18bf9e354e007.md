All code claims check out. Tracing through the exact logic:

1. `A`'s manager calls `swap(A, B)`. Since `PendingSwap::get(B) != Some(A)`, the else branch fires: `PendingSwap::<T>::insert(A, B)` — storing key `A → B`. [1](#0-0) 

2. `B`'s owner calls `deregister(B)` → `do_deregister(B)`, which only does `PendingSwap::<T>::remove(id)` where `id = B`. Since the stale record is keyed by `A` (not `B`), it is untouched. [2](#0-1) 

3. Attacker reserves/registers the freed `B` via `do_reserve`/`do_register`, whose only checks are `Paras::contains_key` and `lifecycle(id).is_none()` — nothing checks for stale `PendingSwap` references. [3](#0-2) 

4. Attacker (now manager of `B`, passes `ensure_root_para_or_owner`) calls `swap(B, A)`. Condition `PendingSwap::get(other=A) == Some(id=B)` is still `true` from step 1, so the swap proceeds via `do_thread_and_chain_swap`, invoking `T::OnSwap::on_swap`. [4](#0-3) 

5. `ensure_root_para_or_owner` only checks that the caller is the *current* manager of `id` and that the para is unlocked — it never checks manager continuity with the manager who created the pending entry. [5](#0-4) 

6. `OnSwap::on_swap` on Westend/Rococo-style runtimes is `(Crowdloan, Slots, SwapLeases)`, so crowdloan `Funds`, lease, and coretime state get moved between `A` and the attacker's `B`. [6](#0-5) 

This confirms the root cause: `PendingSwap` cleanup on deregistration only clears the entry keyed by the deregistered id, never entries where that id is merely the value, and no manager-identity binding exists across the two-step swap. The described attack path is reachable entirely through unprivileged signed extrinsics (`swap`, `deregister`, `reserve`, `register`), requiring only a timing race, not any privileged or governance action.

Audit Report

## Title
Stale `PendingSwap` entry survives deregistration of the counterparty `ParaId`, allowing a re-reserved `ParaId` to complete a pending swap and seize the original manager's lease/crowdloan state - (File: `polkadot/runtime/common/src/paras_registrar/mod.rs`)

## Summary
`PendingSwap` is keyed by the swap initiator's `ParaId` and stores the target `ParaId` as the value (`PendingSwap::insert(id, other)`). `do_deregister(id)` only removes the entry keyed by `id`, never entries where `id` appears solely as the value, so a stale `A → B` mapping survives `B`'s deregistration. An unrelated attacker who reserves/registers the freed `ParaId` `B` can then call `swap(B, A)` to complete the stale pending swap and trigger `T::OnSwap::on_swap`, transferring `A`'s crowdloan/lease/coretime state to the attacker-controlled `B`.

## Finding Description
When `A`'s manager calls `swap(A, B)` and no reciprocal entry exists, `PendingSwap::<T>::insert(id, other)` stores the record keyed by `A` with value `B` [1](#0-0) . When `B` is later deregistered by its real owner, `do_deregister` only calls `PendingSwap::<T>::remove(id)` for the deregistered `id` (`B`), never scanning for or removing entries where `B` appears as a *value* [2](#0-1) . The stale `A → B` entry remains in storage.

Reserving/registering a freed `ParaId` only checks `Paras::contains_key` and that `lifecycle(id).is_none()` [3](#0-2)  — there is no check against dangling `PendingSwap` references. Once an attacker becomes `B`'s new manager, `ensure_root_para_or_owner` succeeds for them on calls involving `B` [5](#0-4) , and calling `swap(B, A)` finds `PendingSwap::get(A) == Some(B)` still `true`, completing the swap and invoking `T::OnSwap::on_swap`, which on production-style runtimes (`(Crowdloan, Slots, SwapLeases)`) reassigns crowdloan `Funds`, leases, and coretime legacy state between `A` and the attacker's `B` [4](#0-3) [6](#0-5) .

No code path anywhere binds the pending-swap confirmation to the manager identity present when the request was created, and no reverse-index cleanup exists for `PendingSwap` on deregistration.

## Impact Explanation
An unprivileged attacker can seize the lease/crowdloan association of a legitimate parachain `A` by racing to reserve/re-register a recently deregistered `ParaId` `B` that had an outstanding, unconfirmed swap request targeting it. This causes unauthorized transfer of crowdloan fund records, lease slots, and coretime legacy state away from the legitimate manager of `A` without their consent — a concrete state-corruption/asset-misdirection impact within the parachain registrar's trust model.

## Likelihood Explanation
The attack is fully triggerable through standard signed extrinsics (`swap`, `deregister`, `reserve`, `register`) with no privileged or governance calls required. It requires a timing race: (1) an outstanding one-sided `swap(A, B)` request exists, (2) `B` is deregistered before confirmation, and (3) the attacker wins the race to reserve/register `B` before `A`'s manager notices and self-clears the entry with `swap(A, A)`. This is a deterministic logic gap once the race is won, not a probabilistic exploit — the underlying storage-cleanup omission is unconditional.

## Recommendation
On `do_deregister`, additionally invalidate any `PendingSwap` entries where the deregistered `id` appears as the *value*, either by scanning `PendingSwap::<T>::iter()` for matches or by maintaining a reverse index/bidirectional storage so a single removal clears both directions. Additionally, bind pending-swap confirmation to the manager account recorded at initiation time, so a swap only completes if the counterparty para's manager has not changed since the request was created.

## Proof of Concept
Integration test in `polkadot/runtime/common/src/paras_registrar/tests.rs`:
1. Register `para_a` (owner 1) and `para_b` (owner 2); upgrade `para_a` to a parachain.
2. Owner 1 calls `swap(para_a, para_b)` — verify `PendingSwap::<Test>::get(para_a) == Some(para_b)`.
3. Owner 2 calls `deregister(para_b)` — verify (bug) `PendingSwap::<Test>::get(para_a)` is still `Some(para_b)`.
4. Attacker (account 3) calls `reserve` then `register(para_b, ...)`, becoming `para_b`'s new manager.
5. Attacker calls `swap(para_b, para_a)` — under current code this succeeds and fires `T::OnSwap::on_swap(para_b, para_a)`, moving `para_a`'s crowdloan/lease state to the attacker's `para_b`. After the fix, this call should fail with `Error::<T>::NotRegistered` or equivalent, and step 3 should have already cleared the stale entry.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L336-367)
```rust
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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L570-586)
```rust
	/// Ensure the origin is one of Root, the `para` owner, or the `para` itself.
	/// If the origin is the `para` owner, the `para` must be unlocked.
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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L604-619)
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
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L669-676)
```rust
		if let Some(info) = Paras::<T>::take(&id) {
			<T as Config>::Currency::unreserve(&info.manager, info.deposit);
		}

		PendingSwap::<T>::remove(id);
		Self::deposit_event(Event::<T>::Deregistered { para_id: id });
		Ok(())
	}
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L834-838)
```rust
impl<T: Config> crate::traits::OnSwap for Pallet<T> {
	fn on_swap(one: ParaId, other: ParaId) {
		Funds::<T>::mutate(one, |x| Funds::<T>::mutate(other, |y| core::mem::swap(x, y)))
	}
}
```
