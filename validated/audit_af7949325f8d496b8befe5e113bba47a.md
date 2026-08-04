No vulnerability found for this question.

The vulnerable Solidity pattern — computing `addingLiquidity` from a single asset balance while ignoring the actual ratio/availability of the paired asset — does not reproduce in the polkadot-sdk analog for liquidity provisioning.

`pallet_asset_conversion::Pallet::do_add_liquidity` (the FRAME analog of `provide()`) explicitly computes reserve-ratio-aware optimal amounts rather than assuming a fixed 1:1 match: when reserves are non-zero it calls `Self::quote(&amount1_desired, &reserve1, &reserve2)` to get `amount2_optimal`, and if that exceeds the desired amount it falls back to quoting the other side (`amount1_optimal`), always picking the amount consistent with actual pool reserves and bounded by the caller's provided `amount1_min`/`amount2_min`. [1](#0-0) 

This is precisely the fix pattern (min/ratio-based calculation instead of naive single-asset truncation) that the external report recommends for the vulnerable `USDMPegRecovery.sol#provide()`. There is no separate "guardian-only, single-balance-driven, fixed 1:1" liquidity-provision path elsewhere in the pallet — `MutateLiquidity::add_liquidity` in `substrate/frame/asset-conversion/src/liquidity.rs` and the `add_liquidity` extrinsic both route through the same `do_add_liquidity` logic. [2](#0-1) [3](#0-2) 

No reachable path with attacker-relevant impact matching this vulnerability class was found in the in-scope code.

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L466-490)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::add_liquidity())]
		pub fn add_liquidity(
			origin: OriginFor<T>,
			asset1: Box<T::AssetKind>,
			asset2: Box<T::AssetKind>,
			amount1_desired: T::Balance,
			amount2_desired: T::Balance,
			amount1_min: T::Balance,
			amount2_min: T::Balance,
			mint_to: T::AccountId,
		) -> DispatchResult {
			let sender = ensure_signed(origin)?;
			Self::do_add_liquidity(
				&sender,
				*asset1,
				*asset2,
				amount1_desired,
				amount2_desired,
				amount1_min,
				amount2_min,
				&mint_to,
			)?;
			Ok(())
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L813-844)
```rust
			let reserve1 = Self::get_balance(&pool_account, asset1.clone());
			let reserve2 = Self::get_balance(&pool_account, asset2.clone());

			let amount1: T::Balance;
			let amount2: T::Balance;
			if reserve1.is_zero() || reserve2.is_zero() {
				amount1 = amount1_desired;
				amount2 = amount2_desired;
			} else {
				let amount2_optimal = Self::quote(&amount1_desired, &reserve1, &reserve2)?;

				if amount2_optimal <= amount2_desired {
					ensure!(
						amount2_optimal >= amount2_min,
						Error::<T>::AssetTwoDepositDidNotMeetMinimum
					);
					amount1 = amount1_desired;
					amount2 = amount2_optimal;
				} else {
					let amount1_optimal = Self::quote(&amount2_desired, &reserve2, &reserve1)?;
					ensure!(
						amount1_optimal <= amount1_desired,
						Error::<T>::OptimalAmountLessThanDesired
					);
					ensure!(
						amount1_optimal >= amount1_min,
						Error::<T>::AssetOneDepositDidNotMeetMinimum
					);
					amount1 = amount1_optimal;
					amount2 = amount2_desired;
				}
			}
```

**File:** substrate/frame/asset-conversion/src/liquidity.rs (L99-116)
```rust
	#[transactional]
	fn add_liquidity(
		who: &T::AccountId,
		asset1: AddLiquidityAsset<Self::AssetKind, Self::Balance>,
		asset2: AddLiquidityAsset<Self::AssetKind, Self::Balance>,
		mint_to: &T::AccountId,
	) -> Result<T::Balance, DispatchError> {
		Self::do_add_liquidity(
			who,
			asset1.asset,
			asset2.asset,
			asset1.amount_desired,
			asset2.amount_desired,
			asset1.amount_min,
			asset2.amount_min,
			mint_to,
		)
	}
```
