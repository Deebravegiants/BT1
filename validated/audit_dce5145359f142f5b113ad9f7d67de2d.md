### Title
Division-by-zero panic in `InvariantPool`/`InvariantToken` share-conversion helpers used by Deposit/Withdraw - (File: `program/src/math.rs`)

### Summary
The LP-share conversion helpers `InvariantPool::exchange_pool_to_token`, `InvariantPool::exchange_token_to_pool`, `InvariantToken::exchange_coin_to_pc`, and `InvariantToken::exchange_pc_to_coin` all perform `checked_div(...).unwrap()` on a denominator derived from mutable, user/market-influenced pool state (`amm.lp_amount`, `total_coin_without_take_pnl`, `total_pc_without_take_pnl`). None of the call sites in `Processor::process_deposit` / `process_withdraw` validate that these denominators are non-zero before invoking the conversion, unlike the analogous `NativeTokenToStkXPRT`/`StkXPRTToNativeToken` issue in the external report, where the fix was to add an explicit zero-denominator guard (mirroring the `MintRate` pattern).

### Finding Description
`InvariantPool::exchange_pool_to_token` / `exchange_token_to_pool` divide by `self.token_total`: [1](#0-0) 

`InvariantToken::exchange_coin_to_pc` / `exchange_pc_to_coin` divide by `self.token_coin` / `self.token_pc`: [2](#0-1) 

In `process_deposit`, the only zero-guard present is on `amm.lp_amount`: [3](#0-2) 

but `total_coin_without_take_pnl` / `total_pc_without_take_pnl` — the denominators used moments later by `InvariantToken::exchange_coin_to_pc`/`exchange_pc_to_coin` and by `InvariantPool::exchange_token_to_pool` (via `token_total: total_coin_without_take_pnl` / `total_pc_without_take_pnl`) — are never checked for zero: [4](#0-3) 

These totals are computed as vault balance minus `need_take_pnl_*`, and are further reduced in-place by `calc_take_pnl` (which subtracts an accumulated PnL delta from `total_pc_without_take_pnl`/`total_coin_without_take_pnl` right before the division): [5](#0-4) [6](#0-5) 

If either `total_coin_without_take_pnl` or `total_pc_without_take_pnl` reaches exactly zero at the point `InvariantToken`/`InvariantPool` is constructed (e.g., a pool driven into a heavily imbalanced state through swap activity and PnL accrual, while `amm.lp_amount` is still non-zero), `checked_div` returns `None` and the subsequent `.unwrap()` panics, aborting the transaction with a Rust runtime panic rather than a handled `ProgramError`.

### Impact Explanation
A Rust panic inside `process_deposit`/`process_withdraw` unwinds through the `entrypoint`, causing an unrecoverable failure of the transaction (denial-of-service for that specific pool's Deposit/Withdraw instruction), exactly matching the class of bug described in the report (panic-based DoS from an unguarded `checked_div().unwrap()` on a zero denominator). Every future Deposit attempt on such a pool would panic, preventing LPs from adding liquidity, which is a High-severity availability impact on a core AMM operation (not merely a compute-only or best-practice issue).

### Likelihood Explanation
Reaching the exact zero-denominator state requires the pool's net coin or pc total (after PnL deduction) to hit zero while `amm.lp_amount` remains non-zero. `calc_take_pnl`'s delta is bounded by `pnl_numerator/pnl_denominator` of the price-divergence amount from the last recorded `target.calc_pnl_x/y` checkpoint, so driving a side fully to zero in one shot is not trivial — it would generally require multiple prior transactions (heavy one-sided swaps followed by repeated deposit/withdraw calls that ratchet `need_take_pnl_*` upward) to push a pool into this edge state. All of these steps use only permissionless, unprivileged instructions (`SwapBaseIn`/`SwapBaseOut`, `Deposit`) with attacker-controlled accounts, so the precondition is reachable without any privileged signer, though it is state-dependent rather than a single-transaction, single-call trigger. This yields a moderate (not trivial) likelihood, consistent with a Medium/High rating for an availability bug rather than a routinely hit path.

### Recommendation
In `InvariantPool::exchange_pool_to_token`/`exchange_token_to_pool` and `InvariantToken::exchange_coin_to_pc`/`exchange_pc_to_coin`, replace the unconditional `.checked_div(...).unwrap()` calls with proper zero-checks that return `None` (already the function's `Option` return type supports this) when the denominator (`token_total`, `token_coin`, `token_pc`) is zero, and ensure callers surface this as `AmmError::CalculationExRateFailure` instead of panicking — mirroring the `MintRate`-style zero-denominator guard recommended in the reference report.

### Proof of Concept
1. Initialize a pool via `Initialize2` with a modest initial coin/pc ratio.
2. Execute a sequence of permissionless `SwapBaseIn`/`SwapBaseOut` transactions that heavily skew the coin:pc ratio (e.g., swap almost the entire coin side out for pc, or vice versa), without any intervening `Deposit`/`Withdraw` to "checkpoint" `target_orders.calc_pnl_x/y`.
3. Call `Deposit` (`process_deposit`): `calc_take_pnl` is invoked with a large price divergence since the last checkpoint, causing a large `pc_pnl_amount`/`coin_pnl_amount` to be subtracted from `total_pc_without_take_pnl`/`total_coin_without_take_pnl` [7](#0-6) 
   If this drives the resulting total to zero on the side used as the divisor of `InvariantToken::exchange_coin_to_pc`/`exchange_pc_to_coin` [8](#0-7) 
   the subsequent `.checked_div(self.token_coin.into()).unwrap()` (or `token_pc`) call panics [9](#0-8) 
   aborting the transaction and blocking further deposits on that pool.

### Citations

**File:** program/src/math.rs (L378-423)
```rust
impl InvariantToken {
    /// Exchange rate
    pub fn exchange_coin_to_pc(
        &self,
        token_coin: u64,
        round_direction: RoundDirection,
    ) -> Option<u64> {
        Some(if round_direction == RoundDirection::Floor {
            U128::from(token_coin)
                .checked_mul(self.token_pc.into())
                .unwrap()
                .checked_div(self.token_coin.into())
                .unwrap()
                .as_u64()
        } else {
            U128::from(token_coin)
                .checked_mul(self.token_pc.into())
                .unwrap()
                .checked_ceil_div(self.token_coin.into())
                .unwrap()
                .as_u64()
        })
    }

    /// Exchange rate
    pub fn exchange_pc_to_coin(
        &self,
        token_pc: u64,
        round_direction: RoundDirection,
    ) -> Option<u64> {
        Some(if round_direction == RoundDirection::Floor {
            U128::from(token_pc)
                .checked_mul(self.token_coin.into())
                .unwrap()
                .checked_div(self.token_pc.into())
                .unwrap()
                .as_u64()
        } else {
            U128::from(token_pc)
                .checked_mul(self.token_coin.into())
                .unwrap()
                .checked_ceil_div(self.token_pc.into())
                .unwrap()
                .as_u64()
        })
    }
```

**File:** program/src/math.rs (L440-455)
```rust
        Some(if round_direction == RoundDirection::Floor {
            U128::from(token_total_amount)
                .checked_mul(self.token_input.into())
                .unwrap()
                .checked_div(self.token_total.into())
                .unwrap()
                .as_u64()
        } else {
            U128::from(token_total_amount)
                .checked_mul(self.token_input.into())
                .unwrap()
                .checked_ceil_div(self.token_total.into())
                .unwrap()
                .as_u64()
        })
    }
```

**File:** program/src/processor.rs (L228-262)
```rust
            let diff_pc_pnl_amount =
                Calculator::restore_decimal(diff_x, amm.pc_decimals, amm.sys_decimal_value);
            let diff_coin_pnl_amount =
                Calculator::restore_decimal(diff_y, amm.coin_decimals, amm.sys_decimal_value);
            let pc_pnl_amount = diff_pc_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            let coin_pnl_amount = diff_coin_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            if pc_pnl_amount != 0 && coin_pnl_amount != 0 {
                amm.state_data.need_take_pnl_pc = amm
                    .state_data
                    .need_take_pnl_pc
                    .checked_add(pc_pnl_amount)
                    .unwrap();
                amm.state_data.need_take_pnl_coin = amm
                    .state_data
                    .need_take_pnl_coin
                    .checked_add(coin_pnl_amount)
                    .unwrap();

                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
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

**File:** program/src/processor.rs (L1200-1250)
```rust
        if deposit.base_side == 0 {
            // base coin
            deduct_pc_amount = invariant
                .exchange_coin_to_pc(deposit.max_coin_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_coin_amount = deposit.max_coin_amount;
            if deduct_pc_amount > deposit.max_pc_amount {
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
                    deduct_coin: deduct_coin_amount,
                    deduct_pc: deduct_pc_amount,
                    mint_lp: 0,
                });
                return Err(AmmError::ExceededSlippage.into());
            }
            // base coin, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_pc_amount < deposit.other_amount_min.unwrap() {
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
                        deduct_coin: deduct_coin_amount,
                        deduct_pc: deduct_pc_amount,
                        mint_lp: 0,
                    });
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```
