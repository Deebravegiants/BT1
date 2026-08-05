### Title
Underpriced repeated `Attribute` prefix drain via mismatched witness in `cancel_item_attributes_approval` - (File: substrate/frame/nfts/src/features/attributes.rs)

### Summary
`do_cancel_item_attributes_approval` performs a full `drain_prefix` scan over all `Attribute` entries for `(collection, item, AttributeNamespace::Account(delegate))` *before* validating the caller-supplied `witness.account_attributes` against the actual count. Because the scan/removal happens inside a `try_mutate` closure, an `Err(BadWitness)` (caused by an intentionally low witness value) rolls back all storage mutations made in the closure, including the `Attribute::drain_prefix` removals, letting an attacker replay the same expensive full-collection scan indefinitely while only ever being charged the (cheap) weight computed from the low witness value they supplied.

### Finding Description
The dispatchable `cancel_item_attributes_approval` takes a `witness: CancelAttributesApprovalWitness { account_attributes }` parameter, and — per the standard Substrate witness pattern used throughout this pallet — its declared extrinsic weight is derived from `witness.account_attributes` (i.e. `T::WeightInfo::cancel_item_attributes_approval(witness.account_attributes)`), the caller-declared, unverified value.

In `do_cancel_item_attributes_approval` [1](#0-0) , the logic is:
1. `ItemAttributesApprovalsOf::<T,I>::try_mutate` opens a transactional storage scope.
2. Inside the closure, `Attribute::<T, I>::drain_prefix((&collection, Some(item), AttributeNamespace::Account(delegate.clone())))` iterates and removes **every** attribute the delegate previously set for that item — cost `O(N)` where `N` is the actual number of attributes, unbounded by the witness.
3. Only *after* the full drain does it check `ensure!(attributes <= witness.account_attributes, Error::<T,I>::BadWitness)`.
4. If the caller supplies a witness smaller than the real `N` (e.g. `0`), the `ensure!` fails, and because `try_mutate` wraps the closure in a storage transaction, **all mutations made during the closure — including the `drain_prefix` removals — are rolled back**. The `N` attributes remain in storage, untouched, ready to be scanned again.

The attacker fully controls the setup: as the item owner (`check_origin == details.owner`, verified at line 425 [2](#0-1) ), they can approve a second account they also control as `delegate` via `do_approve_item_attributes` [3](#0-2) , then use that delegate account to call `set_attribute` repeatedly (self-funding the deposit) to build up an arbitrarily large `N` for `AttributeNamespace::Account(delegate)` on a single item, since nothing bounds the total number of distinct attribute keys per delegate/item over multiple calls/blocks [4](#0-3) .

Once `N` attributes exist, the attacker repeatedly calls `cancel_item_attributes_approval` with `witness.account_attributes = 0` (or any value less than `N`). Each call:
- Is charged/reserves weight proportional to the declared witness (near-zero).
- Actually performs an `O(N)` full prefix scan/removal of the `Attribute` map.
- Fails with `BadWitness`, rolling back the removal, so `N` never shrinks and the attack is repeatable indefinitely at negligible marginal cost to the attacker beyond transaction fees for a cheap (witness=0) call.

This is exactly the "public loop whose true cost grows faster than charged weight" pattern: real computational/DB cost is `O(N)` while charged weight is `O(witness)`, and `witness` is entirely attacker-supplied and unverified until after the expensive work is already done.

### Impact Explanation
An attacker can pre-build a large `N` (bounded only by their own reservable balance for deposits, which is fully recoverable — not burned) and then submit many cheap, failing `cancel_item_attributes_approval(witness=0)` calls. Each call performs `O(N)` storage reads/writes internally (then rolled back) while declaring near-zero weight, causing actual per-extrinsic execution time in a block to be far larger than the weight budget accounted for it. Packed into a block, this desynchronizes real execution time from the block's declared weight limit, degrading block production/import performance — a weight-metering bypass / griefing vector, not a direct fund theft, matching the "persistent slowdown" impact category.

### Likelihood Explanation
Fully reachable by an unprivileged signed account acting as its own item owner and its own delegate — no special permissions needed. Building `N` requires reserving deposits (recoverable capital, not spent), which is a one-time setup cost; after that, the griefing calls are cheap and infinitely repeatable since the underlying attribute set is never actually consumed (rolled back on every failed call). This is fully deterministic and repeatable on any deployment of `pallet-nfts` with the `Attributes` feature enabled (e.g. Asset Hub runtimes).

### Recommendation
Validate `witness.account_attributes` against the actual number of matching `Attribute` entries **before** performing the destructive `drain_prefix`, e.g. by first counting entries with a non-mutating iterator (`Attribute::iter_prefix` counting only) and returning `BadWitness` early if the count exceeds the witness, only calling `drain_prefix` once the count is confirmed to be within bounds. Alternatively, charge/refund weight based on the actual number of attributes scanned (post-dispatch weight correction via `PostDispatchInfo`) so that failed/undersized-witness calls are charged proportionally to the real scan cost rather than the caller-declared value.

### Proof of Concept
Rust integration test (in `substrate/frame/nfts/src/tests.rs` style):
1. Create a collection and mint an item owned by `ALICE`.
2. `ALICE` approves `BOB` as delegate via `approve_item_attributes(item, BOB)`.
3. `BOB` calls `set_attribute` repeatedly (e.g. 500 times with distinct keys) under `AttributeNamespace::Account(BOB)` for the item, each reserving a deposit from `BOB`.
4. Assert `Attribute::iter_prefix((collection, Some(item), AttributeNamespace::Account(BOB))).count() == 500`.
5. `ALICE` calls `cancel_item_attributes_approval(collection, item, BOB, CancelAttributesApprovalWitness { account_attributes: 0 })`.
6. Assert the call returns `Err(Error::BadWitness)`.
7. Assert `Attribute::iter_prefix((collection, Some(item), AttributeNamespace::Account(BOB))).count() == 500` still (i.e., unchanged — proving rollback preserved full state for replay).
8. Repeat step 5–7 in a loop (e.g. 100 iterations) and measure/log the number of storage reads/writes performed by `drain_prefix` per call (via `frame_support::storage::migration` test utilities or a custom storage-access counter), confirming each iteration performs `O(500)` work while the extrinsic's declared weight (`WeightInfo::cancel_item_attributes_approval(0)`) corresponds to `O(0)`/minimal work — demonstrating the weight/computation mismatch and the free replayability of the expensive path.

### Citations

**File:** substrate/frame/nfts/src/features/attributes.rs (L50-157)
```rust
	pub(crate) fn do_set_attribute(
		origin: T::AccountId,
		collection: T::CollectionId,
		maybe_item: Option<T::ItemId>,
		namespace: AttributeNamespace<T::AccountId>,
		key: BoundedVec<u8, T::KeyLimit>,
		value: BoundedVec<u8, T::ValueLimit>,
		depositor: T::AccountId,
	) -> DispatchResult {
		ensure!(
			Self::is_pallet_feature_enabled(PalletFeature::Attributes),
			Error::<T, I>::MethodDisabled
		);

		ensure!(
			Self::is_valid_namespace(&origin, &namespace, &collection, &maybe_item)?,
			Error::<T, I>::NoPermission
		);

		let collection_config = Self::get_collection_config(&collection)?;
		// for the `CollectionOwner` namespace we need to check if the collection/item is not locked
		match namespace {
			AttributeNamespace::CollectionOwner => match maybe_item {
				None => {
					ensure!(
						collection_config.is_setting_enabled(CollectionSetting::UnlockedAttributes),
						Error::<T, I>::LockedCollectionAttributes
					)
				},
				Some(item) => {
					let maybe_is_locked = Self::get_item_config(&collection, &item)
						.map(|c| c.has_disabled_setting(ItemSetting::UnlockedAttributes))?;
					ensure!(!maybe_is_locked, Error::<T, I>::LockedItemAttributes);
				},
			},
			_ => (),
		}

		let mut collection_details =
			Collection::<T, I>::get(&collection).ok_or(Error::<T, I>::UnknownCollection)?;

		let attribute = Attribute::<T, I>::get((collection, maybe_item, &namespace, &key));
		let attribute_exists = attribute.is_some();
		if !attribute_exists {
			collection_details.attributes.saturating_inc();
		}

		let old_deposit =
			attribute.map_or(AttributeDeposit { account: None, amount: Zero::zero() }, |m| m.1);

		let mut deposit = Zero::zero();
		// disabled DepositRequired setting only affects the CollectionOwner namespace
		if collection_config.is_setting_enabled(CollectionSetting::DepositRequired) ||
			namespace != AttributeNamespace::CollectionOwner
		{
			deposit = T::DepositPerByte::get()
				.saturating_mul(((key.len() + value.len()) as u32).into())
				.saturating_add(T::AttributeDepositBase::get());
		}

		let is_collection_owner_namespace = namespace == AttributeNamespace::CollectionOwner;
		let is_depositor_collection_owner =
			is_collection_owner_namespace && collection_details.owner == depositor;

		// NOTE: in the CollectionOwner namespace if the depositor is `None` that means the deposit
		// was paid by the collection's owner.
		let old_depositor =
			if is_collection_owner_namespace && old_deposit.account.is_none() && attribute_exists {
				Some(collection_details.owner.clone())
			} else {
				old_deposit.account
			};
		let depositor_has_changed = old_depositor != Some(depositor.clone());

		// NOTE: when we transfer an item, we don't move attributes in the ItemOwner namespace.
		// When the new owner updates the same attribute, we will update the depositor record
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

		if is_depositor_collection_owner {
			if !depositor_has_changed {
				collection_details.owner_deposit.saturating_reduce(old_deposit.amount);
			}
			collection_details.owner_deposit.saturating_accrue(deposit);
		}

		let new_deposit_owner = match is_depositor_collection_owner {
			true => None,
			false => Some(depositor),
		};
		Attribute::<T, I>::insert(
			(&collection, maybe_item, &namespace, &key),
			(&value, AttributeDeposit { account: new_deposit_owner, amount: deposit }),
		);

		Collection::<T, I>::insert(collection, &collection_details);
		Self::deposit_event(Event::AttributeSet { collection, maybe_item, key, value, namespace });
		Ok(())
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
