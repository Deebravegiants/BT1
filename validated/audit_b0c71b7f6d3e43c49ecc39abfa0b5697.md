### Title
Deposit has no minimum liquidity/output floor while Withdraw reverts on rounding-induced zero output, permanently freezing dust LP positions - (File: program/src/processor.rs)

### Summary
`process_deposit` only requires that the minted LP amount, deducted coin amount, and deducted pc amount are individually non-zero, with no check that the resulting LP position can ever be redeemed later. `process_withdraw` computes `coin_amount`/`pc_amount` from the caller's LP share using floor-rounded division and unconditionally reverts with `AmmError::InvalidInput` if either rounds to zero. A depositor who ends up with a proportionally tiny LP balance relative to the pool's `lp_amount` can therefore mint LP tokens successfully but can never withdraw them, since the withdrawal will always floor to zero and revert — mirroring the reported class of bug where deposit has no lower bound but withdrawal enforces an implicit floor.

### Finding Description
In `Processor::process_deposit` (program/src/processor.rs), the LP amount to mint is computed with `RoundDirection::Floor` via `InvariantPool::exchange_token_to_pool`: [1](#0-0) 
The only guard against a "too small" deposit is a bare non-zero check performed after computing the amounts: [2](#0-1) 
There is no check that the freshly minted LP amount will later be redeemable for non-zero token amounts — i.e., no symmetric minimum applied at deposit time.

In `Processor::process_withdraw`, the coin/pc amounts owed to the withdrawer are computed with `RoundDirection::Floor` via `InvariantPool::exchange_pool_to_token`, using the caller-supplied `withdraw.amount` against the pool's `total_coin_without_take_pnl` / `total_pc_without_take_pnl` and `amm.lp_amount`: [3](#0-2) 
If either floored value is zero, the instruction reverts before any transfer or burn occurs: [4](#0-3) 
The floor-rounding division used for both mint and redemption is implemented identically in `InvariantPool::exchange_pool_to_token` / `exchange_token_to_pool`: [5](#0-4) 

Because deposit only guarantees a non-zero LP mint (which can be as small as `1` unit) and does not guarantee the resulting share is large enough to redeem non-zero coin/pc amounts later, any legitimate small depositor whose LP balance's proportional share of the pool's coin or pc reserves floors to zero will be permanently unable to call `Withdraw` successfully for that balance — the instruction will always compute `coin_amount == 0` or `pc_amount == 0` and revert, exactly analogous to the reported VUSD issue where deposit has no minimum but withdrawal enforces one.

### Impact Explanation
A user's LP tokens become effectively frozen: they were legitimately minted through `Deposit` (a completely unprivileged instruction reachable by any single transaction with attacker/user-chosen accounts and data), but the same user can never later reclaim the underlying coin/pc tokens via `Withdraw` for that dust-sized LP balance, since the required floor-division output will be zero and the instruction reverts by design. This is a permanent freezing of user funds condition, matching the reported bug class (Medium severity), reachable purely through the public `Deposit`/`Withdraw` instructions without any privileged signer.

### Likelihood Explanation
Likelihood is proportional to how small the LP amount minted for a deposit is relative to `amm.lp_amount`, `total_coin_without_take_pnl`, and `total_pc_without_take_pnl`. This becomes more likely as the pool's total LP supply and reserves grow (e.g., an established/high-TVL pool), since the same absolute small deposit produces an even smaller relative LP share, increasing the chance the floor-rounded withdrawal amount is zero. It's also reachable without any privileged access — any normal user depositing a small amount into an already-large pool can trigger it.

### Recommendation
Add a check in `process_deposit` that simulates the eventual withdrawal (using the same `exchange_pool_to_token`/Floor logic) for the freshly minted `mint_lp_amount` against the post-deposit pool totals, and reject the deposit (`AmmError::InvalidInput` or a new dedicated error) if it would compute to zero coin/pc amount on withdrawal — i.e., enforce that any minted LP position is guaranteed to be redeemable for non-zero output before allowing the deposit to proceed.

### Citations

**File:** program/src/processor.rs (L1244-1250)
```rust
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1319-1325)
```rust
        if deduct_coin_amount > user_source_coin.amount || deduct_pc_amount > user_source_pc.amount
        {
            return Err(AmmError::InsufficientFunds.into());
        }
        if mint_lp_amount == 0 || deduct_coin_amount == 0 || deduct_pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```

**File:** program/src/processor.rs (L1751-1761)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1775-1777)
```rust
        if withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```

**File:** program/src/math.rs (L433-477)
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
```
