Confirmed: `calc_total_without_take_pnl_no_orderbook` computes pool totals directly from the live SPL vault balances (`pc_amount`, `coin_amount` passed in from `amm_pc_vault_info`/`amm_coin_vault_info`), only subtracting the tracked `need_take_pnl_pc`/`need_take_pnl_coin`. It does not track a separate "supplied" counter independent of the vault's actual token balance, so any direct SPL transfer into the vault immediately inflates `total_pc_without_take_pnl`/`total_coin_without_take_pnl` used in the deposit math. [1](#0-0) 

### Title
Exchange-rate manipulation via direct vault donation causes new depositor share dilution/rounding loss - (File: program/src/processor.rs, program/src/math.rs)

### Summary
`process_deposit` computes the LP amount to mint using the live token balances of `amm_coin_vault`/`amm_pc_vault` (via `calc_total_without_take_pnl_no_orderbook`) as the denominator against the tracked `amm.lp_amount`, rather than an internal, donation-resistant accounting value. An attacker can inflate the vault balances via a plain SPL `Transfer` directly to the vault (bypassing the `Deposit` instruction entirely) before a victim's deposit lands, causing the victim's `mint_lp_amount` calculation to round down disproportionately, transferring value to the existing (attacker-controlled) LP shares.

### Finding Description
In `process_deposit`, the pool's tracked totals come straight from the vault's SPL balance: [2](#0-1) 

The minted LP amount is then computed as `deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` (or the PC-side equivalent), floored: [3](#0-2) [4](#0-3) 

Crucially, `amm.lp_amount` (the internal share-supply denominator) is only ever changed by `Initialize2`, `Deposit`, and `Withdraw` — it is completely decoupled from the vaults' actual SPL balances. `total_coin_without_take_pnl`/`total_pc_without_take_pnl`, however, are read straight from the live vault token account amounts each time. This means anyone can call the standard SPL Token `Transfer` instruction to send tokens directly to `amm.coin_vault` or `amm.pc_vault` (these are just regular token accounts owned by the AMM authority PDA — no special check on the sender) without going through `Deposit`, inflating the vault balance while `amm.lp_amount` stays unchanged.

At pool creation via `Initialize2`, the first LP shares are computed from `sqrt(pc*coin)` and the attacker (as the pool creator) is minted `liquidity - 10^lp_decimals`: [5](#0-4) 
By choosing `init_pc_amount`/`init_coin_amount` such that `sqrt(pc*coin)` is only marginally above `10^lp_decimals`, the attacker can create a pool where they hold a tiny `user_lp_amount` (e.g. 1) while `amm.lp_amount` is also small (≈`10^lp_decimals` + 1). The attacker then front-runs a victim's `Deposit` by donating a large amount directly to the vault, inflating `total_coin_without_take_pnl` (or `total_pc_without_take_pnl`) far beyond `amm.lp_amount`. When the victim's deposit executes, `mint_lp_amount = deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` rounds toward a disproportionately small number of shares relative to the value the victim actually contributed to the vault, because the denominator (`total_coin_without_take_pnl`) has been artificially inflated by the donation while the numerator's scale (`amm.lp_amount`) was kept deliberately tiny by the attacker at pool creation.

The attacker can then withdraw via `process_withdraw`, which uses the same `amm.lp_amount`-based proportional math to redeem their small number of shares for a disproportionately large share of the now-inflated vault balance (including the victim's freshly deposited funds): [6](#0-5) 

This is the same root cause as the referenced Sherlock report: the deposit/withdraw exchange rate is derived from a balance that can be manipulated by a direct token transfer that bypasses the protocol's own share-accounting instruction.

### Impact Explanation
A victim's deposit can be diluted such that they receive far fewer LP shares than their contribution warrants, while the attacker's pre-existing shares (bought cheaply at pool creation) capture the excess value upon withdrawal. This is a direct theft of user deposit funds and an insolvent-share-accounting condition — the LP token no longer represents a fair claim on the underlying vault balances. This qualifies as unbacked/disproportionate LP share issuance and fund theft.

### Likelihood Explanation
The attack requires the attacker to be the pool creator (calling `Initialize2` with a specific small-liquidity ratio) or otherwise catch a newly created, thinly-liquid pool, and to front-run/precede a victim's `Deposit` with a direct SPL `Transfer` to the vault. On Solana this ordering is achievable by an attacker who controls transaction submission timing or who creates the pool themselves and waits for/baits a deposit. It is most exploitable against newly created, low-liquidity pools, similar to the conditions described in the source report.

### Recommendation
Track pool reserves via an internal state field updated only by `Deposit`/`Withdraw`/`Swap` instructions rather than reading live SPL vault balances for share-mint/redeem math, or reconcile/reject deposits when the vault balance deviates unexpectedly from the last known internally-tracked balance. Additionally, consider enforcing a minimum absolute liquidity threshold (not just a fractional minimum tied to decimals) at `Initialize2` so that `amm.lp_amount` cannot be created near the `10^lp_decimals` floor, making the donation-based dilution attack economically impractical.

### Proof of Concept
1. Attacker calls `Initialize2` with `init_pc_amount`/`init_coin_amount` chosen so `liquidity = sqrt(pc*coin)` is just above `10^lp_decimals` (e.g., `liquidity = 10^lp_decimals + N` for small `N`), yielding `amm.lp_amount = 10^lp_decimals + N` and `user_lp_amount = N` minted to the attacker (per [5](#0-4) ).
2. Attacker observes a victim's pending `Deposit` transaction (base_side coin, `max_coin_amount = C`) in the mempool.
3. Attacker submits an SPL `Transfer` of a large amount `D` directly to `amm.coin_vault` before the victim's transaction lands, inflating `total_coin_without_take_pnl` from its prior small value to `prior + D` (per [1](#0-0) ).
4. Victim's `Deposit` executes: `mint_lp_amount = C * amm.lp_amount / (prior + D)` (per [3](#0-2) ), which rounds down to a value far smaller than the victim's proportional contribution because `amm.lp_amount` was kept small at step 1 while the denominator was inflated in step 3.
5. Attacker calls `Withdraw` for their `N`-share LP balance, redeeming a share of `total_coin_without_take_pnl`/`total_pc_without_take_pnl` (now including the victim's deposit) proportional to `N / amm.lp_amount`, extracting value contributed by both their own donation and the victim's deposit (per [6](#0-5) ).

### Citations

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

**File:** program/src/math.rs (L456-477)
```rust
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
