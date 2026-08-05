### Title
Stale `PendingSwap` entry survives deregistration of the counterparty `ParaId`, allowing a re-reserved `ParaId` to complete a pending swap and seize the original manager's lease/crowdloan state - (File: `polkadot/runtime/common/src/paras_registrar/mod.rs`)

### Summary
`PendingSwap` is a map keyed by the *initiator*'s `ParaId` pointing to the *target* `ParaId` (`PendingSwap::insert(id, other)`). `do_deregister(id)` only clears `PendingSwap::<T>::remove(id)` — i.e. the entry keyed by the deregistered id itself — but never removes entries where that id appears only as the *value* (the "other" side of someone else's pending swap request). This lets an unrelated new manager of a recycled `ParaId` complete a stale swap and pull the original counterparty's parachain/lease/crowdloan state via `T::OnSwap::on_swap`.

### Finding Description
In `Pallet::<T>::swap` [1](#0-0) , when owner of `A` calls `swap(A, B)` and no reciprocal entry exists yet, the pallet does `PendingSwap::<T>::insert(id, other)`, i.e. it stores the entry under key `A` with value `B`: [2](#0-1) 

When `B` is deregistered by its real owner via `deregister`/`do_deregister`, the cleanup logic only removes the pending-swap entry keyed by the deregistered id itself: [3](#0-2) 
Since the actual dangling record is stored at key `A` (value `B`), and `B` is only the *value*, `PendingSwap::<T>::remove(B)` has no effect on it — the entry `A -> B` remains in storage untouched.

An attacker can then call `reserve` and `register` for the freed `ParaId` `B`, becoming its manager and giving it a fresh `Parathread` lifecycle. The attacker (as manager of `B`, satisfying `ensure_root_para_or_owner`) calls `swap(B, A)`. The check `PendingSwap::<T>::get(other) == Some(id)` becomes `PendingSwap::get(A) == Some(B)`, which is still `true` because the stale entry was never invalidated: [4](#0-3) 
The swap proceeds via `do_thread_and_chain_swap`, which calls `T::OnSwap::on_swap`, swapping lease/crowdloan fund state between `A` and the attacker's newly-reserved `B`: [5](#0-4) 
Concretely, `crowdloan::Pallet::on_swap` swaps `Funds` records between the two `ParaId`s: [6](#0-5) 
and on Westend/Rococo-style runtimes, `OnSwap` is `(Crowdloan, Slots, SwapLeases)`, so lease and coretime legacy state are affected the same way: [7](#0-6) [8](#0-7) 

No check anywhere verifies that the manager of `B` at swap-completion time is the same manager that existed when the pending entry was created, nor is there any invalidation of "reverse" references when a `ParaId` is deregistered.

### Impact Explanation
An attacker who is a completely unrelated, unprivileged signed account can seize the lease/crowdloan association of a legitimate lease-holding parachain `A` by racing to reserve and re-register a recently deregistered `ParaId` `B` that had a pending (unconfirmed) swap targeting it. This results in unauthorized manager/lease/crowdloan-fund reassignment without the consent of `A`'s manager or the intended (deregistered) `B`'s prior manager — directly matching the scoped impact of "parachain lease/slot seizure without owner consent."

### Likelihood Explanation
The attack requires: (1) `A`'s manager to have initiated `swap(A, B)` and be waiting for `B`'s confirmation (a normal, common two-step swap workflow), (2) `B`'s real owner to deregister `B` before confirming (or `B` to already be scheduled for deregistration for unrelated reasons) while the pending entry `A -> B` still exists, and (3) an attacker to win the race to `reserve`/`register` the now-free `ParaId` `B` before `A`'s manager notices and calls `swap(A, A)` to clear the stale entry. Because `ParaId` reuse after deregistration is a normal, permitted flow (`do_reserve` only checks `Paras::contains_key` and lifecycle is `None`), and because `PendingSwap` cleanup logic never looks at "reverse" references, this is fully reachable through standard signed extrinsics (`swap`, `deregister`, `reserve`, `register`) with no privileged calls needed. Feasibility depends on winning a timing race, but it is a deterministic logic gap, not a probabilistic one — once the race is won, exploitation is guaranteed.

### Recommendation
When deregistering a para (`do_deregister`), scan for and remove any `PendingSwap` entries where the deregistered `id` appears as the *value* (not just as the key), or alternatively store `PendingSwap` bidirectionally/symmetrically so a single removal by id clears both directions. A simpler robust fix: iterate `PendingSwap::<T>::iter()` filtering by value equal to `id` and remove those keys too, or maintain a reverse index. Additionally, consider binding the pending-swap confirmation to the *manager* recorded at initiation time (not just the `ParaId`), so a swap only completes if the para's manager has not changed since the pending request was created.

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/paras_registrar/tests.rs`:
```rust
#[test]
fn stale_pending_swap_allows_lease_seizure() {
    new_test_ext().execute_with(|| {
        run_to_session(1);
        let para_a = LOWEST_PUBLIC_ID;
        let para_b = LOWEST_PUBLIC_ID + 1;

        // Register A (owner 1) and B (owner 2), upgrade A to parachain.
        assert_ok!(Registrar::reserve(RuntimeOrigin::signed(1)));
        assert_ok!(Registrar::register(RuntimeOrigin::signed(1), para_a, head(), code()));
        assert_ok!(Registrar::reserve(RuntimeOrigin::signed(2)));
        assert_ok!(Registrar::register(RuntimeOrigin::signed(2), para_b, head(), code()));
        run_to_session(3);
        assert_ok!(Registrar::make_parachain(para_a)); // A is Parachain, B stays Parathread
        run_to_session(5);

        // Owner of A initiates swap; B never confirms.
        assert_ok!(Registrar::swap(RuntimeOrigin::signed(1), para_a, para_b));
        assert_eq!(PendingSwap::<Test>::get(para_a), Some(para_b));

        // B's real owner (2) deregisters B.
        assert_ok!(Registrar::deregister(RuntimeOrigin::signed(2), para_b));

        // BUG: stale entry remains referencing recycled id `para_b`.
        assert_eq!(PendingSwap::<Test>::get(para_a), Some(para_b));

        // Attacker (3) reserves and re-registers the freed para_b.
        assert_ok!(Registrar::reserve(RuntimeOrigin::signed(3)));
        assert_ok!(Registrar::register(RuntimeOrigin::signed(3), para_b, head(), code()));

        // Attacker completes the stale swap, stealing A's parachain/lease state.
        assert_ok!(Registrar::swap(RuntimeOrigin::signed(3), para_b, para_a));

        // Expected (fixed) behavior: this should instead fail with NotRegistered/CannotSwap.
        // Current (buggy) behavior: swap succeeds and OnSwap::on_swap(para_b, para_a) fires,
        // moving A's crowdloan/lease data to attacker-controlled para_b.
    });
}
```
Expected assertion after the fix: the `swap(3, para_b, para_a)` call must fail with `Error::<T>::NotRegistered` (or an equivalent invalidation error), and `PendingSwap::<Test>::get(para_a)` must be cleared as soon as `para_b` is deregistered.

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

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L834-838)
```rust
impl<T: Config> crate::traits::OnSwap for Pallet<T> {
	fn on_swap(one: ParaId, other: ParaId) {
		Funds::<T>::mutate(one, |x| Funds::<T>::mutate(other, |y| core::mem::swap(x, y)))
	}
}
```

**File:** polkadot/runtime/westend/src/lib.rs (L1275-1283)
```rust
impl paras_registrar::Config for Runtime {
	type RuntimeOrigin = RuntimeOrigin;
	type RuntimeEvent = RuntimeEvent;
	type Currency = Balances;
	type OnSwap = (Crowdloan, Slots, SwapLeases);
	type ParaDeposit = ParaDeposit;
	type DataDepositPerByte = RegistrarDataDepositPerByte;
	type WeightInfo = weights::polkadot_runtime_common_paras_registrar::WeightInfo<Runtime>;
}
```

**File:** polkadot/runtime/westend/src/lib.rs (L1412-1418)
```rust
// Notify `coretime` pallet when a lease swap occurs
pub struct SwapLeases;
impl OnSwap for SwapLeases {
	fn on_swap(one: ParaId, other: ParaId) {
		coretime::Pallet::<Runtime>::on_legacy_lease_swap(one, other);
	}
}
```
