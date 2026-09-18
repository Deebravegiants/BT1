### Title
LP-mint decimal is attacker-chosen at pool creation, defeating the MINIMUM_LIQUIDITY guard and enabling share-price manipulation on `Deposit` - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives the minimum-liquidity offset used to protect first depositors purely from `amm_lp_mint_info`'s `decimals` field, which is fully attacker-controlled (the LP mint is created and supplied by the pool creator, not derived/validated). By setting the LP mint decimals to `0`, the "locked" minimum-liquidity offset collapses to `1`, effectively disabling the anti-manipulation guard. Combined with the fact that pool "totals" used for LP-mint math are read directly from the live SPL vault balances (which anyone can inflate with a plain token transfer that bypasses `Deposit`/`Swap`), an attacker can execute a classic share-inflation attack against the first real depositor of a freshly created pool.

### Finding Description
In `process_initialize2` (`program/src/processor.rs:908-929`), liquidity accounting is: [1](#0-0) 
```
let liquidity = ...sqrt(pc_amount * coin_amount)...;
let user_lp_amount = liquidity
    .checked_sub((10u64).checked_pow(lp_mint.decimals.into()).unwrap())
    .ok_or(AmmError::InitLpAmountTooLess)?;
...
Invokers::token_mint_to(..., user_lp_amount)?;
amm.lp_amount = liquidity;   // full value including the un-minted offset
```
Only `user_lp_amount` (liquidity minus `10^decimals`) is actually minted to the creator, while the *internal accounting total* `amm.lp_amount` retains the full `liquidity` value. This mirrors Uniswap V2's `MINIMUM_LIQUIDITY` defense, which is supposed to guarantee that a meaningful amount of value is permanently non-redeemable, making the "cheap first depositor" attack economically infeasible.

However, `lp_mint` is unpacked directly from the caller-supplied `amm_lp_mint_info` account with no validation of its `decimals` field: [2](#0-1) 
Only `supply == 0`, `mint_authority`, and `freeze_authority` are checked — `decimals` is never constrained. Since the pool creator supplies (and can pre-create) the LP mint account itself, they can set `decimals = 0`, reducing the "locked" MINIMUM_LIQUIDITY offset from `10^decimals` to `1`. This lets the creator bootstrap a pool where `amm.lp_amount` is arbitrarily small (e.g. `2`) while owning nearly all of the actually-minted LP supply.

Separately, `Deposit`/`Withdraw`/`Swap*` all compute pool totals directly from the live vault token-account balances via `calc_total_without_take_pnl_no_orderbook`: [3](#0-2) 
```
let total_pc_without_take_pnl = pc_amount.checked_sub(amm.state_data.need_take_pnl_pc)...;
let total_coin_without_take_pnl = coin_amount.checked_sub(amm.state_data.need_take_pnl_coin)...;
```
where `pc_amount`/`coin_amount` come straight from `amm_pc_vault.amount` / `amm_coin_vault.amount` — the actual SPL token account balances (see call sites at `program/src/processor.rs:1148-1153`, `1719-1724`, `1940-1945`, `2154-2159`). Because these vault accounts are ordinary SPL token accounts owned by the AMM authority PDA, anyone can increase their balances with a plain `spl_token::instruction::transfer` (no Raydium instruction required) without any corresponding change to `amm.lp_amount`.

`process_deposit` then mints new LP proportionally to the *current* (potentially donation-inflated) total, floored: [4](#0-3) 
```
// coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output)
let invariant_coin = InvariantPool { token_input: deduct_coin_amount, token_total: total_coin_without_take_pnl };
mint_lp_amount = invariant_coin.exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)...;
```
This is exactly the ratio-based share-mint formula (`shares = deposit * totalSupply / totalAssets`) that the referenced report flags as vulnerable to donation manipulation when the totalSupply-to-totalAssets ratio can be driven to an extreme by a party who controls both share issuance and the "assets" balance.

### Impact Explanation
An attacker who creates the pool (permissionless — `Initialize2` is callable by anyone) can:
1. Create the pool supplying a self-created LP mint with `decimals = 0`, contributing minimal `init_coin_amount`/`init_pc_amount` such that `sqrt(pc*coin)` is only slightly above `1`. This yields `amm.lp_amount` = a very small integer (e.g. `2`) while the attacker holds nearly all actually-minted LP supply (e.g. `1` token).
2. Directly transfer (donate) large amounts of coin/pc tokens into `amm_coin_vault`/`amm_pc_vault` via plain SPL transfers, inflating `total_coin_without_take_pnl`/`total_pc_without_take_pnl` without increasing `amm.lp_amount`.
3. Wait for/induce a legitimate user to call `Deposit` with a sizeable amount. Because `mint_lp_amount = floor(deposit * amm.lp_amount / total_without_pnl)` with a tiny numerator (`amm.lp_amount`) and huge denominator (donation-inflated total), the depositor receives disproportionately few LP tokens relative to the value they contribute, transferring value to the attacker's existing LP position.
4. The attacker then calls `Withdraw`, redeeming their LP tokens against the now-inflated total (including the victim's deposit and the attacker's own donation), extracting more value proportionally than they put in — a direct theft of depositor funds, matching the impact class described in the source report (share-price manipulation leading to fund theft from later depositors).

This satisfies "concrete theft ... of user or LP funds" for a High-severity classification.

### Likelihood Explanation
The attack requires only unprivileged, permissionless actions reachable from a single instruction sequence with attacker-chosen accounts: `Initialize2` (self-supplied LP mint with attacker-chosen decimals), a plain SPL Token `Transfer` to the vaults (no program CPI needed, since vaults are regular token accounts), and `Deposit`/`Withdraw`. No privileged signer, leaked key, or off-chain component is required. The main precondition is that a victim actually deposits into this specific newly created, low-liquidity pool — which is a realistic scenario for new/thin pools that get discovered and deposited into by aggregators, bots, or unaware LPs shortly after creation.

### Recommendation
- Enforce a fixed/known LP-mint decimals value (e.g. require `lp_mint.decimals == 9`, or derive/create the LP mint as a program-controlled PDA with fixed decimals) instead of trusting caller-supplied mint metadata for the `MINIMUM_LIQUIDITY` computation in `process_initialize2`.
- Enforce an absolute minimum `init_pc_amount`/`init_coin_amount` (in addition to the decimal-derived offset) so `liquidity` cannot be trivially close to the offset.
- Consider tracking pool reserves internally (as accounted deltas from `Deposit`/`Swap`/`Withdraw`) rather than reading live vault balances directly, so unsolicited external transfers to the vaults cannot be used to manipulate `total_coin_without_take_pnl`/`total_pc_without_take_pnl` used in share-mint math.

### Proof of Concept
1. Attacker calls `initialize2` supplying a freshly created LP mint with `decimals = 0`, `init_pc_amount = 2`, `init_coin_amount = 2` (or values making `sqrt(pc*coin)` just above `1`). Result: `amm.lp_amount = 2`, attacker receives `user_lp_amount = 1` LP token (`program/src/processor.rs:908-929`).
2. Attacker transfers (via plain `spl_token::transfer`, not through the Raydium program) a large amount `D` of coin and pc tokens directly into `amm_coin_vault`/`amm_pc_vault`, inflating live balances without touching `amm.lp_amount`.
3. Victim calls `deposit` with `max_coin_amount ≈ D` (a "fair" sized deposit relative to the now-inflated pool). `total_coin_without_take_pnl ≈ D`; `mint_lp_amount = floor(deposit_coin * amm.lp_amount(=2) / total_coin_without_take_pnl(≈D)) `, yielding only `1` new LP token for a deposit comparable in size to the whole pool (`program/src/processor.rs:1243-1250`).
4. Attacker calls `withdraw` for their `1` LP token; because circulating supply is now `2` (attacker `1`, victim `1`) but pool value roughly doubled from the victim's deposit, the attacker's share of proceeds (`program/src/processor.rs:1752-1761`) exceeds their original contribution proportionally, realizing profit extracted from the victim's deposit.

### Citations

**File:** program/src/processor.rs (L897-906)
```rust
        let lp_mint = Self::unpack_mint(&amm_lp_mint_info, spl_token_program_id)?;
        if lp_mint.supply != 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if COption::Some(*amm_authority_info.key) != lp_mint.mint_authority {
            return Err(AmmError::InvalidOwner.into());
        }
        if lp_mint.freeze_authority.is_some() {
            return Err(AmmError::InvalidFreezeAuthority.into());
        }
```

**File:** program/src/processor.rs (L908-929)
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

        // liquidity is measured in terms of token_a's value since both sides of
        // the pool are equal
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_token_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            init.nonce,
            user_lp_amount,
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

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```
