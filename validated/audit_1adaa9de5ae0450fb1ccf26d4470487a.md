### Title
Missing minimum LP-token slippage check in `Processor::process_deposit` allows sandwiched depositors to receive fewer LP tokens than expected - (File: program/src/processor.rs)

### Summary
`AmmInstruction::Deposit` only bounds the *ratio* between the two deposited token amounts (`max_coin_amount`, `max_pc_amount`, `other_amount_min`), but never lets the caller specify a minimum amount of LP tokens (`mint_lp_amount`) that must be minted. Because `mint_lp_amount` is computed from the live pool reserves (`total_coin_without_take_pnl` / `amm.lp_amount`) at execution time, a depositor can be sandwiched (reserves manipulated by a swap immediately before the deposit is executed) and receive materially fewer LP tokens than expected while every existing check still passes — the same class of bug as the missing `minYT` check in `MetapoolRouter.addLiquidityOneETHKeepYt`, where only one of two resulting outputs (LP vs. YT) is slippage-protected.

### Finding Description
`DepositInstruction` carries `max_coin_amount`, `max_pc_amount`, `base_side`, and an optional `other_amount_min`: [1](#0-0) 

In `process_deposit`, for `base_side == 0` (base coin) the code fixes `deduct_coin_amount = deposit.max_coin_amount`, derives `deduct_pc_amount` from the current pool invariant, and checks it against `max_pc_amount` and the optional `other_amount_min`: [2](#0-1) 

The actual LP amount the user receives, `mint_lp_amount`, is then computed purely from `deduct_coin_amount`, `total_coin_without_take_pnl`, and `amm.lp_amount` — none of which are bounded by any user-supplied minimum: [3](#0-2) 

There is no field in `DepositInstruction`/`WithdrawInstruction`-style parameters, nor any check in `process_deposit`, that enforces a floor on `mint_lp_amount` itself. The instruction only guards the *exchange ratio* between coin and pc (via `max_*_amount` and `other_amount_min`), not the *absolute* amount of pool ownership minted.

Because `total_coin_without_take_pnl` (i.e., the coin-side reserve used in the LP-mint formula) can be changed by an intervening swap (`SwapBaseIn`/`SwapBaseOut`) in the same slot/block without violating the coin/pc ratio bound (an attacker can push the coin reserve up temporarily and reverse it after), the `deduct_coin_amount / total_coin_without_take_pnl * amm.lp_amount` computation can yield a lower `mint_lp_amount` than the depositor expected off-chain, while `deduct_pc_amount` still satisfies `max_pc_amount`/`other_amount_min`. This mirrors the report's root cause: a downstream/secondary quantity derived from a shared pricing state is left completely unprotected by slippage controls, even though a *different* quantity in the same call is protected.

### Impact Explanation
An unprivileged liquidity provider calling `Deposit` can be sandwiched so that they deposit the same coin/pc amounts (still within their specified `max_coin_amount`/`max_pc_amount`/`other_amount_min` bounds) but mint fewer LP tokens than the pool state implied when they signed the transaction. This is a loss of LP-token value to the depositor and a transfer of value to the sandwiching attacker — a concrete theft of user funds reachable from a single submitted transaction with attacker-chosen accounts/data (the attacker's own swap transactions), consistent with a Medium severity slippage-protection gap.

### Likelihood Explanation
Any user calling `Deposit`/`process_deposit` is exposed; the attack only requires the ability to submit ordinary `SwapBaseIn`/`SwapBaseOut` transactions around the victim's deposit (e.g., via MEV/front-running), which is a standard, low-cost, unprivileged capability. No special permissions, leaked keys, or non-default builds are required.

### Recommendation
Add an explicit `min_lp_amount` (or equivalent) parameter to `DepositInstruction`, and in `process_deposit` reject the transaction if the computed `mint_lp_amount` is less than that minimum, mirroring the `min_coin_amount`/`min_pc_amount` protections already present on `WithdrawInstruction`: [4](#0-3) 

### Proof of Concept
1. Attacker observes a pending `Deposit` transaction (`base_side = 0`, fixed `max_coin_amount`, loose `max_pc_amount`/`other_amount_min`).
2. Attacker submits a `SwapBaseIn`/`SwapBaseOut` swap in the same or an earlier slot that increases `total_coin_without_take_pnl` (coin reserve) while keeping the coin/pc price within the victim's tolerance band.
3. Victim's `Deposit` executes: `deduct_coin_amount` and `deduct_pc_amount` still satisfy `max_coin_amount`/`max_pc_amount`/`other_amount_min`, but `mint_lp_amount = deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` (per `program/src/processor.rs` lines 1243-1250) is lower than it would have been without the manipulated reserve.
4. Attacker reverses the swap, restoring the price, and keeps the arbitrage profit extracted from the victim's under-minted LP position — no slippage check exists in `process_deposit` to prevent or revert this outcome.

### Citations

**File:** program/src/instruction.rs (L56-65)
```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct DepositInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub max_coin_amount: u64,
    pub max_pc_amount: u64,
    pub base_side: u64,
    pub other_amount_min: Option<u64>,
}
```

**File:** program/src/processor.rs (L1200-1242)
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
```

**File:** program/src/processor.rs (L1243-1250)
```rust
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1779-1786)
```rust
        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
```
