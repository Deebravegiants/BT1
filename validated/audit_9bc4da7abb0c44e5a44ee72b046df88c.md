Audit Report

## Title
Front-runnable sequential `AssetId` check enables DoS on `pallet_assets::create` - (File: `substrate/frame/assets/src/functions.rs`, `substrate/frame/assets/src/lib.rs`)

## Summary
When the opt-in `AssetIdAllocator`/`NextAssetId` feature is active, `do_force_create` requires the caller-supplied `id` to exactly equal the current `next_id`, and only advances the counter after the create call succeeds. This "check-then-increment-after" pattern lets any unprivileged account front-run another unprivileged user's `create` call for the same expected `id`, causing the victim's transaction to fail with `BadAssetId`.

## Finding Description
The allocator check happens in `do_force_create`: `ensure!(id == next_id, Error::<T, I>::BadAssetId)` is validated before the asset is inserted, and `T::AssetIdAllocator::advance_from(&id)` is only called after successful insertion and callback execution. [1](#0-0) 

`advance_from` in `lib.rs` moves `NextAssetId` forward only when invoked, i.e., only after a successful creation: [2](#0-1) 

This is corroborated directly by the pallet's own test suite, which documents that "only the next id is accepted," and shows that a stale/mismatched id is rejected with `BadAssetId`, while the correct next id succeeds and advances the counter: [3](#0-2) [4](#0-3) 

The feature is deliberately enabled for trust-backed assets on Asset Hub, starting at id `50_000_000`, confirming this is a live, in-scope configuration and not merely theoretical: [5](#0-4) 

Root cause: the "next id" is public, deterministic, on-chain state (`NextAssetId` storage), and any account observing it can submit a competing `create(id = next_id, ...)` with higher priority/tip. Whichever transaction is included first consumes and advances the counter; any other pending transaction targeting the same `id` deterministically fails.

## Impact Explanation
This is a griefing/DoS vector rather than a fund-theft or accounting-break vulnerability: victims lose only transaction fees for reverted `create` calls, and no deposit is actually lost (the deposit is only reserved on success, not before). The `AssetId` a caller ends up with is dependent on transaction ordering rather than the caller's own state, which can create confusion and repeated failed attempts, but does not by itself corrupt pallet accounting, cause fund loss, or allow privilege escalation. This qualifies at most as a low/informational-severity nuisance issue, since the "bad" outcome is a normal, recoverable `DispatchError` (`BadAssetId`) rather than an exploitable state corruption.

## Likelihood Explanation
Exploitability requires the `AssetIdAllocator`/`NextAssetId` feature to be active for a given pallet instance, which is opt-in and only enabled for specific instances (e.g., Asset Hub trust-backed assets). Where active, any account capable of submitting extrinsics (unprivileged) can attempt front-running at low cost by watching the mempool and bidding a higher tip, and can repeat this indefinitely against sequential ids. However, this is an inherent property of any "predictable sequential resource + mempool visibility + tip-based ordering" design, common across many chains, and normal client tooling can mitigate it by re-querying `NextAssetId` and retrying transparently rather than treating it as a security failure.

## Recommendation
- Avoid making callers pre-commit to a specific numeric id for sequential allocation; either ignore/only weakly validate the caller-supplied id and allocate server-side, or offer a variant of `create` that doesn't take an explicit `id` parameter for the auto-increment path.
- If exact-id validation must remain for idempotency, have client tooling gracefully retry with the updated `NextAssetId` on `BadAssetId` failures instead of surfacing a hard revert to the end user.

## Proof of Concept
1. Enable the allocator: `NextAssetId::<T, I>::put(N)`.
2. Bob submits `Assets::create(id = N, owner, min_balance)`.
3. Alice, observing the pending `NextAssetId` value and Bob's pending transaction, submits her own `Assets::create(id = N, ...)` with a higher tip/priority.
4. Alice's transaction is included first; `do_force_create` succeeds and `advance_from` sets `NextAssetId` to `N+1` (per `substrate/frame/assets/src/lib.rs` L285-297).
5. Bob's transaction, now processed against `NextAssetId = N+1`, fails the `ensure!(id == next_id, Error::<T, I>::BadAssetId)` check in `do_force_create` (per `substrate/frame/assets/src/functions.rs` L766-774), matching the exact failure mode shown in `fungibles_create_must_follow_the_allocator` (`substrate/frame/assets/src/tests.rs` L2308-2324).
6. Alice can repeat this for `N+1, N+2, ...` at minimal cost, denying Bob predictable sequential asset ids.

### Citations

**File:** substrate/frame/assets/src/functions.rs (L766-797)
```rust
	) -> DispatchResult {
		ensure!(!Asset::<T, I>::contains_key(&id), Error::<T, I>::InUse);
		ensure!(!min_balance.is_zero(), Error::<T, I>::MinBalanceZero);
		if enforce_allocator {
			if let Some(next_id) = T::AssetIdAllocator::next() {
				ensure!(id == next_id, Error::<T, I>::BadAssetId);
			}
		}

		Asset::<T, I>::insert(
			&id,
			AssetDetails {
				owner: owner.clone(),
				issuer: owner.clone(),
				admin: owner.clone(),
				freezer: owner.clone(),
				supply: Zero::zero(),
				deposit: Zero::zero(),
				min_balance,
				is_sufficient,
				accounts: 0,
				sufficients: 0,
				approvals: 0,
				status: AssetStatus::Live,
			},
		);
		ensure!(T::CallbackHandle::created(&id, &owner).is_ok(), Error::<T, I>::CallbackFailed);
		T::AssetIdAllocator::advance_from(&id)
			.map_err(|_| Error::<T, I>::AssetIdAllocationFailed)?;
		Self::deposit_event(Event::ForceCreated { asset_id: id, owner: owner.clone() });
		Ok(())
	}
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
