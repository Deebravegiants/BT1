## Title
Deposit mints LP tokens and updates virtual PnL reserves based on intended transfer amounts instead of actual vault balance changes, enabling LP dilution and pool-breaking accounting drift for fee-on-transfer tokens - (File: `program/src/processor.rs`)

### Summary
`process_deposit` computes `mint_lp_amount` and updates `target_orders.calc_pnl_x` / `calc_pnl_y` using the *intended* deposit amounts (`deduct_coin_amount`, `deduct_pc_amount`) before invoking `Invokers::token_transfer`, and never re-reads the vault's actual post-transfer balance to confirm how much was really received. For any coin/pc mint that charges a transfer fee (fee-on-transfer SPL tokens, or Token-2022 mints with the `TransferFeeConfig` extension, which the program does not exclude), the vaults will receive strictly less than `deduct_coin_amount`/`deduct_pc_amount`, but the program still mints LP tokens and books internal PnL reserves as if the full amount arrived.

### Finding Description
In `process_deposit` (`program/src/processor.rs:1138-1372`), the deduct amounts and `mint_lp_amount` are derived purely from the pre-transfer vault balances (`amm_coin_vault.amount`, `amm_pc_vault.amount`) and the user-specified `deposit.max_coin_amount`/`max_pc_amount`: [1](#0-0) 
The resulting `deduct_coin_amount`/`deduct_pc_amount` are then transferred via a plain SPL `Transfer` CPI with no balance-delta verification: [2](#0-1) 
Immediately after, `amm.lp_amount` is incremented by `mint_lp_amount`, and the virtual PnL reserves are updated using `deduct_pc_amount`/`deduct_coin_amount` (the intended amounts) rather than any observed delta in vault balance: [3](#0-2) 

Because the vault token accounts are unpacked once, before the transfer, at line 1138-1140, there is no post-transfer read-back to reconcile actual received amount vs. requested amount: [4](#0-3) 

For a fee-on-transfer token, the real coin/pc vault balance increases by `deduct_amount - fee`, while `mint_lp_amount` and `target_orders.calc_pnl_x/y` are computed as if the full `deduct_amount` landed. This directly causes:
1. **Unbacked LP minting / dilution** — the depositor receives LP tokens sized for the full intended deposit while only a smaller amount of real value entered the vault, diluting existing LPs' claim on pool assets.
2. **Corrupted virtual reserve accounting** — `target_orders.calc_pnl_x`/`calc_pnl_y` (the "invariant before pnl" reserves used every single subsequent instruction) drift further and further above the token amounts actually backing the pool.

This corrupted `calc_pnl_x`/`calc_pnl_y` feeds `calc_take_pnl`, which computes `need_take_pnl_pc`/`need_take_pnl_coin` in `AmmInfo.state_data` used by `Calculator::calc_total_without_take_pnl_no_orderbook`: [5](#0-4) 
This function is called by every deposit, withdraw, and swap instruction to compute pool reserves, and uses `checked_sub` that returns `AmmError::CheckedSubOverflow` if the tracked `need_take_pnl_*` value ever exceeds the real vault balance. Since fee-on-transfer deposits systematically overstate the pool's real backing relative to the tracked virtual reserves, repeated deposits of such tokens can push the tracked pnl reserves above the real vault balance, causing this subtraction to fail — bricking every instruction that touches the pool (deposit, withdraw, all four swap variants), permanently freezing the funds of every LP in the pool.

### Impact Explanation
- Immediate: LP token minting is decoupled from actual assets received, letting a depositor of a fee-on-transfer token dilute all other LPs (loss of LP funds), or (depending on rounding) cause insolvent pool accounting where the sum of LP claims exceeds real vault assets.
- Longer-term/systemic: accumulated drift between the program's internal PnL/reserve bookkeeping and the real vault balances can trigger `AmmError::CheckedSubOverflow` in `calc_total_without_take_pnl_no_orderbook`, which is invoked from deposit, withdraw, and all swap instructions — permanently freezing every user's and LP's funds in the pool once triggered.

### Likelihood Explanation
Any unprivileged user can create a pool (`Initialize2`) or deposit into an existing pool for a coin/pc mint they choose. Nothing in `process_deposit` restricts the coin/pc mint to fee-free SPL Token program mints; Token-2022 mints with `TransferFeeConfig`, or any custom fee-charging token accepted as a pool asset, trigger this path on every deposit call. The attacker only needs one transaction (a single `Deposit` instruction) with attacker-chosen mint/vault accounts to realize the LP-dilution impact, and repeated normal use of such a pool progressively increases the risk of the reserve-accounting freeze.

### Recommendation
In `process_deposit`, re-read the coin/pc vault token account balances after invoking `Invokers::token_transfer` and compute `mint_lp_amount` and the `target_orders.calc_pnl_x`/`calc_pnl_y` updates from the actual balance delta (`post_balance - pre_balance`) rather than from the pre-transfer `deduct_coin_amount`/`deduct_pc_amount` values. The same pattern should be applied to `Initialize2` and swap instructions' input-side transfers to keep on-chain reserve tracking consistent with real vault balances regardless of the token's transfer semantics.

### Proof of Concept
1. Create (or use) a pool whose coin or pc mint is a Token-2022 mint with a `TransferFeeConfig` extension charging, e.g., 1% fee on transfer (or any custom fee-on-transfer SPL-compatible token accepted by the pool).
2. Call `Deposit` with `max_coin_amount = 1,000,000`, `base_side = 0`. `process_deposit` computes `deduct_coin_amount = 1,000,000` and a corresponding `deduct_pc_amount`, and `mint_lp_amount` based on the pool's current `lp_amount` and `total_coin_without_take_pnl` [6](#0-5) .
3. `Invokers::token_transfer` moves `1,000,000` from the user, but due to the 1% fee, `amm_coin_vault` only receives `990,000`.
4. The program still mints `mint_lp_amount` LP tokens computed for the full `1,000,000` [7](#0-6) , and books `target_orders.calc_pnl_x`/`calc_pnl_y` as though `1,000,000` was received [8](#0-7) , diluting existing LP holders and permanently overstating internal reserves relative to the real vault balance.

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

**File:** program/src/processor.rs (L1341-1371)
```rust
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

        target_orders.calc_pnl_x = x1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
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
