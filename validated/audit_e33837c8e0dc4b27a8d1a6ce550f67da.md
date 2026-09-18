## Analysis

Raydium's `Initialize2` instruction is the direct analog to the reported `createLoan`/`loanId` collision bug. Just as the Hub Chain's `loanId` is a caller-chosen 32-byte identifier that any account can claim once (causing later collisions to permanently revert), Raydium's AMM pool addresses are deterministic PDAs derived **solely from the `market_info.key`** (plus a fixed seed string) — not from the caller's wallet. Any account willing to call `Initialize2` first for a given market can "claim" that market's pool address before the legitimate creator's transaction lands, permanently blocking the intended pool creation for that market.

### Title
Permissionless, market-keyed PDA derivation in `Initialize2` allows front-running/griefing that permanently blocks legitimate pool creation for a target market - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every pool-critical account (`amm_info`, `target_orders`, `lp_mint`, `coin_vault`, `pc_vault`) via `get_associated_address_and_bump_seed`, keyed only by `market_account.key` and a static seed suffix, with no binding to the caller's wallet.

### Finding Description
`get_associated_address_and_bump_seed` computes the pool's PDAs from `market_address` and a fixed seed only [1](#0-0) . `generate_amm_associated_account` and `generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` create these accounts only if they are currently owned by the system program, otherwise return `AmmError::RepeatCreateAmm` [2](#0-1) [3](#0-2) . `process_initialize2` performs no check tying these derived addresses to the specific `user_wallet_info` signer — any signer can supply any `market_info` and claim the pool for that market, as long as they can fund token vaults with a nonzero balance [4](#0-3) . Because the derivation is 1:1 with `market_info.key`, once an account (accounts, not identity) is created for a market, no other `Initialize2` call for that same market can ever succeed — it will hit `RepeatCreateAmm` at the very first account-creation step (`generate_amm_associated_account` for `amm_target_orders_info`) [5](#0-4) . This mirrors the reported bug class exactly: a publicly-computable, user-independent unique identifier (`loanId` in the report, the market-derived PDA here) can be "claimed" by any front-runner in a single transaction, causing the legitimate actor's transaction to permanently fail.

### Impact Explanation
This is a griefing/DoS vector, not a fund-theft one: an attacker can observe a pending `Initialize2` transaction targeting a specific market (or simply predict which markets are commonly used) and front-run it with minimal token amounts, permanently taking over the canonical pool address for that market. The legitimate pool creator's transaction reverts with `RepeatCreateAmm` and, because the PDA is deterministically bound to the market key with no per-creator entropy, that market can **never** host a Raydium AMM pool through the intended creator again — a permanent (not merely transient) denial of service against pool creation for the targeted market, matching the "Griefing" impact class of the original report.

### Likelihood Explanation
Exploitation requires only a single permissionless transaction with attacker-chosen accounts (`market_info` set to the same market the victim intends to use) and minimal token balances to pass the `amount == 0` checks [6](#0-5) . No privileged role, signer key leak, or validator collusion is needed — any wallet can call `Initialize2` for any market. The only cost to the attacker is minimal token/rent expenditure, making this cheap and repeatable against any market of interest.

### Recommendation
Bind the derived PDA seeds to the caller (e.g., include `user_wallet_info.key` or a caller-supplied nonce/salt in the seed derivation) so that pool-account addresses are not solely a function of the public, pre-known `market_info.key`. Alternatively, require the calling wallet to be recorded/verified as the designated pool creator for that market before allowing account creation, closing the front-running window entirely.

### Proof of Concept
1. Victim prepares an `Initialize2` transaction for market `M` with legitimate `init_coin_amount`/`init_pc_amount` and submits it (or it is visible/predictable before confirmation).
2. Attacker computes the same PDAs via `get_associated_address_and_bump_seed(program_id, M, <seed>, program_id)` [1](#0-0)  — identical for any caller since it only depends on `M`.
3. Attacker submits their own `Initialize2` for market `M` first, with `init_coin_amount = 1`, `init_pc_amount = 1` (or any nonzero minimal amount), successfully creating `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`, and `amm_info` for `M`.
4. Victim's transaction now hits `generate_amm_associated_account` for `amm_target_orders_info`, sees `associated_token_account.owner != system_program_account.key`, and reverts with `AmmError::RepeatCreateAmm` [7](#0-6) .
5. Market `M` can never again be initialized as a pool by the intended creator through this program instance — permanent griefing.

### Citations

**File:** program/src/processor.rs (L112-126)
```rust
pub fn get_associated_address_and_bump_seed(
    info_id: &Pubkey,
    market_address: &Pubkey,
    associated_seed: &[u8],
    program_id: &Pubkey,
) -> (Pubkey, u8) {
    Pubkey::find_program_address(
        &[
            &info_id.to_bytes(),
            &market_address.to_bytes(),
            &associated_seed,
        ],
        program_id,
    )
}
```

**File:** program/src/processor.rs (L317-382)
```rust
        if associated_token_account.owner == system_program_account.key {
            let associated_account_signer_seeds: &[&[_]] = &[
                &program_id.to_bytes(),
                &market_account.key.to_bytes(),
                associated_seed,
                &[bump_seed],
            ];
            let rent = Rent::get()?;
            let required_lamports = rent
                .minimum_balance(spl_token::state::Account::LEN)
                .max(1)
                .saturating_sub(associated_token_account.lamports());
            if required_lamports > 0 {
                invoke(
                    &system_instruction::transfer(
                        user_wallet_account.key,
                        associated_token_account.key,
                        required_lamports,
                    ),
                    &[
                        user_wallet_account.clone(),
                        associated_token_account.clone(),
                        system_program_account.clone(),
                    ],
                )?;
            }
            invoke_signed(
                &system_instruction::allocate(
                    associated_token_account.key,
                    spl_token::state::Account::LEN as u64,
                ),
                &[
                    associated_token_account.clone(),
                    system_program_account.clone(),
                ],
                &[&associated_account_signer_seeds],
            )?;
            invoke_signed(
                &system_instruction::assign(associated_token_account.key, spl_token_program_id),
                &[
                    associated_token_account.clone(),
                    system_program_account.clone(),
                ],
                &[&associated_account_signer_seeds],
            )?;

            invoke(
                &spl_token::instruction::initialize_account(
                    spl_token_program_id,
                    associated_token_account.key,
                    token_mint_account.key,
                    associated_owner_account.key,
                )?,
                &[
                    associated_token_account.clone(),
                    token_mint_account.clone(),
                    associated_owner_account.clone(),
                    rent_sysvar_account.clone(),
                    spl_token_program_account.clone(),
                ],
            )?;
        } else {
            associated_token_address.log();
            return Err(AmmError::RepeatCreateAmm.into());
        }
        Ok(())
```

**File:** program/src/processor.rs (L499-546)
```rust
        if associated_token_account.owner == system_program_account.key {
            let associated_account_signer_seeds: &[&[_]] = &[
                &program_id.to_bytes(),
                &market_account.key.to_bytes(),
                associated_seed,
                &[bump_seed],
            ];
            let rent = Rent::get()?;
            let required_lamports = rent
                .minimum_balance(data_size)
                .max(1)
                .saturating_sub(associated_token_account.lamports());
            if required_lamports > 0 {
                invoke(
                    &system_instruction::transfer(
                        user_wallet_account.key,
                        associated_token_account.key,
                        required_lamports,
                    ),
                    &[
                        user_wallet_account.clone(),
                        associated_token_account.clone(),
                        system_program_account.clone(),
                    ],
                )?;
            }
            invoke_signed(
                &system_instruction::allocate(associated_token_account.key, data_size as u64),
                &[
                    associated_token_account.clone(),
                    system_program_account.clone(),
                ],
                &[&associated_account_signer_seeds],
            )?;
            invoke_signed(
                &system_instruction::assign(associated_token_account.key, assign_to),
                &[
                    associated_token_account.clone(),
                    system_program_account.clone(),
                ],
                &[&associated_account_signer_seeds],
            )?;
        } else {
            associated_token_address.log();
            return Err(AmmError::RepeatCreateAmm.into());
        }
        Ok(())
    }
```

**File:** program/src/processor.rs (L747-758)
```rust
        // create target_order account
        Self::generate_amm_associated_account(
            program_id,
            program_id,
            market_info,
            amm_target_orders_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            TARGET_ASSOCIATED_SEED,
            size_of::<TargetOrders>(),
        )?;
```

**File:** program/src/processor.rs (L775-814)
```rust
        // create coin vault account
        Self::generate_amm_associated_spl_token(
            program_id,
            spl_token_program_id,
            market_info,
            amm_coin_vault_info,
            amm_coin_mint_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            token_program_info,
            amm_authority_info,
            COIN_VAULT_ASSOCIATED_SEED,
        )?;
        // create pc vault account
        Self::generate_amm_associated_spl_token(
            program_id,
            spl_token_program_id,
            market_info,
            amm_pc_vault_info,
            amm_pc_mint_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            token_program_info,
            amm_authority_info,
            PC_VAULT_ASSOCIATED_SEED,
        )?;
        // create amm account
        Self::generate_amm_associated_account(
            program_id,
            program_id,
            market_info,
            amm_info,
            user_wallet_info,
            system_program_info,
            rent_sysvar_info,
            AMM_ASSOCIATED_SEED,
            size_of::<AmmInfo>(),
        )?;
```

**File:** program/src/processor.rs (L858-889)
```rust
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_coin_mint_info.key,
            amm_coin_vault.mint,
            "coin_mint",
            AmmError::InvalidCoinMint
        );
        // unpack and check token_pc
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_pc_vault.owner,
            *amm_authority_info.key,
            "pc_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_pc_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_pc_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_pc_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
```
