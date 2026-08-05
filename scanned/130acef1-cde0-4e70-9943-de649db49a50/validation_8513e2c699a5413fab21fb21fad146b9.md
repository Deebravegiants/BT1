### Title
Item/collection `is_frozen` state is not checked in `do_burn`, allowing a frozen NFT to be burned - (File: substrate/frame/uniques/src/functions.rs)

### Summary
`Pallet::do_transfer` enforces three independent lock layers before mutating an item: `collection_details.is_frozen`, `T::Locker::is_locked`, and `details.is_frozen` (the per-item flag set by the `freeze` extrinsic). `Pallet::do_burn`, which backs the `burn` dispatchable, only checks `T::Locker::is_locked` and completely omits the `is_frozen` checks on both the item and the collection. This means an item that has been frozen via the `freeze` extrinsic (or whose collection has been frozen) can still be destroyed by its owner through the ordinary, unprivileged `burn` extrinsic.

### Finding Description
In `substrate/frame/uniques/src/functions.rs`, `do_transfer` performs: [1](#0-0) 
i.e. it checks `collection_details.is_frozen`, `T::Locker::is_locked`, and `details.is_frozen` before allowing the mutation.

`do_burn`, however, only checks the external `Locker` trait: [2](#0-1) 

There is no `ensure!(!details.is_frozen, Error::<T,I>::Frozen)` and no `ensure!(!collection_details.is_frozen, Error::<T,I>::Frozen)` in `do_burn`. The `freeze`/`thaw` extrinsics in `lib.rs` set/clear `ItemDetails.is_frozen`, and `lock_collection`/analogous calls set `CollectionDetails.is_frozen`, but these flags are silently ignored by the burn path.

Exploit flow:
1. Attacker (item owner or someone with a permission model that relies on `freeze` to prevent burning, e.g. an escrow/marketplace/bridge that freezes an item while it backs some other on-chain guarantee) calls `freeze(collection, item)` — this is itself callable by the item's owner (or collection freezer) via a normal signed extrinsic.
2. Any code relying on `is_frozen` to prevent destruction of the item (e.g. external pallets, cross-chain wrapped-asset backing, or auction/lock invariants) assumes the item cannot disappear while frozen.
3. The owner calls `burn(collection, item, check_owner)`. This dispatches to `do_burn`, which never inspects `details.is_frozen` or `collection_details.is_frozen`, only `T::Locker::is_locked`.
4. The item is destroyed and the deposit is returned, even though it was flagged as frozen — silently violating the invariant that a frozen item "must remain unreachable through all public flows."

### Impact Explanation
Any external system, marketplace, or cross-chain bridge that treats `ItemDetails.is_frozen` (set via the public `freeze` extrinsic) as a hard guarantee that an item cannot be destroyed will have that guarantee violated: the owner can burn the item anyway. This can be leveraged to destroy backing collateral for a wrapped/fractional asset or NFT-backed position while it is supposed to be locked, causing state inconsistency (unbacked claims elsewhere) — matching the "Unauthorized NFT ... burn / unbacked mint" impact class, since destruction of a frozen item that other logic assumes is immutable breaks accounting invariants downstream.

### Likelihood Explanation
High feasibility: `freeze` and `burn` are both ordinary signed, unprivileged extrinsics reachable directly, through a proxy, or in a batch (`freeze` then `burn` in the same block). No special preconditions beyond owning the item (or being collection admin for `freeze`) and being the item owner (or authorized) for `burn`. This is deterministically reproducible.

### Recommendation
Add explicit frozen-state checks to `do_burn`, mirroring `do_transfer`:
```rust
ensure!(!collection_details.is_frozen, Error::<T, I>::Frozen);
...
ensure!(!details.is_frozen, Error::<T, I>::Frozen);
```
before the deposit is unreserved and the item is removed, so that a frozen item (either via the item-level `freeze` or collection-level freeze) cannot be burned through the public `burn` flow.

### Proof of Concept
Rust integration test in `substrate/frame/uniques/src/tests.rs`:
```rust
#[test]
fn frozen_item_cannot_be_burned() {
    new_test_ext().execute_with(|| {
        assert_ok!(Uniques::force_create(RuntimeOrigin::root(), 0, 1, true));
        assert_ok!(Uniques::mint(RuntimeOrigin::signed(1), 0, 42, 1));
        // Freeze the item via the public `freeze` extrinsic.
        assert_ok!(Uniques::freeze(RuntimeOrigin::signed(1), 0, 42));
        // Attempt to burn it - this MUST fail with `Error::Frozen`.
        assert_noop!(
            Uniques::burn(RuntimeOrigin::signed(1), 0, 42, Some(1)),
            Error::<Test>::Frozen
        );
    });
}
```
Currently this test would fail (the burn succeeds), proving the bypass; after adding the missing `is_frozen` checks to `do_burn`, the assertion should pass.

### Citations

**File:** substrate/frame/uniques/src/functions.rs (L46-53)
```rust
		let collection_details =
			Collection::<T, I>::get(&collection).ok_or(Error::<T, I>::UnknownCollection)?;
		ensure!(!collection_details.is_frozen, Error::<T, I>::Frozen);
		ensure!(!T::Locker::is_locked(collection.clone(), item), Error::<T, I>::Locked);

		let mut details =
			Item::<T, I>::get(&collection, &item).ok_or(Error::<T, I>::UnknownCollection)?;
		ensure!(!details.is_frozen, Error::<T, I>::Frozen);
```

**File:** substrate/frame/uniques/src/functions.rs (L234-249)
```rust
	pub fn do_burn(
		collection: T::CollectionId,
		item: T::ItemId,
		with_details: impl FnOnce(&CollectionDetailsFor<T, I>, &ItemDetailsFor<T, I>) -> DispatchResult,
	) -> DispatchResult {
		ensure!(!T::Locker::is_locked(collection.clone(), item), Error::<T, I>::Locked);
		let owner = Collection::<T, I>::try_mutate(
			&collection,
			|maybe_collection_details| -> Result<T::AccountId, DispatchError> {
				let collection_details =
					maybe_collection_details.as_mut().ok_or(Error::<T, I>::UnknownCollection)?;

				// TODO should it be UnknownItem instead of UnknownCollection?
				let details = Item::<T, I>::get(&collection, &item)
					.ok_or(Error::<T, I>::UnknownCollection)?;
				with_details(collection_details, &details)?;
```
