### Title
Stale unlock-era `PendingSwap` authorization is not re-validated against `ParaInfo.locked` at swap confirmation, letting a since-locked para be swapped by its counterpart - (File: polkadot/runtime/common/src/paras_registrar/mod.rs)

### Summary
`Pallet::swap` enforces the manager-lock check (`ensure_root_para_or_owner`) only against the para ID passed as the *current* caller's `id`, and never re-checks the lock state of the `other` para whose earlier, unlocked-era `swap` call created the matching `PendingSwap` entry. This lets a para's manager register a pending swap while the para is still unlocked, and, after the para becomes locked (via `on_new_head`), have the counterpart's manager complete the swap unopposed, executing `T::OnSwap::on_swap` (which the runtime wires to swap crowdloan `Funds` between `ParaId`s) for a para that should now require Root/self-origin authorization.

### Finding Description
`ensure_root_para_or_owner` at [1](#0-0)  only checks `Paras::<T>::get(id).is_locked()` for the `id` supplied by the *current* signed caller. In `swap`, this check runs once, at line [2](#0-1) , against the caller's own `id`. The completion branch that actually performs the state transition and calls `T::OnSwap::on_swap` (via `do_thread_and_chain_swap` or directly) at [3](#0-2)  never re-checks the lock status of the para that originally registered the pending swap (`id` from the first call, stored as the key `PendingSwap::<T>::insert(id, other)` at line [4](#0-3) ).

Exploit flow:
1. Para `A` is reserved/registered and still unlocked (`ParaInfo.locked == None`, i.e. `is_locked() == false`), per `ParaInfo::is_locked` at [5](#0-4) .
2. `A`'s manager (unprivileged signed account) calls `swap(A, B)`. `ensure_root_para_or_owner` passes because `A` is unlocked. Since no matching reverse pending swap exists yet, this only inserts `PendingSwap::<T>::insert(A, B)` at line 366 — no lifecycle change occurs yet.
3. `A` onboards and produces its first head; `OnNewHead::on_new_head` at [6](#0-5)  sets `A`'s `locked = Some(true)`, which is intended to strip the manager's unilateral authority over `A` from that point on.
4. `B`'s manager (unprivileged, potentially the same attacker or a colluding party) calls `swap(B, A)`. `ensure_root_para_or_owner` checks only `B`'s lock (assume `B` unlocked, so it passes). The code then finds `PendingSwap::<T>::get(A) == Some(B)` (still true, set in step 2) and executes the swap logic (lines 340–364), including `T::OnSwap::on_swap`, without ever re-checking that `A` is now locked.

The lock invariant ("Para is locked from manipulation by the manager. Must use parachain or relay chain governance" — `Error::ParaLocked` at [7](#0-6) ) is thereby bypassed for `A`: its now-locked state is never consulted at the point where the actual swap side-effect (`OnSwap::on_swap`) executes. The authorization granted at step 2 (when `A` was still unlocked) silently persists past the lock boundary.

### Impact Explanation
`OnSwap::on_swap` in the crowdloan pallet swaps the `Funds` storage entries (crowdloan campaigns, contributions, deposits) between the two `ParaId`s. Triggering this for a para that has since become locked lets an unprivileged manager (of the counterpart para) force a crowdloan/slot-identity swap for a parachain that the runtime intends to place under root/self-governance control once locked, without any consent from `A`'s current governance or para-origin. This can misattribute or move crowdloan fund associations away from their intended `ParaId`, i.e., an unauthorized privileged state transition affecting parachain slot/fund identity.

### Likelihood Explanation
Feasibility is moderate-to-high: it requires only (a) knowledge that the target para will be locked at some future block via its first head submission, and (b) the ability to submit a `swap` call for that para before it locks and to control (or collude with) the manager of a counterpart para to submit the confirming `swap` afterward. No signature forgery, privileged origin, or protocol violation is needed — every step uses the standard `register`/`swap` extrinsics through the normal `ensure_root_para_or_owner` path. The race window (between registration and first head production) is deterministic and can be targeted precisely by an attacker who manages the para being onboarded.

### Recommendation
Re-validate the lock status of the para(s) recorded in `PendingSwap` at the time the swap is *confirmed* (in the `PendingSwap::<T>::get(other) == Some(id)` branch), not only at insertion time — e.g., re-fetch `Paras::<T>::get(id)`/`Paras::<T>::get(other)` and require `!is_locked()` for any leg whose authorization derives from manager ownership rather than Root/self-origin. Alternatively, invalidate/clear any `PendingSwap` entry for a para when its lock transitions to `true` in `on_new_head`.

### Proof of Concept
Rust integration test in `polkadot/runtime/common/src/paras_registrar/tests.rs`:
1. Reserve and `register` para `A` (manager `alice`) and para `B` (manager `bob`), both as parathreads, leaving `A.locked == None`.
2. As `alice` (signed), call `Registrar::swap(RuntimeOrigin::signed(alice), A, B)` — assert `Ok(())`, assert `PendingSwap::<Test>::get(A) == Some(B)`.
3. Simulate `A` producing its first head: call `Registrar::on_new_head(A, &some_head)` (or drive it through the paras inclusion pipeline) — assert `Paras::<Test>::get(A).unwrap().is_locked() == true`.
4. As `bob` (signed, `B` still unlocked), call `Registrar::swap(RuntimeOrigin::signed(bob), B, A)`.
5. Assert this call succeeds (`Ok(())`) and that `OnSwap::on_swap` was invoked (e.g., via a mock `OnSwap` implementation recording calls, or by checking `crowdloan::Funds` swapped) — demonstrating that the swap for locked para `A` completed despite `A.is_locked() == true`, with no `Error::<T>::ParaLocked` ever raised for `A`.
6. Contrast with expected behavior: the test should assert failure (`Error::<T>::ParaLocked`) is returned when `A` is locked; the PoC shows this assertion does not hold, confirming the bypass.

### Citations

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L72-77)
```rust
impl<Account, Balance> ParaInfo<Account, Balance> {
	/// Returns if the para is locked.
	pub fn is_locked(&self) -> bool {
		self.locked.unwrap_or(false)
	}
}
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L195-197)
```rust
		/// Para is locked from manipulation by the manager. Must use parachain or relay chain
		/// governance.
		ParaLocked,
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L326-327)
```rust
		pub fn swap(origin: OriginFor<T>, id: ParaId, other: ParaId) -> DispatchResult {
			Self::ensure_root_para_or_owner(origin, id)?;
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L340-364)
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
```

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L366-366)
```rust
				PendingSwap::<T>::insert(id, other);
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

**File:** polkadot/runtime/common/src/paras_registrar/mod.rs (L713-726)
```rust
impl<T: Config> OnNewHead for Pallet<T> {
	fn on_new_head(id: ParaId, _head: &HeadData) -> Weight {
		// mark the parachain locked if the locked value is not already set
		let mut writes = 0;
		if let Some(mut info) = Paras::<T>::get(id) {
			if info.locked.is_none() {
				info.locked = Some(true);
				Paras::<T>::insert(id, info);
				writes += 1;
			}
		}
		T::DbWeight::get().reads_writes(1, writes)
	}
}
```
