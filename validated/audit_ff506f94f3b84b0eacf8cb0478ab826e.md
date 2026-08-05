Audit Report

## Title
Item-attribute delegate approvals (`ItemAttributesApprovalsOf`) survive ownership transfer, allowing a former owner to retain write/clear access to `Account(delegate)` namespace attributes on the buyer's NFT - ([File: substrate/frame/nfts/src/features/transfer.rs] / [File: substrate/frame/nfts/src/features/attributes.rs])

## Summary
`do_transfer` clears `details.approvals`, `ItemPriceOf`, and `PendingSwapOf` on ownership change specifically to prevent a "pre-approve attack," but does not clear `ItemAttributesApprovalsOf` for the item. Since `is_valid_namespace` for `AttributeNamespace::Account` only checks membership in this per-item approval set without validating against the item's current owner, a seller who pre-approved themselves as a delegate before selling can continue to write/clear attributes in the `Account(seller)` namespace after the sale.

## Finding Description
`do_approve_item_attributes` lets the current owner insert an arbitrary `delegate` into `ItemAttributesApprovalsOf::<T, I>` for the item, checked only against `details.owner` at call time [1](#0-0) . `do_transfer` updates ownership, clears `details.approvals`, `ItemPriceOf`, and `PendingSwapOf`, but never touches `ItemAttributesApprovalsOf::<T, I>(collection, item)` [2](#0-1) . After transfer, `is_valid_namespace` for `AttributeNamespace::Account(account_id)` checks only `account_id == origin && approvals.contains(&origin)` against the stale per-item approval set — it never re-validates against the item's current owner [3](#0-2) . This means the seller/attacker's approval entry, granted while they were still owner, remains valid indefinitely after the sale, letting them call `set_attribute`/`clear_attribute` with `namespace = Account(attacker)` on an item they no longer own. The developers' own comment on `details.approvals.clear()` explicitly states this exact class of attack ("pre-approve their second account before making the transaction and then claiming the item back") is the reason for clearing approvals on transfer, but the identical mitigation was not applied to `ItemAttributesApprovalsOf`, confirming an inconsistency in invariant enforcement rather than an intentional design choice.

The deposit-reservation aspect of the original scoped impact does not hold: in `do_set_attribute`, the deposit is reserved from the `depositor` parameter, which for the ordinary `set_attribute` extrinsic is the signer (the attacker) themselves, not the victim [4](#0-3) . So the attacker pays their own deposit to retain access; no funds are drawn from the victim.

## Impact Explanation
This is a real, unauthorized capability retained by a former owner: after selling/transferring an NFT, the seller can continue writing or clearing metadata in the `Account(seller)` namespace on the buyer's item without the buyer's knowledge or consent — violating the expectation that ownership transfer conveys exclusive control, an expectation the pallet itself enforces for `details.approvals`, `ItemPriceOf`, and `PendingSwapOf` but inconsistently omits for `ItemAttributesApprovalsOf`. The impact is bounded, however: the new owner can call `do_cancel_item_attributes_approval`, which correctly checks `check_origin == details.owner` against the *current* owner, to remove the stale approval in a single self-service extrinsic [5](#0-4) . No funds are put at risk (attacker uses own deposit), no privilege escalation beyond metadata namespace occurs, and the fix is a simple self-remedy once known. This is best characterized as low/informational-to-low severity metadata-integrity issue rather than a fund-loss or ownership-compromise vulnerability.

## Likelihood Explanation
Fully achievable via ordinary unprivileged extrinsics: `approve_item_attributes` (self-approval succeeds trivially while still owner) → `transfer` → `set_attribute`/`clear_attribute` with `namespace = Account(attacker)`. No special privileges or race conditions are required, and the exploit is deterministic and repeatable per item.

## Recommendation
Clear `ItemAttributesApprovalsOf::<T, I>::remove(&collection, &item)` inside `do_transfer`, mirroring `details.approvals.clear()` and the removal of `ItemPriceOf`/`PendingSwapOf`. If continuity for legitimate delegate use-cases is desired, unreserve/refund delegate deposits for attributes under the cleared approvals at transfer time (similar to `do_cancel_item_attributes_approval`), or require explicit re-approval by the new owner.

## Proof of Concept
1. Attacker mints collection/item and is `details.owner`.
2. Attacker calls `approve_item_attributes(collection, item, attacker)` — succeeds because `check_origin == details.owner` at call time.
3. Attacker calls `transfer(collection, item, victim)` — `do_transfer` clears `details.approvals`, `ItemPriceOf`, `PendingSwapOf`, but leaves `ItemAttributesApprovalsOf(collection, item)` containing `attacker`.
4. Attacker calls `set_attribute(collection, Some(item), AttributeNamespace::Account(attacker), key, value)` — passes `is_valid_namespace` check because `approvals.contains(&attacker)` is still true, despite `attacker` no longer being the item's owner.
5. Expected post-fix behavior: step 4 should fail with `Error::NoPermission` because `ItemAttributesApprovalsOf` should have been cleared during `do_transfer`.

### Citations

**File:** substrate/frame/nfts/src/features/attributes.rs (L127-136)
```rust
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

**File:** substrate/frame/nfts/src/features/attributes.rs (L382-394)
```rust

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

**File:** substrate/frame/nfts/src/features/attributes.rs (L412-453)
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
	}
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

**File:** substrate/frame/nfts/src/features/transfer.rs (L89-103)
```rust
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
