## Title
Permissionless `Initialize2` allows pool creation to be front-run since AMM/vault/mint addresses are deterministically derived from the market pubkey alone - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives the AMM account, LP mint, coin/pc vaults, and target-orders account solely from `market_info.key` (plus fixed seed constants and `program_id`), with no binding to the submitting wallet or any commit/reveal step. Anyone can observe a pending, legitimate `Initialize2` transaction for a given market in the mempool and submit their own `Initialize2` with the same market account first, permanently claiming that market's pool address space.

### Finding Description
The pool's core accounts are derived via `get_associated_address_and_bump_seed(program_id, market_account.key, associated_seed, program_id)` for `AMM_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, and `PC_VAULT_ASSOCIATED_SEED`: [1](#0-0) 

These derivations depend only on `market_info.key`, not on `user_wallet_info` or any signer-specific data, so the resulting addresses are fully predictable and identical regardless of who submits the `Initialize2` instruction for that market: [2](#0-1) [3](#0-2) 

`process_initialize2` performs no check that the caller is the market's creator, an authorized party, or the party who legitimately intends to seed liquidity for that market — the only requirement is `user_wallet_info.is_signer` (any signer) and correct static program IDs: [4](#0-3) 

Because the second attempt to create these same accounts hits `AmmError::RepeatCreateAmm` (the accounts already exist and are no longer owned by the system program), whoever's `Initialize2` transaction lands first "wins" the pool for that market permanently: [5](#0-4) 

An attacker monitoring the mempool can front-run a legitimate creator's `Initialize2` transaction by submitting their own with the same `market` account but attacker-chosen `init_pc_amount`/`init_coin_amount` (and hence attacker-chosen `user_token_coin`/`user_token_pc` source accounts) and a higher priority fee. The initial LP supply and price ratio are computed straight from the attacker's chosen deposit amounts: [6](#0-5) 

### Impact Explanation
Because pool creation is permissionless and unbound to the intended creator, this maps to the report's "Medium" bug class (front-runnable creation flow controlled by any unprivileged, non-governed actor) rather than the disputed governance-only scenario in the original Lens finding. In the AMM context the consequence is worse than simple handle-squatting: the attacker who wins the race controls the initial coin/pc ratio and the initial LP mint. They can:
- Seed the pool with an arbitrary, heavily skewed price (tiny `init_coin_amount` vs `init_pc_amount` or vice versa), then let the legitimate creator's follow-up transaction fail with `RepeatCreateAmm`, permanently denying them the intended pool address for that market.
- Since `Deposit` (`process_deposit`) adds liquidity proportionally to the *existing* vault ratio, any subsequent depositor (including the original intended creator, if they retry via `Deposit` instead) is forced to accept the attacker-set skewed price, resulting in economic loss or an insolvent-looking pool ratio relative to the token's real market value.
- Effectively hold the market's canonical pool address for ransom, exactly analogous to the handle-squatting scenario in the cited report.

### Likelihood Explanation
Any user can watch the mempool for `Initialize2` transactions (the instruction and all accounts, including the `market` pubkey, are visible in the transaction before confirmation), and resubmit an equivalent instruction with higher priority/compute fees. No privileged signer, leaked key, or governance compromise is required — this is reachable by any unprivileged pool-creation participant using the public `Initialize2` instruction, consistent with the reachable-instruction set for this scan (Initialize2, Deposit, Withdraw, swaps).

### Recommendation
Bind the derived AMM/mint/vault addresses (and/or add an explicit check) to the transaction's `user_wallet_info` or to a value only the legitimate market creator can supply (e.g., require `user_wallet_info.key` to match the market's authority, or incorporate a creator-supplied nonce/commitment into the seed derivation) so that the winning creator of a given market cannot be substituted by an unrelated frontrunner. Alternatively, support a commit-reveal pattern for market→pool binding as suggested in the original report.

### Proof of Concept
1. Alice submits `Initialize2` for `market M` with `init_coin_amount = 1_000_000`, `init_pc_amount = 1_000_000` (fair price), sourced from her own coin/pc token accounts.
2. Attacker observes this pending transaction, computes the same deterministic `amm_pool`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`, `amm_target_orders` addresses for market `M` via `get_associated_address_and_bump_seed`, and submits their own `Initialize2` for the same market `M` with `init_coin_amount = 1`, `init_pc_amount = 1_000_000_000` (extreme skew), using their own token accounts, with a higher priority fee.
3. The attacker's transaction lands first: `generate_amm_associated_account`/`generate_amm_associated_spl_mint` succeed (accounts were system-owned), the pool is created with the attacker's skewed ratio and the attacker receives essentially all of the initial LP supply.
4. Alice's original transaction then executes second and fails at `generate_amm_associated_account`/`generate_amm_associated_spl_mint` with `AmmError::RepeatCreateAmm`, since the target accounts are no longer system-owned.
5. Any subsequent legitimate liquidity provider using `Deposit` for market `M` is forced to add liquidity at the attacker's skewed price ratio, and the attacker (holding the dominant LP share) can withdraw the deposited real value via `Withdraw`. [7](#0-6)

### Citations

**File:** program/src/processor.rs (L386-475)
```rust
    fn generate_amm_associated_spl_mint<'a, 'b: 'a>(
        program_id: &Pubkey,
        spl_token_program_id: &Pubkey,
        market_account: &'a AccountInfo<'b>,
        associated_token_account: &'a AccountInfo<'b>,
        user_wallet_account: &'a AccountInfo<'b>,
        system_program_account: &'a AccountInfo<'b>,
        rent_sysvar_account: &'a AccountInfo<'b>,
        spl_token_program_account: &'a AccountInfo<'b>,
        associated_owner_account: &'a AccountInfo<'b>,
        associated_seed: &[u8],
        mint_decimals: u8,
    ) -> ProgramResult {
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

**File:** program/src/processor.rs (L477-546)
```rust
    #[allow(clippy::too_many_arguments)]
    fn generate_amm_associated_account<'a, 'b: 'a>(
        program_id: &Pubkey,
        assign_to: &Pubkey,
        market_account: &'a AccountInfo<'b>,
        associated_token_account: &'a AccountInfo<'b>,
        user_wallet_account: &'a AccountInfo<'b>,
        system_program_account: &'a AccountInfo<'b>,
        _rent_sysvar_account: &'a AccountInfo<'b>,
        associated_seed: &[u8],
        data_size: usize,
    ) -> ProgramResult {
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

**File:** program/src/processor.rs (L684-714)
```rust
        msg!(arrform!(LOG_SIZE, "initialize2: {:?}", init).as_str());
        if !user_wallet_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let spl_token_program_id = token_program_info.key;
        check_assert_eq!(
            *ata_token_program_info.key,
            spl_associated_token_account::id(),
            "spl_associated_token_account",
            AmmError::InvalidSplTokenProgram
        );
        check_assert_eq!(
            *system_program_info.key,
            solana_system_interface::program::id(),
            "sys_program",
            AmmError::InvalidSysProgramAddress
        );
        let (expect_amm_authority, expect_nonce) =
            Pubkey::find_program_address(&[&AUTHORITY_AMM], program_id);
        if *amm_authority_info.key != expect_amm_authority || init.nonce != expect_nonce {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        if *create_fee_destination_info.key != config_feature::create_pool_fee_address::id() {
            return Err(AmmError::InvalidFee.into());
        }
```

**File:** program/src/processor.rs (L748-835)
```rust
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

        // create user ata lp token
        Invokers::create_ata_spl_token(
            user_token_lp_info.clone(),
            user_wallet_info.clone(),
            user_wallet_info.clone(),
            amm_lp_mint_info.clone(),
            token_program_info.clone(),
            ata_token_program_info.clone(),
            system_program_info.clone(),
        )?;

        // transfer user tokens to vault
        Invokers::token_transfer(
            token_program_info.clone(),
            user_token_coin_info.clone(),
            amm_coin_vault_info.clone(),
            user_wallet_info.clone(),
            init.init_coin_amount,
        )?;
        Invokers::token_transfer(
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
