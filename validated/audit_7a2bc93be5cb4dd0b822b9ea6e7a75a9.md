Audit Report

## Title
Underpriced repeated `Attribute` prefix drain via mismatched witness in `cancel_item_attributes_approval` - (File: substrate/frame/nfts/src/features/attributes.rs)

## Summary
`do_cancel_item_attributes_approval` performs the expensive `Attribute::drain_prefix` scan/removal for `(collection, item, AttributeNamespace::Account(delegate))` before validating the caller-supplied `witness.account_attributes` against the real count, all inside an `ItemAttributesApprovalsOf::try_mutate` closure. Since `try_mutate` rolls back all storage mutations performed in the closure when the closure returns `Err`, a caller can pass an intentionally small witness (e.g. `0`), forcing `BadWitness` after the drain has already been performed, which rolls back the drain and leaves the full `N`-sized attribute set intact for indefinite, cheap re-scanning.

## Finding Description
Code path confirmed as described: [1](#0-0)  shows the `try_mutate` closure calling `Attribute::<T, I>::drain_prefix(...)` and accumulating `attributes`/`deposited` before the `ensure!(attributes <= witness.account_attributes, Error::<T, I>::BadWitness)` check runs afterward. The permission check confirming any item owner (an unprivileged, self-controlled role) can invoke this path is present at [2](#0-1) . Attribute count buildup via repeated `set_attribute` calls under `AttributeNamespace::Account(delegate)` is unbounded per delegate/item, as shown in `do_set_attribute` [3](#0-2) , and the delegate approval step is self-servable via `do_approve_item_attributes`, gated only by item ownership [4](#0-3) .

`try_mutate` in FRAME wraps the closure execution in a storage transaction; returning `Err` from the closure discards all storage writes performed within it, including the `drain_prefix` removals, which is exactly the rollback behavior the claim relies on. This means the O(N) drain/scan work is performed on every call regardless of outcome, but the caller only pays weight proportional to the witness value they declare, not the real N scanned — a genuine mismatch between metered weight and real computational/DB cost, matching the pattern flagged.

## Impact Explanation
This is a weight-metering bypass / griefing vector rather than a funds-theft bug: an attacker can build up a large attribute set N (using fully recoverable reserved deposits) and then repeatedly invoke the cancel extrinsic with a deliberately low witness, causing real O(N) storage scan work per call while the extrinsic is priced at O(low witness). This can be used to desynchronize actual per-block execution time from the weight budget accounted for it, which is a legitimate class of issue in Substrate/FRAME (persistent block-processing slowdown), consistent with the impact category claimed.

## Likelihood Explanation
The full exploit path is reachable by a normal, unprivileged signed account: the attacker is both item owner and (via a second account they control) delegate, so no privilege escalation or victim cooperation is required. Building N is a one-time, self-funded, fully recoverable cost (reserved deposits, not burned), after which the griefing calls (witness=0) are cheap and repeatable indefinitely because the rollback preserves the exploitable attribute set on every failed call.

## Recommendation
Validate `witness.account_attributes` against the actual number of matching `Attribute` entries before performing the destructive `drain_prefix`, e.g., first count entries via a non-mutating `iter_prefix` and return `BadWitness` early if the count exceeds the witness, only calling `drain_prefix` once the count is confirmed within bounds. Alternatively, adjust weight post-dispatch based on the real number of attributes scanned (via `PostDispatchInfo`), so failed/undersized-witness calls are charged proportionally to the actual scan cost.

## Proof of Concept
1. Create a collection and mint an item owned by `ALICE`.
2. `ALICE` approves `BOB` as delegate via `approve_item_attributes(item, BOB)`.
3. `BOB` calls `set_attribute` repeatedly (e.g., 500 times with distinct keys) under `AttributeNamespace::Account(BOB)` for the item, each reserving a deposit from `BOB`.
4. Assert `Attribute::iter_prefix((collection, Some(item), AttributeNamespace::Account(BOB))).count() == 500`.
5. `ALICE` calls `cancel_item_attributes_approval(collection, item, BOB, CancelAttributesApprovalWitness { account_attributes: 0 })`.
6. Assert the call returns `Err(Error::BadWitness)`.
7. Assert the attribute count is still 500 (rollback preserved full state for replay).
8. Repeat steps 5–7 in a loop, confirming each iteration performs O(500) internal work while the extrinsic's declared weight (`WeightInfo::cancel_item_attributes_approval(0)`) corresponds to O(0) — demonstrating the weight/computation mismatch and free replayability of the expensive path.

### Citations

**File:** substrate/frame/nfts/src/features/attributes.rs (L50-63)
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

**File:** substrate/frame/nfts/src/features/attributes.rs (L424-425)
```rust
		let details = Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownItem)?;
		ensure!(check_origin == details.owner, Error::<T, I>::NoPermission);
```

**File:** substrate/frame/nfts/src/features/attributes.rs (L427-440)
```rust
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
```
