## Title
Fee-on-transfer tokens cause unbacked LP minting / dilution in `process_deposit` - ([File: program/src/processor.rs])

### Summary
Raydium's `Deposit` instruction computes the LP tokens to mint from the *nominal* `deduct_coin_amount`/`deduct_pc_amount` requested by the depositor, then separately calls `Invokers::token_transfer` to move that same nominal amount from the user into the AMM vaults. If either the coin or pc mint is a fee-on-transfer (deflationary) SPL token, the vault will receive strictly less than `deduct_coin_amount`/`deduct_pc_amount`, but the depositor is still credited LP tokens as if the full nominal amount had landed in the vault. This mints LP shares that are not fully backed by pool assets, diluting existing LPs.

### Finding Description
In `process_deposit` (program/src/processor.rs), the pool's real on-chain balances are read via `unpack_token_account` before the transfer: [1](#0-0) 

The mint amount is then derived purely from the nominal deposit amount and the current pool ratio, with no dependency on what the vault will actually receive: [2](#0-1) 

Finally, the nominal `deduct_coin_amount`/`deduct_pc_amount` is transferred via `Invokers::token_transfer`, and `mint_lp_amount` (computed from the same nominal, pre-fee amount) is minted regardless of the amount actually credited to the vault: [3](#0-2) 

`Invokers::token_transfer` is a thin wrapper over `spl_token::instruction::transfer` and performs no post-transfer balance verification, so a transfer-fee token silently delivers less than `deduct_coin_amount`/`deduct_pc_amount` to the vault while the caller still mints LP based on the full nominal amount: [4](#0-3) 

Because the next operation (deposit, withdraw, or swap) recomputes `total_coin_without_take_pnl`/`total_pc_without_take_pnl` directly from the vault's actual (post-fee) balance via `Calculator::calc_total_without_take_pnl_no_orderbook`, the pool's true backing is permanently lower than what the LP mint assumed at deposit time: [5](#0-4) 

This is the same root-cause class as the referenced report: a promised/nominal token amount is used in critical accounting math instead of the amount actually moved, and the protocol has no mechanism to detect or compensate for the difference when the underlying token charges a transfer fee.

### Impact Explanation
Every fee-on-transfer-token deposit mints LP shares that overstate the value actually contributed to the pool. This permanently dilutes all other LP holders' redeemable share of `coin_vault`/`pc_vault`, i.e., insolvent pool accounting / unbacked LP minting — funds can be withdrawn by the over-minted depositor (and later withdrawers) in excess of what they contributed, at the expense of other liquidity providers. Repeated deposits compound the dilution, and because Raydium AMM pools are permissionless and can be created for arbitrary SPL mints (including deflationary/fee-on-transfer tokens), this is directly reachable by any unprivileged depositor calling `Deposit` with attacker-chosen accounts/data.

### Likelihood Explanation
Likelihood is Medium: it requires the pool's coin or pc mint to implement a transfer fee (uncommon among today's mainstream SPL tokens, but not disallowed by the program, which performs no check rejecting such mints on `Initialize2` or `Deposit`). Any pool created for such a token is immediately and continuously exposed on every deposit.

### Recommendation
For deposits, measure the vault's actual token-account balance immediately before and after the `token_transfer` calls, and use the observed delta (rather than the nominal `deduct_coin_amount`/`deduct_pc_amount`) when computing `mint_lp_amount`, mirroring how withdraw/swap already derive pool totals from live vault balances. Alternatively, explicitly reject Token-2022 mints with the `TransferFeeConfig` extension (or any known fee-on-transfer mint) during `Initialize2`.

### Proof of Concept
1. Attacker (or anyone) creates a Raydium pool via `Initialize2` where the `coin_mint` is a fee-on-transfer SPL/Token-2022 mint (e.g., 1% transfer fee) and `pc_mint` is a normal token.
2. Pool has existing liquidity, e.g. `total_coin_without_take_pnl = 100_000`, `lp_amount = 100_000`.
3. Attacker calls `Deposit` with `base_side = 0`, `max_coin_amount = 10_000` (and corresponding pc amount).
4. `mint_lp_amount` is computed as `10_000 / 100_000 * 100_000 = 10_000` LP tokens (program/src/processor.rs:1243-1250).
5. `Invokers::token_transfer` moves `deduct_coin_amount = 10_000` from the attacker, but due to the 1% fee only `9_900` actually lands in `amm_coin_vault` (program/src/processor.rs:1327-1333, program/src/invokers.rs:148-168).
6. Attacker is minted `10_000` LP tokens backed by only `9_900` coin tokens of real value; the shortfall is socialized across all existing LPs the moment the true vault balance is used in the next `Deposit`/`Withdraw`/`Swap` calculation (program/src/math.rs:238-250).
7. Attacker can immediately withdraw, extracting more value than actually deposited, at other LPs' expense.

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

**File:** program/src/processor.rs (L1327-1350)
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

**File:** program/src/invokers.rs (L147-168)
```rust
    /// Issue a spl_token `Transfer` instruction.
    pub fn token_transfer<'a>(
        token_program: AccountInfo<'a>,
        source: AccountInfo<'a>,
        destination: AccountInfo<'a>,
        owner: AccountInfo<'a>,
        deposit_amount: u64,
    ) -> Result<(), ProgramError> {
        let ix = spl_token::instruction::transfer(
            token_program.key,
            source.key,
            destination.key,
            owner.key,
            &[],
            deposit_amount,
        )?;
        solana_program::program::invoke_signed(
            &ix,
            &[source, destination, owner, token_program],
            &[],
        )
    }
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
