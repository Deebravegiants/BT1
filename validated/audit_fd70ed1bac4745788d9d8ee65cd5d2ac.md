### Title
Unprivileged accounts can permanently graff unremovable `PendingSwaps` entries onto arbitrary victim accounts via `create_swap` - (File: substrate/frame/atomic-swap/src/lib.rs)

### Summary
`create_swap` lets any signed account create a `PendingSwaps` entry keyed by an arbitrary `target` account and an attacker-chosen `hashed_proof`, while only reserving the swap's `value` from the *caller's own* balance (which can be `0`, making the operation essentially free beyond the flat tx fee). The only two removal paths — `claim_swap` (needs the real preimage, known only to the attacker who never has to reveal it) and `cancel_swap` (restricted to `swap.source == caller`, i.e. only the original attacker) — leave the `target` account with **no way to ever clean up** entries created against it.

### Finding Description
In `create_swap` [1](#0-0) , the only precondition is that `(target, hashed_proof)` is not already occupied, and that `action.reserve(&source)` succeeds. For `BalanceSwapAction`, `reserve` simply calls `C::reserve(source, self.value)` [2](#0-1) , and the balances pallet's `ReservableCurrency::reserve` is a documented no-op when `value` is zero (`if value.is_zero() { return Ok(()); }`) [3](#0-2) . So an attacker can call `create_swap` with `value = 0`, any `target` account they don't control, and a `hashed_proof` they generate but never reveal, at essentially just the flat weight/fee cost of the extrinsic — no funds are locked, no deposit is taken for the storage entry itself.

The resulting `PendingSwap` is stored in `PendingSwaps<T>` keyed by `(target, hashed_proof)` [4](#0-3) . Removal is only possible via:
- `claim_swap`, which requires the caller (`target`) to supply a `proof` whose `blake2_256` hash matches `hashed_proof` [5](#0-4)  — impossible for the victim since the attacker chose an arbitrary hash and need never disclose a preimage.
- `cancel_swap`, which requires `swap.source == source` (the caller must be the original creator) [6](#0-5)  — the victim `target` is never `swap.source`, so they can never invoke this.

There is no third path (no permissionless/"public" purge, no expiry-based auto-removal, no deposit-refund-on-cleanup mechanism) anywhere in the pallet. Consequently the victim account has zero agency over storage entries created under its own key, and the attacker who created them has no economic incentive to ever cancel them (their reserved amount is `0`).

### Impact Explanation
An unprivileged attacker can repeatedly call `create_swap` (paying only the flat, storage-unaware transaction fee) to permanently attach an unbounded number of `PendingSwaps` entries to any chosen victim account, using `value = 0` so no attacker funds are locked. These entries are durable chain state that: (a) cannot be removed by the victim under any circumstance, (b) cannot be removed by anyone except the original attacker (who has no incentive to do so), and (c) accumulate without any storage deposit proportional to their long-term storage cost — an underpriced, permanent state-growth vector attributable to an unprivileged actor targeting arbitrary accounts.

### Likelihood Explanation
This requires no privilege beyond a signed origin and a minimal existential balance to submit extrinsics, is fully repeatable (bounded only by attacker's willingness to pay flat tx fees), and works against any `target` account chosen by the attacker, including accounts the attacker has no relationship with. There's no rate limiting, deposit, or per-target quota preventing this.

### Recommendation
- Require a storage deposit (reserved from `source`, refundable on `claim`/`cancel`) sized to cover the `PendingSwaps` entry's storage cost, independent of the swap `value`, so zero-value swaps are not free to create.
- Allow the `target` to remove/reject stale or unwanted swap entries addressed to them (e.g., a `reject_swap` call analogous to `cancel_swap` but callable by `target` after `end_block`), rather than restricting cleanup solely to `source`.
- Consider bounding the number of concurrent pending swaps per `target` account, or requiring `target`'s implicit consent (e.g., via an allow-list or opt-in) before a swap can be created against them.

### Proof of Concept
Rust integration test sketch (in `substrate/frame/atomic-swap/src/tests.rs` or an equivalent mock runtime):
```rust
#[test]
fn attacker_can_griff_target_storage_with_zero_value_swaps() {
    new_test_ext().execute_with(|| {
        let attacker = 1;
        let victim = 2; // never signs anything

        // Attacker floods victim's PendingSwaps bucket with zero-value, unrevealable swaps.
        for i in 0u8..50 {
            let hashed_proof = blake2_256(&[i]); // attacker never reveals a preimage matching this
            assert_ok!(AtomicSwap::create_swap(
                RuntimeOrigin::signed(attacker),
                victim,
                hashed_proof,
                BalanceSwapAction::new(0), // zero value: reserve is a documented no-op
                100,
            ));
        }

        // Assert: 50 entries now permanently exist under `victim`'s key.
        let count = PendingSwaps::<Test>::iter_prefix(victim).count();
        assert_eq!(count, 50);

        // Victim has no dispatchable that can remove any of these entries:
        // - claim_swap requires knowing the (unrevealed) preimage -> always fails with InvalidProof.
        // - cancel_swap requires swap.source == caller; victim is never `source` -> fails with SourceMismatch.
        assert_noop!(
            AtomicSwap::cancel_swap(RuntimeOrigin::signed(victim), victim, blake2_256(&[0u8])),
            Error::<Test>::SourceMismatch // (or NotExist if key mismatched by design)
        );

        // Attacker also has zero balance locked, so griefing is essentially free.
        assert_eq!(Balances::reserved_balance(attacker), 0);
    });
}
```
Expected assertions: entries persist indefinitely, `victim` has no successful call path to remove them, and `attacker`'s reserved balance remains `0` throughout, demonstrating the state-bloat/griefing asymmetry at negligible attacker cost.

### Citations

**File:** substrate/frame/atomic-swap/src/lib.rs (L149-151)
```rust
	fn reserve(&self, source: &AccountId) -> DispatchResult {
		C::reserve(source, self.value)
	}
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L197-205)
```rust
	#[pallet::storage]
	pub type PendingSwaps<T: Config> = StorageDoubleMap<
		_,
		Twox64Concat,
		T::AccountId,
		Blake2_128Concat,
		HashedProof,
		PendingSwap<T>,
	>;
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L255-280)
```rust
		pub fn create_swap(
			origin: OriginFor<T>,
			target: T::AccountId,
			hashed_proof: HashedProof,
			action: T::SwapAction,
			duration: BlockNumberFor<T>,
		) -> DispatchResult {
			let source = ensure_signed(origin)?;
			ensure!(
				!PendingSwaps::<T>::contains_key(&target, hashed_proof),
				Error::<T>::AlreadyExist
			);

			action.reserve(&source)?;

			let swap = PendingSwap {
				source,
				action,
				end_block: frame_system::Pallet::<T>::block_number() + duration,
			};
			PendingSwaps::<T>::insert(target.clone(), hashed_proof, swap.clone());

			Self::deposit_event(Event::NewSwap { account: target, proof: hashed_proof, swap });

			Ok(())
		}
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L297-313)
```rust
		pub fn claim_swap(
			origin: OriginFor<T>,
			proof: Vec<u8>,
			action: T::SwapAction,
		) -> DispatchResult {
			ensure!(proof.len() <= T::ProofLimit::get() as usize, Error::<T>::ProofTooLarge);

			let target = ensure_signed(origin)?;
			let hashed_proof = blake2_256(&proof);

			let swap =
				PendingSwaps::<T>::get(&target, hashed_proof).ok_or(Error::<T>::InvalidProof)?;
			ensure!(swap.action == action, Error::<T>::ClaimActionMismatch);

			let succeeded = swap.action.claim(&swap.source, &target);

			PendingSwaps::<T>::remove(target.clone(), hashed_proof);
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L332-347)
```rust
		pub fn cancel_swap(
			origin: OriginFor<T>,
			target: T::AccountId,
			hashed_proof: HashedProof,
		) -> DispatchResult {
			let source = ensure_signed(origin)?;

			let swap = PendingSwaps::<T>::get(&target, hashed_proof).ok_or(Error::<T>::NotExist)?;
			ensure!(swap.source == source, Error::<T>::SourceMismatch);
			ensure!(
				frame_system::Pallet::<T>::block_number() >= swap.end_block,
				Error::<T>::DurationNotPassed,
			);

			swap.action.cancel(&swap.source);
			PendingSwaps::<T>::remove(&target, hashed_proof);
```

**File:** substrate/frame/balances/src/impl_currency.rs (L624-630)
```rust
	/// Move `value` from the free balance from `who` to their reserved balance.
	///
	/// Is a no-op if value to be reserved is zero.
	fn reserve(who: &T::AccountId, value: Self::Balance) -> DispatchResult {
		if value.is_zero() {
			return Ok(());
		}
```
