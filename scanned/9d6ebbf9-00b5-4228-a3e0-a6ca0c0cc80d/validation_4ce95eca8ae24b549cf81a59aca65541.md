### Title
Stale `ItemAttributesApprovalsOf` delegate approvals survive ownership changes caused by `claim_swap` - (File: substrate/frame/nfts/src/features/transfer.rs)

### Summary
`claim_swap` (via `do_claim_swap`) transfers ownership of both swapped items by calling `Pallet::do_transfer`, which correctly clears the owner-transfer approvals (`details.approvals`), `ItemPriceOf`, and `PendingSwapOf`, but never clears `ItemAttributesApprovalsOf`. As a result, an account previously approved by the *old* owner to set attributes in the `Account(delegate)` namespace remains approved to mutate item metadata/attributes after the item has changed hands through a swap (or any other transfer), without the new owner's consent.

### Finding Description
`do_transfer` in `substrate/frame/nfts/src/features/transfer.rs` performs the following cleanup on ownership change: [1](#0-0) 
It clears `Account`, updates `details.owner`, clears `details.approvals` (the transfer-delegate approvals baked into `ItemDetails`), and removes `ItemPriceOf` and `PendingSwapOf`. It does **not** touch `ItemAttributesApprovalsOf`, a separate storage map that tracks accounts approved by the item owner to write attributes under the `Account(delegate)` namespace: [2](#0-1) 

`do_claim_swap` (invoked by the `claim_swap` extrinsic) calls `Self::do_transfer` for both the sent and received items to finalize the swap: [3](#0-2) 
This confirms `PendingSwapOf` itself is properly cleared (verified by the pallet's own test asserting `!PendingSwapOf::<Test>::contains_key(...)` after `claim_swap`), so the swap-request state does not leak. However, `ItemAttributesApprovalsOf` for the item is left untouched by this same code path.

Consequently, a delegate previously approved by the pre-swap owner (via `do_approve_item_attributes`) continues to satisfy the namespace check in `do_set_attribute` / `do_set_attributes_pre_signed`, which look up `ItemAttributesApprovalsOf::<T, I>::get(&collection, &item)` and check membership only — not whether the current item owner is the account that originally granted the approval: [4](#0-3) 
The only way to revoke this is an explicit `do_cancel_item_attributes_approval` call by whoever the *current* owner happens to be: [5](#0-4) 
which the new owner has no reason to know is necessary, since normal transfer/swap flows give no indication that a stale delegate approval exists.

### Impact Explanation
This allows an unprivileged attacker (the former owner or their colluding delegate) to retain the ability to write/mutate attributes on an item after selling, trading, or swapping it away via `claim_swap`, without the new owner's authorization. This matches the "metadata mutation" impact in the scoped Immunefi impact list: an account that should have lost all rights to the item after `claim_swap` can still mutate its on-chain attributes/metadata.

### Likelihood Explanation
Highly feasible and fully reproducible with only signed-extrinsic calls:
1. Owner A approves delegate D via `approve_item_attributes` (`do_approve_item_attributes`).
2. A creates a swap via `create_swap` and lists it for `claim_swap` by another user B.
3. B calls `claim_swap`, which transfers the item from A to B via `do_transfer`.
4. D (or A acting as D) calls `set_attribute` / `set_attributes_pre_signed` with `AttributeNamespace::Account(D)` on the item now owned by B — this succeeds because `ItemAttributesApprovalsOf` was never cleared.

No privileged origin, race condition, or unusual batching is required — this is a straightforward lifecycle-transition gap.

### Recommendation
Clear `ItemAttributesApprovalsOf::<T, I>::remove(&collection, &item)` (and refund/unreserve any associated attribute deposits, mirroring the logic in `do_cancel_item_attributes_approval`) inside `do_transfer` whenever ownership changes, so that attribute-delegate approvals expire exactly when the item's owner changes, consistent with how `details.approvals`, `ItemPriceOf`, and `PendingSwapOf` are already cleared.

### Proof of Concept
Rust integration test in `substrate/frame/nfts/src/tests.rs`:
```rust
#[test]
fn claim_swap_leaves_stale_attribute_approval() {
    new_test_ext().execute_with(|| {
        // setup collection, mint item_1 owned by user_1, item_2 owned by user_2
        // user_1 approves delegate `attacker` for item_1 attributes
        assert_ok!(Nfts::approve_item_attributes(
            RuntimeOrigin::signed(user_1.clone()), collection_id, item_1, attacker.clone()
        ));
        assert!(ItemAttributesApprovalsOf::<Test>::get(collection_id, item_1).contains(&attacker));

        // user_1 creates swap offering item_1 for item_2
        assert_ok!(Nfts::create_swap(
            RuntimeOrigin::signed(user_1.clone()), collection_id, item_1,
            collection_id, Some(item_2), None, duration
        ));
        // user_2 claims swap -> item_1 now owned by user_2
        assert_ok!(Nfts::claim_swap(
            RuntimeOrigin::signed(user_2.clone()), collection_id, item_2,
            collection_id, item_1, None
        ));
        assert_eq!(Item::<Test>::get(collection_id, item_1).unwrap().owner, user_2);

        // BUG: stale approval still present
        assert!(ItemAttributesApprovalsOf::<Test>::get(collection_id, item_1).contains(&attacker));

        // attacker (never approved by new owner user_2) can still set attributes
        assert_ok!(Nfts::set_attribute(
            RuntimeOrigin::signed(attacker.clone()),
            collection_id, Some(item_1),
            AttributeNamespace::Account(attacker.clone()),
            bvec![1], bvec![2],
        )); // should fail with NoPermission after fix, currently succeeds
    });
}
```
Expected assertions after fix: `ItemAttributesApprovalsOf::<Test>::get(collection_id, item_1)` no longer contains `attacker` post-swap, and the subsequent `set_attribute` call by `attacker` fails with `Error::<Test>::NoPermission`.

### Citations

**File:** substrate/frame/nfts/src/features/transfer.rs (L90-103)
```rust
		Account::<T, I>::remove((&details.owner, &collection, &item));
		Account::<T, I>::insert((&dest, &collection, &item), ());
		let origin = details.owner;
		details.owner = dest;

		// The approved accounts have to be reset to `None`, because otherwise pre-approve attack
		// would be possible, where the owner can approve their second account before making the
		// transaction and then claiming the item back.
		details.approvals.clear();

		// Update item details.
		Item::<T, I>::insert(&collection, &item, &details);
		ItemPriceOf::<T, I>::remove(&collection, &item);
		PendingSwapOf::<T, I>::remove(&collection, &item);
```

**File:** substrate/frame/nfts/src/lib.rs (L365-375)
```rust
	/// Item attribute approvals.
	#[pallet::storage]
	pub type ItemAttributesApprovalsOf<T: Config<I>, I: 'static = ()> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		T::CollectionId,
		Blake2_128Concat,
		T::ItemId,
		ItemAttributesApprovals<T, I>,
		ValueQuery,
	>;
```

**File:** substrate/frame/nfts/src/features/atomic_swap.rs (L210-219)
```rust
		// This also removes the swap.
		Self::do_transfer(send_collection_id, send_item_id, receive_item.owner.clone(), |_, _| {
			Ok(())
		})?;
		Self::do_transfer(
			receive_collection_id,
			receive_item_id,
			send_item.owner.clone(),
			|_, _| Ok(()),
		)?;
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L236-250)
```rust
		// For the Account() namespace we check and set the approval if it wasn't set before.
		match &namespace {
			AttributeNamespace::CollectionOwner => {},
			AttributeNamespace::Account(account) => {
				ensure!(account == &signer, Error::<T, I>::NoPermission);
				let approvals = ItemAttributesApprovalsOf::<T, I>::get(&collection, &item);
				if !approvals.contains(account) {
					Self::do_approve_item_attributes(
						origin.clone(),
						collection,
						item,
						account.clone(),
					)?;
				}
			},
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L412-452)
```rust
	pub(crate) fn do_cancel_item_attributes_approval(
		check_origin: T::AccountId,
		collection: T::CollectionId,
		item: T::ItemId,
		delegate: T::AccountId,
		witness: CancelAttributesApprovalWitness,
	) -> DispatchResult {
		ensure!(
			Self::is_pallet_feature_enabled(PalletFeature::Attributes),
			Error::<T, I>::MethodDisabled
		);

		let details = Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownItem)?;
		ensure!(check_origin == details.owner, Error::<T, I>::NoPermission);

		ItemAttributesApprovalsOf::<T, I>::try_mutate(collection, item, |approvals| {
			approvals.remove(&delegate);

			let mut attributes: u32 = 0;
			let mut deposited: DepositBalanceOf<T, I> = Zero::zero();
			for (_, (_, deposit)) in Attribute::<T, I>::drain_prefix((
				&collection,
				Some(item),
				AttributeNamespace::Account(delegate.clone()),
			)) {
				attributes.saturating_inc();
				deposited = deposited.saturating_add(deposit.amount);
			}
			ensure!(attributes <= witness.account_attributes, Error::<T, I>::BadWitness);

			if !deposited.is_zero() {
				T::Currency::unreserve(&delegate, deposited);
			}

			Self::deposit_event(Event::ItemAttributesApprovalRemoved {
				collection,
				item,
				delegate,
			});
			Ok(())
		})
```
