## Title
First-Pool-Creator Can Nullify the LP Virtual-Liquidity Floor by Choosing a Zero/Low-Decimal Coin Mint, Enabling Donation-Based Share-Price Inflation - ([File: program/src/processor.rs])

### Summary
`process_initialize2` derives the LP mint's decimals directly from the attacker-supplied `coin_mint` and uses `10^lp_decimals` as the only "virtual liquidity" floor subtracted from the initial LP supply. Because the pool creator freely chooses `coin_mint` (and the OpenBook market backing it), they can use a mint with `decimals = 0`, reducing the permanent floor to `10^0 = 1`. This defeats the intended Uniswap-V2-style minimum-liquidity protection and lets the pool creator mint essentially all of `sqrt(coin*pc)` LP tokens to themselves, then inflate the pool's real token balances via a plain SPL transfer so that subsequent depositors' LP-mint calculation rounds to zero (or to a value producing severe rounding loss), exactly the bug class described in the report (first depositor manipulates share price via a low/degenerate share-to-asset accounting granularity, combined with donation).

### Finding Description
In `process_initialize2`: [1](#0-0) 

`lp_decimals` is set to `coin_mint.decimals`, and this value is used to create the LP mint. Later, the floor is computed as: [2](#0-1) 

```
let liquidity = sqrt(pc_vault.amount * coin_vault.amount);
let user_lp_amount = liquidity - 10^lp_mint.decimals;
```

`amm.lp_amount` is set to the full `liquidity` value, and `user_lp_amount` (the amount actually minted) is `liquidity` minus the "locked"/virtual portion. This asymmetry — where `amm.lp_amount` (the accounting denominator used in `Deposit`/`Withdraw`) can never fall below the unminted `10^decimals` offset — is the pool's only defense against the classic first-depositor share-inflation attack, functioning like the OpenZeppelin virtual-shares fix.

However, `coin_mint` is a completely attacker-controlled account (any SPL mint paired with a permissionlessly-creatable OpenBook market can be used). The creator can mint an SPL token with `decimals = 0` and use it as `coin_mint`. This collapses the floor to `10^0 = 1`, i.e. `user_lp_amount = liquidity - 1`. The only guard against a pool with degenerate liquidity is: [3](#0-2) 

which merely requires vault balances to be non-zero, and [4](#0-3) 

which only fails if `liquidity <= 10^decimals` — trivially satisfied (`liquidity > 1`) when decimals is 0.

With this, the creator can initialize a pool with e.g. `init_coin_amount = 1`, `init_pc_amount = 4`, yielding `liquidity = 2` and `user_lp_amount = 1`, so `amm.lp_amount == 1` and the creator holds the entire LP supply.

Both `Deposit` and `Withdraw` compute the pool's tradable balances by reading the **live** SPL vault balances directly: [5](#0-4) 

There is no "internal accounting vs. real balance" desync requiring a `sync()` call as in the referenced report — any plain token transfer to `amm_coin_vault`/`amm_pc_vault` immediately and directly inflates `total_coin_without_take_pnl` / `total_pc_without_take_pnl` used in share-price math for every subsequent depositor/withdrawer, while `amm.lp_amount` (the share denominator) stays at `1`.

A subsequent depositor's minted LP amount is computed with floor rounding: [6](#0-5) 

With `amm.lp_amount == 1` and vault balances inflated by a large donation, `mint_lp_amount` for any deposit not matching the inflated ratio nearly exactly rounds down to `0`, which reverts the deposit: [7](#0-6) 

Symmetrically, `Withdraw` also floor-rounds against `amm.lp_amount`: [8](#0-7) 

so any depositor who does manage to deposit at the required (attacker-dictated) inflated ratio, and any subsequent partial withdrawal, suffers rounding losses that accrue to the attacker's single remaining LP token, mirroring the exact mechanism in the referenced report.

### Impact Explanation
This breaks the pool's core invariant that LP share value should track deposited assets proportionally for all participants. The pool creator can, at negligible cost (a self-created 0-decimal mint and a minimal Initialize2 call), collapse the anti-inflation floor to `1`, then use ordinary SPL token transfers to the vaults to:
- Permanently deny deposits to normal users unless they deposit amounts matching the attacker-chosen, arbitrarily inflated ratio (freezing the pool for practical LP use), and/or
- Force any successful depositor to lose value to floor-rounding, which is captured by the attacker's own LP token upon withdrawal.

This is a concrete mechanism for insolvent/unfair pool accounting and fund loss for LPs, reachable by any unprivileged pool creator using only `Initialize2` and standard SPL transfers — no privileged signer or off-chain component required.

### Likelihood Explanation
Likelihood is high: pool creation via `Initialize2` is fully permissionless, `coin_mint` is entirely attacker-supplied, and creating a 0-decimal SPL token plus pairing it with an OpenBook market is a normal, low-cost, unprivileged operation. No special timing/front-running is even required beyond the creator being the pool initializer, which they already are by construction.

### Recommendation
Use a fixed, protocol-defined minimum liquidity constant (independent of the attacker-controlled `coin_mint.decimals`) for the burned/virtual LP amount in `process_initialize2`, or enforce a minimum absolute `liquidity` value (e.g., require `liquidity` to exceed a large fixed constant such as `10^9`) regardless of the LP mint's decimals, so the virtual-liquidity offset cannot be trivially nullified by choosing a low-decimal coin mint.

### Proof of Concept
1. Attacker creates an SPL mint `coin_mint` with `decimals = 0` and total supply they control, and creates (or uses) an OpenBook market pairing it with any `pc_mint`.
2. Attacker calls `Initialize2` with `init_coin_amount = 1`, `init_pc_amount = 4` (so `liquidity = sqrt(1*4) = 2`); `lp_decimals = coin_mint.decimals = 0` so `user_lp_amount = 2 - 10^0 = 1`. Attacker now holds the entire LP supply (`1` token), and `amm.lp_amount == 1`.
3. Attacker transfers a large amount of `coin_mint`/`pc_mint` tokens directly to `amm_coin_vault`/`amm_pc_vault` via a normal SPL `Transfer` (no special instruction needed, since `Deposit`/`Withdraw` read live vault balances, per `processor.rs` lines 1138–1153).
4. Any victim calling `Deposit` with typical amounts now computes `mint_lp_amount` via `exchange_token_to_pool(amm.lp_amount = 1, Floor)` (processor.rs lines 1243–1250), which rounds to `0` and reverts (`processor.rs` lines 1323–1325), or, if the victim deposits at the exact inflated ratio, receives a share so coarse that any imprecision in future withdrawals rounds in favor of the attacker's single LP token (processor.rs lines 1751–1761). [9](#0-8)

### Citations

**File:** program/src/processor.rs (L760-774)
```rust
        // create lp mint account
        let lp_decimals = coin_mint.decimals;
        Self::generate_amm_associated_spl_mint(
            program_id,
            spl_token_program_id,
            market_info,
            amm_lp_mint_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            token_program_info,
            amm_authority_info,
            LP_MINT_ASSOCIATED_SEED,
            lp_decimals,
        )?;
```

**File:** program/src/processor.rs (L858-863)
```rust
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
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

**File:** program/src/processor.rs (L1323-1325)
```rust
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

**File:** program/src/error.rs (L142-143)
```rust
    #[error("Initial LP amount is too low.")]
    InitLpAmountTooLess,
```
