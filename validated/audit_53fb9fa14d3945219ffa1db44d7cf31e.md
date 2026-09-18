### Title
Deflationary/Fee-on-Transfer or Rebasing SPL Tokens Break Pool Accounting Because Deposit/Withdraw/Swap Trust Nominal Transfer Amounts Instead of Verifying Actual Vault Balance Changes - (File: `program/src/processor.rs`)

### Summary
`process_deposit`, `process_withdraw`, `process_swap_base_in`, and `process_swap_base_out` all compute pool state (`total_coin_without_take_pnl`/`total_pc_without_take_pnl`, `amm.lp_amount`, `target_orders.calc_pnl_x/y`) from a single snapshot of vault balances taken via `Self::unpack_token_account`, then issue `Invokers::token_transfer` calls for fixed, pre-computed amounts without re-reading the vault balance afterward to confirm the actual amount received.

### Finding Description
In `process_deposit`, the vault balances are read once via `Self::unpack_token_account(&amm_coin_vault_info, ...)` and `Self::unpack_token_account(&amm_pc_vault_info, ...)` [1](#0-0) , and the pnl-adjusted totals are derived from those balances [2](#0-1) . The program then transfers `deduct_coin_amount`/`deduct_pc_amount` — nominal amounts computed off the pre-transfer snapshot — into the vaults and immediately updates `amm.lp_amount` and `target_orders.calc_pnl_x/y` as if those exact nominal amounts landed in the vault [3](#0-2) . The same pattern repeats for swaps: `process_swap_base_in`/`process_swap_base_out` transfer `swap.amount_in`/`swap_in_after_add_fee` into the source vault and `swap_amount_out`/`swap.amount_out` out of the destination vault based purely on AMM-invariant math over the stale balance snapshot, with no post-transfer balance verification [4](#0-3) [5](#0-4) [6](#0-5) . The underlying `Invokers::token_transfer`/`token_transfer_with_authority` helpers merely issue an `spl_token::instruction::transfer` for the given amount and return without reading resulting balances [7](#0-6) .

If either the coin or pc mint is a fee-on-transfer (deflationary), rebasing, or inflationary SPL token, the amount actually credited to `amm_coin_vault`/`amm_pc_vault` diverges from the nominal amount used in the program's internal accounting (`amm.lp_amount`, `target_orders.calc_pnl_x`/`calc_pnl_y`, and the invariant-derived `total_coin_without_take_pnl`/`total_pc_without_take_pnl` used on the next instruction). This breaks the constant-product invariant tracked by the program versus the real on-chain vault balances.

### Impact Explanation
For a fee-on-transfer coin/pc mint, every deposit mints LP tokens as if the full nominal amount reached the vault, while the vault actually received less — over-minting LP relative to real backing and diluting/insolvency-risking other LPs' claims on withdrawal. Conversely, on withdraw and on the swap "transfer out" leg, the fixed amount computed from stale/nominal accounting is sent via `token_transfer_with_authority`, which can drain more value out of the vault than the invariant intends if the output-side token is itself fee-bearing or rebasing, or leave residual balance mismatches that a later swap can exploit to extract value. Because `amm.lp_amount` and `target_orders.calc_pnl_x/y` are updated using the pre-transfer nominal deltas rather than the observed vault delta, the pool's internal ledger permanently diverges from real vault balances, resulting in unbacked LP minting or insolvent pool accounting exploitable by any user who deposits/withdraws/swaps against such a pool.

### Likelihood Explanation
This is reachable by any unprivileged user simply by creating a pool (via `Initialize2`) or interacting with an already-initialized pool whose `coin_mint`/`pc_mint` is a fee-on-transfer, rebasing, or elastic-supply SPL token, then calling `Deposit`, `Withdraw`, `SwapBaseIn`, or `SwapBaseOut` with attacker-chosen accounts and amounts — no privileged signer or off-chain component is required.

### Recommendation
Before and after each `Invokers::token_transfer`/`token_transfer_with_authority` call that moves funds into or out of `amm_coin_vault`/`amm_pc_vault`, re-read the vault token account balance and use the observed delta (rather than the nominal instruction amount) when updating `amm.lp_amount`, `target_orders.calc_pnl_x/calc_pnl_y`, and when computing `total_coin_without_take_pnl`/`total_pc_without_take_pnl` for subsequent calculations. Alternatively, explicitly disallow pool creation/initialization for mints with nonstandard transfer/rebase semantics (e.g., reject any mint carrying a transfer-fee/hook extension) at `Initialize2` time.

### Proof of Concept
1. Attacker (or anyone) initializes an AMM pool via `Initialize2` where `coin_mint` is a fee-on-transfer token that deducts e.g. 5% on every transfer.
2. Attacker calls `Deposit` with `max_coin_amount = 1000`. The program computes `deduct_coin_amount = 1000`, calls `Invokers::token_transfer` for 1000, but the vault only receives 950 due to the transfer fee, per `processor.rs` lines 1327-1333 [8](#0-7) .
3. The program still mints `mint_lp_amount` computed from the nominal 1000 and updates `target_orders.calc_pnl_x/calc_pnl_y` and `amm.lp_amount` as if the full 1000 arrived [9](#0-8) , creating LP tokens backed by only 950 real coin tokens.
4. Repeating deposits/withdrawals compounds the discrepancy between recorded (`total_coin_without_take_pnl`) and actual vault balances, letting an attacker withdraw disproportionate value or drain the pool relative to genuine LP backing.

### Citations

**File:** program/src/processor.rs (L1138-1144)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_source_coin =
            Self::unpack_token_account(&user_source_coin_info, spl_token_program_id)?;
        let user_source_pc =
            Self::unpack_token_account(&user_source_pc_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L1148-1153)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
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

**File:** program/src/processor.rs (L2000-2048)
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
            SwapDirection::PC2Coin => {
                if swap_amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source pc to amm_pc_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_coin_vault to destination coin
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
        };
        amm.recent_epoch = Clock::get()?.epoch;
```

**File:** program/src/processor.rs (L2212-2260)
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
            }
            SwapDirection::PC2Coin => {
                if swap.amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }

                // deposit source pc to amm_pc_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_source_owner.clone(),
                    swap_in_after_add_fee,
                )?;
                // withdraw amm_coin_vault to destination coin
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap.amount_out,
                )?;
            }
        };
```

**File:** program/src/processor.rs (L2402-2450)
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
            SwapDirection::PC2Coin => {
                if swap_amount_out >= total_coin_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source pc to amm_pc_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_pc_vault_info.clone(),
                    user_source_owner.clone(),
                    swap.amount_in,
                )?;
                // withdraw amm_coin_vault to destination coin
                Invokers::token_transfer_with_authority(
                    token_program_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_destination_info.clone(),
                    amm_authority_info.clone(),
                    AUTHORITY_AMM,
                    amm.nonce as u8,
                    swap_amount_out,
                )?;
            }
        };
        amm.recent_epoch = Clock::get()?.epoch;
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
