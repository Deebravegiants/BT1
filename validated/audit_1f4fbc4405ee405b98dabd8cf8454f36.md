### Title
Withdraw reverts entirely (rather than skipping only the zero-value leg) whenever proportional LP share rounds to zero on either token side, permanently freezing dust LP positions - (File: program/src/processor.rs)

### Summary
`Processor::process_withdraw` computes both `coin_amount` and `pc_amount` from the LP amount being redeemed using floor-rounding division against the pool's current vault balances, and then unconditionally reverts the whole instruction with `AmmError::InvalidInput` if **either** side rounds down to zero. There is no code path that allows a partial withdrawal (only the non-zero leg) or that special-cases dust amounts, so any LP holder whose proportional share of one vault is below 1 raw token unit can never redeem their LP tokens at all, permanently freezing that user's funds — the same root cause pattern as the referenced `SfrxEth.withdraw()` revert-on-small-amount issue, just manifesting in an AMM LP redemption instead of a liquid-staking redemption.

### Finding Description
In `process_withdraw` (`program/src/processor.rs`), the coin/pc output amounts are derived via `InvariantPool::exchange_pool_to_token` with `RoundDirection::Floor`: [1](#0-0) 

Immediately afterward, the code treats a zero result on **either** side as a total, non-recoverable input error, aborting the whole withdraw: [2](#0-1) 

The only guard against degenerate withdraw sizes is the "not-all" check earlier, which merely prevents draining the entire LP supply, not dust amounts: [3](#0-2) 

The floor-division math itself is defined in `InvariantPool::exchange_pool_to_token`: [4](#0-3) 

Because `coin_amount = floor(total_coin_without_take_pnl * withdraw.amount / amm.lp_amount)` and `pc_amount` is computed the same way against the other vault, whenever `withdraw.amount / amm.lp_amount < 1 / total_coin_without_take_pnl` (or the analogous ratio for `pc`), the corresponding output floors to `0`. Any LP holder in that situation is permanently unable to call `Withdraw` with that balance — the instruction always returns `AmmError::InvalidInput` — exactly mirroring the mitigated-but-not-fixed root cause in the referenced report: a legitimate, non-zero redemption request reverting purely because of rounding-to-zero on the calculated output, with no way to skip/adjust for the zero-valued leg only.

This is directly reachable by any unprivileged liquidity provider through the standard `Withdraw` instruction and requires no privileged accounts, and it can occur at any point where the balance of one vault becomes small relative to `amm.lp_amount` (e.g., after most other LPs have withdrawn, or on a pool where one side's token has very different decimals/liquidity depth), not merely at extreme edge values.

### Impact Explanation
An LP holder whose remaining LP balance's proportional share of the pool has rounded to zero on either token leg has that LP position **permanently locked**: they can never burn it to redeem the underlying coin/pc since `process_withdraw` always errors out before any transfer/burn occurs (the burn at line ~1805 is only reached in the `else` success branch, which is unreachable when either amount is zero). This constitutes permanent freezing of user LP funds, matching the "Medium" bug class of the referenced finding. It is also more likely to bite integrators/contracts built atop the AMM that programmatically withdraw exact or dust-level LP amounts, which is precisely the residual-risk scenario called out in the source report.

### Likelihood Explanation
This requires no privileged access — any liquidity provider calling `Withdraw` with an LP amount whose proportional share of either vault floors to zero triggers it. It becomes increasingly likely as a pool's vault balance shrinks relative to outstanding `lp_amount` (e.g. large withdrawals by other LPs, PnL take-profit draining one side more than the other, or naturally low-decimal/low-liquidity token pairs), so it is a realistic occurrence rather than a purely theoretical corner case.

### Recommendation
Do not abort the whole `Withdraw` instruction when only one of `coin_amount`/`pc_amount` rounds to zero. Instead, allow redemption of the non-zero leg only (burn the LP amount and transfer the non-zero token, skipping the CPI transfer for the zero-valued token), or alternatively perform the ceiling-direction rounding consistently combined with an explicit "insufficient dust" check that lets the user still recover at least the non-zero portion. At minimum, expose a way for holders of such dust LP balances to eventually recover value rather than being unconditionally blocked forever.

### Proof of Concept
1. Set up a pool where `amm.lp_amount` is large relative to `total_coin_without_take_pnl` (e.g., after heavy net withdrawals or PnL extraction has drained the coin vault far more than the pc vault, or use a token pair whose coin side has few remaining raw units in the vault).
2. A user holds a small LP balance `L` such that `L * total_coin_without_take_pnl / amm.lp_amount == 0` (floor), while `pc_amount` may or may not be nonzero.
3. Call `Withdraw` with `amount = L`. Because `coin_amount == 0`, `process_withdraw` hits the check at `program/src/processor.rs:1775-1777` and returns `AmmError::InvalidInput` before performing any burn or transfer.
4. There is no alternate code path to withdraw only the pc-side value or to reduce `L` further to still receive something nonzero for both legs (making a smaller amount even more likely to hit the same zero-floor problem), so the user's LP position for balance `L` is permanently stuck.

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
