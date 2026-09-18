Confirmed: all associated accounts (AMM pool, LP mint, coin/pc vaults, target orders) are PDAs derived purely from `program_id`, `market_account.key`, and a fixed seed constant — the mint addresses and initial amounts are never bound into that derivation. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Permissionless `Initialize2` allows front-running/squatting of a project's AMM pool address, permanently freezing the intended pool - ([File: program/src/processor.rs])

### Summary
`Initialize2` can be invoked by any unprivileged signer to create a Raydium AMM pool. The pool's address and all of its associated accounts (LP mint, coin/pc vaults, target-orders) are PDAs derived solely from `program_id`, the `market` account's public key, and a fixed seed string — never from the coin/pc mint addresses or the caller's identity. [4](#0-3) 

### Finding Description
`process_initialize2` treats the `market` account purely "as a seed" and explicitly does not validate that it is a genuine OpenBook/Serum market matching the supplied `coin_mint`/`pc_mint` (the code comments even say "Won't use. Can be any account." for the market program and "Just a seed for AMM account. Can be any account." for market). [5](#0-4) 

Because `generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` derive the target addresses only from `market_account.key` + seed, an attacker who learns the `market` pubkey a legitimate project intends to use (visible in the mempool once the legitimate `Initialize2` transaction is broadcast, or simply known in advance since it's a public OpenBook market) can submit their own `Initialize2` transaction first, using the same `market` account but attacker-chosen `coin_mint`/`pc_mint`, `init_coin_amount`/`init_pc_amount`, and `open_time`. [6](#0-5) 

Once the attacker's transaction lands first, the AMM PDA, LP mint PDA, and vault PDAs for that `market` key are permanently assigned to the program with the attacker's chosen mints/state. Any subsequent legitimate `Initialize2` call referencing the same `market` account hits the `owner == system_program` check and fails with `AmmError::RepeatCreateAmm`, since the account is no longer owned by the system program. [7](#0-6) 

This is a direct analog of the reported GSP `init()` front-running issue: an unprivileged actor races a benign initializer to "steal" a one-time initialization, permanently controlling the resulting state (here: which mints back the pool, what the initial price ratio is, and who receives the initial LP mint).

### Impact Explanation
The legitimate project can never create its intended coin/pc pool for that `market` account — the pool address is permanently squatted with attacker-controlled mints and an attacker-chosen initial price, since `amm.status`, `lp_mint`, and vault mints are fixed by whoever wins the race and cannot be changed afterward. [8](#0-7) 
This constitutes a permanent denial-of-service / freezing of the intended pool for that market, and the attacker also captures the entire initial LP mint (`user_lp_amount`) for whatever skewed price/liquidity they chose, which they can then trade against or simply hold as an intentionally mis-seeded pool. [9](#0-8) 

### Likelihood Explanation
Any user can construct and submit an `Initialize2` transaction with attacker-chosen accounts and data; no signer other than a generic "user wallet" is required, and the `market` account is unauthenticated as a real market. An attacker only needs to observe or predict the target `market` pubkey (which is typically public before the pool-creation transaction is even sent) and front-run it with a higher-priority/higher-fee transaction — a standard, low-cost MEV front-running pattern on Solana.

### Recommendation
Bind the initial trusted parameters into the pool derivation and/or into authorization: e.g., verify `market_account` is actually owned by/matches the expected market program and its declared coin/pc mints (as the original Raydium market-based AMM does for the deprecated `Initialize`), and/or require that the accounts used for `Initialize2` be constrained to prevent race-based squatting (e.g., allow only a designated authority, or derive the pool PDA from `(market, coin_mint, pc_mint)` together with a commit-reveal or reserved creation window so the intended creator cannot be pre-empted with mismatched mints/amounts).

### Proof of Concept
1. Legitimate team broadcasts (or is about to broadcast) `Initialize2` for a real OpenBook `market` M with `coin_mint` A and `pc_mint` B, supplying real `init_coin_amount`/`init_pc_amount`.
2. Attacker observes market `M`'s pubkey (public on-chain or in mempool) and submits their own `Initialize2` transaction referencing the same `market` M but with attacker-controlled `coin_mint`/`pc_mint` (or the same mints with a heavily skewed `init_coin_amount`/`init_pc_amount` ratio) and their own `user_wallet`/`user_token_lp` accounts, with a higher priority fee.
3. The attacker's transaction executes first: `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token` succeed because the PDAs (derived only from `market` + seed) are still system-owned, so all pool/vault/mint accounts get created and assigned to the program under attacker-chosen parameters, and the attacker receives the entire initial LP mint. [10](#0-9) 
4. The legitimate team's `Initialize2` transaction subsequently fails: `associated_token_account.owner == system_program_account.key` is now false, so `generate_amm_associated_account` returns `Err(AmmError::RepeatCreateAmm)` for the same `market` seed, permanently blocking creation of the intended pool. [11](#0-10)

### Citations

**File:** program/src/processor.rs (L307-316)
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
```

**File:** program/src/processor.rs (L317-380)
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
```

**File:** program/src/processor.rs (L399-408)
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
```

**File:** program/src/processor.rs (L489-498)
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
```

**File:** program/src/processor.rs (L541-544)
```rust
        } else {
            associated_token_address.log();
            return Err(AmmError::RepeatCreateAmm.into());
        }
```

**File:** program/src/processor.rs (L548-646)
```rust
    /// Processes an [Initialize](enum.Instruction.html).
    pub fn process_initialize2(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        init: InitializeInstruction2,
    ) -> ProgramResult {
        let input_account_len = accounts.len();
        let (
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
        ) = if input_account_len == 19 {
            // Recommended use due to openbook has not supported.
            let account_info_iter = &mut accounts.iter();
            let token_program_info = next_account_info(account_info_iter)?;
            let ata_token_program_info = next_account_info(account_info_iter)?;
            let system_program_info = next_account_info(account_info_iter)?;
            let rent_sysvar_info = next_account_info(account_info_iter)?;
            let amm_info = next_account_info(account_info_iter)?;
            let amm_authority_info = next_account_info(account_info_iter)?;
            let amm_lp_mint_info = next_account_info(account_info_iter)?;
            let amm_coin_mint_info = next_account_info(account_info_iter)?;
            let amm_pc_mint_info = next_account_info(account_info_iter)?;
            let amm_coin_vault_info = next_account_info(account_info_iter)?;
            let amm_pc_vault_info = next_account_info(account_info_iter)?;
            let amm_target_orders_info = next_account_info(account_info_iter)?;
            let amm_config_info = next_account_info(account_info_iter)?;
            let create_fee_destination_info = next_account_info(account_info_iter)?;
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

**File:** program/src/processor.rs (L775-815)
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

**File:** program/src/processor.rs (L930-983)
```rust

        amm.initialize(
            init.nonce,
            init.open_time,
            coin_mint.decimals,
            pc_mint.decimals,
            0,
            0,
        )?;
        encode_ray_log(InitLog {
            log_type: LogType::Init.into_u8(),
            time: init.open_time,
            pc_decimals: amm.pc_decimals as u8,
            coin_decimals: amm.coin_decimals as u8,
            pc_lot_size: 0,
            coin_lot_size: 0,
            pc_amount: amm_pc_vault.amount,
            coin_amount: amm_coin_vault.amount,
            market: *market_info.key,
        });
        let x = Calculator::normalize_decimal_v2(
            amm_pc_vault.amount,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y = Calculator::normalize_decimal_v2(
            amm_coin_vault.amount,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        // check and init target orders account
        if amm_target_orders_info.owner != program_id {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        let mut target_order = TargetOrders::load_mut(amm_target_orders_info)?;
        target_order.check_init(x.as_u128(), y.as_u128(), amm_info.key)?;

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
        amm.status = if init.open_time > (Clock::get()?.unix_timestamp as u64) {
            AmmStatus::WaitingTrade.into_u64()
        } else {
            AmmStatus::SwapOnly.into_u64()
        };
        amm.reset_flag = AmmResetFlag::ResetYes.into_u64();
```
