### Title
Direct SPL token donations to `amm_coin_vault`/`amm_pc_vault` desynchronize real pool balances from `amm.lp_amount`, enabling an ERC4626-style inflation attack on `Deposit`/`Withdraw` - (File: `program/src/processor.rs`)

### Summary
Raydium's constant-product pool tracks LP ownership with a scalar field `amm.lp_amount`, while the actual redeemable value is computed from the *live* SPL token balances of `amm_coin_vault`/`amm_pc_vault`. Because these vault accounts are ordinary SPL Token accounts owned by the AMM authority PDA, anyone can transfer extra tokens into them directly using the SPL Token program, without going through `Deposit`. This creates the exact "donation/inflation" precondition described in the referenced ERC4626 report: total assets can be inflated independently of the LP-share ledger, and a subsequent depositor's `mint_lp_amount` computation rounds down disproportionately, letting the pool creator later capture more than their fair share on `Withdraw`.

### Finding Description
- `process_initialize2` mints only `user_lp_amount = liquidity - 10^lp_decimals` real LP tokens to the pool creator, while `amm.lp_amount` is set to the full `liquidity = sqrt(coin*pc)` value: [1](#0-0) , [2](#0-1) . This is a fixed "virtual liquidity" offset (analogous to Uniswap V2's `MINIMUM_LIQUIDITY`), but it is a constant amount, not a value that scales with an attacker-chosen donation.
- `process_deposit` computes `total_coin_without_take_pnl`/`total_pc_without_take_pnl` from the *actual* vault balances (`amm_coin_vault.amount`, `amm_pc_vault.amount`) via `Calculator::calc_total_without_take_pnl_no_orderbook`, and then computes `mint_lp_amount` as `deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` (Floor rounding): [3](#0-2) , [4](#0-3) .
- `process_withdraw` mirrors this: it computes `coin_amount`/`pc_amount` as `withdraw.amount * total_coin_without_take_pnl / amm.lp_amount` (Floor), again using the live vault balances as numerator and the LP ledger as denominator: [5](#0-4) .
- Nothing in `Deposit`/`Withdraw` verifies that `amm_coin_vault.amount`/`amm_pc_vault.amount` match what would be expected from `amm.lp_amount` and prior instruction history — they simply trust the current SPL balance. An attacker can therefore:
  1. Call `Initialize2` (unprivileged, any user can create a pool) with a small `init_coin_amount`/`init_pc_amount` just above the `InitLpAmountTooLess` floor, becoming sole LP holder of a small `user_lp_amount`.
  2. Use a plain SPL Token `Transfer`/`TransferChecked` instruction (not routed through the AMM program) to donate a large amount of coin and pc tokens directly into `amm_coin_vault`/`amm_pc_vault`, inflating `total_coin_without_take_pnl`/`total_pc_without_take_pnl` while `amm.lp_amount` stays unchanged.
  3. Wait for (or front-run) a victim's `Deposit`; the victim's `mint_lp_amount` rounds down severely because `amm.lp_amount` (denominator numerator side) is now tiny relative to the inflated `total_coin_without_take_pnl` (denominator).
  4. Call `Withdraw` with the original small LP amount; `coin_amount`/`pc_amount` are computed as a fraction of the inflated real vault balances (now including the victim's freshly-deposited assets), so the attacker extracts more value than they contributed.

### Impact Explanation
This allows the pool-creator/attacker to steal a portion of a subsequent depositor's coin/pc tokens by manipulating the implied LP share price through direct vault donations, which is not prevented by the fixed `10^lp_decimals` virtual-liquidity offset applied only at `Initialize2`. This is a direct theft of user funds from LP depositors, matching the High severity of the referenced report.

### Likelihood Explanation
Creating a pool via `Initialize2` and depositing/withdrawing are all unprivileged, single-transaction operations reachable by any user. Donating tokens to a vault via a standard SPL Token transfer requires no special privilege — the vault is just a normal token account owned by the AMM authority PDA. The attack is most practical on newly created, low-liquidity pools where the attacker controls the initial LP supply, which is a realistic and common scenario for new pools on Raydium.

### Recommendation
Do not trust raw `amm_coin_vault.amount`/`amm_pc_vault.amount` as the sole basis for share-price calculations in `Deposit`/`Withdraw`. Consider tracking accounted vault balances internally (updated only through program instructions) and reconciling/capping any external donations, or enforce a substantially larger, non-bypassable minimum-liquidity lock (proportional to deposit size rather than a fixed `10^decimals`) similar to virtual-share offsets recommended in the referenced mitigation, and add sanity checks comparing tracked vs. actual vault balances before allowing deposit/withdraw math to proceed.

### Proof of Concept
Not independently executed against a live cluster; based on static analysis of `process_initialize2`, `process_deposit`, and `process_withdraw` cited above. Conceptual reproduction:
1. Attacker calls `Initialize2` with minimal `init_coin_amount`/`init_pc_amount` just above the floor set at [6](#0-5) , receiving nearly all resulting LP tokens.
2. Attacker issues a raw SPL `Transfer` into `amm_coin_vault` and `amm_pc_vault` (bypassing `Deposit`), inflating balances read at [7](#0-6) .
3. Victim calls `Deposit`; `mint_lp_amount` computed at [4](#0-3)  rounds down heavily due to the inflated denominator.
4. Attacker calls `Withdraw`, redeeming a share of the now-inflated pool (including the victim's deposit) at [8](#0-7) , capturing more value than originally contributed.

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

**File:** program/src/processor.rs (L967-977)
```rust
        amm.coin_vault = *amm_coin_vault_info.key;
        amm.pc_vault = *amm_pc_vault_info.key;
        amm.coin_vault_mint = *amm_coin_mint_info.key;
        amm.pc_vault_mint = *amm_pc_mint_info.key;
        amm.lp_mint = *amm_lp_mint_info.key;
        amm.open_orders = Pubkey::default();
        amm.market = *market_info.key;
        amm.market_program = Pubkey::default();
        amm.target_orders = *amm_target_orders_info.key;
        amm.amm_owner = config_feature::amm_owner::ID;
        amm.lp_amount = liquidity;
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

**File:** program/src/processor.rs (L1719-1761)
```rust
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
```
