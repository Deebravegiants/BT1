### Title
Front-runnable initial exchange-rate manipulation in `pallet_asset_conversion::do_add_liquidity` via pre-funding the deterministic pool account - (File: `substrate/frame/asset-conversion/src/lib.rs`)

### Summary
`pallet_asset_conversion` computes a pool's address deterministically from the asset pair (`T::PoolLocator::address`), exactly like the Spartan `Pool` contract in the referenced report. Because `do_add_liquidity` derives the amounts to actually transfer, and the resulting LP-token mint, from the pool account's *live on-chain balances* (`reserve1`/`reserve2`) rather than from an isolated internal ledger, an attacker who transfers assets directly into the pool's account between the `create_pool` extrinsic and the first `add_liquidity` extrinsic can dictate the effective exchange rate the legitimate liquidity provider ends up locking in — the same "front-run pool creation, seed extreme rate" pattern as the Spartan `createPoolADD` bug.

### Finding Description
`create_pool`/`do_create_pool` only registers the pool and touches the asset accounts for `asset1`/`asset2`/the LP token at the deterministic `pool_account`; it never asserts that the pool account's balances are zero before or after creation: [1](#0-0) 

Once the pool exists, any unprivileged account can transfer `asset1`/`asset2` directly to `pool_account` (it already has touched asset accounts), exactly as the Spartan attacker sent DAI/BNB to the pre-computed pool address. This is demonstrated by the pallet's own test, which sends tokens to the deterministically-computed pool account *before* the legitimate `add_liquidity` call lands: [2](#0-1) 

The crux of the analog vulnerability is in `do_add_liquidity`, which reads the pool account's *actual* asset balances as `reserve1`/`reserve2` and branches on whether they are already non-zero: [3](#0-2) 

- If an attacker donates only one of the two assets before the legitimate LP's `add_liquidity`, either `reserve1` or `reserve2` stays zero, so the "first branch" is taken and the depositor's own desired amounts are used for the transfer — but the donated tokens remain in the pool without being reflected in the LP token supply, permanently skewing the real reserve ratio away from what the depositor intended.
- If an attacker donates *both* assets (in the ratio they want) before the legitimate LP's `add_liquidity`, both `reserve1` and `reserve2` become non-zero, so `do_add_liquidity` takes the `quote()`-based branch (lines 821-843) and forces the legitimate LP's contribution to conform to the attacker-set ratio rather than the ratio the depositor originally intended to establish.

Meanwhile, the LP token minted for the "first liquidity" case is computed purely from the newly-transferred `amount1`/`amount2` (not from the full reserve including the attacker's donation): [4](#0-3) 

but subsequent swaps price against the pool's *actual* balances (`get_reserves`, used identically in `do_remove_liquidity`/swap paths): [5](#0-4) 

This is the same root cause as the Spartan report: price/rate at first liquidity provisioning is derived from the pool contract/account's actual balance, which is attacker-writable before the legitimate initializer's transaction executes, because the account address is deterministic and reachable by anyone once the pool is registered.

### Impact Explanation
An attacker can skew the effective exchange rate a newly created pool starts trading at, either by:
1. Forcing the legitimate LP to seed liquidity at an attacker-chosen ratio (quote-based branch), enabling the attacker to immediately arbitrage the mispriced pool via `swap_exact_tokens_for_tokens`, or
2. Donating unmatched assets that inflate the pool's real reserves without minting corresponding LP shares, permanently misallocating value between the legitimate LP and whoever swaps against the skewed reserve afterward.

This mirrors the Spartan report's "huge arbitrage space" impact — value is transferred from the legitimate pool creator/first LP to an attacker/arbitrageur at pool-bootstrap time.

### Likelihood Explanation
This requires `create_pool` and the first `add_liquidity` to be **separate, non-atomic extrinsics** so an attacker can insert a donation transaction between them (front-run the mempool). This is the pattern the pallet's own integration-test and benchmarking helpers use — `create_pool` followed later by a separate `add_liquidity` call — e.g.: [6](#0-5) 
If a runtime/dApp does not batch these two calls atomically (e.g., via `utility.batchAll`), the window for an unprivileged front-runner to pre-fund the deterministic `pool_account` exists on any parachain exposing this pallet in its runtime (e.g., Asset Hub). The pallet's existing `cannot_block_pool_creation` test only verifies that such donations don't block pool creation/liquidity provisioning — it does not verify the resulting exchange rate is unaffected, indicating the rate-manipulation angle was not the focus of the existing mitigation.

### Recommendation
- In `do_add_liquidity`, base the "first liquidity" branch decision and the initial LP mint calculation on `Pools::<T>::get(&pool_id)` / `PoolAssets::total_issuance` state alone (already used for the `total_supply.is_zero()` check) rather than on the pool account's live asset balances, or explicitly reconcile any pre-existing/donated balance into the LP-token accounting so donated tokens cannot silently skew the reserve ratio.
- Alternatively, require `create_pool` and the first `add_liquidity` (or `create_pool_with_fee`) to be combined into a single atomic call/extrinsic at the protocol level, or have `do_create_pool` capture/burn any pre-existing balance in `asset1`/`asset2` at `pool_account` before the first `add_liquidity` uses it as `reserve1`/`reserve2`.
- Consider emitting a warning/require `T::Assets::balance(asset, pool_account) == 0` for both assets inside `do_create_pool`, analogous to the recommended fix in the referenced report (`require balances == 0` before allowing pool initialization to proceed).

### Proof of Concept
1. Legitimate creator submits `create_pool(asset1, asset2)`. This registers the pool and touches `asset1`/`asset2` accounts at the deterministic `pool_account` (computed via `PoolLocator::address`).
2. Before the creator's follow-up `add_liquidity(amount1_desired, amount2_desired, ...)` extrinsic is included, an attacker observes the pool creation on-chain (address is fully deterministic and computable off-chain) and submits `Assets::transfer`/`Balances::transfer_allow_death` sending `asset1`/`asset2` directly to `pool_account` in whatever ratio benefits them — analogous to the `pallet_asset_conversion::tests::cannot_block_pool_creation` scenario at: [7](#0-6) 
3. When the creator's `add_liquidity` executes, `reserve1`/`reserve2` in `do_add_liquidity` are already non-zero from the attacker's donation, so the `quote()` branch runs and forces the creator's contribution ratio to match the attacker-controlled reserve ratio (lib.rs:818-843).
4. The attacker immediately calls `swap_exact_tokens_for_tokens` to arbitrage the pool at the rate they set, extracting value from the newly-seeded liquidity — replicating the Spartan `createPoolADD` front-run exactly.

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L741-774)
```rust
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

```

**File:** substrate/frame/asset-conversion/src/lib.rs (L809-844)
```rust
			let pool = Pools::<T>::get(&pool_id).ok_or(Error::<T>::PoolNotFound)?;
			let pool_account =
				T::PoolLocator::address(&pool_id).map_err(|_| Error::<T>::InvalidAssetPair)?;

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

**File:** substrate/frame/asset-conversion/src/lib.rs (L858-872)
```rust
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

**File:** substrate/frame/asset-conversion/src/lib.rs (L911-920)
```rust
			let pool_account =
				T::PoolLocator::address(&pool_id).map_err(|_| Error::<T>::InvalidAssetPair)?;
			let (reserve1, reserve2) = Self::get_reserves(asset1.clone(), asset2.clone())?;

			let total_supply = T::PoolAssets::total_issuance(pool.lp_token.clone());
			let withdrawal_fee_amount = T::LiquidityWithdrawalFee::get() * lp_token_burn;
			let lp_redeem_amount = lp_token_burn.saturating_sub(withdrawal_fee_amount);

			let amount1 = Self::mul_div(&lp_redeem_amount, &reserve1, &total_supply)?;
			let amount2 = Self::mul_div(&lp_redeem_amount, &reserve2, &total_supply)?;
```

**File:** substrate/frame/asset-conversion/src/tests.rs (L2334-2391)
```rust
#[test]
fn cannot_block_pool_creation() {
	new_test_ext().execute_with(|| {
		// User 1 is the pool creator
		let user = 1;
		// User 2 is the attacker
		let attacker = 2;

		let ed = get_native_ed();
		assert_ok!(Balances::force_set_balance(RuntimeOrigin::root(), attacker, 10000 + ed));

		// The target pool the user wants to create is Native <=> WithId(2)
		let token_1 = NativeOrWithId::Native;
		let token_2 = NativeOrWithId::WithId(2);

		// Attacker computes the still non-existing pool account for the target pair
		let pool_account =
			<Test as Config>::PoolLocator::address(&(token_1.clone(), token_2.clone())).unwrap();
		// And transfers the ED to that pool account
		assert_ok!(Balances::transfer_allow_death(
			RuntimeOrigin::signed(attacker),
			pool_account,
			ed
		));
		// Then, the attacker creates 14 tokens and sends one of each to the pool account
		for i in 10..25 {
			create_tokens(attacker, vec![NativeOrWithId::WithId(i)]);
			assert_ok!(Assets::mint(RuntimeOrigin::signed(attacker), i, attacker, 1000));
			assert_ok!(Assets::transfer(RuntimeOrigin::signed(attacker), i, pool_account, 1));
		}

		// User can still create the pool
		create_tokens(user, vec![token_2.clone()]);
		assert_ok!(AssetConversion::create_pool(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone())
		));

		// User has to transfer one WithId(2) token to the pool account (otherwise add_liquidity
		// will fail with `AssetTwoDepositDidNotMeetMinimum`)
		assert_ok!(Balances::force_set_balance(RuntimeOrigin::root(), user, 10000 + ed));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(user), 2, user, 10000));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(user), 2, pool_account, 1));

		// add_liquidity shouldn't fail because of the number of consumers
		assert_ok!(AssetConversion::add_liquidity(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone()),
			10000,
			100,
			10000,
			10,
			user,
		));
	});
}
```

**File:** cumulus/parachains/integration-tests/emulated/common/src/pools.rs (L33-55)
```rust
				assert_ok!(<$chain as [<$chain Pallet>]>::AssetConversion::create_pool(
					signed_owner.clone(),
					Box::new(native_location.clone()),
					Box::new($asset_id.clone()),
				));

				assert_expected_events!(
					$chain,
					vec![
						RuntimeEvent::AssetConversion($crate::pools::pallet_asset_conversion::Event::PoolCreated { .. }) => {},
					]
				);

				assert_ok!(<$chain as [<$chain Pallet>]>::AssetConversion::add_liquidity(
					signed_owner,
					Box::new(native_location),
					Box::new($asset_id),
					$wnd_amount,
					$asset_amount,
					0,
					0,
					owner.into()
				));
```
