### Title
Deposit LP-share pricing relies on live SPL vault balances with no minimum-LP-out check, enabling a donation/front-run attack that steals value from depositors - (File: `program/src/processor.rs`, `process_deposit`)

### Summary
`process_deposit` (and `process_withdraw`, and all swap handlers) compute the pool's "total assets" directly from the live SPL token balances of `amm_coin_vault`/`amm_pc_vault` via `unpack_token_account(...).amount`, rather than from an internally-tracked, deposit/withdraw-attributed total. Because an unprivileged attacker can transfer tokens directly into these vault accounts (a plain SPL transfer, no AMM instruction required) with no LP minted in return, and because `Deposit` has no minimum-LP-out ("slippage on shares") parameter, a front-run donation can dilute a victim's deposit — the same root cause the ERC4626 reference report describes (`get_total_assets_helper` using `balance_of` instead of internally tracked totals).

### Finding Description
`process_deposit` reads live vault balances and computes `total_coin_without_take_pnl`/`total_pc_without_take_pnl` from them: [1](#0-0) 

The number of LP tokens minted for a deposit is then computed as a floor-rounded ratio of the deposited amount to this live total, scaled by `amm.lp_amount` (the internally tracked LP supply, not `lp_mint.supply`): [2](#0-1) 

`DepositInstruction` only exposes `max_coin_amount`, `max_pc_amount`, `base_side`, and `other_amount_min` — the latter only bounds the *ratio* of the second token relative to the base token, not the resulting `mint_lp_amount`: [3](#0-2) 

The only protection against a degenerate mint is a check against exact zero: [4](#0-3) 

There is no field the caller can supply to bound the minimum amount of LP tokens received. Since `total_coin_without_take_pnl`/`total_coin_without_take_pnl` are derived straight from `amm_coin_vault.amount`/`amm_pc_vault.amount` (live balance, exactly analogous to the `balance_of`-based `get_total_assets_helper` in the reference report), an attacker can, in the same slot/transaction ordering window, transfer additional coin and pc tokens directly into `amm_coin_vault`/`amm_pc_vault` in the pool's current ratio right before a victim's `Deposit` instruction executes. This inflates the "total" used in the ratio calculation without minting any LP for the attacker, so the victim's `mint_lp_amount = floor(deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl)` is diluted (rounded further down) relative to what the victim would have received absent the donation, while `other_amount_min`/`max_*_amount` checks (which only bound token ratio/amounts, not LP output) still pass. The victim pays the same coin/pc amount but receives fewer LP shares than the pre-donation exchange rate implied — a direct value loss for the victim mirroring the impact described in the reference finding, where second depositors received disproportionately few shares relative to assets contributed due to balance-based total-asset accounting.

### Impact Explanation
A victim's deposit transaction, when preceded (front-run in the same block, e.g. via a bundled/adjacent transaction) by an attacker's plain SPL token transfer into the AMM's coin/pc vaults, mints the victim fewer LP tokens than the fair exchange rate would dictate. This is a direct, permanent loss of the victim's contributed value (their assets remain in the pool but their proportional claim, tracked via `amm.lp_amount`, is diluted) with no on-chain check to prevent it, since `Deposit` lacks a minimum-LP-out parameter. This matches the Medium-severity impact class in the reference report: unmitigated donation-style manipulation of a balance-derived total-asset figure causing normal users to lose value.

### Likelihood Explanation
The attack requires only a standard SPL `Transfer` instruction targeting publicly known, non-privileged vault token accounts (`amm.coin_vault`/`amm.pc_vault`, derivable from any `AmmInfo` account) ahead of a victim's `Deposit` call — no signer privileges, no protocol-specific instruction, and no special account setup beyond knowledge of the pool's vault addresses, which are public. This is reachable by any unprivileged actor capable of transaction ordering (e.g., via same-block bundling), making likelihood moderate-to-high in adversarial/MEV environments, though it does require the attacker to accept the cost of donating funds (which are not directly recovered but which dilute all future/other depositors, and can be recovered if the attacker also holds/acquires LP before or after donating).

### Recommendation
Do not derive the LP-share-minting exchange rate solely from live SPL vault balances (`unpack_token_account(...).amount`). Instead, track deposited/withdrawn totals internally (already partially done via `amm.lp_amount` for LP supply) and reconcile against the vault balance only for detecting/handling external donations explicitly (e.g., treat any balance excess over the internally tracked total as protocol-owned surplus rather than folding it silently into the price used for the next depositor). Additionally, add an optional minimum-LP-out parameter to `DepositInstruction` so callers can enforce a floor on `mint_lp_amount`, protecting against any single-block manipulation of the deposit exchange rate regardless of its source.

### Proof of Concept
1. Pool exists with `amm.lp_amount = L`, vault balances `coin = C`, `pc = P` (ratio `C:P` maintained).
2. Attacker observes a pending victim `Deposit` transaction for `deduct_coin_amount = c`, `deduct_pc_amount = p` (in the same ratio `C:P`).
3. Attacker submits an SPL `Transfer` to `amm_coin_vault` and `amm_pc_vault` for amounts `Δc, Δp` in the same ratio (no AMM instruction, no LP minted), landing before the victim's transaction in the same block.
4. Victim's `Deposit` executes; `total_coin_without_take_pnl = C + Δc` (inflated), so
`mint_lp_amount = floor(c * L / (C + Δc))`, strictly less than `floor(c * L / C)` that the victim expected/priced their transaction for.
5. Victim's `Deposit` still succeeds (ratio checks/`other_amount_min` unaffected since attacker donated in the pool's ratio; `mint_lp_amount` only checked against `== 0`), but the victim receives fewer LP shares for the same coin/pc contribution than fair value — a direct loss, with no on-chain mechanism (no min-LP-out param) to detect or reject it.

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

**File:** program/src/instruction.rs (L57-65)
```rust
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
