### Title
Unprivileged front-running of `Initialize2` allows griefing/hijacking of a target market's AMM pool address with an attacker-chosen price ratio - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` (invoked via `AmmInstruction::Initialize2`) creates the `AmmInfo` account, coin/pc vaults and LP mint at addresses that are deterministically derived from the `market_info.key` seed alone [1](#0-0) . There is no check that `market_info` corresponds to a real, matching OpenBook/Serum market for the supplied `amm_coin_mint_info`/`amm_pc_mint_info` — the account is explicitly documented as "Just a seed for AMM account. Can be any account" [2](#0-1) . Any signer can submit `Initialize2` for a given market key with self-chosen mints, vault balances, and `init_pc_amount`/`init_coin_amount`, permanently claiming the PDA for that market before the legitimate pool creator's transaction lands.

### Finding Description
`generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` derive the AMM, vault, and LP-mint addresses purely from `program_id` + `market_info.key` + a fixed seed suffix (e.g. `AMM_ASSOCIATED_SEED`) [3](#0-2) . Because these addresses depend only on the market key (which is public/predictable once a project decides which market to use), any unprivileged party watching the network can submit their own `Initialize2` transaction using the same `market` account before the intended pool creator's transaction executes.

The only checks performed are: signer presence, program-id/authority PDA correctness, the AMM config account, and that `create_fee_destination` matches the hardcoded fee address [4](#0-3) . Nothing binds `amm_coin_mint_info`/`amm_pc_mint_info` to the actual base/quote mints of the referenced market, and nothing prevents an arbitrary caller from choosing the initial reserve ratio via `init_pc_amount`/`init_coin_amount` [5](#0-4) . The attacker only needs enough of the two tokens to satisfy `InitLpAmountTooLess` (`liquidity > 10^lp_decimals`) [6](#0-5) , which can be trivially small.

Once the attacker's transaction lands first, `generate_amm_associated_account` will see the target address already assigned and fail the legitimate creator's later attempt with `AmmError::RepeatCreateAmm` [7](#0-6) , permanently preventing the intended pool from ever being created with the intended price/parameters for that market.

### Impact Explanation
By front-running `Initialize2`, an attacker permanently seizes the deterministic PDA for a targeted market and sets an arbitrary initial coin:pc reserve ratio while minting themselves virtually the entire initial LP supply (`user_lp_amount = liquidity - 10^decimals`) [8](#0-7) . This enables:
- Denial of service for the legitimate project (their pool creation transaction reverts with `RepeatCreateAmm`, permanently blocking that market from ever hosting the intended pool address).
- Price manipulation griefing: the attacker can set a heavily skewed initial ratio, then any subsequent depositors/swappers who assume the pool reflects a fair market price interact with a mispriced pool, allowing the attacker (holding nearly all LP tokens and controlling the initial state) to extract value from unsuspecting swappers via the swap instructions once real liquidity/trading volume arrives.

This is a fund-safety issue for future users of that market's pool (mispriced trades, LP dilution against a hijacked ratio) rather than a direct drain of an existing pool's vaults, but it is a concrete, unprivileged, reachable attack via a single transaction using attacker-chosen accounts and data.

### Likelihood Explanation
High reachability: `Initialize2` is a fully public, unprivileged instruction reachable in a single transaction; the only "cost" is paying the (possibly zero) `create_pool_fee` and providing minimal token amounts to satisfy the liquidity floor [9](#0-8) . Any observer of a pending pool-creation transaction (or anyone who knows in advance which market a project intends to use) can race it.

### Recommendation
Bind the pool address to more than just the market pubkey (e.g., require the transaction to be signed by a designated pool-creation authority, or add a create-pool allow-list/registry keyed by market that only a trusted party can populate), and/or validate that `amm_coin_mint_info`/`amm_pc_mint_info` genuinely match the base/quote mints of the OpenBook market referenced by `market_info` before allowing initialization, rather than treating `market_info` as an arbitrary seed.

### Proof of Concept
1. Attacker observes (or predicts) the `market` pubkey a project intends to use for `Initialize2`.
2. Attacker derives the same PDAs (`AmmInfo`, coin vault, pc vault, lp mint) via `AMM_ASSOCIATED_SEED`/`COIN_VAULT_ASSOCIATED_SEED`/etc. using that `market` key [10](#0-9) .
3. Attacker submits their own `Initialize2` transaction first, supplying arbitrary/self-controlled coin & pc mints (or matching mints but a skewed `init_pc_amount`/`init_coin_amount` ratio) and their own wallet as `user_wallet`/`user_token_lp`.
4. `process_initialize2` succeeds, creates the accounts at the market-derived PDAs, and mints almost all initial LP supply to the attacker [11](#0-10) .
5. The legitimate project's subsequent `Initialize2` transaction for the same market fails with `AmmError::RepeatCreateAmm` [7](#0-6) , permanently blocking legitimate pool creation and leaving an attacker-controlled, mispriced pool associated with that market.

### Citations

**File:** program/src/processor.rs (L478-546)
```rust
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

**File:** program/src/processor.rs (L592-594)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
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

**File:** program/src/processor.rs (L715-729)
```rust
        let amm_config = AmmConfig::load_checked(&amm_config_info, program_id)?;
        // Charge the fee to create a pool
        if amm_config.create_pool_fee != 0 {
            invoke(
                &system_instruction::transfer(
                    user_wallet_info.key,
                    create_fee_destination_info.key,
                    amm_config.create_pool_fee,
                ),
                &[
                    user_wallet_info.clone(),
                    create_fee_destination_info.clone(),
                    system_program_info.clone(),
                ],
            )?;
```

**File:** program/src/processor.rs (L748-814)
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

**File:** program/src/instruction.rs (L29-38)
```rust
pub struct InitializeInstruction2 {
    /// nonce used to create valid program address
    pub nonce: u8,
    /// utc timestamps for pool open
    pub open_time: u64,
    /// init token pc amount
    pub init_pc_amount: u64,
    /// init token coin amount
    pub init_coin_amount: u64,
}
```
