### Title
Stale `PendingSwap` entries pointing to a deregistered `ParaId` allow an unprivileged attacker who re-registers the freed ID to force-complete a swap against the original counterparty, hijacking its lease/crowdloan association via `OnSwap::on_swap` - (File: polkadot/runtime/common/src/paras_registrar/mod.rs)

### Summary
`do_deregister` only clears `PendingSwap::<T>::remove(id)` for the entry keyed by the *deregistering* para, but never scans for or clears entries where the deregistered `id` is the *value* (i.e. the counterparty referenced by another para's still-open swap request). If the ID that was pointed to is later reused by a new, unrelated registrant via `reserve()`/`register()`, that new owner can call `swap()` and satisfy the stale `PendingSwap::get(other) == Some(id)` check, completing a swap against the original initiator's para without their renewed consent.

### Finding Description
`swap(origin, id, other)` in [1](#0-0)  implements a two-phase handshake: the first caller does `PendingSwap::<T>::insert(id, other)`; the second, opposite caller triggers the actual swap when `PendingSwap::<T>::get(other) == Some(id)` holds, and only then removes the entry via `PendingSwap::<T>::remove(other)`.

`do_deregister(id)` in [2](#0-1)  only removes `PendingSwap::<T>::remove(id)` — the slot keyed by the deregistering para itself. It never checks or clears entries where `id` appears as the *value* held under some other para's key. Concretely: if para `A`'s owner calls `swap(A, B)`, this stores `PendingSwap[A] = B`. If `B`'s owner instead deregisters `B` (a perfectly normal, permitted call to `deregister(B)` via `ensure_root_para_or_owner`), `do_deregister(B)` clears `PendingSwap[B]` (which does not exist) but leaves `PendingSwap[A] = B` intact.

Because `ParaId`s are recycled (`NextFreeParaId`/manual `reserve`) and `do_reserve`/`do_register` never consult `PendingSwap` at all ( [3](#0-2) ), an unprivileged attacker can `reserve()` and `register()` a brand-new, unrelated para under the now-free ID `B`. The attacker, as the legitimate manager of the new `B`, then calls `swap(B, A)`. Inside `swap`, this evaluates `PendingSwap::get(other=A) == Some(id=B)` — which is still `true` from the stale entry — and the check in `ensure_root_para_or_owner(origin, id=B)` passes trivially since the attacker is `B`'s real manager. The swap proceeds, invoking `T::OnSwap::on_swap(A, B)` (via `do_thread_and_chain_swap` or the direct `Parachain`/`Parachain` branch), which per the trait definition swaps "leases, deposits held and thread/chain nature" between the two IDs [4](#0-3) . The crowdloan pallet implements `OnSwap` (confirmed via its `on_swap` handler in `polkadot/runtime/common/src/crowdloan/mod.rs`), so this swap propagates into crowdloan/lease state associated with `A`, transferring it onto the attacker's freshly registered, otherwise-unrelated para `B`.

None of the existing checks stop this: `ensure_root_para_or_owner` only verifies the caller manages the para ID passed as `id`, not that the para behind that ID is the same "logical" para that `A`'s owner originally intended to swap with; and `paras::Pallet::<T>::lifecycle(id)`/`lifecycle(other)` only check that both IDs are currently live parathreads/parachains, which the attacker's fresh registration trivially satisfies.

### Impact Explanation
An attacker with no special privileges can hijack a victim para's swap-transferable state (parachain/parathread status, deposits, and any `OnSwap`-linked crowdloan/lease association) by reusing a `ParaId` that was the un-cleared target of the victim's earlier `swap()` call. This is a genuine cross-pallet state-confusion bug distinct from the FundIndex-keyed crowdloan concern raised in the prompt (which is correctly not exploitable) — the real exploitable surface is the `PendingSwap` map itself.

### Likelihood Explanation
Requires a specific but realistic precondition: a para (`A`) owner initiates `swap(A, B)` and the counterparty (`B`)'s owner deregisters `B` instead of completing the swap (e.g., abandoning the on-demand para or having it fail onboarding). This is plausible since nothing prevents `B`'s manager from deregistering while a swap request against them is pending, and there is no UI/warning tying the two. Once this occurs, exploitation only needs a signed `reserve()` + `register()` + `swap()` sequence by any user — fully within a normal user's capabilities, repeatable for any recycled ID with a dangling pending-swap reference.

### Recommendation
When deregistering a para (`do_deregister`), also remove any `PendingSwap` entries where the deregistered `id` appears as the *value* (not just the key), e.g. by tracking swap requests bidirectionally or by additionally storing/checking a reverse index, so that a freed `ParaId` can never satisfy a stale pending-swap match. Alternatively, invalidate `PendingSwap` values whenever the pointed-to para transitions out of registration (via a hook in `schedule_para_cleanup`), and re-validate that both `id`/`other` in `swap()` have not been re-registered since the pending entry was created (e.g., by keying `PendingSwap` on `(ParaId, registration generation)` rather than raw `ParaId`).

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/integration_tests.rs` (mirrors `basic_swap_works`):
1. Register on-demand para `A` (owner `alice`) and on-demand para `B` (owner `bob`).
2. `alice` calls `Registrar::swap(A, B)` → assert `PendingSwap::<T>::get(A) == Some(B)`.
3. `bob` calls `Registrar::deregister(B)` → assert `Paras::<T>::get(B).is_none()` and `PendingSwap::<T>::get(B).is_none()`, but assert `PendingSwap::<T>::get(A) == Some(B)` **still holds** (stale entry).
4. Attacker `mallory` calls `Registrar::reserve()` then `Registrar::register(B, ..., ...)` to claim the freed ID `B`.
5. `mallory` calls `Registrar::swap(B, A)`.
6. Assert the swap executes successfully (no `CannotSwap`/`NotRegistered` error), `PendingSwap::<T>::get(A).is_none()` afterward, and that `A`'s lease/deposit/`OnSwap`-tracked state (e.g., crowdloan fund association if configured) is now associated with `mallory`'s para `B`, demonstrating the hijack of `alice`'s original swap counterpart state by an unrelated, newly-registered para.

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

**File:** polkadot/runtime/common/src/traits.rs (L258-265)
```rust
/// Runtime hook for when we swap a lease holding parachain and an on-demand parachain.
#[impl_trait_for_tuples::impl_for_tuples(30)]
pub trait OnSwap {
	/// Updates any needed state/references to enact a logical swap of two parachains. Identity,
	/// code and `head_data` remain equivalent for all parachains/threads, however other properties
	/// such as leases, deposits held and thread/chain nature are swapped.
	fn on_swap(one: ParaId, other: ParaId);
}
```
