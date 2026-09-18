### Title
Last LP holder cannot fully withdraw their position, permanently freezing a residual balance - (File: program/src/processor.rs)

### Summary
`process_withdraw` in the Raydium AMM program blocks any withdrawal that would drive `amm.lp_amount` to zero. As a direct consequence, whoever ends up holding the entire remaining LP supply for a pool (the "last" LP, e.g. after all other LPs have exited) can never redeem their full position — the instruction always reverts on the final unit of LP tokens, permanently trapping the corresponding coin/pc reserves in the vaults.

### Finding Description
`process_withdraw` enforces:
```rust
if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
    return Err(AmmError::NotAllowZeroLP.into());
}
``` [1](#0-0) 

This check uses `>=` against `amm.lp_amount` (not `>`), so a withdrawal request equal to the entire outstanding `amm.lp_amount` is always rejected, regardless of who the caller is or how much LP they actually own. This mirrors the analog bug class: a boundary/status check that is only correct for the "many participants remain" case and incorrectly forbids the legitimate final exit. In the reported Unitas issue, `_checkReserveRatio` wrongly reverted when both `liabilities` and `allReserves` became zero at the very end; here, the withdraw path wrongly reverts whenever the withdrawal would legitimately zero out `amm.lp_amount`, which is exactly what happens when the sole remaining LP tries to withdraw 100% of the pool.

The exchange-rate math further depends on `amm.lp_amount` as a denominator:
```rust
let invariant = InvariantPool {
    token_input: withdraw.amount,
    token_total: amm.lp_amount,
};
``` [2](#0-1) 
so the developers intentionally guard against `amm.lp_amount` reaching zero to avoid a division by zero for subsequent withdrawals — but the guard is implemented by unconditionally blocking the *caller's own* final full exit rather than only guarding future divisions once the pool is actually empty of participants.

### Impact Explanation
Any account that legitimately owns the entirety of a pool's outstanding LP tokens (a single depositor pool, or an LP who has bought out/absorbed all other positions) is permanently unable to withdraw 100% of their underlying coin/pc collateral through `Withdraw`. They are forced to always leave at least 1 LP unit (and its proportional coin/pc share) locked in the vaults with no code path to redeem it, since `withdraw.amount >= amm.lp_amount` is rejected for every possible value up to and including the total. This is a permanent freezing of user/LP funds, matching the class of bug in the reference report (last withdrawer blocked from claiming otherwise-available, fully-backed collateral).

### Likelihood Explanation
Reachable by any unprivileged LP through the standard `Withdraw` instruction with attacker/user-chosen `withdraw.amount` equal to their full balance — no privileged signer or special conditions are required beyond naturally holding 100% of `amm.lp_amount` (a state that arises whenever a single LP is the sole remaining depositor, which is common for small or newly created pools, or occurs at the tail end of a pool's lifecycle as other LPs exit).

### Recommendation
Change the boundary condition so a withdrawal that consumes the entire remaining `amm.lp_amount` is allowed when the caller genuinely owns the total supply, e.g. change `withdraw.amount >= amm.lp_amount` to `withdraw.amount > amm.lp_amount`, and instead special-case/guard the zero-`lp_amount` state only for downstream divisions (or require pool closure/re-initialization semantics when the last LP exits), rather than rejecting the caller's legitimate full redemption.

### Proof of Concept
1. Create a pool via `Initialize2` and have a single account deposit, becoming the sole LP holder so `amm.lp_amount == lp_mint.supply == N` and the user's LP token balance is `N`.
2. Call `Withdraw` with `withdraw.amount = N` (their entire balance).
3. The check `withdraw.amount >= amm.lp_amount` (`N >= N`) is true, so the instruction returns `AmmError::NotAllowZeroLP` and the transaction reverts.
4. The user can withdraw at most `N-1`, permanently leaving 1 LP unit's worth of coin/pc unredeemable in `amm_coin_vault`/`amm_pc_vault`, with no instruction available to reclaim it.

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

**File:** program/src/processor.rs (L1752-1755)
```rust
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
```
