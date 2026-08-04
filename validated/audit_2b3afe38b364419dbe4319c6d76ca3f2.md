### Title
Missing slippage protection (`amount_out_min = None`) in `swap_and_burn` allows front-running/sandwich attacks on tip-asset-to-Ether swaps - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The `snowbridge-pallet-system-frontend` pallet swaps a user-supplied "tip" asset into Ether via `pallet_asset_conversion::Swap::swap_exact_tokens_for_tokens` before burning the resulting Ether for a teleport, but it passes `None` for the `amount_out_min` parameter, explicitly disabling slippage protection. This is the same root-cause pattern as the reported Beedle `Fees.sol::sellProfits` issue: an automated AMM swap executed with no minimum-output/price guard, which becomes exploitable when the underlying pool has thin or attacker-influenced liquidity.

### Finding Description
`Self::swap_and_burn` calls the generic `Swap` trait (backed by `pallet-asset-conversion`, a Uniswap-V2-style AMM) with the minimum-out parameter hard-coded to `None`: [1](#0-0) 

This is invoked from `swap_fee_asset_and_burn`, which converts an arbitrary `fee_asset` (the tip asset chosen by the caller/origin) into Ether whenever the tip is not already denominated in Ether: [2](#0-1) 

Because `amount_out_min` is `None`, `pallet_asset_conversion::Pallet::do_swap_exact_tokens_for_tokens` skips the check that would otherwise revert the swap if the output amount falls below a caller-specified floor: [3](#0-2) 

`pallet-asset-conversion` pools are constant-product (Uniswap V2 style) and are permissionlessly created by anyone via `create_pool`/`do_create_pool`, with an initial reserve ratio fully controlled by the pool creator: [4](#0-3) 

As in the original report, if no pool exists yet for the tip-asset/Ether pair, an attacker can pre-create the pool with a skewed price and then let the victim's zero-slippage swap execute against it. Even where a pool already exists, the absence of any `amount_out_min` floor means the swap is exposed to ordinary sandwich/front-running manipulation of pool reserves within the same block, since the pallet provides the min/max parameters specifically to protect against this and they are being deliberately bypassed here.

### Impact Explanation
A manipulated or newly created skewed pool causes the tip-asset-to-Ether swap to execute at an arbitrarily bad rate, so the Ether amount burned/teleported (`ether_gained`) can be driven close to zero, effectively destroying the tip value. Because the resulting Ether credit is what gets burned for the cross-chain message, this also affects the fee/tip actually delivered on the Ethereum side, degrading the relayer incentive the tip is meant to fund.

### Likelihood Explanation
Likelihood is low-to-moderate and comparable to the original report's own "low" severity rating: it requires (a) the fee/tip asset chosen to not already be Ether, and (b) either no existing pool for that asset/Ether pair, or a thinly-liquid pool that can be manipulated within a single block window (classic AMM sandwich). Whether the `fee_asset` is fully attacker-controlled, and the exact public entry points that reach `swap_fee_asset_and_burn`, could not be fully traced in this pass — I was not able to confirm from the index whether this path is reachable by an arbitrary unprivileged caller supplying an arbitrary asset id, or whether the set of permissible tip assets is restricted elsewhere in the pallet/runtime configuration. This should be verified before treating the likelihood as high.

### Recommendation
Compute an `amount_out_min` from `QuotePrice::quote_price_exact_tokens_for_tokens` (or an oracle/expected-price bound) before calling `swap_exact_tokens_for_tokens`, and pass that as `Some(min_out)` instead of `None`, mirroring the mitigation recommended in the original report (bound the acceptable exchange rate rather than accepting any price).

### Proof of Concept
1. Attacker observes a pending extrinsic in `snowbridge-pallet-system-frontend` that will trigger `swap_fee_asset_and_burn` for a tip asset `X` that has no pool with `Ether`, or has a thin `X`/`Ether` pool.
2. Attacker front-runs by calling `pallet_asset_conversion::create_pool` (or `add_liquidity`/manipulative swap) to set an extremely skewed `X`/`Ether` ratio.
3. The victim's `swap_and_burn` call executes `swap_exact_tokens_for_tokens(..., None, ...)` at the manipulated ratio, receiving near-zero Ether.
4. The near-zero Ether amount is burned/teleported, and the attacker can immediately reverse the pool skew (remove liquidity / swap back) to recover value, at the victim's expense.

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L301-308)
```rust
			let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
				who.clone(),
				swap_path,
				tip_amount,
				None, // No minimum amount required
				who,
				true,
			)?;
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L372-404)
```rust
		fn swap_fee_asset_and_burn(
			origin: Location,
			fee_asset: Asset,
		) -> Result<u128, DispatchError> {
			let ether_location = T::EthereumLocation::get();
			let (fee_asset_location, fee_amount) = match fee_asset {
				Asset { id: AssetId(ref loc), fun: Fungible(amount) } => (loc, amount),
				_ => {
					tracing::debug!(target: LOG_TARGET, ?fee_asset, "error matching fee asset");
					return Err(Error::<T>::UnsupportedAsset.into());
				},
			};
			if fee_amount == 0 {
				return Ok(0);
			}

			let ether_gained = if *fee_asset_location != ether_location {
				Self::swap_and_burn(
					origin.clone(),
					fee_asset_location.clone(),
					ether_location,
					fee_amount,
				)
				.inspect_err(|&e| {
					tracing::debug!(target: LOG_TARGET, ?e, "error swapping asset");
				})?
			} else {
				burn_for_teleport::<T::AssetTransactor>(&origin, &fee_asset)
					.map_err(|_| Error::<T>::BurnError)?;
				fee_amount
			};
			Ok(ether_gained)
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L729-746)
```rust
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
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L987-1002)
```rust
		) -> Result<T::Balance, DispatchError> {
			ensure!(amount_in > Zero::zero(), Error::<T>::ZeroAmount);
			if let Some(amount_out_min) = amount_out_min {
				ensure!(amount_out_min > Zero::zero(), Error::<T>::ZeroAmount);
			}

			Self::validate_swap_path(&path)?;
			let path = Self::balance_path_from_amount_in(amount_in, path)?;

			let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
			if let Some(amount_out_min) = amount_out_min {
				ensure!(
					amount_out >= amount_out_min,
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
			}
```
