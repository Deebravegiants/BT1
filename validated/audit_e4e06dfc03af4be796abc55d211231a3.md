Audit Report

## Title
Front-runnable sequential `AssetId` check enables griefing/DoS on `pallet_assets::create` - (File: `substrate/frame/assets/src/functions.rs`, `substrate/frame/assets/src/lib.rs`)

## Summary
When the auto-increment allocator is active (`NextAssetId` populated), `do_force_create` requires the caller-supplied `id` to equal the current `next_id` before the asset is created, and only advances `NextAssetId` after the create succeeds. This "check-then-increment-after" pattern lets an attacker front-run a pending `create(id = next_id, ...)` transaction with their own transaction for the same id, causing the original submitter's transaction to fail with `BadAssetId`.

## Finding Description
`do_force_create` in `substrate/frame/assets/src/functions.rs` validates the caller-supplied `id` against `T::AssetIdAllocator::next()` via `ensure!(id == next_id, Error::<T, I>::BadAssetId)` [1](#0-0) , then only afterward calls `T::AssetIdAllocator::advance_from(&id)` to bump `NextAssetId` [2](#0-1) . The `AutoIncAssetId::advance_from` implementation confirms `NextAssetId` storage is only updated at this point in the transaction, not beforehand [3](#0-2) . This is a genuine check-then-effect race on shared storage that any transaction ordering (tips/priority) can exploit — whichever transaction executes first for a given `next_id` consumes it and advances the counter, causing any other transaction targeting the same `id` to revert with `BadAssetId`. The pallet's own tests explicitly demonstrate this behavior (rejecting ids that are not exactly the current `next_id`) [4](#0-3) [5](#0-4) , and the feature is documented as being enabled for trust-backed assets on Asset Hub starting at id `50_000_000` [6](#0-5) .

## Impact Explanation
The impact is limited to griefing/DoS on asset creation, not fund loss or protocol insolvency: deposits are only reserved on a successful create call, so a front-run victim only loses transaction fees and must retry, and the "impact" is that the asset id they receive is contingent on tx ordering rather than deterministic. This is a real but low-severity nuisance-class issue — it does not break any accounting invariant, does not allow theft, and does not escalate privilege; it merely allows one unprivileged user to force another's `create` call to revert and to consume the id first.

## Likelihood Explanation
The condition is opt-in (only active when `NextAssetId` is populated for a given pallet instance) and, where active, requires an attacker to observe pending `create` calls and win transaction ordering with a higher tip/priority — a realistic but low-value griefing vector, not free money for the attacker (they must actually pay to create assets under ids they may not want) and not persistent censorship (a victim can simply re-query `NextAssetId` and resubmit). This matches ordinary "front-running is possible in public mempools" behavior common to many blockchain systems, rather than a design flaw unique to unsafe accounting.

## Recommendation
- Do not force the caller to pre-commit to an exact numeric id for the sequential-allocation path; either always derive the id server-side (ignore/only optionally validate any caller-supplied id) or provide a dedicated "auto id" call variant without an `id` parameter.
- If callers must supply the id (e.g. for idempotent retries or cross-chain predictability), have tooling/UX transparently retry with the updated `NextAssetId` on `BadAssetId` failure rather than surfacing this as a hard failure to the user.

## Proof of Concept
1. Set `NextAssetId::<T, I>::put(N)` to enable the allocator.
2. Bob submits `Assets::create(id = N, owner, ...)`.
3. Alice observes Bob's pending transaction and submits her own `Assets::create(id = N, ...)` with higher priority/tip.
4. Alice's transaction executes first: `do_force_create` succeeds, `NextAssetId` advances to `N+1` (per `advance_from` at `substrate/frame/assets/src/lib.rs:285-297`).
5. Bob's transaction for `id = N` now fails with `Error::<T, I>::BadAssetId`, matching the pallet's own test assertions at `substrate/frame/assets/src/tests.rs:2232-2243` and `2308-2324`.
6. Alice can repeat this for `N+1, N+2, ...` to continually disrupt Bob's expected sequential id, at the cost of actually creating assets herself each time.

### Citations

**File:** substrate/frame/assets/src/functions.rs (L769-773)
```rust
		if enforce_allocator {
			if let Some(next_id) = T::AssetIdAllocator::next() {
				ensure!(id == next_id, Error::<T, I>::BadAssetId);
			}
		}
```

**File:** substrate/frame/assets/src/functions.rs (L792-794)
```rust
		ensure!(T::CallbackHandle::created(&id, &owner).is_ok(), Error::<T, I>::CallbackFailed);
		T::AssetIdAllocator::advance_from(&id)
			.map_err(|_| Error::<T, I>::AssetIdAllocationFailed)?;
```

**File:** substrate/frame/assets/src/lib.rs (L285-297)
```rust
	fn advance_from(id: &T::AssetId) -> Result<(), ()> {
		let Some(next_id) = NextAssetId::<T, I>::get() else {
			// Auto increment for the asset id is not active.
			return Ok(());
		};
		// Only advance when the forced id is at or beyond the sequence; ids below `next_id` belong
		// to a range that can be reserved for deliberate, forced assignment.
		if *id >= next_id {
			let next_id = id.increment().ok_or(())?;
			NextAssetId::<T, I>::put(next_id);
		}
		Ok(())
	}
```

**File:** substrate/frame/assets/src/tests.rs (L2232-2243)
```rust
		// Enable auto increment. Next asset id must be 5.
		pallet::NextAssetId::<Test>::put(5);

		// `create` must follow the sequence: only the next id is accepted.
		assert_noop!(Assets::create(RuntimeOrigin::signed(1), 0, 1, 1), Error::<Test>::BadAssetId);
		assert_noop!(Assets::create(RuntimeOrigin::signed(1), 1, 1, 1), Error::<Test>::BadAssetId);

		// Asset with id `5` is created and the sequence advances to `6`.
		assert_ok!(Assets::create(RuntimeOrigin::signed(1), 5, 1, 1));
		assert!(Asset::<Test>::contains_key(5));
		assert_eq!(pallet::NextAssetId::<Test>::get(), Some(6));

```

**File:** substrate/frame/assets/src/tests.rs (L2308-2324)
```rust
#[test]
fn fungibles_create_must_follow_the_allocator() {
	build_and_execute(|| {
		use frame_support::traits::fungibles::Create;

		pallet::NextAssetId::<Test>::put(5);

		// Not gated on `ForceOrigin`, so a non-sequential id is rejected.
		assert_noop!(<Assets as Create<_>>::create(0, 1, false, 1), Error::<Test>::BadAssetId);
		assert!(!Asset::<Test>::contains_key(0));
		assert_eq!(pallet::NextAssetId::<Test>::get(), Some(5));

		// The sequential id is accepted and advances the allocator.
		assert_ok!(<Assets as Create<_>>::create(5, 1, false, 1));
		assert!(Asset::<Test>::contains_key(5));
		assert_eq!(pallet::NextAssetId::<Test>::get(), Some(6));
	});
```

**File:** prdoc/stable2412/pr_5687.prdoc (L4-17)
```text
title: "Westend/Rococo Asset Hub: auto incremented asset id for trust backed assets"

doc:
  - audience: Runtime User
    description: |
      Setup auto incremented asset id to `50_000_000` for trust backed assets.

      ### Migration
      This change does not break the API but introduces a new constraint. It implements 
      an auto-incremented ID strategy for Trust-Backed Assets (50 pallet instance indexes on both 
      networks), starting at ID 50,000,000. Each new asset must be created with an ID that is one 
      greater than the last asset created. The next ID can be fetched from the `NextAssetId` 
      storage item of the assets pallet. An empty `NextAssetId` storage item indicates no 
      constraint on the next asset ID and can serve as a feature flag for this release.
```
