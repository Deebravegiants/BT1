### Title
Stale `PendingSwap` entry survives `deregister`, allowing a re-registered `ParaId` to trigger an unintended forced swap - (File: `polkadot/runtime/common/src/paras_registrar/mod.rs`)

### Summary
The specific scenario described in the question (the *initiator* of `swap` deregistering their own para before the reciprocal call) is **not** exploitable, because `do_deregister` calls `PendingSwap::<T>::remove(id)`, which deletes exactly the entry the initiator's own `swap(id, other)` call just created. However, a closely related and still-reachable variant exists: if the **counterpart** (`other`) submits `swap(other, id)` first, and then `id`'s manager calls `deregister(id)` directly (without ever calling `swap`), the stale entry `PendingSwap[other] = id` is never cleaned up, since `do_deregister` only removes `PendingSwap::<T>::remove(id)` (keyed by `id`), not entries where `id` appears as the *value*.

### Finding Description
- `swap` at [1](#0-0)  inserts a one-sided pending record `PendingSwap[id] = other` when no reciprocal exists yet, or completes and clears `PendingSwap[other]` when a match is found.
- `do_deregister` at [2](#0-1)  only clears `PendingSwap::<T>::remove(id)` — i.e. the entry keyed by the para being deregistered — and does not scan for or remove any entry elsewhere in the map whose *value* equals `id`.
- Case A (as literally asked): `id`'s manager calls `swap(id, other)` → `PendingSwap[id] = other`. If `id`'s manager then calls `deregister(id)`, `do_deregister` removes `PendingSwap[id]`, which is precisely the entry just created. No dangling reference to `id` remains from this call. This exact path is **not** exploitable.
- Case B (real gap): `other`'s manager calls `swap(other, id)` first → `PendingSwap[other] = id`. `id`'s manager then calls `deregister(id)` directly (bypassing `swap` entirely — deregister only requires `ensure_root_para_or_owner`, no dependency on `PendingSwap` state). `do_deregister` removes `PendingSwap[id]` (which doesn't exist, no-op) but leaves `PendingSwap[other] = id` dangling, referencing a para that has now had its `Paras::<T>` entry removed and its lifecycle scheduled for cleanup via `schedule_para_cleanup`.
- After the on-chain cleanup completes at a session boundary, `id` becomes fully deregistered and can be freely re-registered (via `reserve`/`register`) by any user, since `ParaId`s ≥ `LOWEST_PUBLIC_ID` are not otherwise reserved.
- If a new (unrelated or same) manager later re-registers `id` and calls `swap(id, other)`, the check `PendingSwap::<T>::get(other) == Some(id)` at [3](#0-2)  still evaluates true against the stale entry, causing `Self::do_thread_and_chain_swap` (or `T::OnSwap::on_swap`) to execute between `other` and the *new, unrelated* para that happens to reuse `id`, silently completing a swap that `other`'s manager never intended against this new para.

### Impact Explanation
This lets `other`'s pending-swap intent be hijacked by whoever later comes to control the recycled `ParaId`, causing `T::OnSwap::on_swap` to exchange lifecycle/scheduling state (and any data swapped by downstream consumers such as slots/leases) between `other` and an unrelated parachain. This is a logic-integrity/state-corruption issue for the `other` para's manager, not a direct token theft, but it violates the invariant that pending swap confirmations should only complete against the para that was actually agreed to.

### Likelihood Explanation
Requires: (1) `other`'s manager to submit an unconfirmed `swap(other, id)`, (2) `id`'s manager to deregister without going through `swap`, (3) `id` to be re-registered (by anyone) before `other`'s manager notices and calls `swap(other, other)` to clear the stale entry themselves. Step 2 requires no special privilege — `deregister` is callable by the para's own manager. Step 3 requires ParaId reuse, which is permitted by design once a para's lifecycle transitions to fully deregistered. This is feasible but requires specific sequencing/timing across session boundaries and depends on `other`'s manager not proactively clearing their pending entry — a plausible but not automatically pathological scenario.

### Recommendation
In `do_deregister`, in addition to `PendingSwap::<T>::remove(id)`, also clear any pending swap entry that references `id` as its *value* (i.e., iterate/check `PendingSwap` for `other` such that `PendingSwap[other] == Some(id)` and remove it), or maintain a reverse index so stale swap intents referencing a deregistered para cannot later be "confirmed" against a re-registered, unrelated para reusing the same `ParaId`.

### Proof of Concept
Rust unit test in `polkadot/runtime/common/src/paras_registrar/tests.rs`:
1. Register para `A` (on-demand) and para `B` (on-demand/parachain per lifecycle needs for a valid `swap` combination).
2. `B`'s manager calls `swap(B, A)` → assert `PendingSwap::<Test>::get(B) == Some(A)`.
3. `A`'s manager calls `deregister(A)` directly (not via `swap`) → assert success, `Paras::<Test>::get(A).is_none()`.
4. Assert (current buggy behavior) `PendingSwap::<Test>::get(B) == Some(A)` still exists — dangling entry.
5. Advance session so `A`'s cleanup completes; re-register `A` under a new/unrelated manager `C` via `reserve`+`register`.
6. `C` calls `swap(A, B)` → currently succeeds and triggers `do_thread_and_chain_swap`/`on_swap` between `B` and the new `A`, even though `B`'s original swap intent was with the old, now-deleted `A`.
7. Expected (fixed) behavior: step 4 should show `PendingSwap::<Test>::get(B) == None` after deregistration, and step 6 should fall into the "insert pending" branch rather than immediately completing the swap.

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
