## Analysis: Analogous accounting-comparison DoS in Raydium's `calc_take_pnl`

The reported Flatcoin bug is a class of vulnerability where an accounting function's boundary comparison is written incorrectly, so that instead of gracefully clamping/handling an edge case, it unconditionally reverts — and because that function is a mandatory step in essentially every core state-changing instruction, the entire protocol becomes permanently bricked. I looked for the same bug class (a comparison whose failure branch hard-reverts a value that should instead be handled gracefully, in a function invoked by every deposit/withdraw/pnl instruction) in the Raydium AMM program, and found a structurally analogous pattern in `calc_take_pnl`.

### Title
Hard-revert invariant check in `calc_take_pnl` permanently DoSes Deposit/Withdraw/WithdrawPnl once the live pool invariant dips below the cached `calc_pnl_x * calc_pnl_y` - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` requires the live product of vault reserves to be `>=` the cached product of `target_orders.calc_pnl_x * calc_pnl_y` before it will compute PnL; if that ever fails, it returns `Err(AmmError::CalcPnlError)` instead of handling the case, and this function is an unconditional `?`-chained step inside `process_deposit`, `process_withdraw` (except in `WithdrawOnly` status), and `process_withdrawpnl`.

### Finding Description
`calc_take_pnl` gates its whole computation on: [1](#0-0) 
If `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount` (i.e. the live invariant computed from current vault balances falls below the previously cached invariant stored in `target_orders.calc_pnl_x`/`calc_pnl_y`), the function does not attempt to gracefully resolve/clamp the situation — it hard-fails: [2](#0-1) 

`calc_pnl_x`/`calc_pnl_y` are running, decimal-normalized checkpoints of the pool's reserves that get updated after every deposit and withdraw via `normalize_decimal_v2`/`restore_decimal` round-trips: [3](#0-2) [4](#0-3) 

Because `normalize_decimal`/`restore_decimal` perform floor-division decimal conversions, each deposit/withdraw round-trip can lose precision, and the running checkpoint (`calc_pnl_x`/`calc_pnl_y`) can drift out of sync with what a subsequent, freshly-computed live invariant (`pool_pc_amount * pool_coin_amount`, from raw un-normalized vault balances) will produce. There is no tolerance/clamping in this comparison — unlike a correctly designed version that should clamp `delta_x`/`delta_y` to 0 and continue when the pool has "lost" value relative to the checkpoint (analogous to Flatcoin's documented intent to clamp `marginDepositedTotal` to 0 rather than revert).

`calc_take_pnl` is called, unconditionally propagating its error via `?`, from every liquidity-mutating instruction:
- `process_deposit`: [5](#0-4) 
- `process_withdraw` (whenever status isn't `WithdrawOnly`): [6](#0-5) 
- `process_withdrawpnl`: [7](#0-6) 

### Impact Explanation
Once the live-vs-cached invariant comparison fails even once, `Deposit`, `Withdraw`, and `WithdrawPnl` all permanently revert with `AmmError::CalcPnlError`, because none of these call sites catch or recover from the error — they all propagate it with `?`. Since `target_orders.calc_pnl_x`/`calc_pnl_y` is only ever mutated by these same instructions (there is no reset/repair path reachable by an unprivileged user), the pool would become permanently stuck: LPs can no longer withdraw their principal via `Withdraw`, cannot deposit, and the `pnl_owner` cannot sweep accrued PnL — a permanent freeze of LP funds inside the vaults.

### Likelihood Explanation
This requires the accumulated floor-rounding error across `normalize_decimal_v2`/`restore_decimal` round trips (driven purely by ordinary deposit/withdraw traffic from unprivileged LPs) to eventually push the live invariant below the stored checkpoint by even one base unit. Given enough deposit/withdraw volume/precision loss (more likely on pools with large `native_decimal` vs `sys_decimal_value` mismatches), this boundary condition becomes reachable without any privileged or malicious action — an ordinary sequence of deposits/withdraws from regular users is sufficient to trigger it.

### Recommendation
Do not hard-revert when `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount`. Instead, treat this branch the way Flatcoin's fix treats the analogous underflow case: skip/clamp the PnL extraction (set `delta_x = delta_y = 0`, and reset/clamp `target_orders.calc_pnl_x`/`calc_pnl_y` to the live invariant) and continue processing the deposit/withdraw instead of returning `AmmError::CalcPnlError`.

### Proof of Concept
1. Repeated `Deposit`/`Withdraw` calls by ordinary LPs, each round-tripping amounts through `Calculator::normalize_decimal_v2` → `Calculator::restore_decimal` (both floor-dividing), incrementally desynchronizes `target_orders.calc_pnl_x * calc_pnl_y` from the true reserve product.
2. Eventually a `Deposit` or `Withdraw` call computes `total_pc_without_take_pnl * total_coin_without_take_pnl` (from live, un-normalized vault balances) that is strictly less than `restore_decimal(calc_pnl_x) * restore_decimal(calc_pnl_y)`.
3. `calc_take_pnl` hits the `else` branch at `program/src/processor.rs:267-278` and returns `AmmError::CalcPnlError`, which bubbles up through `?` in `process_deposit`/`process_withdraw`/`process_withdrawpnl`.
4. From this point on, every `Deposit`, `Withdraw`, and `WithdrawPnl` transaction on this pool reverts, since `calc_pnl_x`/`calc_pnl_y` can only be updated by those same (now-broken) instructions — permanently freezing LP funds in the coin/pc vaults.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L267-278)
```rust
        } else {
            msg!(arrform!(
                LOG_SIZE,
                "calc_take_pnl error x:{}, y:{}, calc_pnl_x:{}, calc_pnl_y:{}",
                x1,
                y1,
                identity(target.calc_pnl_x),
                identity(target.calc_pnl_y)
            )
            .as_str());
            return Err(AmmError::CalcPnlError.into());
        }
```

**File:** program/src/processor.rs (L1166-1173)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1352-1371)
```rust
        target_orders.calc_pnl_x = x1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```

**File:** program/src/processor.rs (L1495-1502)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1740-1749)
```rust
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

**File:** program/src/processor.rs (L1818-1838)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```
