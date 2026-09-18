### Title
Permanent front-running DoS of pool creation via unchecked `market_info` seed reuse in `Initialize2` - (File: `program/src/processor.rs`)

### Summary
`PirexGmx.initiateMigration` was blockable because an attacker could force a *precondition* (zero vester balance) to permanently fail before the legitimate state transition occurred. `Raydium-amm`'s `process_initialize2` has an analogous blockable precondition: all of the pool's core PDAs (`target_orders`, `lp_mint`, `coin_vault`, `pc_vault`, `amm` account) are derived deterministically from the `market_info` account key alone, and the helper that creates them only succeeds if the target address is still owned by the System Program. An attacker can pre-claim these PDAs for an arbitrary `market_info` key before the legitimate pool creator does, permanently blocking that market from ever getting a real AMM pool.

### Finding Description
The associated PDA addresses are derived purely from `market_info.key` and a static seed, with `program_id` used for both the info-namespace and derivation program: [1](#0-0) 

`process_initialize2` explicitly documents that `market_info` is not validated against any real market program and "can be any account": [2](#0-1) 

The account-creation helpers (`generate_amm_associated_spl_token`, `generate_amm_associated_spl_mint`, `generate_amm_associated_account`) only proceed to allocate/assign the PDA if it is still owned by the System Program; otherwise they permanently fail with `RepeatCreateAmm`: [3](#0-2) [4](#0-3) [5](#0-4) 

Because `market_info` is unchecked, any unprivileged caller can invoke `Initialize2` first using the intended/target market's public key as `market_info`, together with attacker-chosen (garbage) mints and a tiny/self-funded `init_coin_amount`/`init_pc_amount`. This causes `generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` to actually allocate and assign ownership of the `target_orders`, `lp_mint`, `coin_vault`, `pc_vault`, and `amm` PDAs derived from that `market_info` key — permanently changing their owner away from the System Program. All subsequent `Initialize2` calls for that same `market_info` key (including the legitimate one, with the correct mints) will hit the `owner == system_program` check, find it false, and return `AmmError::RepeatCreateAmm` forever, since these PDAs can never be reset or reused once claimed.

This mirrors the report's root cause exactly: a required "clean/zero" precondition for a subsequent legitimate operation (there: zero vester balance for `signalTransfer`; here: System-Program ownership of the PDA for pool creation) can be permanently poisoned by an unprivileged attacker in a single transaction, blocking the legitimate flow indefinitely.

### Impact Explanation
This permanently prevents any AMM pool from ever being created for the targeted market, denying LPs/traders access to that trading pair on Raydium and freezing/wasting rent already reserved for that market's intended pool creation. Unlike the original GMX report — which the project ultimately invalidated because the `Vester` token contract makes `transfer`/`transferFrom` revert, closing the actual attack path — here there is no equivalent protection: `market_info` truly is unchecked and reusable as an attacker-chosen seed, and the PDA-ownership precondition is a real, unguarded gate for pool creation.

### Likelihood Explanation
High. The attack requires only a single transaction, standard SPL Token/System Program CPIs, and attacker-controlled accounts (arbitrary mints/vaults/wallet); no privileged signer, leaked key, or off-chain assumption is needed. Any party who can predict or observe the intended `market_info` key for an upcoming pool (e.g., a newly created OpenBook market) can front-run the real `Initialize2` call.

### Recommendation
Validate `market_info` in `process_initialize2` (e.g., require it be owned by the expected market program and/or bind PDA derivation to both `market_info.key` and the specific `coin_mint`/`pc_mint` pair) so that a pool address cannot be squatted independent of the intended token pair, and/or require additional authorization (e.g., signer whitelist or market-program-verified state) before allowing PDA claims for a given market.

### Proof of Concept
1. Attacker observes/derives the `market_info` pubkey intended for a new legitimate pool (e.g., a freshly created OpenBook market for TOKEN/USDC).
2. Attacker calls `Initialize2` with that exact `market_info` account but with attacker's own throwaway `amm_coin_mint`/`amm_pc_mint`, self-owned vault/mint accounts, and minimal `init_coin_amount`/`init_pc_amount` (using `initialize2` builder): [6](#0-5) 
3. `process_initialize2` derives `target_orders`, `lp_mint`, `coin_vault`, `pc_vault`, and `amm` PDAs solely from `market_info.key` and successfully allocates/assigns them to the attacker's chosen mints, since ownership checks pass (System Program owns them initially): [7](#0-6) 
4. The legitimate team now calls `Initialize2` for the same `market_info` with the correct TOKEN/USDC mints; every associated-account creation helper finds `associated_token_account.owner != system_program_account.key` and returns `AmmError::RepeatCreateAmm`, permanently blocking legitimate pool creation for that market.

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

**File:** program/src/processor.rs (L313-382)
```rust
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

**File:** program/src/processor.rs (L399-475)
```rust
        let (associated_token_address, bump_seed) = get_associated_address_and_bump_seed(
            program_id,
            &market_account.key,
            associated_seed,
            program_id,
        );
        if associated_token_address != *associated_token_account.key {
            msg!("Error: Associated mint address does not match seed derivation");
            return Err(AmmError::ExpectedMint.into());
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
                .minimum_balance(spl_token::state::Mint::LEN)
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
                    spl_token::state::Mint::LEN as u64,
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
                &spl_token::instruction::initialize_mint(
                    spl_token_program_id,
                    associated_token_account.key,
                    associated_owner_account.key,
                    None,
                    mint_decimals,
                )?,
                &[
                    associated_token_account.clone(),
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
    }
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

**File:** program/src/processor.rs (L747-814)
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

**File:** program/src/instruction.rs (L663-729)
```rust
/// Creates an 'initialize2' instruction.
pub fn initialize2(
    amm_program: &Pubkey,
    amm_pool: &Pubkey,
    amm_authority: &Pubkey,
    amm_open_orders: &Pubkey,
    amm_lp_mint: &Pubkey,
    amm_coin_mint: &Pubkey,
    amm_pc_mint: &Pubkey,
    amm_coin_vault: &Pubkey,
    amm_pc_vault: &Pubkey,
    amm_target_orders: &Pubkey,
    amm_config: &Pubkey,
    create_fee_destination: &Pubkey,
    market_program: &Pubkey,
    market: &Pubkey,
    user_wallet: &Pubkey,
    user_token_coin: &Pubkey,
    user_token_pc: &Pubkey,
    user_token_lp: &Pubkey,
    nonce: u8,
    open_time: u64,
    init_pc_amount: u64,
    init_coin_amount: u64,
) -> Result<Instruction, ProgramError> {
    let init_data = AmmInstruction::Initialize2(InitializeInstruction2 {
        nonce,
        open_time,
        init_pc_amount,
        init_coin_amount,
    });
    let data = init_data.pack()?;

    let accounts = vec![
        // spl & sys
        AccountMeta::new_readonly(spl_token::id(), false),
        AccountMeta::new_readonly(spl_associated_token_account::id(), false),
        AccountMeta::new_readonly(solana_system_interface::program::id(), false),
        AccountMeta::new_readonly(sysvar::rent::id(), false),
        // amm
        AccountMeta::new(*amm_pool, false),
        AccountMeta::new_readonly(*amm_authority, false),
        AccountMeta::new(*amm_open_orders, false),
        AccountMeta::new(*amm_lp_mint, false),
        AccountMeta::new_readonly(*amm_coin_mint, false),
        AccountMeta::new_readonly(*amm_pc_mint, false),
        AccountMeta::new(*amm_coin_vault, false),
        AccountMeta::new(*amm_pc_vault, false),
        AccountMeta::new(*amm_target_orders, false),
        AccountMeta::new_readonly(*amm_config, false),
        AccountMeta::new(*create_fee_destination, false),
        // market
        AccountMeta::new_readonly(*market_program, false),
        AccountMeta::new_readonly(*market, false),
        // user wallet
        AccountMeta::new(*user_wallet, true),
        AccountMeta::new(*user_token_coin, false),
        AccountMeta::new(*user_token_pc, false),
        AccountMeta::new(*user_token_lp, false),
    ];

    Ok(Instruction {
        program_id: *amm_program,
        accounts,
        data,
    })
}
```
