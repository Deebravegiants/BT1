### Title
Deposit LP-share minting uses live (donatable) vault balances with no minimum-LP-output check, enabling share-price manipulation via front-run donation - (File: `program/src/processor.rs`)

### Summary
Raydium's `process_deposit` computes the number of LP tokens minted to a depositor using the AMM's live SPL token vault balances (`amm_pc_vault.amount` / `amm_coin_vault.amount`) rather than an internally-tracked, deposit-gated reserve, and the `DepositInstruction` exposes no minimum-LP-output ("min_lp_amount") parameter analogous to Solmate's ERC4626 first-deposit rounding issue. An attacker can inflate the vault balances by directly transferring tokens into the public `amm_coin_vault`/`amm_pc_vault` token accounts immediately before a victim's `Deposit` transaction, which shifts the coin/pc ratio used to compute `mint_lp_amount`, causing the victim to receive far fewer LP shares than the value of tokens they deposit while `amm.lp_amount` (and hence the value backing existing LP holders, including the attacker) increases.

### Finding Description
`process_deposit` derives the pool's effective reserves purely from the vaults' live SPL token balances: [1](#0-0) 
and then computes the LP tokens to mint proportionally to these live balances vs. the fixed `amm.lp_amount`: [2](#0-1) [3](#0-2) 

Because `amm_coin_vault_info`/`amm_pc_vault_info` are ordinary SPL token accounts, anyone can call the SPL Token program to transfer additional coin/pc tokens directly into these vaults without going through `Deposit`, `Withdraw`, or swap instructions. Such a "donation" instantly and permanently inflates `total_coin_without_take_pnl`/`total_pc_without_take_pnl` without minting any new LP tokens or changing `amm.lp_amount`. If this donation is executed in the same slot immediately before a victim's `Deposit` transaction, the victim's `mint_lp_amount = invariant.exchange_token_to_pool(amm.lp_amount, Floor)` is computed against the inflated denominator, so the victim receives disproportionately fewer LP shares for the real value of coin/pc tokens they transfer into the vaults (`deduct_coin_amount`/`deduct_pc_amount`, at line [4](#0-3) ).

The only depositor-side protections are:
- `other_amount_min` — an optional bound only on the *other-side token amount*, not on LP output.
- `mint_lp_amount == 0` revert check: [5](#0-4) 

Neither protects against the case where `mint_lp_amount` is nonzero but far smaller than fair value due to a just-in-time donation — there is no `min_lp_amount` field in `DepositInstruction`: [6](#0-5) 

This is the direct analog of the ERC4626 report's core issue: the vault's share-price/exchange-rate is derived from a manipulable raw balance, and depositors lack a minimum-shares-received guard, allowing an attacker to dilute a depositor's fair share of the pool via donation. Note `Initialize2` does implement a MINIMUM_LIQUIDITY-style lock (`user_lp_amount = liquidity - 10^decimals`, [7](#0-6) ) which mitigates the classic *first-deposit* zero-liquidity attack, but this protection only applies at pool creation — it does not prevent the same class of exchange-rate manipulation against *subsequent* depositors via direct vault donation.

### Impact Explanation
A malicious actor can, using only a standard SPL Token transfer (a normal CPI any signer can invoke) plus knowledge of a pending victim `Deposit` transaction, inflate vault balances to dilute the victim's minted LP shares. The victim's real tokens (transferred per `deduct_coin_amount`/`deduct_pc_amount`) end up backing the pool while the victim receives disproportionately few LP shares — the value differential is captured by existing LP holders (including the attacker if they hold LP or later exploit the position), constituting direct theft of depositor funds. This matches the "concrete theft of user funds" bar for validity.

### Likelihood Explanation
The attack requires the attacker to front-run (or land immediately before, in the same block/slot due to Solana's leader-controlled ordering) a target's `Deposit` transaction with a plain SPL token transfer to the public, non-privileged vault accounts, and requires enough capital to meaningfully move the ratio, which is feasible especially for smaller/newer pools with low TVL. This is a realistic, single-transaction, unprivileged attack path, though its magnitude scales inversely with existing pool depth (very large, deep pools require proportionally larger donations to have significant effect).

### Recommendation
- Add a `min_lp_amount` (or equivalent minimum-shares-out) parameter to `DepositInstruction` and enforce it in `process_deposit`, rejecting the transaction if `mint_lp_amount` falls below the caller-specified minimum, similar to slippage checks already used for swaps.
- Consider tracking pool reserves independently of raw vault balances (updated only through `Deposit`/`Withdraw`/swap instructions) so that unsolicited direct transfers into vault accounts cannot instantaneously affect the coin/pc ratio used for LP-share accounting, or alternatively reconcile/quarantine unexpected excess balance (similar to Uniswap V2's `skim`/`sync` pattern) instead of implicitly folding it into the next depositor's exchange rate.

### Proof of Concept
1. Attacker observes a pending `Deposit` transaction from a victim targeting an existing Raydium pool (pool_id) with a modest amount of TVL.
2. In an earlier transaction landing in the same or a preceding slot, attacker calls the SPL Token program `Transfer` instruction directly into `amm_coin_vault` (and/or `amm_pc_vault`) — no Raydium program interaction is needed, since these are normal token accounts owned by the AMM authority PDA but transfers into them require no special authorization.
3. When the victim's `Deposit` instruction executes, `Calculator::calc_total_without_take_pnl_no_orderbook` reads the now-inflated `amm_coin_vault.amount`/`amm_pc_vault.amount` at [1](#0-0) , inflating `total_coin_without_take_pnl`.
4. `mint_lp_amount = invariant_coin.exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)` at [2](#0-1)  computes a much smaller LP amount for the victim's `deduct_coin_amount` than would have been fair prior to the donation.
5. The victim's transaction still succeeds (as long as `mint_lp_amount != 0`, check at [5](#0-4) ), transferring their full `deduct_coin_amount`/`deduct_pc_amount` into the vaults while minting them disproportionately few LP tokens — the excess value (including the attacker's earlier donation) now backs `amm.lp_amount` and is redeemable by existing/attacker LP holders via `Withdraw`.

### Citations

**File:** program/src/processor.rs (L908-917)
```rust
        let liquidity = Calculator::to_u64(
            U128::from(amm_pc_vault.amount)
                .checked_mul(amm_coin_vault.amount.into())
                .unwrap()
                .integer_sqrt()
                .as_u128(),
        )?;
        let user_lp_amount = liquidity
            .checked_sub((10u64).checked_pow(lp_mint.decimals.into()).unwrap())
            .ok_or(AmmError::InitLpAmountTooLess)?;
```

**File:** program/src/processor.rs (L1148-1153)
```rust
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

**File:** program/src/processor.rs (L1327-1340)
```rust
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_coin_info.clone(),
            amm_coin_vault_info.clone(),
            source_owner_info.clone(),
            deduct_coin_amount,
        )?;
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_pc_info.clone(),
            amm_pc_vault_info.clone(),
            source_owner_info.clone(),
            deduct_pc_amount,
        )?;
```

**File:** program/src/instruction.rs (L58-65)
```rust
pub struct DepositInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub max_coin_amount: u64,
    pub max_pc_amount: u64,
    pub base_side: u64,
    pub other_amount_min: Option<u64>,
}
```
