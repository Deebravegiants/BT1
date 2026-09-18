### Title
Vault-inflation-style share manipulation via `amm.lp_amount` accounting divergence from real `lp_mint` supply - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` computes `liquidity = sqrt(pc_amount * coin_amount)` and only mints `user_lp_amount = liquidity - 10^lp_decimals` real SPL LP tokens to the pool creator, while setting the internal accounting field `amm.lp_amount = liquidity` (the full, un-discounted value). [1](#0-0)  Every subsequent `Deposit`/`Withdraw` share-price computation uses `amm.lp_amount` (not the real `lp_mint.supply`) as the "total shares" denominator: `mint_lp_amount = invariant.exchange_token_to_pool(amm.lp_amount, ...)` and `coin_amount = invariant.exchange_pool_to_token(total_coin_without_take_pnl, ...)` with `token_total: amm.lp_amount`. [2](#0-1) [3](#0-2) 

### Finding Description
This is structurally the same pattern flagged in the Peapods H-2 report: an initial "dead"/minimum-liquidity quantity is folded into the total-supply figure used for exchange-rate math, but is not actually held by a burned/unspendable account — instead of being permanently unredeemable it is simply *never minted at all*, while `amm.lp_amount` still counts it as if it existed. The pool creator who calls `Initialize2` fully controls `init_pc_amount`/`init_coin_amount` (arbitrary user-chosen values in the same transaction), so — unlike the Peapods case, which required front-running a factory deploy — the creator here is trivially the "attacker" from turn one, with no race condition needed.

An attacker can choose `init_coin_amount`/`init_pc_amount` such that `liquidity` is only marginally above `10^lp_decimals` (checked via `checked_sub(...).ok_or(AmmError::InitLpAmountTooLess)`), so they receive only a small number of *real* LP tokens (e.g. `user_lp_amount = 1`) while `amm.lp_amount` records the full `liquidity` value. [4](#0-3)  Because `calc_total_without_take_pnl_no_orderbook` derives pool assets from the *live* vault token balances rather than a cached total, an attacker can donate tokens directly to `amm_coin_vault`/`amm_pc_vault` to inflate `total_coin_without_take_pnl`/`total_pc_without_take_pnl` without affecting `amm.lp_amount`. [5](#0-4)  The attacker (holding real, spendable LP tokens, since they were minted directly to them, not to a dead address) can then loop `Deposit`/`Withdraw` to compound rounding in their favor — `exchange_token_to_pool` rounds `Floor` on deposit and `exchange_pool_to_token` rounds `Floor` on withdraw — driving up the effective coin/pc-per-LP-share ratio while `amm.lp_amount` stays artificially small. `process_withdraw`'s only floor protections are `withdraw.amount >= amm.lp_amount` (must leave at least 1 unit of `amm.lp_amount`) and non-zero output checks, which do not prevent the share price from being pushed to an extreme value. [6](#0-5)  A subsequent victim's `Deposit` computes `mint_lp_amount` via the same `Floor`-rounded formula against the inflated `amm.lp_amount`/vault-balance ratio, and can receive far fewer LP tokens than their deposit is proportionally worth (only guarded by an all-or-nothing `mint_lp_amount == 0` revert, not by any minimum-share-value protection). [7](#0-6) 

### Impact Explanation
If exploitable, this allows the pool creator to later extract value from subsequent depositors via rounding-driven share dilution — the exact class of loss identified in the source report (attacker profit, victim loss) rather than a benign self-inflicted loss, since victims are typical LPs interacting with what appears to be a normal pool.

### Likelihood Explanation
Low/uncertain. Two structural differences from the Peapods bug significantly reduce or eliminate exploitability, and I could not fully verify within the available tool budget whether they close the path entirely:
1. `checked_sub(...).ok_or(AmmError::InitLpAmountTooLess)` requires `liquidity > 10^lp_decimals`; the practical minimum real-LP mint an attacker can achieve depends on `lp_decimals` (= `coin_mint.decimals`), which is developer-controlled at mint-creation time, not attacker-controlled at pool-creation time in most real-world coin mints (typically 6–9 decimals), making `liquidity` need to exceed a fairly large threshold (e.g. `10^6`) before any real LP is mintable — this is a much larger "dead" buffer than Peapods' fixed `1e3`, and the profitable-inflation math from the original PoC (which relied on a very small total supply, e.g. 1 share) may not be economically reachable.
2. I was unable to fully trace `calc_take_pnl` and the PnL-accounting adjustments applied to `total_pc_without_take_pnl`/`total_coin_without_take_pnl` before the exchange-rate math in `process_withdraw`/`process_deposit`, which could further dampen or block the donation-based inflation step described above; this needs deeper verification (e.g. of `Calculator::calc_take_pnl` in `program/src/math.rs`) that was not completed.

Given this uncertainty and the significantly larger practical "dead-share" floor compared to the reference bug, I cannot confirm this rises to a concretely provable Medium/High finding rather than a structurally-similar-but-likely-mitigated pattern.

### Recommendation
If confirmed exploitable: mint the discounted `MINIMUM_LIQUIDITY`-equivalent portion (`10^lp_decimals`) to a burn/dead LP token account instead of implicitly excluding it from the real mint while still counting it in `amm.lp_amount`, so `amm.lp_amount` accurately reflects tokens that exist and are permanently unredeemable, closing the gap between real supply and the accounting total used in share-price math.

### Proof of Concept
Not independently constructed/tested — a concrete PoC would require simulating `Initialize2` with `lp_decimals` chosen at the low end, followed by direct vault-token donation and a `Deposit`/`Withdraw` loop, and comparing a subsequent victim `Deposit`'s minted LP amount against their proportional deposit value. This was not completed given the tool-call budget; treat this finding as a hypothesis requiring further validation rather than a proven exploit.

### Citations

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

**File:** program/src/processor.rs (L1319-1350)
```rust
        if deduct_coin_amount > user_source_coin.amount || deduct_pc_amount > user_source_pc.amount
        {
            return Err(AmmError::InsufficientFunds.into());
        }
        if mint_lp_amount == 0 || deduct_coin_amount == 0 || deduct_pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }

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
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_dest_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            amm.nonce as u8,
            mint_lp_amount,
        )?;
        amm.lp_amount = amm.lp_amount.checked_add(mint_lp_amount).unwrap();
```

**File:** program/src/processor.rs (L1713-1777)
```rust
        if withdraw.amount > user_source_lp.amount {
            return Err(AmmError::InsufficientFunds.into());
        }
        if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
            return Err(AmmError::NotAllowZeroLP.into());
        }
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );

        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }

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

        encode_ray_log(WithdrawLog {
            log_type: LogType::Withdraw.into_u8(),
            withdraw_lp: withdraw.amount,
            user_lp: user_source_lp.amount,
            pool_coin: total_coin_without_take_pnl,
            pool_pc: total_pc_without_take_pnl,
            pool_lp: amm.lp_amount,
            calc_pnl_x: target_orders.calc_pnl_x,
            calc_pnl_y: target_orders.calc_pnl_y,
            out_coin: coin_amount,
            out_pc: pc_amount,
        });
        if withdraw.amount == 0 || coin_amount == 0 || pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```
