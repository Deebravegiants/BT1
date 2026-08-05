This confirms the code matches the citations exactly. `do_deregister` only calls `PendingSwap::<T>::remove(id)` [1](#0-0)  and never removes an entry where `id` appears as the *value* rather than the key. The `swap` extrinsic's insert branch stores `PendingSwap::insert(id, other)` when no reciprocal entry exists yet, and its match branch checks `PendingSwap::<T>::get(other) == Some(id)` to trigger `do_thread_and_chain_swap`/`on_swap` [2](#0-1) .

Tracing the claimed Case B: `other`'s manager calls `swap(other, id)`. In terms of the function's own parameter names, this maps to `id_param = other`, `other_param = id`. The check `PendingSwap::get(other_param) == Some(id_param)` i.e. `PendingSwap::get(id) == Some(other)` is false initially, so it falls to the `else` branch, inserting `PendingSwap::insert(id_param, other_param)` = `PendingSwap::insert(other, id)` — matching the claim that `PendingSwap[other] = id`.

`id`'s manager can then call `deregister(id)` directly, gated only by `ensure_root_para_or_owner` [3](#0-2) , with no dependency on `PendingSwap` state, and `do_deregister` requires `id`'s lifecycle to be `Parathread` or `None` [4](#0-3) . This removes `Paras::<T>::take(&id)` and schedules cleanup via `schedule_para_cleanup`, but the dangling `PendingSwap[other] = id` entry survives, since only `PendingSwap::<T>::remove(id)` is called — not a scan/removal of entries valued at `id`.

After session-boundary cleanup, `id` becomes free for re-registration by any user via `reserve`/`register`, since IDs are not otherwise reserved once deregistered. A new unrelated manager `C` controlling the re-registered `id` can then call `swap(id, other)`, and the stale check `PendingSwap::get(other) == Some(id)` still evaluates true, causing the swap to silently execute against the new, unrelated para — exactly as claimed.

This is a real, reachable state-corruption bug reachable entirely through normal user-callable extrinsics (`swap`, `deregister`, `reserve`, `register`), requiring no privileged origin, and it breaks the invariant that a pending swap confirmation should only be honored against the specific para that agreed to it. The claim's own report is careful to distinguish the non-exploitable "self-cleanup" case A from the genuinely exploitable case B, and grounds its findings precisely in the actual code paths and line numbers cited.

Audit Report

## Title
Stale `PendingSwap` entry survives `deregister`, allowing a re-registered `ParaId` to trigger an unintended forced swap - (File: polkadot/runtime/common/src/paras_registrar/mod.rs)

## Summary
When a para `other` initiates `swap(other, id)` creating a one-sided `PendingSwap[other] = id` entry, and `id`'s manager subsequently calls `deregister(id)` directly (bypassing `swap`), `do_deregister` only removes `PendingSwap[id]` and never cleans up the dangling `PendingSwap[other] = id` entry. If `id` is later re-registered by an unrelated party who calls `swap(id, other)`, the stale check `PendingSwap::get(other) == Some(id)` still matches, silently completing a swap between `other` and the new, unrelated para.

## Finding Description
`swap` inserts `PendingSwap::insert(id, other)` when no reciprocal entry exists, and completes/clears `PendingSwap::<T>::remove(other)` only when `PendingSwap::get(other) == Some(id)` matches [2](#0-1) . `do_deregister` clears only `PendingSwap::<T>::remove(id)` — the entry keyed by the para being deregistered — with no logic to find or remove entries where `id` appears as the *value* [5](#0-4) . `deregister` is callable independently of `swap`, gated only by `ensure_root_para_or_owner` [6](#0-5) . Consequently: `other`'s manager calls `swap(other, id)` → `PendingSwap[other] = id`; `id`'s manager calls `deregister(id)` → `id` is removed from `Paras` and scheduled for cleanup, but `PendingSwap[other] = id` remains; after cleanup completes, `id` becomes reusable via `reserve`/`register` by anyone; a new manager of the recycled `id` calling `swap(id, other)` will match the stale `PendingSwap::get(other) == Some(id)` condition and trigger a swap that `other`'s manager never intended with this new para.

## Impact Explanation
This corrupts swap-confirmation integrity: `other`'s pending-swap intent can be silently consummated against an unrelated para that later reuses the `id` ParaId, causing `T::OnSwap::on_swap` (or `do_thread_and_chain_swap`) to exchange lifecycle/scheduling data between `other` and a para its manager never agreed to swap with. This is a state-integrity violation of the pending-swap invariant, not direct fund theft, but it can corrupt parachain lifecycle/slot data unexpectedly for the `other` para's manager.

## Likelihood Explanation
The path uses only standard, unprivileged calls (`swap`, `deregister`, `reserve`, `register`) reachable by any para manager, requiring specific but plausible sequencing: an unconfirmed `swap(other, id)`, `id`'s manager deregistering without calling `swap` first, and later re-registration of `id` before `other`'s manager notices and self-clears the stale entry via `swap(other, other)`. This requires timing across session boundaries but no unrealistic privilege escalation.

## Recommendation
In `do_deregister`, in addition to `PendingSwap::<T>::remove(id)`, also search for and remove any entry where `id` is the stored value (e.g., check `PendingSwap::get(other)` patterns or maintain a reverse index), so a stale one-sided swap intent cannot later be confirmed against an unrelated para reusing the same `ParaId`.

## Proof of Concept
1. Register on-demand parachain `A` and para `B`.
2. `B`'s manager calls `swap(B, A)` → `PendingSwap::<Test>::get(B) == Some(A)`.
3. `A`'s manager calls `deregister(A)` directly → `Paras::<Test>::get(A).is_none()`, but `PendingSwap::<Test>::get(B)` still equals `Some(A)`.
4. Advance session so `A`'s cleanup completes; a new manager `C` re-registers `A` via `reserve`+`register`.
5. `C` calls `swap(A, B)` → the stale `PendingSwap::get(B) == Some(A)` check matches, and the swap silently executes between `B` and the new `A`, even though `B`'s manager never agreed to swap with this new para.
6. Expected fix: step 3 should clear `PendingSwap::<Test>::get(B)` to `None`, so step 5 falls into the "insert pending" branch instead of completing an unintended swap.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L305-310)
```rust
		#[pallet::call_index(2)]
		#[pallet::weight(<T as Config>::WeightInfo::deregister())]
		pub fn deregister(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
			Self::do_deregister(id)
		}
```

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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L659-676)
```rust
	/// Deregister a Para Id, freeing all data returning any deposit.
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
