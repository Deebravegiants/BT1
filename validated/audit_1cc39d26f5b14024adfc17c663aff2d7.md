### Title
Front-running/poisoning of the deterministic `Initialize2` PDA set permanently blocks legitimate pool creation for a given market account - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives the AMM pool, target-orders, LP-mint, coin-vault and pc-vault addresses as PDAs seeded solely by the attacker-supplied `market_info` account key (plus a fixed seed constant and the program id), and the code explicitly treats `market_info` as an arbitrary, unchecked account ("Just a seed for AMM account. Can be any account."). Any unprivileged caller can submit an `Initialize2` transaction using a chosen `market_info` pubkey (including a market account the legitimate pool creator intends to use) with attacker-controlled mints/amounts, permanently occupying that deterministic address space and causing every subsequent legitimate `Initialize2` attempt for that market to revert with `RepeatCreateAmm`.

### Finding Description
`get_associated_address_and_bump_seed` computes the AMM-related PDAs from `[program_id_bytes, market_pubkey_bytes, associated_seed]` [1](#0-0) . In `process_initialize2`, the `market_info` account is taken directly from the instruction's account list and is commented as arbitrary/unchecked seed material rather than a validated Serum/OpenBook market account [2](#0-1) .

The helper functions `generate_amm_associated_spl_token`, `generate_amm_associated_spl_mint`, and `generate_amm_associated_account` all derive the target address from `market_account.key` and only proceed to create/initialize the account if its current owner is still the System Program; otherwise they return `AmmError::RepeatCreateAmm` [3](#0-2) [4](#0-3) . This is a one-time "claim" pattern: whoever's `Initialize2` transaction lands first for a given `market_info` pubkey permanently owns that PDA family (AMM info account, target orders, LP mint, coin vault, pc vault).

Because there is no check that `market_info` is a real market tied to the legitimate token pair, or any reservation/allow-list mechanism, an adversary who observes (or predicts) which market account a legitimate team intends to use can submit their own `Initialize2` first — with garbage/attacker-chosen mints and a minimal `init_pc_amount`/`init_coin_amount` — and successfully claim all derived PDAs for that market before the legitimate initializer's transaction lands. This is directly analogous to the reported Salty DAO issue, where an attacker exploits a deterministic naming/derivation scheme (`ballotName + "_confirm"`) to preemptively occupy a key namespace and permanently block the legitimate protocol operation tied to that name.

### Impact Explanation
Once poisoned, the legitimate project can never create the intended AMM pool for that specific market account, because every one of `generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint`/`generate_amm_associated_account` will hit the `owner == system_program` check and fail with `AmmError::RepeatCreateAmm` [5](#0-4) . This is a permanent, irreversible denial of service against pool creation for a targeted market — the legitimate team's chosen market account is permanently unusable for creating a Raydium pool through `Initialize2`, forcing them to abandon that market account entirely. This matches the "prevent DAO/protocol function from operating correctly" impact class from the referenced report, translated to on-chain pool bootstrapping.

### Likelihood Explanation
The attack requires only a single unprivileged transaction with attacker-chosen accounts and data (a standard `Initialize2` call using a chosen `market_info` and small/garbage mints and amounts) — well within the reachable surface for a single submitted transaction from any user. The main precondition is that the attacker knows or can predict the `market_info` pubkey the victim intends to use (e.g., pools are typically created for well-known/newly-listed market accounts, which are often public or guessable before the creation transaction lands), making front-running practical, especially on a public mempool/leader schedule.

### Recommendation
Do not allow `market_info` to be an arbitrary, attacker-controlled seed for the AMM PDA family without binding it to something the legitimate creator controls or reserves in advance. Options:
- Require `market_info` to be owned by a whitelisted market/order-book program and validated (mint match, active market state) before being used as a derivation seed, as the pre-`no-openbook` code path apparently intended (`market_program_info` handling) rather than treating it as "any account."
- Alternatively, add a reservation step (e.g., binding the AMM PDA derivation to the pool creator's pubkey and/or the coin/pc mint pair with an owner-gated creation authority) so an unrelated third party cannot squat a market's derived PDA set with unrelated mints before the intended creator's pool creation transaction executes.
- At minimum, add a check that `init_coin_amount`/`init_pc_amount` and the coin/pc mints supplied match an expected/allow-listed configuration for that `market_info`, preventing garbage-parameter squatting.

### Proof of Concept
1. Adversary selects (or predicts) the `market_info` pubkey that a legitimate team intends to use to create a Raydium pool via `Initialize2`.
2. Adversary submits their own `Initialize2` transaction first, supplying that same `market_info` account, along with attacker-controlled `amm_coin_mint`/`amm_pc_mint`, minimal `init_coin_amount`/`init_pc_amount`, and their own wallet as `user_wallet_info`.
3. `process_initialize2` derives the AMM info, target-orders, LP-mint, coin-vault, and pc-vault PDAs solely from `market_info.key` [1](#0-0)  and successfully creates/assigns them to the program since they are currently owned by the System Program [6](#0-5) .
4. When the legitimate team later submits their own `Initialize2` using the same `market_info` account (with the real mints and amounts), every associated-account creation call now finds `associated_token_account.owner != system_program` and returns `AmmError::RepeatCreateAmm`, permanently blocking pool creation for that market [7](#0-6) [8](#0-7) .

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

**File:** program/src/processor.rs (L307-382)
```rust
        let (associated_token_address, bump_seed) = get_associated_address_and_bump_seed(
            program_id,
            &market_account.key,
            associated_seed,
            program_id,
        );
        if associated_token_address != *associated_token_account.key {
            msg!("Error: Associated token address does not match seed derivation");
            return Err(AmmError::ExpectedAccount.into());
        }
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

**File:** program/src/processor.rs (L489-546)
```rust
        let (associated_token_address, bump_seed) = get_associated_address_and_bump_seed(
            &program_id,
            &market_account.key,
            associated_seed,
            program_id,
        );
        if associated_token_address != *associated_token_account.key {
            msg!("Error: Associated token address does not match seed derivation");
            return Err(AmmError::ExpectedAccount.into());
        }
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

**File:** program/src/processor.rs (L592-646)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;

            let user_wallet_info = next_account_info(account_info_iter)?;
            let user_token_coin_info = next_account_info(account_info_iter)?;
            let user_token_pc_info = next_account_info(account_info_iter)?;
            let user_token_lp_info = next_account_info(account_info_iter)?;

            (
                token_program_info,
                ata_token_program_info,
                system_program_info,
                rent_sysvar_info,
                amm_info,
                amm_authority_info,
                amm_lp_mint_info,
                amm_coin_mint_info,
                amm_pc_mint_info,
                amm_coin_vault_info,
                amm_pc_vault_info,
                amm_target_orders_info,
                amm_config_info,
                create_fee_destination_info,
                market_info,
                user_wallet_info,
                user_token_coin_info,
                user_token_pc_info,
                user_token_lp_info,
            )
        } else {
            let account_info_iter = &mut accounts.iter();
            let token_program_info = next_account_info(account_info_iter)?;
            let ata_token_program_info = next_account_info(account_info_iter)?;
            let system_program_info = next_account_info(account_info_iter)?;
            let rent_sysvar_info = next_account_info(account_info_iter)?;
            let amm_info = next_account_info(account_info_iter)?;
            let amm_authority_info = next_account_info(account_info_iter)?;
            // Won't use.
            // Can be any account.
            let _amm_open_orders_info = next_account_info(account_info_iter)?;
            let amm_lp_mint_info = next_account_info(account_info_iter)?;
            let amm_coin_mint_info = next_account_info(account_info_iter)?;
            let amm_pc_mint_info = next_account_info(account_info_iter)?;
            let amm_coin_vault_info = next_account_info(account_info_iter)?;
            let amm_pc_vault_info = next_account_info(account_info_iter)?;
            let amm_target_orders_info = next_account_info(account_info_iter)?;
            let amm_config_info = next_account_info(account_info_iter)?;
            let create_fee_destination_info = next_account_info(account_info_iter)?;
            // Won't use.
            // Can be any account.
            let _market_program_info = next_account_info(account_info_iter)?;
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/error.rs (L124-125)
```rust
    #[error("Repeat AMM creation for the market.")]
    RepeatCreateAmm,
```
