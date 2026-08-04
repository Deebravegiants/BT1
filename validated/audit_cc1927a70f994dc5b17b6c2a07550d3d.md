### Title
Unbounded `Pools` storage iteration in `PoolAdapter::get_assets_in_pool_with` runtime API helper - ([File: cumulus/parachains/runtimes/assets/common/src/lib.rs])

### Summary
`pallet_asset_conversion` allows any signed account to permissionlessly create new liquidity pools via `create_pool`/`create_pool_with_fee`, growing the unbounded `Pools` storage map without limit. The Asset Hub runtimes expose `PoolAdapter::get_assets_in_pool_with`, which is documented as being used from a Runtime API and internally iterates the *entire* `Pools` map to find all assets paired with a given asset — directly analogous to the reported `getTickState()` issue, which iterated the full tick linked list with no bound or pagination.

### Finding Description
`PoolAdapter::iter_assets_in_pool_with` performs a full scan of `pallet_asset_conversion::Pools::<Runtime>::iter_keys()`, filtering for pairs containing the queried asset: [1](#0-0) 

The doc comment explicitly flags the risk: "Should only be used in runtime APIs since it iterates over the whole `pallet_asset_conversion::Pools` map." [2](#0-1) 

`get_assets_in_pool_with` (the public wrapper collecting into a `Vec<AssetId>`) is used in the Asset Hub Rococo/Westend runtimes and in `substrate/frame/staking-async/runtimes/parachain/src/lib.rs`, confirming it's wired into a live production runtime API surface, not merely a test helper.

Pool creation is permissionless — any signed account paying `PoolSetupFee` can create a pool for any valid asset pair: [3](#0-2) 

There is no `MaxPools`-style bound on `Pools` (unlike, e.g., `pallet_nomination_pools`'s `MaxPools`), so the map can grow to an attacker-influenced size over time as long as attackers are willing to pay the setup fee repeatedly for distinct asset pairs.

This is the same vulnerability *class* as the `getTickState()` finding: a query-style helper that walks an entire, growable on-chain collection with no starting-index/pagination parameter and no cap on iteration count.

### Impact Explanation
Because this helper is invoked from a **Runtime API** (called via RPC `state_call`, not as a dispatched, weight-metered extrinsic), it is not gas/weight-limited the way an on-chain transaction is. If the `Pools` map grows large enough (through repeated permissionless pool creation across many distinct assets), a call to the runtime API that uses `get_assets_in_pool_with` will decode and filter every entry in `Pools`, consuming node CPU/DB-read resources for the duration of the call. Because RPC/state_call read execution is generally bounded by node-level timeouts rather than on-chain weight, this manifests as a computational-cost/DoS-style issue for whichever node services the RPC call, and could degrade responsiveness rather than corrupting on-chain state — this differs from the original report's on-chain gas exhaustion but is the direct analog for a substrate runtime, where storage-iterating "view" functions are exposed off-chain rather than metered.

### Likelihood Explanation
Likelihood is moderate-to-low in practice: pool creation costs `PoolSetupFee` plus asset deposits for every new pair, so growing `Pools` to a size that meaningfully impacts a single RPC call requires sustained spending by an attacker (or organic ecosystem growth over a long period). There is no per-account or global cap preventing the number of pools from growing unbounded over time, so the risk increases as the parachain matures, and no explicit code path currently limits `get_assets_in_pool_with`'s iteration.

### Recommendation
Add pagination/limiting to `iter_assets_in_pool_with`/`get_assets_in_pool_with`, e.g., a `max_results` and/or a starting cursor (analogous to the suggested `startIndex`/`tickCount` fix), or restrict its use to a bounded reverse index instead of a full linear scan of `Pools`. If the API needs to remain unbounded, ensure Runtime API/RPC call sites enforce practical limits (backpressure to callers, or bail out after a defensive iteration cap) rather than relying on the caller to bound the result set.

### Proof of Concept
1. Repeatedly call `pallet_asset_conversion::create_pool` (paying `PoolSetupFee` each time) with N distinct asset pairs, all sharing a common asset `X`, to grow `Pools` to a large size — this is fully within an unprivileged signed account's capability, subject only to the recurring setup fee. [4](#0-3) 
2. Invoke the Runtime API/host function that calls `PoolAdapter::get_assets_in_pool_with(X)` (exposed in `asset-hub-rococo`/`asset-hub-westend` runtimes) via RPC `state_call`. [5](#0-4) 
3. Observe that the call must decode and filter every entry of `Pools::<Runtime>` regardless of how many pairs actually match `X`, with execution cost scaling linearly with total pool count and no way for the caller to limit or paginate the scan. [1](#0-0)

### Citations

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L185-204)
```rust
	/// Returns a vector of all assets in a pool with `asset`.
	///
	/// Should only be used in runtime APIs since it iterates over the whole
	/// `pallet_asset_conversion::Pools` map.
	///
	/// It takes in any version of an XCM Location but always returns the latest one.
	/// This is to allow some margin of migrating the pools when updating the XCM version.
	///
	/// An error of type `()` is returned if the version conversion fails for XCM locations.
	/// This error should be mapped by the caller to a more descriptive one.
	pub fn get_assets_in_pool_with(asset: Location) -> Result<Vec<AssetId>, ()> {
		// convert latest to the `L` version.
		let asset: L = asset.try_into().map_err(|_| ())?;
		Self::iter_assets_in_pool_with(&asset)
			.map(|location| {
				// convert `L` to the latest `AssetId`
				location.try_into().map_err(|_| ()).map(AssetId)
			})
			.collect::<Result<Vec<_>, _>>()
	}
```

**File:** cumulus/parachains/runtimes/assets/common/src/lib.rs (L230-241)
```rust
	/// Helper function for filtering pool.
	pub fn iter_assets_in_pool_with(asset: &L) -> impl Iterator<Item = L> + '_ {
		pallet_asset_conversion::Pools::<Runtime>::iter_keys().filter_map(|(asset_1, asset_2)| {
			if asset_1 == *asset {
				Some(asset_2)
			} else if asset_2 == *asset {
				Some(asset_1)
			} else {
				None
			}
		})
	}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L726-788)
```rust
		/// Create a new liquidity pool.
		///
		/// **Warning**: The storage must be rolled back on error.
		pub(crate) fn do_create_pool(
			creator: &T::AccountId,
			asset1: T::AssetKind,
			asset2: T::AssetKind,
			initial_fee: Option<Permill>,
		) -> Result<T::PoolId, DispatchError> {
			ensure!(asset1 != asset2, Error::<T>::InvalidAssetPair);
			if let Some(fee) = initial_fee {
				ensure!(fee <= T::MaxSwapFee::get(), Error::<T>::FeeTooHigh);
			}

			// prepare pool_id
			let pool_id = T::PoolLocator::pool_id(&asset1, &asset2)
				.map_err(|_| Error::<T>::InvalidAssetPair)?;
			ensure!(!Pools::<T>::contains_key(&pool_id), Error::<T>::PoolExists);

			let pool_account =
				T::PoolLocator::address(&pool_id).map_err(|_| Error::<T>::InvalidAssetPair)?;

			// pay the setup fee
			let fee =
				Self::withdraw(T::PoolSetupFeeAsset::get(), creator, T::PoolSetupFee::get(), true)?;
			T::PoolSetupFeeTarget::on_unbalanced(fee);

			if T::Assets::should_touch(asset1.clone(), &pool_account) {
				T::Assets::touch(asset1.clone(), &pool_account, creator)?
			};

			if T::Assets::should_touch(asset2.clone(), &pool_account) {
				T::Assets::touch(asset2.clone(), &pool_account, creator)?
			};

			let lp_token = NextPoolAssetId::<T>::get()
				.or(T::PoolAssetId::initial_value())
				.ok_or(Error::<T>::IncorrectPoolAssetId)?;
			let next_lp_token_id = lp_token.increment().ok_or(Error::<T>::IncorrectPoolAssetId)?;
			NextPoolAssetId::<T>::set(Some(next_lp_token_id));

			T::PoolAssets::create(lp_token.clone(), pool_account.clone(), false, 1u32.into())?;
			if T::PoolAssets::should_touch(lp_token.clone(), &pool_account) {
				T::PoolAssets::touch(lp_token.clone(), &pool_account, creator)?
			};

			let pool_info = PoolInfo { lp_token: lp_token.clone() };
			Pools::<T>::insert(pool_id.clone(), pool_info);

			Self::deposit_event(Event::PoolCreated {
				creator: creator.clone(),
				pool_id: pool_id.clone(),
				pool_account,
				lp_token,
			});

			if let Some(fee) = initial_fee {
				PoolFees::<T>::insert(&pool_id, fee);
				Self::deposit_event(Event::PoolFeeSet { pool_id: pool_id.clone(), fee });
			}

			Ok(pool_id)
		}
```
