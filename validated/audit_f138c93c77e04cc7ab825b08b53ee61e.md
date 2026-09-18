## Title
Division-by-zero panic in `calc_take_pnl`/`calc_x_power` on a fully-drained pool freezes `Deposit`/`Withdraw`/`WithdrawPnl` - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
The free5GC UDM CVE-2025-69252 is a NULL pointer dereference: an unauthenticated, attacker-influenced value (`ueId`) reaches a lookup/dereference path that was never validated for the "not found / empty" case, panicking the service. Raydium's `calc_take_pnl` pnl-rebalancing routine has the same bug class in Rust form: it performs `checked_div(...).unwrap()` on pool totals that can legitimately be zero (an emptied pool), and the code path that would reject a zero-liquidity pool (`amm.lp_amount == 0`) is checked *after* the panicking division, not before.

### Finding Description
`Processor::calc_take_pnl` normalizes the "before-pnl" snapshot (`target.calc_pnl_x`/`calc_pnl_y`) against the pool's current totals (`x1`, `y1`) and calls `Calculator::calc_x_power`: [1](#0-0) 

`calc_x_power` divides by `current_y` (the pool's normalized coin/pc total) with `.checked_div(current_y).unwrap()`, and `calc_take_pnl` itself later divides by `x1` again with `.checked_div(x1).unwrap()`: [2](#0-1) 

Neither `x1` nor `y1` is checked for zero before these divisions. In `process_deposit`, `x1`/`y1` are computed straight from the live vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook` and `normalize_decimal_v2`, and `calc_take_pnl` is invoked with them *before* the guard that rejects an empty pool: [3](#0-2) 

The `amm.lp_amount == 0` rejection only happens afterwards: [4](#0-3) 

The same ordering issue applies to `process_withdraw` and `process_withdrawpnl`, both of which call `calc_take_pnl` with `x1`/`y1` derived from live vault state: [5](#0-4) 

Any liquidity provider can permissionlessly withdraw 100% of the pool's LP supply via `Withdraw`, driving both vault balances (and `target_orders.calc_pnl_x`/`calc_pnl_y`, which are recomputed from the same totals) to zero while `amm.lp_amount` becomes 0 but the pool account itself is *not* reset to `Uninitialized`. Any subsequent `Deposit` (or `Withdraw`/`WithdrawPnl`) call against that now-empty pool computes `x1 = 0` and/or `y1 = 0`, and `calc_x_power`/`calc_take_pnl` then executes `checked_div(0).unwrap()`, which returns `None` and panics.

### Impact Explanation
A Solana program panic aborts the failing transaction, but because the on-chain state (`lp_amount == 0`, empty vaults, `target_orders.calc_pnl_x/y == 0`) persists permanently after the drain, *every* future `Deposit`, `Withdraw`, or `WithdrawPnl` instruction submitted against that pool will hit the same panicking division before ever reaching the `NotAllowZeroLP`/status checks that were meant to gracefully reject it. This permanently freezes the pool: it can never be refilled or have PnL settled again through the normal instruction set, matching the "permanent freezing of user or LP funds / pool accounting" impact bar. Remaining balances (e.g. any dust or accrued but unswept PnL fees still owed to the fee/PnL owner) become permanently unreachable through the standard instructions.

### Likelihood Explanation
Reaching this requires only a single permissionless `Withdraw` transaction that redeems 100% of a pool's LP supply — trivially possible for the pool creator immediately after `Initialize2` (before any other LP joins), or for any pool that a single LP fully controls. No privileged signer, leaked key, or off-chain component is needed; it is entirely reachable from a single submitted transaction with attacker-chosen accounts and data through the standard `Deposit`/`Withdraw` instructions.

### Recommendation
In `Processor::calc_take_pnl` and `Calculator::calc_x_power`, explicitly check `x1 != 0` and `current_y != 0` (and the equivalent divisors) before performing `checked_div`, returning a proper `AmmError` (e.g. `CalcPnlError`) instead of relying on `unwrap()`. Additionally, move the `amm.lp_amount == 0` check in `process_deposit` (and equivalent zero-liquidity checks in `process_withdraw`/`process_withdrawpnl`) to occur *before* `calc_take_pnl` is invoked, so an emptied pool is rejected gracefully rather than panicking.

### Proof of Concept
1. Call `Initialize2` to create a new pool; the initializing wallet receives 100% of the initial LP supply.
2. Immediately call `Withdraw` redeeming the entire LP balance, draining `amm_coin_vault`/`amm_pc_vault` to 0 and causing `target_orders.calc_pnl_x`/`calc_pnl_y` to be updated to 0 (via the same `calc_take_pnl` pnl-settlement logic at the end of `process_withdraw`), while `amm.lp_amount` becomes 0 (pool status is not reset to `Uninitialized`).
3. Submit a `Deposit` instruction against this now-empty pool with any nonzero `max_coin_amount`/`max_pc_amount`.
4. Inside `process_deposit`, `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are 0, so `x1`/`y1` normalize to 0; `calc_take_pnl` → `calc_x_power` executes `checked_div(0).unwrap()` and panics, aborting the transaction before the `amm.lp_amount == 0` guard is ever reached.
5. Every future `Deposit`/`Withdraw`/`WithdrawPnl` transaction against this pool reproduces the same panic, permanently freezing the pool.

### Citations

**File:** program/src/math.rs (L50-59)
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
```

**File:** program/src/processor.rs (L196-209)
```rust
            // let current_k: u128 = (x1 as u128).checked_mul(y1 as u128).unwrap();
            // current p is
            // let current_p: u128 = (x1 as u128).checked_div(y1 as u128).unwrap();
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
```

**File:** program/src/processor.rs (L1147-1173)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1179-1196)
```rust
        // let lp_mint  = Self::unpack_mint(&lp_mint_info, spl_token_program_id)?;
        if amm.lp_amount == 0 {
            encode_ray_log(DepositLog {
                log_type: LogType::Deposit.into_u8(),
                max_coin: deposit.max_coin_amount,
                max_pc: deposit.max_pc_amount,
                base: deposit.base_side,
                pool_coin: total_coin_without_take_pnl,
                pool_pc: total_pc_without_take_pnl,
                pool_lp: amm.lp_amount,
                calc_pnl_x: target_orders.calc_pnl_x,
                calc_pnl_y: target_orders.calc_pnl_y,
                deduct_coin: 0,
                deduct_pc: 0,
                mint_lp: 0,
            });
            return Err(AmmError::NotAllowZeroLP.into());
        }
```

**File:** program/src/processor.rs (L1466-1495)
```rust
        msg!(arrform!(
            LOG_SIZE,
            "withdrawpnl need_take_coin:{}, need_take_pc:{}",
            identity(amm.state_data.need_take_pnl_coin),
            identity(amm.state_data.need_take_pnl_pc)
        )
        .as_str());

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        msg!(arrform!(
            LOG_SIZE,
            "withdrawpnl total_pc:{}, total_coin:{}, x:{}, y:{}",
            total_pc_without_take_pnl,
            total_coin_without_take_pnl,
            x1,
            y1
        )
        .as_str());

        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
```
