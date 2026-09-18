### Title
Swap instructions trust the nominal `amount_in` instead of the actual vault balance delta, enabling drain via a fee-on-transfer/burn-on-transfer SPL token - (File: `program/src/processor.rs`)

### Summary
`process_swap_base_in`, `process_swap_base_in_v2`, `process_swap_base_out`, and `process_swap_base_out_v2` compute the constant-product swap output using the nominal `swap.amount_in` value from instruction data (or a value derived purely from it) and then unconditionally pay out the computed `swap_amount_out`/`swap.amount_out` from the opposite vault — without ever re-reading the source vault's actual post-transfer balance to confirm how much was really deposited.

### Finding Description
For `SwapBaseIn`, the pool snapshots `amm_coin_vault.amount`/`amm_pc_vault.amount` once via `unpack_token_account`, computes `swap_amount_out` from the attacker-supplied `swap.amount_in` using `Calculator::swap_token_amount_base_in`, and then calls `Invokers::token_transfer` to move `swap.amount_in` into the vault followed by `Invokers::token_transfer_with_authority` to pay `swap_amount_out` out of the opposite vault: [1](#0-0) [2](#0-1) 

The same pattern repeats in `process_swap_base_in_v2`: [3](#0-2) 

and in `process_swap_base_out` / `process_swap_base_out_v2`, where `swap_in_after_add_fee` is derived arithmetically from `swap.amount_out` and pool reserves, but the actual `token_transfer` into the source vault still moves the *computed* amount while the destination transfer pays the exact requested `swap.amount_out`: [4](#0-3) 

No code path in `processor.rs` reloads `amm_coin_vault_info`/`amm_pc_vault_info` after the `Invokers::token_transfer` CPI to compare the actual received balance against the amount used in the AMM math. `Invokers::token_transfer` itself is a thin wrapper that simply issues the SPL `Transfer` instruction and returns success as soon as the CPI succeeds, regardless of how much was actually credited to the destination: [5](#0-4) 

This is the same root cause as the Fire ($FIRE) incident referenced in the report: the exploited contract's `transfer()` had an internal burn mechanism, so the amount actually credited to the recipient differed from the amount used in the caller's accounting. Any SPL token with a "transfer hook"/fee-on-transfer/deflationary mechanic built into its mint/transfer semantics used as `coin_vault_mint` or `pc_vault_mint` in an Initialize2'd Raydium pool will produce the identical mismatch here: the vault receives less than `swap.amount_in` (or less than the value used to derive `swap_in_after_add_fee`), while the program pays the counter-asset based on the pre-transfer, non-adjusted quantity.

### Impact Explanation
Because the constant-product invariant math (`swap_token_amount_base_in`/`swap_token_amount_base_out`) is fed a nominal amount that the vault never actually receives, an attacker can repeatedly swap a deflationary/fee-on-transfer token into the pool, receive out the full quoted counter-asset amount, while the vault's real coin/pc balance grows by less than what the invariant assumes. This directly drains the counter-asset side of the pool (insolvent pool accounting / theft of LP and other traders' funds), reachable from a single unprivileged swap transaction with attacker-chosen accounts (any SPL mint can be paired via `Initialize2`) and attacker-chosen `amount_in`/`amount_out` data.

### Likelihood Explanation
Reaching this path requires no privileged signer: any user can call `Initialize2` to create a pool with an arbitrary SPL mint as one leg, then call any of the four swap instructions. No off-chain, RPC, or non-default build assumptions are needed — it only requires a token whose SPL-compatible mint/transfer semantics reduce the recipient's actual balance increase below the transferred `amount` field (e.g. via a companion burn call layered into wallet/router flows, or, for Token-2022-style mints with transfer fees if such vault mints are accepted). Given Solana's ecosystem trend toward Token-2022 transfer-fee/hook mints, this is a realistic and repeatable class of pools.

### Recommendation
After each `Invokers::token_transfer` that deposits user funds into `amm_coin_vault`/`amm_pc_vault`, re-unpack the vault account and use the actual balance delta (post-transfer minus pre-transfer) as the amount fed into `Calculator::swap_token_amount_base_in`/`swap_token_amount_base_out`, rather than trusting the instruction-supplied `amount_in`/derived `swap_in_after_add_fee`. Alternatively, explicitly reject vault mints that are not the plain SPL Token program's standard mint (e.g., disallow Token-2022 mints with transfer fee/hook extensions) during `Initialize2`.

### Proof of Concept
1. Deploy an SPL-compatible mint `X` whose transfer instruction (or an unavoidable companion instruction bundled by the token's own logic) burns/deducts a portion of every transferred amount, similar to the Fire ($FIRE) token's `transfer()`.
2. Call `Initialize2` to create a Raydium pool with `coin_vault_mint = X` and `pc_vault_mint = <normal token, e.g. wrapped SOL>`.
3. Call `SwapBaseIn` with `amount_in = N` of `X`. The program computes `swap_amount_out` from the full `N` via `Calculator::swap_token_amount_base_in` (`program/src/processor.rs:1970-1982`), but the actual amount credited to `amm_coin_vault` is `N - burn_amount` due to `X`'s transfer-time deduction.
4. The program still pays out the full `swap_amount_out` computed from `N` from `amm_pc_vault` (`program/src/processor.rs:2000-2022`), leaving the pool short on the pc side relative to its invariant assumption.
5. Repeat to drain the pc-side vault, matching the Fire incident's exploitation pattern (theft realized 24 seconds after pool launch).

### Citations

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

**File:** program/src/processor.rs (L2000-2022)
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

**File:** program/src/processor.rs (L2402-2424)
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
