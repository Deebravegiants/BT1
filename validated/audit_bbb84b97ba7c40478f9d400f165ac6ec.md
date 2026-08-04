### Title
Stale `ItemAttributesApprovalsOf` delegate approvals survive item ownership transfer in pallet-nfts - (File: `substrate/frame/nfts/src/features/transfer.rs`)

### Summary
`pallet-nfts` lets an item owner delegate a third-party account to write attributes under the `AttributeNamespace::Account(delegate)` namespace via `approve_item_attributes`, recorded in the `ItemAttributesApprovalsOf` storage map keyed only by `(collection, item)`. When the item is later transferred to a new owner, `do_transfer` resets the transfer-approvals field (`details.approvals.clear()`) but never clears `ItemAttributesApprovalsOf`, so the previous owner's delegate remains authorized to set attributes on the item after it has a new owner — the same "stale permission mapping not cleared on ownership transfer" pattern described in the Open Dollar `handlerCan` report.

### Finding Description
`do_transfer` in [1](#0-0)  updates `Account` ownership, resets `details.approvals` (the item transfer-approvals), and removes `ItemPriceOf`/`PendingSwapOf`, but it does **not** touch `ItemAttributesApprovalsOf`.

`ItemAttributesApprovalsOf` is a separate storage map keyed only by `(collection, item)` [2](#0-1) , populated by `do_approve_item_attributes` when the (old) owner approves a delegate [3](#0-2) .

Authorization to write an attribute in the `Account(account)` namespace is checked purely against this approvals set, with no cross-check against the item's *current* owner: [4](#0-3) 

By contrast, the pallet's own `do_burn` function explicitly clears this exact map when the item ceases to exist, proving the developers recognize it must be cleaned up when the item state changes ownership/lifecycle: [5](#0-4) . That same cleanup call is simply missing from `do_transfer`.

The only way to remove a stale delegate's approval is `cancel_item_attributes_approval`, which requires `check_origin == details.owner` [6](#0-5)  — i.e. only the *current* owner can revoke it, but the current (new) owner has no on-chain signal that a stale delegate exists unless they inspect `ItemAttributesApprovalsOf` directly, exactly mirroring the Open Dollar scenario where the new safe owner is unaware of old `handlerCan` permissions.

### Impact Explanation
After Owner A sells/transfers an NFT item to Owner B, any account Owner A previously approved via `approve_item_attributes` retains the ability to call `set_attribute`/`set_attributes_pre_signed` and write/overwrite data in the `Account(delegate)` namespace for that item, without Owner B's knowledge or consent. Attributes are commonly used by marketplaces/wallets to store item-relevant metadata (traits, provenance, external links). A malicious former owner can continue mutating this metadata after sale (e.g., inserting misleading or malicious values) or force the current holder's understanding of the item's on-chain data to remain manipulable by a party they no longer trust. Because `do_set_attribute` for the `Account` namespace charges the deposit to the caller (the delegate) rather than the new owner, there is no funds-theft vector, so this is a state-integrity/griefing issue rather than a fund-loss issue — consistent with the referenced report being judged Medium rather than High severity for the analogous lack of financial exploitation path.

### Likelihood Explanation
This is fully reachable by any unprivileged user through a normal sequence of extrinsics: `approve_item_attributes` → `transfer` (or `buy_item`, which reuses `do_transfer`) → the old delegate calls `set_attribute`. No privileged origin, mocked path, or trusted-role compromise is required; it works exactly as coded in the production dispatchables `transfer`, `approve_item_attributes`, and `set_attribute` in `pallet-nfts`, which is deployed on Asset Hub parachains (Rococo/Westend) per the weight files referencing `pallet_nfts`.

### Recommendation
In `do_transfer` (and any other item-lifecycle function that changes `details.owner`, e.g. `do_claim_swap`), clear `ItemAttributesApprovalsOf::<T, I>::remove(&collection, &item)` — mirroring the cleanup already performed in `do_burn` — and consider draining/refunding attributes+deposits held in now-stale `Account(delegate)` namespaces, analogous to what `do_cancel_item_attributes_approval` already does.

### Proof of Concept
1. Owner A mints item `(collection=0, item=42)` and owns it.
2. Owner A calls `approve_item_attributes(collection=0, item=42, delegate=X)`, adding `X` to `ItemAttributesApprovalsOf(0, 42)` (see `do_approve_item_attributes`, `substrate/frame/nfts/src/features/attributes.rs:372-394`).
3. Owner A transfers/sells the item to Owner B via `transfer` → `do_transfer` (`substrate/frame/nfts/src/features/transfer.rs:46-113`). Note only `details.approvals.clear()` (the transfer-approval map) is reset; `ItemAttributesApprovalsOf(0, 42)` still contains `X`.
4. `X` (controlled by/colluding with A) calls `set_attribute(collection=0, item=Some(42), namespace=Account(X), key, value)`. `is_valid_namespace` checks only `approvals.contains(&origin)` (`substrate/frame/nfts/src/features/attributes.rs:474-479`) — it succeeds despite Owner B now owning the item and never having approved `X`.
5. Owner B has no dispatchable visibility of this stale approval unless they manually query `ItemAttributesApprovalsOf`; only Owner B can call `cancel_item_attributes_approval` to remove it, but is unaware it exists.

### Citations

**File:** substrate/frame/nfts/src/features/transfer.rs (L82-103)
```rust
		// Retrieve the item details.
		let mut details =
			Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownItem)?;

		// Perform the transfer with custom details using the provided closure.
		with_details(&collection_details, &mut details)?;

		// Update account ownership information.
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

**File:** substrate/frame/nfts/src/features/create_delete_item.rs (L260-264)
```rust
		Item::<T, I>::remove(&collection, &item);
		Account::<T, I>::remove((&owner, &collection, &item));
		ItemPriceOf::<T, I>::remove(&collection, &item);
		PendingSwapOf::<T, I>::remove(&collection, &item);
		ItemAttributesApprovalsOf::<T, I>::remove(&collection, &item);
```
