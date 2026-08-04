### Title
Front-running of `pallet-assets::force_create` at the auto-increment boundary lets an unprivileged user hijack an asset ID intended for privileged/reserved allocation - (File: `substrate/frame/assets/src/lib.rs`)

### Summary
`pallet-assets` supports an `AssetIdAllocator` policy (`AutoIncAssetId`) that reserves the ID range `< NextAssetId` for deliberate `force_create` assignment while enforcing that permissionless `create` must use exactly `id == NextAssetId`. Because `force_create` is also permitted to use `id == NextAssetId` (which additionally advances the sequence), a privileged origin's intent to reserve the "next" sequential ID for a special/system asset can be front-run by any signed account calling the permissionless `create` extrinsic with the same ID before the privileged transaction is included.

### Finding Description
The allocator explicitly reserves ids below `NextAssetId` for privileged, forced assignment, but the boundary id (`id == NextAssetId`) is claimable by both paths: [1](#0-0) 

Permissionless `create` requires `id == AssetIdAllocator::next()`: [2](#0-1) 

Privileged `force_create` (gated by `ForceOrigin`) accepts *any* unused id, including exactly `NextAssetId`, and if so also advances the sequence: [3](#0-2) [4](#0-3) 

The test suite even documents this exact race condition ("Forcing exactly the next id also advances the sequence"): [5](#0-4) 

`NextAssetId` is public on-chain storage, so any observer can predict the exact ID a governance/`ForceOrigin` `force_create` transaction targets when it uses the boundary value. This is structurally the same vulnerability class as the DeGate report: two registration paths (privileged vs. permissionless) share a namespace/slot, and an attacker can win the race for a specific slot by front-running the privileged transaction with the permissionless one, causing the asset to end up under attacker-chosen (non-privileged) ownership/config instead of the governance-intended, privileged configuration. Root cause: `id`-collision checking is done only via `ensure!(!Asset::<T,I>::contains_key(&id), Error::InUse)` at execution time (mempool-ordering dependent), not via any commit-reveal or reservation prior to broadcast: [6](#0-5) 

### Impact Explanation
If the winning front-run transaction is `create`, the attacker becomes owner/admin/issuer/freezer of that asset ID (paying only the standard `AssetDeposit`), while the privileged `force_create(id=NextAssetId, ...)` then simply fails with `Error::InUse`. This is a low-severity griefing/DoS on a specific, deliberate privileged asset-creation flow (the intended asset never gets created at that id; governance must retry with a different id and any hard-coded/expected id assumptions elsewhere — e.g., bridged asset id mappings the code's own doc-comment warns about — could be disrupted). Unlike the DeGate report, this does not cause silent misclassification (the privileged call reverts rather than succeeding into the wrong bucket), so the practical protocol impact is materially lower.

### Likelihood Explanation
Exploitation requires: (1) a runtime configuring `AssetIdAllocator = AutoIncAssetId<...>`, (2) a `ForceOrigin` transaction that deliberately targets `id == NextAssetId` (rather than a value strictly below it, which the reserved range in the tests/docs is designed to accommodate without risk), and (3) the attacker observing the pending transaction/storage state and successfully front-running it in the same or an earlier block. Reviewing the searched code, no in-scope production runtime (asset-hub-westend/rococo) was confirmed to actually set `NextAssetId` and then deliberately `force_create` at the exact boundary value in the indexed code; this specific pattern (using `id == NextAssetId` in `force_create`) is discouraged by the pallet's own design intent (reserved range is `< NextAssetId`), making real-world exploitation unlikely and largely avoidable by governance simply picking an id below the sequence boundary.

### Recommendation
- Short term: In `force_create`, when `enforce_allocator` is false, disallow `id == AssetIdAllocator::next()` (the boundary value) to force privileged callers to use ids strictly below the reserved boundary, eliminating the race entirely.
- Long term: Document clearly (in `AssetIdAllocator` trait docs and `force_create`'s doc-comment "Warning" section) that ids at or above `NextAssetId` are contested with permissionless `create` and must not be relied upon for security-sensitive privileged registrations; consider requiring `ForceOrigin` calls to always target ids strictly below `NextAssetId` when auto-increment is enabled.

### Proof of Concept
1. Runtime configures `type AssetIdAllocator = AutoIncAssetId<Runtime, Instance1>;` and `NextAssetId::put(N)` is set.
2. Governance/root submits `Assets::force_create(id = N, owner = Governance, ...)` intending to reserve asset `N` for a privileged purpose.
3. An attacker observing chain state (or the transaction pool) submits `Assets::create(id = N, admin = Attacker, min_balance = 1)` with higher priority/tip, or simply gets included first within the same block.
4. Attacker's `create` succeeds (per `substrate/frame/assets/src/lib.rs:843-889`), setting `Asset::<T,I>::contains_key(N) = true` and advancing `NextAssetId` to `N+1`.
5. Governance's `force_create(id = N, ...)` now fails with `Error::InUse` (per `substrate/frame/assets/src/functions.rs:767`), confirmed by the equivalent ordering test at `substrate/frame/assets/src/tests.rs:2271-2275`.

### Citations

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

**File:** substrate/frame/assets/src/lib.rs (L843-858)
```rust
		pub fn create(
			origin: OriginFor<T>,
			id: T::AssetIdParameter,
			admin: AccountIdLookupOf<T>,
			min_balance: T::Balance,
		) -> DispatchResult {
			let id: T::AssetId = id.into();
			let owner = T::CreateOrigin::ensure_origin(origin, &id)?;
			let admin = T::Lookup::lookup(admin)?;

			ensure!(!Asset::<T, I>::contains_key(&id), Error::<T, I>::InUse);
			ensure!(!min_balance.is_zero(), Error::<T, I>::MinBalanceZero);

			if let Some(next_id) = T::AssetIdAllocator::next() {
				ensure!(id == next_id, Error::<T, I>::BadAssetId);
			}
```

**File:** substrate/frame/assets/src/lib.rs (L920-931)
```rust
		#[pallet::call_index(1)]
		pub fn force_create(
			origin: OriginFor<T>,
			id: T::AssetIdParameter,
			owner: AccountIdLookupOf<T>,
			is_sufficient: bool,
			#[pallet::compact] min_balance: T::Balance,
		) -> DispatchResult {
			T::ForceOrigin::ensure_origin(origin)?;
			let owner = T::Lookup::lookup(owner)?;
			let id: T::AssetId = id.into();
			Self::do_force_create(id, owner, is_sufficient, min_balance, false)
```

**File:** substrate/frame/assets/src/functions.rs (L760-797)
```rust
	pub(super) fn do_force_create(
		id: T::AssetId,
		owner: T::AccountId,
		is_sufficient: bool,
		min_balance: T::Balance,
		enforce_allocator: bool,
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

**File:** substrate/frame/assets/src/tests.rs (L2277-2292)
```rust
		// A forced id at or beyond the sequence advances `NextAssetId` past it, so the sequence
		// never later collides.
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 60, 1, false, 1));
		assert!(Asset::<Test>::contains_key(60));
		assert_eq!(pallet::NextAssetId::<Test>::get(), Some(61));

		// A subsequent sequential `create` picks up from the advanced sequence.
		assert_noop!(Assets::create(RuntimeOrigin::signed(1), 50, 1, 1), Error::<Test>::BadAssetId);
		Balances::make_free_balance_be(&1, 100);
		assert_ok!(Assets::create(RuntimeOrigin::signed(1), 61, 1, 1));
		assert_eq!(pallet::NextAssetId::<Test>::get(), Some(62));

		// Forcing exactly the next id also advances the sequence.
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 62, 1, false, 1));
		assert_eq!(pallet::NextAssetId::<Test>::get(), Some(63));
	});
```
