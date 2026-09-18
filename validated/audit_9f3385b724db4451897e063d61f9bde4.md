### Title
Deposit LP-share minting is based on live, donatable vault balances with no minimum-LP-out protection, enabling share-dilution theft from depositors - ([File: program/src/processor.rs])

### Summary
`process_deposit` computes the number of LP tokens to mint using the *live* SPL token balances of `amm_coin_vault` / `amm_pc_vault` (`total_coin_without_take_pnl` / `total_pc_without_take_pnl`) divided into the internally tracked `amm.lp_amount`, but `DepositInstruction` exposes no "minimum LP tokens out" parameter. `other_amount_min` only bounds the *paired token amount*, not the number of shares minted. Because any unprivileged account can transfer tokens directly into the public `amm_coin_vault`/`amm_pc_vault` accounts (a plain SPL Token transfer, no program permission required), an attacker can inflate the reserve figures used as the denominator in the share-minting formula immediately before a victim's `Deposit`, causing the victim to receive fewer LP shares than their contribution is worth. The attacker, holding pre-existing LP shares, then reclaims the inflated value via `Withdraw`.

### Finding Description
In `process_deposit`, reserves are read directly from the token accounts every call: [1](#0-0) 

The minted LP amount for a `base_side == 0` (base coin) deposit is: [2](#0-1) 

and for `base_side != 0` (base pc): [3](#0-2) 

`DepositInstruction` only carries `max_coin_amount`, `max_pc_amount`, `base_side`, and an optional `other_amount_min` that bounds the *paired* token amount, not the LP output: [4](#0-3) 

The only guard on the minted amount itself is a strict zero check, not a "minimum acceptable" check: [5](#0-4) 

Because `amm_coin_vault.amount`/`amm_pc_vault.amount` are plain SPL Token account balances, any account can inflate them via a direct SPL `Transfer` to the (publicly known, deterministic) vault address — this requires no signature from the AMM authority and is not mediated by the AMM program at all. If an attacker inflates `total_coin_without_take_pnl` (the denominator for a base-coin deposit) right before/atomically with a victim's `Deposit`, `mint_lp_amount = deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` (floored) shrinks for the exact same `deduct_coin_amount` the victim contributes. Meanwhile `deduct_pc_amount` for that same deposit is computed from the *same* inflated ratio, so it typically decreases too, meaning the victim's transaction does not trip the `ExceededSlippage` check on `max_pc_amount` (which only reverts if the required amount is *too high*) and, absent an `other_amount_min`, is not caught at all. The victim's real capital is added to the vaults, but they receive a smaller LP-share claim than that capital is worth; the discrepancy accrues to existing LP holders (i.e., the attacker) in proportion to their existing `amm.lp_amount` share, which is realized on the next `Withdraw`: [6](#0-5) 

`Withdraw` also computes payouts strictly from `amm.lp_amount` fraction against the current (post-donation, post-victim-deposit) live reserves, so any value not captured by the victim's freshly minted shares flows to whoever holds the remaining share fraction — the attacker.

This is the same accounting root cause as the referenced Surge Protocol report: share-mint/redemption math is keyed off a spoofable "live balance" figure that any unprivileged actor can inflate via direct token transfer, and the corresponding deposit instruction lacks a slippage check on the actual output (LP shares) rather than only on the paired input token amount.

### Impact Explanation
A victim depositor can receive fewer LP tokens than their contributed coin/pc value warrants, permanently and non-refundably diluting them in favor of existing LP holders. An attacker who is an existing (even a very small) LP holder — e.g., the pool creator via `Initialize2`, or anyone who deposited earlier — can realize this diluted value by calling `Withdraw`, effectively extracting part of the victim's deposited funds. This is a direct, unauthorized transfer of value between unprivileged users of the pool, matching the "theft of funds from depositors" impact class of the source report.

### Likelihood Explanation
The attack requires only: (1) a plain SPL Token `Transfer` into the publicly known `amm_coin_vault` or `amm_pc_vault` address — no special authority or program interaction needed — and (2) ordering that transfer immediately before (or in the same slot/bundle as) a target `Deposit` transaction that does not set (or sets a loose) `other_amount_min`. Since `other_amount_min` is optional and does not bound LP output at all, many integrators/front-ends that omit it (or cannot meaningfully bound the actual metric that matters — LP shares) leave depositors exposed. The requirement to be an existing LP holder to profit is trivially satisfiable by the attacker (e.g., by being the pool creator or making a prior small deposit), and pool creation itself is unprivileged (`Initialize2` is callable by anyone).

### Recommendation
Add an explicit minimum-LP-out parameter to `DepositInstruction` (analogous to `min_coin_amount`/`min_pc_amount` in `WithdrawInstruction`) and enforce `mint_lp_amount >= min_lp_amount` in `process_deposit`, so depositors can directly bound the number of shares they receive regardless of how `total_coin_without_take_pnl`/`total_pc_without_take_pnl` were manipulated between transaction construction and execution.

### Proof of Concept
1. Attacker creates (or already holds LP in) a pool via `Initialize2`, obtaining `user_lp_amount` LP tokens tracked in `amm.lp_amount`.
2. Attacker observes a pending victim `Deposit` (`base_side = 0`, `max_coin_amount = C`, `max_pc_amount = P` generous, `other_amount_min = None`).
3. Attacker submits a plain SPL Token `Transfer` of a large amount `D` of the coin mint directly to `amm.coin_vault` (no AMM instruction call needed), landing before the victim's `Deposit` executes.
4. Victim's `Deposit` executes: `total_coin_without_take_pnl` now includes `D`, so
   `mint_lp_amount = floor(C * amm.lp_amount / (total_coin_without_take_pnl_old + D))`
   is much smaller than the fair-value share for contributing `C` (and the paired `deduct_pc_amount`, computed from the same skewed ratio, still satisfies `<= max_pc_amount`, so the tx does not revert).
5. Attacker calls `Withdraw` for their existing LP tokens; payout is `amm.lp_amount`-fraction of the now-larger `total_coin_without_take_pnl`/`total_pc_without_take_pnl` (which includes both the donated `D` and the undervalued portion of the victim's contribution), letting the attacker recoup the donation plus a share of the victim's diluted deposit.

### Citations

**File:** program/src/processor.rs (L1138-1153)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_source_coin =
            Self::unpack_token_account(&user_source_coin_info, spl_token_program_id)?;
        let user_source_pc =
            Self::unpack_token_account(&user_source_pc_info, spl_token_program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
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

**File:** program/src/processor.rs (L1295-1302)
```rust
            let invariant_pc = InvariantPool {
                token_input: deduct_pc_amount,
                token_total: total_pc_without_take_pnl,
            };
            // pc_amount/ (total_pc_amount + pc_amount)  = output / (lp_mint.supply + output) =>  output = pc_amount / total_pc_amount * lp_mint.supply
            mint_lp_amount = invariant_pc
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
