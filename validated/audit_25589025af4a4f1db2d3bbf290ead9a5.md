Audit Report

## Title
Stale `PendingSwap` entry survives `deregister`, allowing a re-registered `ParaId` to trigger an unintended forced swap - (File: `polkadot/runtime/common/src/paras_registrar/mod.rs`)

## Summary
`do_deregister` only clears `PendingSwap::<T>::remove(id)` — the entry keyed by the para being deregistered — but never removes any entry elsewhere in the map where `id` appears as the *value* (i.e. `PendingSwap[other] == Some(id)`) [1](#0-0) . If `other`'s manager previously called `swap(other, id)` to register a one-sided pending swap intent [2](#0-1) , and `id`'s manager then calls `deregister(id)` directly instead of confirming/cancelling the swap, the entry `PendingSwap[other] = id` becomes stale but is never cleared.

## Finding Description
The `swap` extrinsic inserts a pending record `PendingSwap[id] = other` if no reciprocal exists, or completes the swap and clears `PendingSwap[other]` if `PendingSwap::<T>::get(other) == Some(id)` [3](#0-2) . `deregister` is callable independently by root, the para's own manager, or the para itself via `ensure_root_para_or_owner`, with no dependency on `PendingSwap` state [4](#0-3) . `do_deregister` schedules cleanup, removes the `Paras` entry, and only removes `PendingSwap::<T>::remove(id)` — not any reverse reference — before emitting `Deregistered` [1](#0-0) .

Exploit path:
1. `other`'s manager calls `swap(other, id)` → `PendingSwap[other] = id`.
2. `id`'s manager calls `deregister(id)` directly (bypassing `swap`) → `do_deregister` removes `PendingSwap[id]` (a no-op since it doesn't exist) but leaves `PendingSwap[other] = id` dangling.
3. After session-boundary cleanup completes, `id` is fully deregistered; `do_reserve`/`do_register` only require `paras::Pallet::<T>::lifecycle(id).is_none()` [5](#0-4) [6](#0-5) , so any unrelated user can `reserve`/`register` the same `id` again.
4. The new controller of `id` calls `swap(id, other)`. The check `PendingSwap::<T>::get(other) == Some(id)` still evaluates true against the stale entry [7](#0-6) , causing `do_thread_and_chain_swap` or `T::OnSwap::on_swap` to execute between `other` and the new, unrelated para reusing `id` — without `other`'s manager's renewed consent.

This is a real and reachable gap: no code path clears reverse references to a deregistered `ParaId` in `PendingSwap`, and `ParaId` reuse after full cleanup is by-design behavior (`NextFreeParaId` only affects `reserve`'s auto-assigned IDs; direct reuse via `reserve`/`register` targeting an available `id` is not blocked). The report's Case A (self-created entry cleared by the initiator's own deregister) is correctly identified as non-exploitable and is not part of the claimed vulnerability.

## Impact Explanation
This breaks the intended security invariant that a `swap` confirmation should only execute against the specific para that was mutually agreed upon. `other`'s manager loses control over which para their pending swap intent completes against — a completely unrelated party who later acquires the recycled `ParaId` can trigger an actual lifecycle/data swap (`do_thread_and_chain_swap` or `OnSwap::on_swap`, which can affect slot/lease-related state depending on downstream consumers) without `other`'s renewed consent. This is a logic-integrity/state-corruption issue affecting `other`'s para lifecycle and any data exchanged via `OnSwap`, rather than direct fund theft, but it is a genuine violation of the swap-confirmation invariant enforced entirely by on-chain pallet logic.

## Likelihood Explanation
The exploit requires: (1) `other`'s manager to submit an unconfirmed `swap(other, id)`; (2) `id`'s manager to deregister without going through `swap` to cancel it; (3) `id` to be re-registered before `other`'s manager notices and self-clears the entry via `swap(other, other)`. All of these are ordinary, permission-appropriate operations (manager-level actions on paras they legitimately control), requiring no privilege escalation — deregistration and swap are both callable by a para's own manager. The main constraint is timing/sequencing across a session boundary and depends on `other`'s manager not proactively clearing the stale entry, which is a plausible but not guaranteed sequence of events in a live network with many parachain managers.

## Recommendation
In `do_deregister`, in addition to `PendingSwap::<T>::remove(id)`, also clear any pending entry where `id` appears as the value (scan/maintain a reverse index for `PendingSwap`, or restructure the swap-intent bookkeeping to be symmetric/keyed so that deregistration of either side of a pending swap invalidates it). Alternatively, require that `swap` re-validate a freshness/nonce tied to registration to prevent a recycled `ParaId` from satisfying a stale pending-swap match.

## Proof of Concept
Rust unit test (to be added to `polkadot/runtime/common/src/paras_registrar/tests.rs`):
1. Register on-demand paras `A` and `B` with appropriate lifecycle for a valid swap.
2. `B`'s manager calls `swap(B, A)` → assert `PendingSwap::<Test>::get(B) == Some(A)`.
3. `A`'s manager calls `deregister(A)` directly → assert success and `Paras::<Test>::get(A).is_none()`.
4. Assert `PendingSwap::<Test>::get(B) == Some(A)` still exists (dangling entry) — demonstrates the bug.
5. Advance session so `A`'s cleanup completes; a new/unrelated user `C` calls `reserve`+`register` to re-acquire `A`.
6. `C` calls `swap(A, B)` → observe it succeeds and triggers `do_thread_and_chain_swap`/`on_swap` between `B` and the new `A`, even though `B`'s original intent targeted the old, now-deleted `A`.
7. Expected fixed behavior: step 4 should show `PendingSwap::<Test>::get(B) == None`, and step 6 should fall into the "insert pending" branch instead of immediately completing the swap.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L307-310)
```rust
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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L609-610)
```rust
		ensure!(!Paras::<T>::contains_key(id), Error::<T>::AlreadyRegistered);
		ensure!(paras::Pallet::<T>::lifecycle(id).is_none(), Error::<T>::AlreadyRegistered);
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L636-639)
```rust
			ensure!(!ensure_reserved, Error::<T>::NotReserved);
			Default::default()
		};
		ensure!(paras::Pallet::<T>::lifecycle(id).is_none(), Error::<T>::AlreadyRegistered);
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
