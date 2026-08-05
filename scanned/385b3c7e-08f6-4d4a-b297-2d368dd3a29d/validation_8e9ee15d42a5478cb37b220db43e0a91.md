No vulnerability found for this question.

The vulnerability class in the report is specific to Dango DEX's `geometric` pool design, where passive order prices/sizes are derived directly from an oracle price combined with raw pool reserves (`base_reserve`/`quote_reserve`), independent of any deposit-time ratio check [1](#0-0) . The closest analog in this codebase is `pallet-asset-conversion`, a standard Uniswap-V2-style constant-product AMM [2](#0-1) .

Critically, `do_add_liquidity` does not accept arbitrary asymmetric deposits at face value: when reserves are non-zero, it computes the "optimal" counterpart amount via `Self::quote(&amount1_desired, &reserve1, &reserve2)` (i.e., strictly proportional to the *current pool reserve ratio*, not an external oracle price), and mints LP tokens proportionally to `min(side1, side2)` [3](#0-2) . Because the deposit ratio is forced to match the existing reserve ratio, a depositor cannot use `add_liquidity` + `remove_liquidity` to execute a "virtual swap" that shifts the pool away from its constant-product curve — there is no oracle-anchored flat price to arbitrage against, and no mechanism by which an asymmetric deposit bypasses the `x*y=k` price-impact curve the way it bypasses the geometric pool's tick/ratio ladder in the Dango report.

`remove_liquidity` similarly returns assets strictly proportional to reserves at burn time (`mul_div(lp_redeem_amount, reserve, total_supply)`), with no path for extracting a favorable "virtual swap" profit purely from the add/remove liquidity round-trip [4](#0-3) .

There is also a `pallet-oracle` pallet in the codebase for feeding off-chain price data [5](#0-4) , but it is a generic, standalone data-feed pallet with no coupling to `pallet-asset-conversion` or any AMM pricing/order-reflection logic — there is no oracle-anchored geometric/passive-order DEX pool in this repository that reproduces the root cause described in the report (price/size derived from oracle price + fixed spacing/ratio parameters, independent of deposit ratio checks).

Since the only in-scope AMM pallet structurally forecloses the asymmetric-liquidity attack vector by enforcing reserve-ratio-proportional deposits/withdrawals, and no oracle-price-reflected liquidity curve exists in this codebase, this vulnerability class does not have a valid, reachable analog here.

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L813-872)
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

			ensure!(
				amount1.saturating_add(reserve1) >= T::Assets::minimum_balance(asset1.clone()),
				Error::<T>::AmountOneLessThanMinimal
			);
			ensure!(
				amount2.saturating_add(reserve2) >= T::Assets::minimum_balance(asset2.clone()),
				Error::<T>::AmountTwoLessThanMinimal
			);

			T::Assets::transfer(asset1, who, &pool_account, amount1, Preserve)?;
			T::Assets::transfer(asset2, who, &pool_account, amount2, Preserve)?;

			let total_supply = T::PoolAssets::total_issuance(pool.lp_token.clone());

			let lp_token_amount: T::Balance;
			if total_supply.is_zero() {
				lp_token_amount = Self::calc_lp_amount_for_zero_supply(&amount1, &amount2)?;
				T::PoolAssets::mint_into(
					pool.lp_token.clone(),
					&pool_account,
					T::MintMinLiquidity::get(),
				)?;
			} else {
				let side1 = Self::mul_div(&amount1, &total_supply, &reserve1)?;
				let side2 = Self::mul_div(&amount2, &total_supply, &reserve2)?;
				lp_token_amount = side1.min(side2);
			}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L913-920)
```rust
			let (reserve1, reserve2) = Self::get_reserves(asset1.clone(), asset2.clone())?;

			let total_supply = T::PoolAssets::total_issuance(pool.lp_token.clone());
			let withdrawal_fee_amount = T::LiquidityWithdrawalFee::get() * lp_token_burn;
			let lp_redeem_amount = lp_token_burn.saturating_sub(withdrawal_fee_amount);

			let amount1 = Self::mul_div(&lp_redeem_amount, &reserve1, &total_supply)?;
			let amount2 = Self::mul_div(&lp_redeem_amount, &reserve2, &total_supply)?;
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1388-1419)
```rust
		pub fn get_amount_out(
			fee: Permill,
			amount_in: &T::Balance,
			reserve_in: &T::Balance,
			reserve_out: &T::Balance,
		) -> Result<T::Balance, Error<T>> {
			let amount_in = T::HigherPrecisionBalance::from(*amount_in);
			let reserve_in = T::HigherPrecisionBalance::from(*reserve_in);
			let reserve_out = T::HigherPrecisionBalance::from(*reserve_out);

			if reserve_in.is_zero() || reserve_out.is_zero() {
				return Err(Error::<T>::ZeroLiquidity);
			}

			let fee_complement = fee.left_from_one().deconstruct();
			let amount_in_with_fee = amount_in
				.checked_mul(&T::HigherPrecisionBalance::from(fee_complement))
				.ok_or(Error::<T>::Overflow)?;

			let numerator =
				amount_in_with_fee.checked_mul(&reserve_out).ok_or(Error::<T>::Overflow)?;

			let denominator = reserve_in
				.checked_mul(&T::HigherPrecisionBalance::from(Permill::ACCURACY))
				.ok_or(Error::<T>::Overflow)?
				.checked_add(&amount_in_with_fee)
				.ok_or(Error::<T>::Overflow)?;

			let result = numerator.checked_div(&denominator).ok_or(Error::<T>::Overflow)?;

			result.try_into().map_err(|_| Error::<T>::Overflow)
		}
```

**File:** substrate/frame/asset-conversion/README.md (L1-6)
```markdown
# asset-conversion

## A swap pallet

This pallet allows assets to be converted from one type to another by means of a constant product formula.
The pallet based is based on [Uniswap V2](https://github.com/Uniswap/v2-core) logic.
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L18-39)
```rust
//! # Oracle
//!
//! A pallet that provides a decentralized and trustworthy way to bring external, off-chain data
//! onto the blockchain.
//!
//! ## Pallet API
//!
//! See the [`pallet`] module for more information about the interfaces this pallet exposes,
//! including its configuration trait, dispatchables, storage items, events and errors.
//!
//! ## Overview
//!
//! The Oracle pallet enables blockchain applications to access real-world data through a
//! decentralized network of trusted data providers. It's designed to be flexible and can handle
//! various types of external data such as cryptocurrency prices, weather data, sports scores, or
//! any other off-chain information that needs to be brought on-chain.
//!
//! The pallet operates on a permissioned model where only authorized oracle operators can submit
//! data. This ensures data quality and prevents spam while maintaining decentralization through
//! multiple independent operators. The system aggregates data from multiple sources using
//! configurable algorithms, typically taking the median to resist outliers and manipulation
//! attempts.
```
