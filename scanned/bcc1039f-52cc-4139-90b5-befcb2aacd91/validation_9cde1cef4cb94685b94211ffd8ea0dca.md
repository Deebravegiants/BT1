### Title
LP share (points) minting in `pallet-asset-conversion` derives from a raw, unprotected account balance that can be permissionlessly inflated by direct token transfers, causing under-minting / DoS of legitimate liquidity deposits - (File: `substrate/frame/asset-conversion/src/lib.rs`)

### Summary
The Opus report describes a vault (`gate.cairo`/`absorber.cairo`) that computes shares-per-asset using `asset.balance_of(vault_address)` instead of an internally tracked reserve variable, letting anyone permissionlessly inflate the "assets" side of the ratio via a plain token transfer, which distorts share issuance for later depositors. Searching the analogous share/points-accounting code in this repo, `pallet-nomination-pools` is **not** vulnerable to this class, because its `points_to_balance`/`balance_to_point` math is driven by `T::StakeAdapter::active_stake`, which reads the `StakingLedger.active` field maintained internally by `pallet-staking` (mutated only via `bond`/`bond_extra`/`unbond`/slashing), not by a raw account/currency balance query [1](#0-0) [2](#0-1) . A plain `transfer` of tokens into a pool's bonded account cannot move this value, so donation-style dilution is not reachable there.

`pallet-asset-conversion`, however, reproduces the same *pattern* the Opus report warns about: it computes pool "reserves" via a live balance read of the pool's sovereign account rather than an internally accounted variable, and uses that reserve directly in the share-minting formula.

### Finding Description
In `do_add_liquidity`, the reserves used to price a deposit and mint LP tokens are obtained with `Self::get_balance(&pool_account, asset)` — i.e., the *current spendable balance* of the pool's sovereign account for each asset: [3](#0-2) 

When the pool already has liquidity (`total_supply != 0`), the number of LP tokens minted to a depositor is:

```
side1 = amount1 * total_supply / reserve1
side2 = amount2 * total_supply / reserve2
lp_token_amount = min(side1, side2)
``` [4](#0-3) 

Because `reserve1`/`reserve2` are raw balances of the pool's sovereign account (an ordinary account, reachable by any `Assets::transfer` or `Balances::transfer`), any unprivileged user can inflate them by directly sending tokens to the pool account **without** calling `add_liquidity` and therefore **without** minting any LP tokens or increasing `total_supply`. This is the exact analog of Opus's `get_total_assets_helper` reading `asset.balance_of(gate_address)` [5](#0-4) .

The pallet's own test suite explicitly acknowledges that arbitrary balances can land in the pool account before/independent of `add_liquidity`: [6](#0-5) 

The only guardrails present are:
1. `MintMinLiquidity`, which protects strictly the *very first* depositor (pool creation) by locking a minimum LP amount to the pool account, analogous to Uniswap V2's `MINIMUM_LIQUIDITY` — this is a sufficient mitigation for the first-depositor case and is **not** broken.
2. A post-mint check `ensure!(lp_token_amount > T::MintMinLiquidity::get(), Error::<T>::InsufficientLiquidityMinted)` [7](#0-6) .
3. `amount1_min`/`amount2_min` slippage bounds on the *asset amounts contributed*.

Critically, there is **no minimum-LP-token-out parameter** in `add_liquidity`/`do_add_liquidity`. A caller can only bound the two asset amounts they contribute, not the number of LP tokens they receive in return. If an attacker inflates `reserve1` (or `reserve2`) between when a victim decides on their deposit amounts and when their extrinsic executes, the victim's minted `lp_token_amount` can be driven arbitrarily low relative to the value they contributed, with no on-chain mechanism to detect or reject that outcome (short of the coarse `MintMinLiquidity` floor check).

Because FRAME dispatchables roll back all storage mutations (including the `T::Assets::transfer` calls already executed inside `do_add_liquidity`) on an `Err` return, the worst-case single-block outcome when `lp_token_amount` floors to at or below `MintMinLiquidity` is a full-transaction revert (`InsufficientLiquidityMinted`), not silent asset loss. That still yields a concrete, unprivileged, low-cost **denial-of-service against `add_liquidity` for a targeted pool**: an attacker can transfer a comparatively large amount of the pool's assets directly to the pool's sovereign account (analogous to `pool_account` derivable via `PoolLocator::address`), inflating `reserve1`/`reserve2` so that legitimate depositors' `add_liquidity` calls with realistic amounts systematically round `lp_token_amount` down to ≤ `MintMinLiquidity` and revert, effectively locking new liquidity provision to that pool until someone deposits an impractically large, disproportionate amount.

I was not able to fully verify within the available time whether a *non-reverting* but still economically unfair mint (i.e., `lp_token_amount` still above `MintMinLiquidity` but materially below fair value, causing an actual value transfer to pre-existing LP holders as in the Opus PoC) is achievable in practice for realistic reserve/`MintMinLiquidity` ratios; that requires numeric modelling of `mul_div`'s floor-division error bound versus typical `MintMinLiquidity` values (100 in the referenced mock configs) that I could not complete before the iteration limit. The DoS vector, however, is directly reachable and provable from the code shown above.

### Impact Explanation
- Direct, reachable analog to the reported pattern: pool "reserves" are derived from a raw, externally-influenceable account balance rather than an internally tracked counter, exactly as flagged in the Opus report for `gate.cairo`/`absorber.cairo`.
- Concrete, provable impact: any unprivileged account can grief a specific liquidity pool, blocking further `add_liquidity` calls (or forcing depositors to contribute disproportionately large, economically unreasonable amounts) by donating tokens directly to the pool's sovereign account, without needing any special role or permission.
- Because FRAME's transactional dispatch rolls back the attempted deposit on `InsufficientLiquidityMinted`, this does not, by itself, directly steal victim funds the way the Opus PoC did — the primary confirmed impact here is availability/DoS-class rather than confirmed silent fund loss. Whether an unfair-but-passing mint (real value loss without revert) is achievable needs further quantitative analysis.

### Likelihood Explanation
High for the DoS variant: the pool's sovereign account address is deterministically derivable by any observer via `PoolLocator::address`, and a plain asset transfer to that account is available to any unprivileged user with no special preconditions, at the cost of the tokens donated (which remain in the pool, eventually benefiting existing/future LPs, so the "cost" to the attacker is bounded and could be as low as the marginal cost required to push `reserve` far enough above `total_supply` for a targeted pool with low existing liquidity, e.g. right after pool creation before it attracts real volume).

### Recommendation
- Track pool reserves as an internally maintained storage value updated only by `do_add_liquidity`/`do_remove_liquidity`/swap logic, instead of deriving them from a live balance query of the pool's sovereign account (mirroring the Opus fix recommendation of not using `balance_of`/`get_balance` for share pricing).
- If retaining balance-based reserves for compatibility, add an explicit `lp_token_min` (minimum LP tokens to mint) parameter to `add_liquidity`, giving depositors the same slippage protection on the LP-token side that `amount1_min`/`amount2_min` already give on the asset side.
- Consider adding a permissionless "sync"/"skim" extrinsic (as in Uniswap V2) that reconciles any balance beyond the tracked reserves into the reserve accounting fairly (e.g., pro-rata to existing LP holders) rather than allowing it to distort a single depositor's mint calculation.

### Proof of Concept
1. Attacker (or anyone) observes a target pool via `Pools::<T>` / derives its sovereign account with `T::PoolLocator::address(&pool_id)`.
2. Attacker transfers a large amount of `asset1` directly to that pool account using a standard `Assets::transfer` / `Balances::transfer` call — no interaction with `pallet-asset-conversion` extrinsics is required, and no LP tokens are minted, so `total_supply` (via `T::PoolAssets::total_issuance`) stays unchanged. This mirrors `add_tiny_liquidity_directly_to_pool_address` in the pallet's own test file [8](#0-7) , but with a value large enough (rather than "tiny") to dominate `reserve1`.
3. A legitimate user then calls `add_liquidity` with realistic `amount1_desired`/`amount2_desired`. `reserve1 = get_balance(pool_account, asset1)` reflects the attacker's donation [3](#0-2) , so `side1 = amount1 * total_supply / reserve1` rounds down; if it lands at or below `MintMinLiquidity`, the whole extrinsic reverts with `InsufficientLiquidityMinted` [4](#0-3) , denying the deposit.
4. Repeating step 2 with progressively larger donations keeps `add_liquidity` unusable for that pool for any depositor contributing "normal" amounts, at the attacker's cost of the donated tokens (which are not directly recoverable by the attacker since no LP tokens were minted to them).

### Citations

**File:** substrate/frame/nomination-pools/src/adapter.rs (L128-131)
```rust
	/// See [`StakingInterface::active_stake`].
	fn active_stake(pool_account: Pool<Self::AccountId>) -> Self::Balance {
		Self::CoreStaking::active_stake(&pool_account.0).unwrap_or_default()
	}
```

**File:** substrate/primitives/staking/src/lib.rs (L225-236)
```rust
	/// Returns the [`Stake`] of `who`.
	fn stake(who: &Self::AccountId) -> Result<Stake<Self::Balance>, DispatchError>;

	/// Total stake of a staker, `Err` if not a staker.
	fn total_stake(who: &Self::AccountId) -> Result<Self::Balance, DispatchError> {
		Self::stake(who).map(|s| s.total)
	}

	/// Total active portion of a staker's [`Stake`], `Err` if not a staker.
	fn active_stake(who: &Self::AccountId) -> Result<Self::Balance, DispatchError> {
		Self::stake(who).map(|s| s.active)
	}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L809-814)
```rust
			let pool = Pools::<T>::get(&pool_id).ok_or(Error::<T>::PoolNotFound)?;
			let pool_account =
				T::PoolLocator::address(&pool_id).map_err(|_| Error::<T>::InvalidAssetPair)?;

			let reserve1 = Self::get_balance(&pool_account, asset1.clone());
			let reserve2 = Self::get_balance(&pool_account, asset2.clone());
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L856-877)
```rust
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
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L890-892)
```rust

			Ok(lp_token_amount)
		}
```

**File:** substrate/frame/asset-conversion/src/tests.rs (L469-509)
```rust
#[test]
fn add_tiny_liquidity_directly_to_pool_address() {
	new_test_ext().execute_with(|| {
		let user = 1;
		let token_1 = NativeOrWithId::Native;
		let token_2 = NativeOrWithId::WithId(2);
		let token_3 = NativeOrWithId::WithId(3);

		create_tokens(user, vec![token_2.clone(), token_3.clone()]);
		assert_ok!(AssetConversion::create_pool(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone())
		));
		assert_ok!(AssetConversion::create_pool(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_3.clone())
		));

		let ed = get_native_ed();
		assert_ok!(Balances::force_set_balance(RuntimeOrigin::root(), user, 10000 * 2 + ed));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(user), 2, user, 1000));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(user), 3, user, 1000));

		// check we're still able to add the liquidity even when the pool already has some
		// token_1.clone()
		let pallet_account =
			<Test as Config>::PoolLocator::address(&(token_1.clone(), token_2.clone())).unwrap();
		assert_ok!(Balances::force_set_balance(RuntimeOrigin::root(), pallet_account, 1000));

		assert_ok!(AssetConversion::add_liquidity(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone()),
			10000,
			10,
			10000,
			10,
			user,
		));
```
