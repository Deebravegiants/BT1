### Title
Unchecked division by zero reserve amounts in `InvariantToken`/`InvariantPool` during Deposit can permanently brick liquidity provisioning - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
`Processor::process_deposit` only guards against `amm.lp_amount == 0` before performing exchange-rate math, but never checks that `total_pc_without_take_pnl` or `total_coin_without_take_pnl` (the actual divisors used in the deposit math) are non-zero. If either reserve value can reach zero while `lp_amount` remains non-zero, the unguarded `checked_div(...).unwrap()` calls inside `InvariantToken`/`InvariantPool` panic, aborting the transaction and permanently disabling that side of `Deposit`, analogous to the `totalWeightLocked == 0` division-by-zero freeze described in the reference report.

### Finding Description
`process_deposit` builds an `InvariantToken` from the currently-computed reserves: [1](#0-0) 

It only checks `amm.lp_amount == 0` before proceeding, never checking whether `total_pc_without_take_pnl` or `total_coin_without_take_pnl` is zero: [2](#0-1) 

Depending on `deposit.base_side`, the code calls `exchange_coin_to_pc` / `exchange_pc_to_coin` on `InvariantToken`, and then `exchange_token_to_pool` on `InvariantPool` using `total_coin_without_take_pnl` / `total_pc_without_take_pnl` as the divisor (`token_total`): [3](#0-2) [4](#0-3) 

Both `InvariantToken::exchange_coin_to_pc`/`exchange_pc_to_coin` and `InvariantPool::exchange_token_to_pool` perform `checked_div(...).unwrap()` on the reserve value with no zero-check: [5](#0-4) [6](#0-5) 

`checked_div` returns `None` when the divisor is `0`, and `.unwrap()` on `None` panics, aborting the instruction. Unlike the `Withdraw` path — which explicitly rejects `withdraw.amount >= amm.lp_amount` so its divisor (`amm.lp_amount`) can never reach zero — the deposit path never validates that `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (which are derived every call from vault balances minus accrued PnL, see `Calculator::calc_total_without_take_pnl_no_orderbook` and `calc_take_pnl`) stay strictly positive: [7](#0-6) [8](#0-7) 

Since these reserve totals are recomputed from live vault balances on every instruction, if repeated legitimate `Withdraw`/`WithdrawPnl` operations (subject to floor-rounding in `InvariantPool::exchange_pool_to_token`) ever drive one side's vault balance down to exactly zero while `amm.lp_amount` remains non-zero, `Deposit` using that side as `base_side` becomes permanently unusable (panics every time), and even the alternate `base_side` produces `deduct_coin_amount`/`deduct_pc_amount == 0` and reverts with `InvalidInput`, so no further liquidity can be added to restore the pool.

### Impact Explanation
This falls under the same "loss of funds via permanent DoS of a core state-transition function" bug class as the reference finding: once one reserve total reaches zero, `Deposit` can never succeed again on that pool, permanently freezing the ability for LPs to add liquidity back and effectively bricking the pool's growth path while existing LP token holders are left holding a position tied to a reserve that cannot be restored through the normal deposit flow. This constitutes potential permanent freezing of protocol functionality for the affected pool.

### Likelihood Explanation
The precondition (one reserve reaching exactly zero while `lp_amount > 0`) requires an edge case of accumulated floor-rounding through many small legitimate `Withdraw`/`WithdrawPnl` calls or extreme token decimal/reserve ratios; it is not trivially triggerable in one transaction by an attacker, matching the "requires certain external conditions or specific states" pattern of the referenced medium-severity issue rather than a trivially/always-reachable bug.

### Recommendation
Before performing any exchange-rate division in `process_deposit` (and inside `InvariantToken`/`InvariantPool` methods generally), explicitly check that `total_pc_without_take_pnl` and `total_coin_without_take_pnl` (and any other divisor) are non-zero, returning a graceful error such as `AmmError::NotAllowZeroLP`/`CalculationExRateFailure` instead of relying on an unwrap-triggered panic, e.g.:
```rust
if total_pc_without_take_pnl == 0 || total_coin_without_take_pnl == 0 {
    return Err(AmmError::NotAllowZeroLP.into());
}
```

### Proof of Concept
1. Create a pool and let its reserves and `lp_amount` evolve through many legitimate `Withdraw` calls (each individually valid per the `withdraw.amount < amm.lp_amount` check).
2. Due to `RoundDirection::Floor` rounding in `InvariantPool::exchange_pool_to_token`, craft withdrawal amounts/timing such that `total_coin_without_take_pnl` (or `total_pc_without_take_pnl`) reaches exactly `0` in the vault while `amm.lp_amount` remains `> 0` (state passes the existing `amm.lp_amount == 0` guard).
3. Call `Deposit` with `base_side == 0` (base coin): `InvariantToken::exchange_coin_to_pc` divides by `self.token_coin == 0`, causing `checked_div(...).unwrap()` to panic and the instruction to always fail.
4. Call `Deposit` with `base_side == 1` (base pc): `exchange_pc_to_coin` computes `deduct_coin_amount = 0` (since `token_coin == 0`), and the subsequent check `deduct_coin_amount == 0` forces `Err(AmmError::InvalidInput)`.
5. Both deposit paths now permanently fail — the pool can never receive additional liquidity to recover the zeroed-out reserve side.

### Citations

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

**File:** program/src/processor.rs (L1174-1177)
```rust
        let invariant = InvariantToken {
            token_coin: total_coin_without_take_pnl,
            token_pc: total_pc_without_take_pnl,
        };
```

**File:** program/src/processor.rs (L1180-1196)
```rust
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

**File:** program/src/processor.rs (L1197-1250)
```rust
        let deduct_pc_amount;
        let deduct_coin_amount;
        let mint_lp_amount;
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

**File:** program/src/processor.rs (L1251-1303)
```rust
        } else {
            // base pc
            deduct_coin_amount = invariant
                .exchange_pc_to_coin(deposit.max_pc_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_pc_amount = deposit.max_pc_amount;
            if deduct_coin_amount > deposit.max_coin_amount {
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
            // base pc, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_coin_amount < deposit.other_amount_min.unwrap() {
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

            let invariant_pc = InvariantPool {
                token_input: deduct_pc_amount,
                token_total: total_pc_without_take_pnl,
            };
            // pc_amount/ (total_pc_amount + pc_amount)  = output / (lp_mint.supply + output) =>  output = pc_amount / total_pc_amount * lp_mint.supply
            mint_lp_amount = invariant_pc
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
        }
```

**File:** program/src/processor.rs (L1716-1718)
```rust
        if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
            return Err(AmmError::NotAllowZeroLP.into());
        }
```

**File:** program/src/math.rs (L380-423)
```rust
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

**File:** program/src/math.rs (L456-477)
```rust
    /// Exchange rate
    pub fn exchange_token_to_pool(
        &self,
        pool_total_amount: u64,
        round_direction: RoundDirection,
    ) -> Option<u64> {
        Some(if round_direction == RoundDirection::Floor {
            U128::from(pool_total_amount)
                .checked_mul(self.token_input.into())
                .unwrap()
                .checked_div(self.token_total.into())
                .unwrap()
                .as_u64()
        } else {
            U128::from(pool_total_amount)
                .checked_mul(self.token_input.into())
                .unwrap()
                .checked_ceil_div(self.token_total.into())
                .unwrap()
                .as_u64()
        })
    }
```
