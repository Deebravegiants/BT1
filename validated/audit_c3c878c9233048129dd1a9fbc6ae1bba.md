This confirms the analog is fully reachable: `market_info` in `process_initialize2` is explicitly documented as "Just a seed for AMM account. Can be any account." with zero ownership/ type validation, and all deterministic AMM accounts (`amm_info`, `amm_target_orders_info`, `amm_lp_mint_info`, `amm_coin_vault_info`, `amm_pc_vault_info`) are derived solely from `(program_id, market_info.key, seed)` via `get_associated_address_and_bump_seed`, then created only if the target account is still system-owned (`generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` at [1](#0-0)  and [2](#0-1) ), otherwise erroring with `AmmError::RepeatCreateAmm` [3](#0-2) .

### Title
Front-running `Initialize2` with an attacker-chosen `market` key permanently blocks legitimate pool creation for that market - (File: program/src/processor.rs)

### Summary
`process_initialize2` derives every deterministic AMM account (pool state, LP mint, coin/pc vaults, target orders) solely from `(program_id, market_info.key, seed)`, and the account's PDA-derivation key `market_info` is explicitly unvalidated ("Just a seed for AMM account. Can be any account."). Anyone can submit an `Initialize2` transaction naming the same OpenBook market pubkey that a legitimate market maker intends to use, with attacker-controlled mint/vault accounts and a minimal deposit, permanently occupying the PDA slots tied to that market before the legitimate creator's transaction lands.

### Finding Description
In `process_initialize2` [4](#0-3) , `market_info` is taken from the accounts list with the comment "Just a seed for AMM account. Can be any account." and is never checked for ownership, type, or association with the intended coin/pc mints. Yet it is the sole seed (besides `program_id` and a fixed suffix) used to compute the deterministic addresses for `amm_info`, `amm_target_orders_info`, `amm_lp_mint_info`, `amm_coin_vault_info`, and `amm_pc_vault_info` via `get_associated_address_and_bump_seed` [5](#0-4) .

Each of these accounts is created only in the branch where `associated_token_account.owner == system_program_account.key`; otherwise the call fails with `AmmError::RepeatCreateAmm` [6](#0-5)  and similarly in `generate_amm_associated_account` [7](#0-6) . Once these PDAs are assigned to the AMM program (owner no longer System Program), no instruction exists to reset them back to system-owned, so a second `Initialize2` call using the same `market_info.key` will always fail this ownership check.

This is directly analogous to the SEDA `CreateVestingAccount` bug: there, anyone could front-run with a `Bank::Send` to pre-create the recipient account and permanently block `CreateVestingAccount` from succeeding for that address, because creation is gated on "account does not yet exist." Here, anyone can front-run with their own `Initialize2` call (using attacker-supplied mints and a trivial deposit) to pre-create the market-derived PDAs and permanently block the legitimate pool creation for that specific OpenBook market, because creation is gated on the PDA still being system-owned.

### Impact Explanation
Since Raydium's off-chain tooling, indexers, and the CLI/library (`initialize2` builder in `program/src/instruction.rs` and `AmmCommands::CreatePool`) derive the canonical AMM pool address purely from the market pubkey, an attacker can permanently squat the pool address space for any targeted OpenBook market by submitting a cheap `Initialize2` transaction first (e.g., with a self-created dummy mint pair and near-zero `init_coin_amount`/`init_pc_amount`). This permanently denies the intended market maker/protocol the ability to ever create the canonical Raydium pool for that market address, since the underlying PDAs can never be reset to system-owned once assigned to the program. This is a permanent, front-runnable denial-of-service against pool creation with no privileged access required, satisfying the "permanent freezing"/blocking class described in the report analog.

### Likelihood Explanation
Any user can observe a pending `Initialize2` transaction for a desirable market in the mempool (or simply predict which markets are likely to get pools created) and submit their own `Initialize2` with the same `market_info` key and a trivial fee/deposit, landing before or in the same slot as the legitimate transaction. No special privileges, existing state, or non-default configuration are required — only a single transaction with attacker-chosen accounts and data, matching the reachable-path criteria.

### Recommendation
Require `market_info` to be validated as an actual OpenBook/Serum market account (owned by the expected market program and containing the specified coin/pc mints) rather than an arbitrary unchecked seed account, and/or require the pool creator's wallet or a permissioned governance/config account to co-sign or be embedded in the PDA seeds so that an unrelated attacker cannot squat the deterministic addresses tied to a specific market before the legitimate owner's transaction lands.

### Proof of Concept
1. Attacker observes that market `M` (a real OpenBook market pubkey) will soon be used for legitimate Raydium pool creation.
2. Attacker creates two throwaway SPL mints `mintA`/`mintB` and funds a tiny token balance.
3. Attacker submits `Initialize2` (per `initialize2` builder in `program/src/instruction.rs`, lines 664-729) with `market = M`, `amm_coin_mint = mintA`, `amm_pc_mint = mintB`, `init_coin_amount = 1`, `init_pc_amount = 1`, and all PDA accounts correctly derived via `get_associated_address_and_bump_seed(program_id, M, seed, program_id)`.
4. `process_initialize2` succeeds, assigning `amm_info`, `amm_target_orders_info`, `amm_lp_mint_info`, `amm_coin_vault_info`, `amm_pc_vault_info` (all derived from `M`) to the AMM program.
5. The legitimate market maker later submits their own `Initialize2` for market `M` with the correct mints; every `generate_amm_associated_*` call now hits the `owner == system_program` check as false and returns `AmmError::RepeatCreateAmm`, permanently blocking creation of the intended pool for market `M`.

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

**File:** program/src/processor.rs (L317-381)
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
```

**File:** program/src/processor.rs (L495-544)
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
