## Title
Stale `ItemAttributesApprovalsOf` delegate survives `do_transfer`, letting a former owner keep write access to a buyer's NFT attributes - (File: substrate/frame/nfts/src/features/transfer.rs)

### Summary
`do_transfer` clears `details.approvals`, `ItemPriceOf`, and `PendingSwapOf` on ownership change, but never touches `ItemAttributesApprovalsOf` for the item. Since `is_valid_namespace` for `AttributeNamespace::Account(account_id)` only checks `account_id == origin && approvals.contains(&origin)` — with no ownership check — a delegate approved before the sale keeps write access to `set_attribute`/`clear_attribute` in that namespace after the item changes hands.

### Finding Description
`do_approve_item_attributes` lets the current owner add an arbitrary `delegate` to `ItemAttributesApprovalsOf::<T, I>` for an item [1](#0-0) . This mapping is keyed only by `(collection, item)` and is never linked to, or invalidated by, item ownership after creation.

`do_transfer` performs the ownership swap and resets `details.approvals` (the transfer-delegate list), `ItemPriceOf`, and `PendingSwapOf`, but has no corresponding line clearing `ItemAttributesApprovalsOf::<T, I>::remove(&collection, &item)`: [2](#0-1) 

The permission check used by `set_attribute`/`clear_attribute` for the `Account(delegate)` namespace, `is_valid_namespace`, only verifies the caller equals `account_id` and is present in `ItemAttributesApprovalsOf` — it does not check that the caller (or anyone) is still the item's current owner: [3](#0-2) 

Exploit flow:
1. Attacker owns `item` in `collection`.
2. Attacker calls `approve_item_attributes(origin=attacker, collection, item, delegate=attacker)`, which succeeds because `check_origin == details.owner` [4](#0-3) .
3. Attacker transfers/sells the item to victim via `transfer` → `do_transfer`. Ownership (`Account`, `Item.owner`), transfer-approvals, price, and pending swap are all reset, but `ItemAttributesApprovalsOf` is left intact [2](#0-1) .
4. Attacker calls `set_attribute(origin=attacker, collection, item, namespace=Account(attacker), key, value)`. `do_set_attribute` calls `is_valid_namespace`, which passes because `attacker == origin` and `attacker` is still in the stale approvals set — it never re-checks who currently owns the item [5](#0-4) .
5. The attribute write reserves a new deposit from the attacker (self-paid in this scenario, since `depositor` defaults to `origin` unless a different `depositor` param is supplied) — see the reserve logic [6](#0-5)  — meaning the attacker can force new `Account(attacker)`-namespace attributes/data to persist against the victim's item, and can later `clear_attribute` (also relying on the same stale-approval check, since `AttributeNamespace::Account` falls into the generic `_ => ()` no-op branch for the extra lock checks in `do_clear_attribute`) to manipulate metadata associated with the NFT the victim now owns, without the victim's consent or ability to revoke it (only the *current* owner can call `cancel_item_attributes_approval`, and the current owner — the victim — never learns the stale approval exists unless they inspect `ItemAttributesApprovalsOf` directly).

The new owner has no built-in way to detect or block this: `do_cancel_item_attributes_approval` can be called by the current owner (the victim) to explicitly remove the stale delegate [7](#0-6) , but nothing forces or informs them to do so before or during purchase — the transfer itself gives no indication that a delegate approval still exists, unlike `details.approvals` which is proactively cleared.

### Impact Explanation
A former owner (or a colluding third party pre-approved as delegate) retains persistent write access to the `Account(delegate)` attribute namespace of an NFT after selling/transferring it. This allows the attacker to continue setting/clearing metadata under that namespace on an item now owned by an unsuspecting buyer, and to force new deposit reservations (paid by whichever account is passed as `depositor`, potentially the attacker or, via `do_set_attributes_pre_signed`, tied to the item's actual current owner if they naively sign a pre-signed message) without the new owner's ongoing consent — impact is scoped to unauthorized persistent read/write access to attribute data plus deposit-handling friction, not to theft of the NFT itself or of the transfer-approval delegate rights (those are correctly cleared).

### Likelihood Explanation
Fully feasible with only standard, unprivileged extrinsics: `approve_item_attributes`, `transfer` (or `buy_item`/any transfer-triggering flow that calls `do_transfer`), and `set_attribute`/`clear_attribute`. No special origin, proxy, or governance access is required — any account that currently owns an item can pre-approve itself as a delegate before selling. This is trivially repeatable for every item an attacker sells.

### Recommendation
Clear `ItemAttributesApprovalsOf::<T, I>::remove(&collection, &item)` inside `do_transfer` (alongside the existing `ItemPriceOf`/`PendingSwapOf` removal at lines 102-103), unreserving/settling any outstanding deposits held by prior delegates for that item's `Account(*)` attributes, mirroring how `details.approvals` is already reset to prevent the analogous "pre-approve attack" called out in the existing code comment.

### Proof of Concept
Rust integration test in `substrate/frame/nfts/src/tests.rs`:
```rust
#[test]
fn stale_item_attribute_approval_survives_transfer() {
    new_test_ext().execute_with(|| {
        Balances::make_free_balance_be(&1, 100);
        Balances::make_free_balance_be(&2, 100);
        assert_ok!(Nfts::create(RuntimeOrigin::signed(1), 1, default_collection_config()));
        assert_ok!(Nfts::mint(RuntimeOrigin::signed(1), 0, 42, 1, None));

        // Attacker (1) approves self as Account delegate while still owner.
        assert_ok!(Nfts::approve_item_attributes(RuntimeOrigin::signed(1), 0, 42, 1));

        // Transfer item to victim (2).
        assert_ok!(Nfts::transfer(RuntimeOrigin::signed(1), 0, 42, 2));

        // BUG: attacker (1) can still write attributes in Account(1) namespace
        // on an item now owned by 2.
        assert_ok!(Nfts::set_attribute(
            RuntimeOrigin::signed(1),
            0,
            Some(42),
            AttributeNamespace::Account(1),
            bvec![0],
            bvec![1],
        ));

        // Expected (fixed) behavior: this should fail with NoPermission
        // because ItemAttributesApprovalsOf should have been cleared on transfer.
        // assert_noop!(..., Error::<Test>::NoPermission);
    });
}
```
Assertion of the bug: the `set_attribute` call succeeds post-transfer even though account `1` is no longer the item's owner, proving the stale delegate approval was not invalidated.

### Citations

**File:** substrate/frame/nfts/src/features/attributes.rs (L64-67)
```rust
		ensure!(
			Self::is_valid_namespace(&origin, &namespace, &collection, &maybe_item)?,
			Error::<T, I>::NoPermission
		);
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L126-136)
```rust
		// and return the deposit to the previous owner.
		if depositor_has_changed {
			if let Some(old_depositor) = old_depositor {
				T::Currency::unreserve(&old_depositor, old_deposit.amount);
			}
			T::Currency::reserve(&depositor, deposit)?;
		} else if deposit > old_deposit.amount {
			T::Currency::reserve(&depositor, deposit - old_deposit.amount)?;
		} else if deposit < old_deposit.amount {
			T::Currency::unreserve(&depositor, old_deposit.amount - deposit);
		}
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L372-394)
```rust
	pub(crate) fn do_approve_item_attributes(
		check_origin: T::AccountId,
		collection: T::CollectionId,
		item: T::ItemId,
		delegate: T::AccountId,
	) -> DispatchResult {
		ensure!(
			Self::is_pallet_feature_enabled(PalletFeature::Attributes),
			Error::<T, I>::MethodDisabled
		);

		let details = Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownItem)?;
		ensure!(check_origin == details.owner, Error::<T, I>::NoPermission);

		ItemAttributesApprovalsOf::<T, I>::try_mutate(collection, item, |approvals| {
			approvals
				.try_insert(delegate.clone())
				.map_err(|_| Error::<T, I>::ReachedApprovalLimit)?;

			Self::deposit_event(Event::ItemAttributesApprovalAdded { collection, item, delegate });
			Ok(())
		})
	}
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L412-425)
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
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L474-479)
```rust
			AttributeNamespace::Account(account_id) => {
				if let Some(item) = maybe_item {
					let approvals = ItemAttributesApprovalsOf::<T, I>::get(&collection, &item);
					result = account_id == origin && approvals.contains(&origin)
				}
			},
```

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
