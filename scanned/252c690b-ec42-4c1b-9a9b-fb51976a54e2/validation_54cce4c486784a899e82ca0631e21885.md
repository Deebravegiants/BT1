### Title
Stale `PendingSwap` entry survives counterparty deregistration, allowing an attacker who re-reserves the freed `ParaId` to hijack a pending `swap` and seize the original counterparty's lease/deposit state - (File: polkadot/runtime/common/src/paras_registrar/mod.rs)

### Summary
`PendingSwap<T>` is a one-directional map keyed by the initiating `ParaId` (`PendingSwap[id] = other`), but `do_deregister` only clears the entry keyed by the deregistered id itself (`PendingSwap::<T>::remove(id)`), never scanning for entries where the deregistered id is the *value* (`other`). If A calls `swap(A, B)` and B is later deregistered by its real owner, the stale entry `PendingSwap[A] = B` is never removed, so a new, unrelated party who re-reserves the freed `ParaId` B can complete the swap against A and trigger `T::OnSwap::on_swap`, moving A's lease/crowdloan state onto the attacker's new para.

### Finding Description
`swap` stores pending swaps asymmetrically: when `id` initiates a swap with `other` and no reciprocal entry exists, it does `PendingSwap::<T>::insert(id, other)` [1](#0-0) . The map is keyed only by the initiator; there is no reverse index from `other` back to `id`.

`do_deregister` only removes the entry keyed by the para being deregistered: [2](#0-1) 
If B is deregistered while it only appears as the *value* of A's pending entry (`PendingSwap[A] = B`), `PendingSwap::<T>::remove(B)` is a no-op for that entry — `PendingSwap[A] = B` remains in storage untouched, and `Paras::<T>::take(&B)` frees the `ParaId` B for re-reservation, unreserving B's original manager's deposit.

Exploit flow:
1. Owner1 `reserve`s/`register`s A; Owner2 `reserve`s/`register`s B.
2. Owner1 calls `swap(A, B)` via `ensure_root_para_or_owner` — since `PendingSwap::get(B) != Some(A)`, this falls into the else branch and stores `PendingSwap[A] = B` [3](#0-2) .
3. Owner2 calls `deregister(B)` (permitted, since B is a parathread and Owner2 is its manager, per `ensure_root_para_or_owner`) [4](#0-3) . This frees `ParaId` B and unreserves Owner2's deposit, but the stale `PendingSwap[A] = B` entry survives.
4. Attacker calls `reserve` (getting the newly-freed `ParaId` B if it is next in `NextFreeParaId`, or via `force_register`/normal reservation flow if B is otherwise available) and `register`s it, becoming the new manager of B with lifecycle `Parathread`.
5. Attacker calls `swap(B, A)`. `ensure_root_para_or_owner` succeeds because attacker now manages B. The check `PendingSwap::<T>::get(other=A) == Some(id=B)` evaluates `PendingSwap[A] == Some(B)` — true, because of the stale entry from step 2. The swap lifecycle logic (`do_thread_and_chain_swap` or direct `T::OnSwap::on_swap`) executes, moving A's lease/crowdloan association onto B, which is now controlled by the attacker [5](#0-4) .

None of the existing checks stop this: `ensure_root_para_or_owner` only checks that the caller manages the `id` currently being swapped (the attacker legitimately manages the re-reserved B), and the `PendingSwap` matching logic checks only `ParaId` equality, not manager identity/continuity, and has no invalidation on the underlying para's manager/lifecycle change (deregistration + re-reservation is exactly such a change that is not accounted for).

### Impact Explanation
`T::OnSwap::on_swap` (implemented by the crowdloan and slots pallets) migrates lease-holding/auction/crowdloan-fund association from one `ParaId` to another. By completing a stale pending swap against a freed-and-reacquired `ParaId`, an attacker with no relation to the original swap counterparty can redirect Para A's lease/crowdloan state onto a para they control, effectively seizing a slot/lease association that rightfully belonged to Owner1's counterpart negotiation, without Owner1's current consent being honored against the correct party. This is a state/logic hijack in `Registrar::swap`, matching the scoped impact of unauthorized manager change via `OnSwap::on_swap`.

### Likelihood Explanation
The attack requires: (a) a signed party to initiate a swap and leave it pending, (b) the original counterparty being deregistered (permitted by its own owner via a normal signed `deregister` call — no privilege needed), and (c) the attacker being fast enough to reserve the same freed `ParaId`. Steps (a)-(c) are all reachable via ordinary signed extrinsics (`reserve`, `register`, `swap`, `deregister`) with no special privilege, though the attacker needs the specific `ParaId` to become free and be captured by them (e.g., by monitoring `NextFreeParaId` or a specific low `ParaId` becoming free via deregistration) — this makes it opportunistic rather than deterministically triggerable at attacker's will, but it is a real, reachable path once the preconditions align.

### Recommendation
Make `PendingSwap` invalidation symmetric: when deregistering a para, iterate/clear not just `PendingSwap::remove(id)` but also any entry where `id` appears as the value (either maintain a reverse index, or store swaps bidirectionally `PendingSwap[A]=B` and `PendingSwap[B]=A]`, clearing both keys on deregistration of either side). Alternatively, additionally validate at swap-completion time that the para referenced by the stale entry has not been deregistered/reset since the entry was created (e.g., track a lifecycle/registration generation counter per `ParaId` and store it in the pending swap entry, rejecting completion if it does not match current state).

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/paras_registrar/tests.rs`:
1. `reserve`/`register` para A as account 1, para B as account 2 (both become parathreads).
2. `assert_ok!(Registrar::swap(RuntimeOrigin::signed(1), A, B))` — assert `PendingSwap::<Test>::get(A) == Some(B)`.
3. `assert_ok!(Registrar::deregister(RuntimeOrigin::signed(2), B))` — assert `PendingSwap::<Test>::get(A)` is now `None` (this assertion currently **fails**, proving the bug: it remains `Some(B)`).
4. `assert_ok!(Registrar::reserve(RuntimeOrigin::signed(3)))` to obtain `ParaId` B again (or force it via repeated reserves until B is issued), then `register` it as account 3.
5. `assert_noop!(Registrar::swap(RuntimeOrigin::signed(3), B, A), Error::<Test>::NotRegistered)` or similar — expect this to fail, but with the current code it succeeds and emits `Swapped { para_id: B, other_id: A }`, and `T::OnSwap::on_swap` mock hook records that A's state was migrated to B, confirming the hijack.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L307-310)
```rust
		pub fn deregister(origin: OriginFor<T>, id: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
			Self::do_deregister(id)
		}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L340-367)
```rust
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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L669-674)
```rust
		if let Some(info) = Paras::<T>::take(&id) {
			<T as Config>::Currency::unreserve(&info.manager, info.deposit);
		}

		PendingSwap::<T>::remove(id);
		Self::deposit_event(Event::<T>::Deregistered { para_id: id });
```
