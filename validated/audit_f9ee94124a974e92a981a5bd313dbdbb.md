I have enough evidence to render a verdict now.

### Title
Fee-on-transfer/deflationary SPL tokens corrupt AMM swap, deposit and withdraw accounting - ([File: program/src/processor.rs])

### Summary
Raydium's AMM computes swap/deposit output amounts and updates internal invariant state (`calc_pnl_x`/`calc_pnl_y`, `amm.lp_amount`) using the *nominal* instruction-supplied amount (`swap.amount_in`, `deposit.max_coin_amount`/`max_pc_amount`) rather than the amount actually received by the vault after the `spl_token::instruction::transfer` CPI completes. Any SPL mint whose `Transfer` (or, post-Token-2022, `TransferChecked` with a `TransferFeeConfig` extension) deducts a fee will cause the vault to receive less than the accounted-for amount, permanently desynchronizing the pool's internal accounting from its real token balances.

### Finding Description
In `process_swap_base_in` the pool reads the current vault balances via `Self::unpack_token_account` [1](#0-0) , computes `total_pc_without_take_pnl`/`total_coin_without_take_pnl` from these balances, and then derives `swap_amount_out` purely from `swap.amount_in` and the pre-trade reserves via the constant-product formula [2](#0-1) . It never re-reads the vault balance after the inbound transfer to confirm how much was actually deposited. The subsequent transfers then execute the trade based on that nominal `swap.amount_in`/`swap_amount_out` pair: [3](#0-2) . The identical pattern (transfer-in based on nominal amount, then payout from the other vault, with no post-transfer balance verification) also appears in `process_swap_base_out` [4](#0-3) , and in the two other swap entry points at lines 2402-2424 and 2591-2613 of the same file.

The same root cause affects deposits: `deduct_coin_amount`/`deduct_pc_amount` (computed from the *requested* amounts) are transferred into the vaults and used directly to mint LP tokens and update `calc_pnl_x`/`calc_pnl_y`, again without checking actual post-transfer vault balances: [5](#0-4) .

`Invokers::token_transfer` and `Invokers::token_transfer_with_authority` are thin wrappers around `spl_token::instruction::transfer` that return `Ok(())` as soon as the CPI succeeds, irrespective of the actual amount credited to the destination: [6](#0-5) . Nothing in `Initialize2`'s vault/mint validation restricts `coin_vault_mint`/`pc_vault_mint` to fee-free tokens, so a pool creator can freely pair a standard token with a fee-on-transfer or Token-2022 transfer-fee mint.

### Impact Explanation
Because swap output is computed from the nominal `amount_in` instead of the amount actually credited to the vault, every swap against a fee-on-transfer token silently drains real value from the pool: the payout leg (`amm_pc_vault_info`/`amm_coin_vault_info` → user) is calculated as if the fee never existed, so the pool systematically pays out more than it received. Over repeated swaps this creates a growing insolvency between one side's real balance and the internal invariant (`total_coin_without_take_pnl`/`total_pc_without_take_pnl`, `calc_pnl_x`/`calc_pnl_y`), permanently impairing LP redemption value and ultimately allowing the pool to be drained by the last swappers before the shortfall is discovered. The same corruption applies to `Deposit`, where LP tokens are minted based on the nominal, not actual, deposited amount, diluting/overpaying LP shares and further destabilizing the invariant that `Withdraw` and `calc_take_pnl` rely on. This is a direct path to insolvent pool accounting and fund loss reachable by any unprivileged swapper or pool creator, matching the High-severity report's "internal accounting corruption" bug class.

### Likelihood Explanation
Any pool creator can pair a legitimate token with a fee-on-transfer/deflationary SPL mint (or a Token-2022 mint with the `TransferFeeConfig` extension) at `Initialize2` time, since there is no mint-type or fee-extension whitelist check evident in the vault/mint validation. Once such a pool exists, any unprivileged trader interacting with the four swap instructions or `Deposit` triggers the corrupted accounting on a single transaction with no special privileges required — likelihood is high once such a pool is created, and pool creation itself is permissionless.

### Recommendation
For every inbound token transfer into an AMM-controlled vault (`Deposit`, `SwapBaseIn`, `SwapBaseOut`), snapshot the vault's token balance immediately before and after the `Invokers::token_transfer` CPI, and use the observed delta — not the nominal instruction amount — for all invariant math, LP-minting, and `calc_pnl_x`/`calc_pnl_y` updates. Alternatively/additionally, reject pools whose `coin_vault_mint`/`pc_vault_mint` carry a Token-2022 transfer-fee extension, and document/enforce that only standard, fee-free SPL tokens are supported.

### Proof of Concept
1. Pool creator calls `Initialize2` pairing a normal token (PC) with a deflationary/fee-on-transfer mint (COIN) as `coin_vault_mint`; no check rejects this token type [7](#0-6) .
2. A trader calls `SwapBaseIn` with `amount_in = 1_000_000` COIN. The pool reads pre-trade vault balances, computes `swap_amount_out` from the full `1_000_000` figure [2](#0-1) .
3. `Invokers::token_transfer` moves the COIN from the trader to `amm_coin_vault_info`, but the mint's transfer-fee logic deducts, e.g., 10%, so the vault only receives `900_000` [8](#0-7) .
4. The pool nonetheless pays the trader `swap_amount_out` (computed against `1_000_000` in, i.e., inflated) worth of PC from `amm_pc_vault_info` via `token_transfer_with_authority` [9](#0-8) .
5. Repeating the swap (or reversing direction) continually extracts more PC/COIN than the pool actually received, while `amm.state_data`/`target_orders.calc_pnl_x`/`calc_pnl_y` continue to reflect the inflated, non-existent balances, until the vault backing one side is fully drained relative to the recorded invariant — an unrecoverable, permanent shortfall for remaining LPs.

### Citations

**File:** program/src/processor.rs (L850-864)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_coin_vault.owner,
            *amm_authority_info.key,
            "coin_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
```

**File:** program/src/processor.rs (L1327-1372)
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
        amm.recent_epoch = Clock::get()?.epoch;
```

**File:** program/src/processor.rs (L1919-1925)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;

        let user_source = Self::unpack_token_account(&user_source_info, spl_token_program_id)?;
        let user_destination =
            Self::unpack_token_account(&user_destination_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L1970-1982)
```rust
        let swap_fee = U128::from(swap.amount_in)
            .checked_mul(amm.fees.swap_fee_numerator.into())
            .unwrap()
            .checked_ceil_div(amm.fees.swap_fee_denominator.into())
            .unwrap();
        let swap_in_after_deduct_fee = U128::from(swap.amount_in).checked_sub(swap_fee).unwrap();
        let swap_amount_out = Calculator::swap_token_amount_base_in(
            swap_in_after_deduct_fee,
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        )
        .as_u64();
```

**File:** program/src/processor.rs (L2000-2023)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap_amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_pc_vault to destination pc
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
```

**File:** program/src/processor.rs (L2212-2234)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap_in_after_add_fee,
                )?;
                // withdraw amm_pc_vault to destination pc
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap.amount_out,
                )?;
```

**File:** program/src/invokers.rs (L147-195)
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

    /// Issue a spl_token `Transfer` instruction.
    pub fn token_transfer_with_authority<'a>(
        token_program: AccountInfo<'a>,
        source: AccountInfo<'a>,
        destination: AccountInfo<'a>,
        authority: AccountInfo<'a>,
        amm_seed: &[u8],
        nonce: u8,
        amount: u64,
    ) -> Result<(), ProgramError> {
        let authority_signature_seeds = [amm_seed, &[nonce]];
        let signers = &[&authority_signature_seeds[..]];
        let ix = spl_token::instruction::transfer(
            token_program.key,
            source.key,
            destination.key,
            authority.key,
            &[],
            amount,
        )?;
        solana_program::program::invoke_signed(
            &ix,
            &[source, destination, authority, token_program],
            signers,
        )
    }
```
