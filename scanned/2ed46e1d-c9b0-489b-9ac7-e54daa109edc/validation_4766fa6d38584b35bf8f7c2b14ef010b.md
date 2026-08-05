### Title
Liquidity provider deposits into `pallet-asset-conversion` are not validated against the actual amount credited, allowing under-collateralized LP token minting — ([File: substrate/frame/asset-conversion/src/lib.rs])

### Summary
`Pallet::do_add_liquidity` in `pallet-asset-conversion` transfers `amount1`/`amount2` from the liquidity provider into the pool account via `T::Assets::transfer(...)` but never checks the value the call actually returns. It then mints LP tokens using the *requested* `amount1`/`amount2` values rather than the amount the pool account actually received. This is the structural analog of the "deflationary token" bug in the external report: crediting a user's accounting entry based on the amount *requested* to be moved instead of the amount *actually* moved.

### Finding Description
In `do_add_liquidity`: [1](#0-0) 
the pallet calls `T::Assets::transfer(asset1, who, &pool_account, amount1, Preserve)?;` and `T::Assets::transfer(asset2, who, &pool_account, amount2, Preserve)?;` and discards the `Ok(actual_amount)` return value, then computes `lp_token_amount` purely from the requested `amount1`/`amount2`.

The `fungibles::Mutate::transfer` default implementation is best-effort by construction: it calls `decrease_balance(..., BestEffort, preservation, Polite)` on the source and `increase_balance(..., BestEffort)` on the destination: [2](#0-1) 
`BestEffort` precision means that if the full `amount` cannot be moved (e.g., because the source account's *reducible* balance is lower than `amount` due to holds/freezes/locks from another pallet, or because of existential-deposit dust handling), the function silently transfers less than requested and returns that lesser value — it does not error.

Critically, `pallet-assets`' own low-level documentation for the analogous `do_transfer` function explicitly states this contract: [3](#0-2) 
"Returns the actual amount placed into `dest`... Exact semantics are determined by the flags `f`." The codebase is aware that requested and actual transferred amounts can diverge — indeed, `pallet-asset-conversion-ops`'s pool-account-migration logic explicitly guards against this exact scenario: [4](#0-3) 
by asserting `balance1 == T::Assets::transfer(...)` and erroring with `Error::<T>::PartialTransfer` if the actual transferred amount doesn't match. `do_add_liquidity` and `do_remove_liquidity` in the core `pallet-asset-conversion` do not apply this same defensive check.

`do_remove_liquidity` has the analogous but generally self-inflicted issue on the withdrawal side (transfers computed `amount1`/`amount2` to `withdraw_to` without verifying the delivered amount): [5](#0-4) 

### Impact Explanation
If any asset registered as `T::AssetKind` in a deployment's pool can, under some circumstance, deliver less than the requested `amount` on transfer (e.g., an account with an active `hold`/`freeze` reducing its reducible balance, or an asset implementation with non-trivial `Freezer`/`Holder` hooks), `do_add_liquidity` will mint LP tokens computed from the nominal `amount1`/`amount2` even though the pool account actually received less. This under-collateralizes the pool relative to the LP token supply, silently diluting the redeemable value of all other liquidity providers' LP tokens — an accounting/state-transition defect directly analogous to the deflationary-token issue in the report (crediting a "requested" amount instead of the "received" amount).

### Likelihood Explanation
This is difficult to trigger with the pallet's standard, unmodified `pallet-assets`/`pallet-balances` implementations, because normal token transfers there do not have a fee-on-transfer mechanism comparable to an ERC-20 deflationary token, and `can_withdraw`/`can_deposit` pre-checks are performed before the transfer. The realistic trigger vector would require a source account whose *reducible* balance is lower than its *free* balance at call time (via holds/freezes from a separate pallet interacting with the same asset), causing `BestEffort` to silently short the transfer. I was not able to fully verify, within the available tool budget, whether `can_withdraw`'s pre-check (`Preservation::Preserve` requires "extra" to succeed) would already reject such a scenario before `decrease_balance` is reached, which is necessary to establish a concretely reachable, unprivileged attacker path. This uncertainty, combined with the requirement of a non-trivial hold/freeze configuration coexisting with the asset-conversion pool asset, makes the likelihood uncertain and possibly low without further verification of `WithdrawConsequence::into_result` semantics in `substrate/frame/support/src/traits/tokens/misc.rs` (not confirmed here due to tool-call exhaustion).

### Recommendation
Mirror the defensive pattern already used in `pallet-asset-conversion-ops` (`substrate/frame/asset-conversion/ops/src/lib.rs:209-243`): capture the actual amount returned by each `T::Assets::transfer` call in `do_add_liquidity` and `do_remove_liquidity`, and either (a) fail the extrinsic (e.g., a new `PartialTransfer` error) if it doesn't match the intended `amount1`/`amount2`, or (b) base all downstream LP-token-minting/reserve math strictly on the actual transferred amounts rather than the requested ones.

### Proof of Concept
Could not be constructed with certainty within the available investigation budget — a concrete PoC requires confirming that `Preservation::Preserve` + `can_withdraw` in `substrate/frame/support/src/traits/tokens/fungible(s)/regular.rs` permits reaching `decrease_balance`'s `BestEffort` short-transfer path with an unprivileged account holding a partial lock/freeze on the relevant asset. This should be verified directly against `WithdrawConsequence`/`into_result` before treating this as a confirmed, reproducible exploit rather than a code-quality/defense-in-depth gap.

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L855-892)
```rust
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

			ensure!(
				lp_token_amount > T::MintMinLiquidity::get(),
				Error::<T>::InsufficientLiquidityMinted
			);

			T::PoolAssets::mint_into(pool.lp_token.clone(), mint_to, lp_token_amount)?;

			Self::deposit_event(Event::LiquidityAdded {
				who: who.clone(),
				mint_to: mint_to.clone(),
				pool_id,
				amount1_provided: amount1,
				amount2_provided: amount2,
				lp_token: pool.lp_token,
				lp_token_minted: lp_token_amount,
			});

			Ok(lp_token_amount)
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L941-965)
```rust
			// burn the provided lp token amount that includes the fee
			T::PoolAssets::burn_from(
				pool.lp_token.clone(),
				who,
				lp_token_burn,
				Expendable,
				Exact,
				Polite,
			)?;

			T::Assets::transfer(asset1, &pool_account, withdraw_to, amount1, Expendable)?;
			T::Assets::transfer(asset2, &pool_account, withdraw_to, amount2, Expendable)?;

			Self::deposit_event(Event::LiquidityRemoved {
				who: who.clone(),
				withdraw_to: withdraw_to.clone(),
				pool_id,
				amount1,
				amount2,
				lp_token: pool.lp_token,
				lp_token_burned: lp_token_burn,
				withdrawal_fee: T::LiquidityWithdrawalFee::get(),
			});

			Ok((amount1, amount2))
```

**File:** substrate/frame/support/src/traits/tokens/fungibles/regular.rs (L366-386)
```rust
	fn transfer(
		asset: Self::AssetId,
		source: &AccountId,
		dest: &AccountId,
		amount: Self::Balance,
		preservation: Preservation,
	) -> Result<Self::Balance, DispatchError> {
		let _extra = Self::can_withdraw(asset.clone(), source, amount)
			.into_result(preservation != Expendable)?;
		Self::can_deposit(asset.clone(), dest, amount, Extant).into_result()?;
		if source == dest {
			return Ok(amount);
		}

		Self::decrease_balance(asset.clone(), source, amount, BestEffort, preservation, Polite)?;
		// This should never fail as we checked `can_deposit` earlier. But we do a best-effort
		// anyway.
		let _ = Self::increase_balance(asset.clone(), dest, amount, BestEffort);
		Self::done_transfer(asset, source, dest, amount);
		Ok(amount)
	}
```

**File:** substrate/frame/assets/src/functions.rs (L623-631)
```rust
	/// Reduces the asset `id` balance of `source` by some `amount` and increases the balance of
	/// `dest` by (similar) amount.
	///
	/// Returns the actual amount placed into `dest`. Exact semantics are determined by the flags
	/// `f`.
	///
	/// Will fail if the amount transferred is so small that it cannot create the destination due
	/// to minimum balance requirements.
	pub fn do_transfer(
```

**File:** substrate/frame/asset-conversion/ops/src/lib.rs (L209-219)
```rust
			ensure!(
				balance1 ==
					T::Assets::transfer(
						asset1.clone(),
						&prior_account,
						&new_account,
						balance1,
						Preservation::Expendable,
					)?,
				Error::<T>::PartialTransfer
			);
```
