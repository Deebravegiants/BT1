### Title
Division-by-zero panic in `calc_take_pnl` permanently DoSes `Withdraw`/`WithdrawPnl` when pool reserves are drained to the take-pnl threshold - ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl` computes a new equilibrium point for the AMM's tracked PnL invariant by calling `Calculator::calc_x_power`, which divides by the *current* pool coin total (`current_y`) with an unchecked `.unwrap()` on `checked_div`. Neither `process_withdraw` nor `process_withdrawpnl` verify that the normalized pool totals (`x1`, `y1`) are non-zero before invoking `calc_take_pnl`. If swap activity (or the natural drift between `need_take_pnl_*` and vault balances) drives `total_coin_without_take_pnl` (or `total_pc_without_take_pnl`) down to the exact value tracked by `need_take_pnl_coin`/`need_take_pnl_pc`, the normalized total becomes `0`, and `calc_x_power`'s `checked_div(current_y).unwrap()` panics, aborting the transaction. This mirrors the reported bug class: a missing zero-guard on a value feeding a downstream operation that unconditionally executes and reverts, causing denial of service for a critical, time-sensitive user operation.

### Finding Description
`calc_take_pnl` is invoked unconditionally (except when `amm.status == WithdrawOnly`) from `process_withdraw` [1](#0-0)  and always from `process_withdrawpnl` [2](#0-1) . Both callers pass `x1`/`y1` derived directly from `Calculator::normalize_decimal_v2(total_pc_without_take_pnl, ...)` / `normalize_decimal_v2(total_coin_without_take_pnl, ...)` without checking they are non-zero.

Inside `calc_take_pnl`, when the `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` branch is taken, `Calculator::calc_x_power(target.calc_pnl_x, target.calc_pnl_y, x1, y1)` is called [3](#0-2) , and `calc_x_power` divides by `current_y` with no zero check: [4](#0-3) .

`total_coin_without_take_pnl` (and `total_pc_without_take_pnl`) is computed as `vault_amount - amm.state_data.need_take_pnl_coin` (or `_pc`) via `calc_total_without_take_pnl_no_orderbook` [5](#0-4) . Because ordinary swaps continuously shift vault balances relative to the fixed `need_take_pnl_*` counters, this difference can be driven to exactly `0` through normal (attacker-directed) swap activity without violating any other invariant/slippage check in `process_swap_base_in`/`process_swap_base_out` [6](#0-5) . Once that state is reached, any call into `process_withdraw` or `process_withdrawpnl` panics inside `calc_x_power`'s unchecked division, aborting the transaction — a program-level panic behaves as an unconditional revert of the entire instruction, functionally identical to the `InsufficientReward` revert in the original report.

### Impact Explanation
This blocks `Withdraw` and `WithdrawPnl` — the two paths through which LPs recover principal and the protocol owner extracts PnL — while the pool is in this state. An attacker can repeatedly re-create the zero-total condition via cheap swaps immediately before legitimate LPs attempt to withdraw, front-running and bricking withdrawals (a direct analog to the "frontrun to drain vault balance and brick the operation" scenario in the source report). Because the condition is a hard panic rather than a graceful error, it is also harder to work around on-chain (no simple "top-up 1 wei" mitigation applies here, since it requires restoring the exact reserve/pnl-tracking relationship). This qualifies as a Medium/High-severity DoS of user/LP fund withdrawal, a permitted analog category.

### Likelihood Explanation
Reaching `total_coin_without_take_pnl == 0` (or the pc equivalent) requires the vault's coin balance to equal `need_take_pnl_coin` exactly. `need_take_pnl_coin` only grows via prior PnL accrual events and is a fixed counter set by protocol PnL takes, while vault balances continuously change with every swap; an attacker with control over swap size (a standard unprivileged operation) can compute the exact `amount_in`/`amount_out` needed to hit this equality using the same on-chain-visible values (`amm_coin_vault.amount`, `amm.state_data.need_take_pnl_coin`), making this reachable in a single attacker-crafted transaction sequence.

### Recommendation
Guard `calc_take_pnl`/`calc_x_power` against zero denominators: return an explicit `AmmError` (e.g., `CalcPnlError` or a new zero-amount error) instead of panicking when `current_y` (or `current_x`) is `0`, mirroring the mitigation pattern from the source report (explicit zero check before the operation that would otherwise revert unconditionally).

### Proof of Concept
Conceptual sequence (not executed, derived from code reading):
1. Observe `amm.state_data.need_take_pnl_coin` and `amm_coin_vault.amount` for a target pool.
2. Submit a `SwapBaseIn`/`SwapBaseOut` (`PC2Coin` direction) with `amount_in`/`amount_out` chosen so that, post-swap, `amm_coin_vault.amount == amm.state_data.need_take_pnl_coin` exactly, driving `total_coin_without_take_pnl` to `0`.
3. Any subsequent call to `Withdraw` or `WithdrawPnl` computes `y1 = normalize_decimal_v2(0, ...) = 0`, then `calc_take_pnl` invokes `Calculator::calc_x_power(..., x1, y1)`, which executes `.checked_div(current_y).unwrap()` with `current_y == 0`, panicking and reverting the transaction — blocking all withdrawals until the attacker allows the imbalance to change (which the attacker can continue to prevent by repeating step 2).

### Citations

**File:** program/src/processor.rs (L199-204)
```rust
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
```

**File:** program/src/processor.rs (L1494-1502)
```rust
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

**File:** program/src/processor.rs (L1970-2048)
```rust
        let swap_fee = U128::from(swap.amount_in)
            .checked_mul(amm.fees.swap_fee_numerator.into())
            .unwrap()
            .checked_ceil_div(amm.fees.swap_fee_denominator.into())
            .unwrap();
        let swap_in_after_deduct_fee = U128::from(swap.amount_in).checked_sub(swap_fee).unwrap();
        let swap_amount_out = Calculator::swap_token_amount_base_in(
            swap_in_after_deduct_fee,
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        )
        .as_u64();
        encode_ray_log(SwapBaseInLog {
            log_type: LogType::SwapBaseIn.into_u8(),
            amount_in: swap.amount_in,
            minimum_out: swap.minimum_amount_out,
            direction: swap_direction as u64,
            user_source: user_source.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            out_amount: swap_amount_out,
        });
        if swap_amount_out < swap.minimum_amount_out {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_amount_out == 0 || swap.amount_in == 0 {
            return Err(AmmError::InvalidInput.into());
        }

        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap_amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_pc_vault to destination pc
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
            SwapDirection::PC2Coin => {
                if swap_amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source pc to amm_pc_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_coin_vault to destination coin
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
        };
        amm.recent_epoch = Clock::get()?.epoch;
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

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```
