### Title
Unchecked `U128::as_u64()` truncation in `InvariantToken`/`InvariantPool` exchange-rate math allows attacker-controlled Deposit amounts to bypass slippage checks and mint unbacked LP - ([File: program/src/math.rs])

### Summary
`InvariantToken::exchange_coin_to_pc`, `InvariantToken::exchange_pc_to_coin`, `InvariantPool::exchange_pool_to_token`, and `InvariantPool::exchange_token_to_pool` all compute a `U128` intermediate (`token_a * token_b`) and then truncate it to `u64` with the unchecked `.as_u64()` call instead of the checked `Calculator::to_u64()` helper (which uses `try_into` and returns `AmmError::ConversionFailure` on overflow) that is used everywhere else in the same file. [1](#0-0) [2](#0-1) [3](#0-2) 

This is the same bug class as the report: a wider integer (`U128`) is silently narrowed to `u64` via an unchecked cast rather than a checked conversion, so on overflow the result wraps instead of erroring, producing an unintended value rather than reverting the transaction.

### Finding Description
In `process_deposit` (`program/src/processor.rs`), the amount of the "other" token the user must deposit is derived from user-supplied `deposit.max_pc_amount` / `deposit.max_coin_amount` via `InvariantToken::exchange_pc_to_coin` / `exchange_coin_to_pc`, and the LP amount to mint is derived from the deduced deposit amount via `InvariantPool::exchange_token_to_pool`: [4](#0-3) 

Both `max_pc_amount`/`max_coin_amount` are fully attacker-controlled `u64` instruction-data fields unpacked directly from the transaction: [5](#0-4) 

Because `exchange_pc_to_coin`/`exchange_coin_to_pc` and `exchange_token_to_pool` multiply an attacker-chosen `u64` by a pool-state `u64` inside a `U128` and then call `.as_u64()` unconditionally (no bounds check, no `checked_mul`/`try_into` guard against the final truncation), a sufficiently large user-supplied amount combined with a small pool-side reserve can push the `U128` quotient above `u64::MAX`. `.as_u64()` on the `uint` crate's `U128` type keeps only the low 64 bits, so the truncated `deduct_coin_amount` (or `mint_lp_amount`) becomes a value that has no arithmetic relationship to the real ratio the code intends to enforce.

Because the truncated value is what is subsequently compared against `deposit.max_coin_amount` / `deposit.other_amount_min` and used to compute `mint_lp_amount`, an attacker can pick `max_pc_amount`/`max_coin_amount` such that:
- the truncated `deduct_*_amount` passes the slippage checks (`deduct_coin_amount > deposit.max_coin_amount` / `other_amount_min`) even though it is unrelated to the real proportional deposit, and
- the truncated `mint_lp_amount` computed from the same untruncated-but-huge `deduct_pc_amount`/`deduct_coin_amount` value can be tuned independently, breaking the intended `token_in / total_token = lp_mint_out / total_lp` invariant.

### Impact Explanation
If exploitable end-to-end, this breaks the pool's LP-share accounting invariant that is supposed to guarantee minted LP is exactly backed by deposited tokens. Since `mint_lp_amount` and the actual token amounts transferred into the vaults are derived from the same unchecked-truncation math, an attacker could obtain LP tokens disproportionate to the tokens actually contributed, i.e., unbacked LP minting / insolvent pool accounting - the exact class of impact this analog scan is meant to flag.

### Likelihood Explanation
The affected functions are reachable directly from the `Deposit` instruction with attacker-chosen `max_coin_amount`/`max_pc_amount` in a single transaction, requiring no privileged signer, no validator collusion, and no off-chain component. However, triggering an actual overflow requires the attacker to find `max_pc_amount`/`max_coin_amount` values whose product with the current pool reserves exceeds `u64::MAX` (~1.8e19) while also satisfying the pool's real (much smaller) reserve values and the subsequent slippage checks — this is a non-trivial but deterministic search, entirely computable off-chain by the attacker since all inputs (pool reserves) are public account data. I was not able to fully trace the remainder of `process_deposit` (base_coin branch, final `mint_lp_amount` computation and token transfer call) within the available context to confirm the exact numeric conditions and full transfer/mint sequencing, so likelihood should be treated as plausible but not fully proven without further code review.

### Recommendation
Replace all unchecked `.as_u64()` truncations in `InvariantToken::exchange_coin_to_pc`, `InvariantToken::exchange_pc_to_coin`, `InvariantPool::exchange_pool_to_token`, and `InvariantPool::exchange_token_to_pool` with the existing checked `Calculator::to_u64()` helper (or equivalent `try_into`/`checked_*` calls) so that any value that would not fit in `u64` causes the instruction to fail with `AmmError::ConversionFailure` instead of silently wrapping.

### Proof of Concept
Not independently verified end-to-end due to incomplete visibility into the full `process_deposit` base-coin branch and the final mint/transfer sequencing in the indexed context; the root-cause code path (unchecked `U128::as_u64()` truncation reachable from user-supplied `Deposit` amounts) is confirmed via the cited `math.rs` and `processor.rs`/`instruction.rs` locations above.

### Citations

**File:** program/src/math.rs (L42-48)
```rust
    pub fn to_u128(val: u64) -> Result<u128, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }

    pub fn to_u64(val: u128) -> Result<u64, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }
```

**File:** program/src/math.rs (L378-424)
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
}
```

**File:** program/src/math.rs (L433-478)
```rust
impl InvariantPool {
    /// Exchange rate
    pub fn exchange_pool_to_token(
        &self,
        token_total_amount: u64,
        round_direction: RoundDirection,
    ) -> Option<u64> {
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
}
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

**File:** program/src/instruction.rs (L355-371)
```rust
            3 => {
                let (max_coin_amount, rest) = Self::unpack_u64(rest)?;
                let (max_pc_amount, rest) = Self::unpack_u64(rest)?;
                let (base_side, rest) = Self::unpack_u64(rest)?;
                let other_amount_min = if rest.len() >= 8 {
                    let (other_amount_min, _rest) = Self::unpack_u64(rest)?;
                    Some(other_amount_min)
                } else {
                    None
                };
                Self::Deposit(DepositInstruction {
                    max_coin_amount,
                    max_pc_amount,
                    base_side,
                    other_amount_min,
                })
            }
```
