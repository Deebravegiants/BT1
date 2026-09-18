### Title
Small LP-holders can be permanently unable to `Withdraw` due to floor-rounded `coin_amount`/`pc_amount` reverting to zero - ([File: program/src/processor.rs])

### Summary
`process_withdraw` computes the coin/pc amounts owed to a withdrawing LP holder using floor-rounded division (`InvariantPool::exchange_pool_to_token`), then hard-reverts the whole transaction if either resulting amount is `0`. Because the division always floors to the same result for a given LP balance and pool ratio, a user whose LP balance is too small relative to the pool's total supply and vault balances will have their withdrawal amount permanently computed as `0` for one of the two tokens, causing every withdrawal attempt to fail and their LP position (and underlying value) to become permanently frozen — the same "sub-threshold amount causes irrecoverable revert" bug class described in the referenced Tokemak report (there caused by `GPToke.MIN_STAKE_AMOUNT`, here caused by floor-rounding to zero plus a hard revert instead of a graceful fallback).

### Finding Description
In `process_withdraw` (`program/src/processor.rs`), the LP amount a user wants to redeem is converted into coin/pc token amounts via: [1](#0-0) 

using the `InvariantPool::exchange_pool_to_token` helper, which explicitly floors the result: [2](#0-1) 

Immediately afterward, the processor enforces an all-or-nothing check that reverts the entire instruction — burning nothing, transferring nothing — if either computed amount is zero: [3](#0-2) 

`withdraw.amount` is capped by the caller's own LP balance (`withdraw.amount > user_source_lp.amount` is rejected) and by the pool's total LP supply (`withdraw.amount >= amm.lp_amount` is rejected): [4](#0-3) 

but there is no lower bound ensuring the redeemable coin/pc amounts are non-zero before this point. For an LP holder whose full balance is small relative to `amm.lp_amount` and the pool's vault reserves (e.g., very early/small depositors, or pools with a much more valuable coin/pc side), `coin_amount = floor(total_coin * withdraw.amount / amm.lp_amount)` or `pc_amount = floor(total_pc * withdraw.amount / amm.lp_amount)` can floor to `0`. Since the user cannot request more than their own LP balance, and the ratio is deterministic given the current pool state, every withdrawal attempt using their maximum balance (or any amount up to it) will floor to the same `0` and revert with `AmmError::InvalidInput`, with no way for the user to legitimately clear the threshold on their own.

### Impact Explanation
Affected LP holders are permanently unable to redeem their LP tokens for the underlying coin/pc tokens through the `Withdraw` instruction, effectively freezing their share of pool funds — a direct parallel to the referenced report where users below `MIN_STAKE_AMOUNT` could not withdraw from `LMPVault`. Unlike a temporary staking/queue delay, this is a floor-rounding artifact of the pool's current reserve ratio and total LP supply, so it does not resolve simply by waiting; it only changes if the pool ratio or `amm.lp_amount` shifts enough (via other users' deposits/withdrawals/swaps) to raise the affected user's proportional share above the rounding floor for both tokens.

### Likelihood Explanation
This is reachable by an ordinary LP holder submitting a normal `Withdraw` instruction with their own account and their full (or any) LP balance — no privileged signer or special conditions are required. It is more likely to manifest in pools with highly disparate coin/pc valuations, low-decimal tokens, or for very small depositors, but any pool configuration where `total_coin_without_take_pnl * lp_balance / amm.lp_amount` or the pc equivalent rounds to zero triggers it.

### Recommendation
Instead of unconditionally reverting when either `coin_amount` or `pc_amount` floors to zero, consider: (1) rejecting the withdrawal earlier with a clearer, LP-amount-specific error that lets the client compute a safe minimum withdrawal size, and/or (2) allowing partial withdrawal of only the non-zero side while still burning the corresponding LP amount rather than blocking the entire operation, and/or (3) rounding in favor of the user for the smaller-valued side (as some pools do) so a nonzero payout is still made when the LP amount is genuinely worth a fractional-but-positive amount of that token.

### Proof of Concept
1. Initialize a pool where the pc/coin reserve ratio is such that `amm.lp_amount` is large relative to reserves on one side (e.g., low-decimal or low-value coin side).
2. A user deposits a very small amount, receiving a correspondingly small LP token balance.
3. The user calls `Withdraw` with `amount = <their full LP balance>`.
4. In `process_withdraw`, `coin_amount` (or `pc_amount`) computed via `InvariantPool::exchange_pool_to_token` floors to `0` because `total_coin_without_take_pnl * withdraw.amount < amm.lp_amount`.
5. The check at `program/src/processor.rs:1775-1777` triggers, returning `AmmError::InvalidInput`, and the transaction reverts — no LP is burned, no tokens are transferred, and the user cannot withdraw with any amount up to their balance, permanently locking their funds in the pool.

### Citations

**File:** program/src/processor.rs (L1713-1718)
```rust
        if withdraw.amount > user_source_lp.amount {
            return Err(AmmError::InsufficientFunds.into());
        }
        if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
            return Err(AmmError::NotAllowZeroLP.into());
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

**File:** program/src/math.rs (L433-455)
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
```
