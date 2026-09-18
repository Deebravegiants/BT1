### Title
Unhandled panic (`attempt to subtract with overflow`) in `calc_take_pnl` reachable from the unprivileged `Withdraw` instruction can permanently freeze LP funds - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` uses an outer sanity check computed on **native-decimal** token amounts to decide whether it is safe to enter a branch that performs unchecked subtractions on **sys-decimal-normalized** amounts. Because decimal normalization (`normalize_decimal_v2`/`restore_decimal`) truncates rather than rounds, the two representations are not guaranteed to stay monotonically consistent, so the outer guard can pass while the inner invariant it is supposed to protect (`current_x >= x2`, `current_y >= y2`) does not hold. This causes `checked_sub(...).unwrap()` to panic on `None`, which is functionally the same failure class as the referenced "attempt to subtract with overflow" bug. `calc_take_pnl` is invoked from the unprivileged `Withdraw` instruction, so any LP withdrawal that lands on this edge case reverts, and because the pool state that produced the mismatch is never advanced by a reverted transaction, subsequent withdrawals hit the same panic — permanently freezing LP principal in the vaults.

### Finding Description
`calc_take_pnl` gates its pnl-taking branch with a comparison done in native token units: [1](#0-0) 

Once inside the branch, it recomputes `x2`/`y2` in sys-decimal-normalized units via `calc_x_power` and then unconditionally subtracts: [2](#0-1) 

`calc_x_power` performs `last_x * last_y * current_x / current_y` in `U256` with truncating integer division: [3](#0-2) 

The values fed into this computation (`x1`, `y1`, and the stored `target.calc_pnl_x`/`calc_pnl_y`) are produced by `normalize_decimal_v2`/`restore_decimal`, which truncate on every conversion rather than round: [4](#0-3) 

Because the outer gate (line 190-192) is evaluated on native-decimal vault/target amounts while the actual subtraction operates on independently-truncated normalized amounts, the two do not have to agree bit-for-bit — truncation loss accumulated across `coin_decimals`/`pc_decimals` vs `sys_decimal_value` conversions can make `x2 > current_x` (or `y2 > current_y`) even though the outer check passed, triggering the `unwrap()` panic on the `checked_sub` at line 213/214.

This function is reached from the unprivileged `Withdraw` instruction (any LP holder, no special signer) whenever the pool is not in `WithdrawOnly` status: [5](#0-4) 

### Impact Explanation
A panic inside `calc_take_pnl` aborts the withdraw transaction (Solana reverts all state changes), so no funds move — but since the transaction is rolled back, the on-chain state (target orders `calc_pnl_x`/`calc_pnl_y`, vault balances) that produced the mismatch is unchanged. Any LP attempting to withdraw afterward hits the identical computation and the identical panic. This effectively creates a permanent denial-of-service for the `Withdraw` instruction on that pool, locking all LP principal in the vaults with no code path to recover it (the only other consumer, `process_withdrawpnl`, is restricted to the privileged `pnl_owner` and out of scope). This matches the "permanent freezing of user or LP funds" impact category.

### Likelihood Explanation
Triggering the mismatch requires the pool's vault balances and `target_orders.calc_pnl_x/calc_pnl_y` to drift into a state where native-unit and normalized-unit representations disagree by enough truncation error to flip the strict inequality needed by `calc_x_power`'s output relative to `current_x`/`current_y`. This is most plausible for token pairs with divergent `coin_decimals`/`pc_decimals` relative to `sys_decimal_value`, and it can be reached purely through ordinary sequences of swaps/withdrawals over time (all attacker-observable, no privileged accounts needed) — an attacker can also actively drive the pool toward this state via chosen swap sizes designed to maximize truncation loss before calling `Withdraw`. The condition is data-dependent rather than guaranteed on every call, so likelihood is assessed as Medium rather than High.

### Recommendation
Replace the unchecked `unwrap()` calls in `calc_take_pnl` (`math.rs`/`processor.rs` `checked_sub(...).unwrap()` on `x1`/`x2` and `y1`/`y2`) with `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?` or `saturating_sub` (clamping delta to zero and skipping the pnl transfer) so that a truncation-induced mismatch degrades gracefully instead of permanently reverting all withdrawals. Additionally, align the outer gating comparison (native-decimal `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount`) with the actual units used inside the branch, or recompute both sides in the same (normalized) unit space to remove the truncation-induced inconsistency entirely.

### Proof of Concept
1. Create a pool with `coin_decimals` and `pc_decimals` that differ substantially from `sys_decimal_value` to maximize truncation loss in `normalize_decimal_v2`/`restore_decimal` round-trips.
2. Drive the pool through a sequence of swaps/withdrawals (all standard unprivileged instructions) that push `target_orders.calc_pnl_x`/`calc_pnl_y` and the vault balances into a state where the native-unit product check at `processor.rs:190-192` passes but the normalized-space quantities computed by `calc_x_power` (`math.rs:50-60`) yield `x2 > current_x` or `y2 > current_y`.
3. Call `Withdraw` as any LP holder; `Processor::calc_take_pnl` is invoked (`processor.rs:1741-1748`), enters the branch, and panics on `x1.checked_sub(x2).unwrap()` or `y1.checked_sub(y2).unwrap()` (`processor.rs:213-214`), reverting the transaction.
4. Because the underlying pool/target-orders state is unchanged (transaction reverted), every subsequent `Withdraw` call reproduces the same panic, permanently freezing LP funds in the vaults.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L199-214)
```rust
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
            // let x2 = Calculator::sqrt(x2_power).unwrap();
            let x2 = x2_power.integer_sqrt();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl x2_power:{}, x2:{}", x2_power, x2).as_str());
            let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl y2:{}", y2).as_str());

            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
```

**File:** program/src/processor.rs (L1737-1749)
```rust
        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }
```

**File:** program/src/math.rs (L50-60)
```rust
    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }
```

**File:** program/src/math.rs (L96-116)
```rust
    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }

    pub fn normalize_decimal_v2(val: u64, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = ret_mut
            .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        ret
    }
```
