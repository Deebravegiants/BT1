### Title
Permissionless `Initialize2` pool-account PDAs are derived only from the `market` key, letting an attacker front-run pool creation and permanently deny a chosen market's legitimate AMM pool - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every account tied to a new AMM pool — the AMM state account, its LP mint, coin/pc vaults, and target-orders account — from a PDA that is seeded **only** by the `market` account key and a fixed seed string, never by the coin/pc mint, config, or initial amounts supplied in the instruction. Because `Initialize2` has no signer/authority check binding the caller to the `market` account (any account can be supplied as the "market" seed and any wallet can sign as `user_wallet_info`), an attacker who observes a pending `Initialize2` transaction in the mempool can front-run it using the *same* `market_info` account but attacker-chosen mints/config/amounts. Since the PDAs collide (they don't encode the mints), the attacker's transaction wins the race and permanently claims all the associated accounts for that market, causing the legitimate creator's transaction to fail with `RepeatCreateAmm` forever. This is the same "hash/ID excludes a critical parameter" root cause seen in the Ajna `proposeExtraordinary` finding — the identifying key that gates "does this state already exist" omits distinguishing inputs, enabling risk-free front-run griefing that permanently blocks legitimate operation.

### Finding Description
The AMM-associated PDA is computed by `get_associated_address_and_bump_seed`, seeded with `program_id`, `market_address`, and a static seed suffix — nothing else: [1](#0-0) 

`process_initialize2` uses this helper to create the target-orders account, LP mint, coin vault, pc vault, and the AMM state account, all keyed off the same `market_info` account: [2](#0-1) 

Each `generate_amm_associated_*` helper only checks that the target PDA is still owned by the System Program (i.e., unclaimed); if it has already been allocated/assigned, it returns `AmmError::RepeatCreateAmm` instead of succeeding: [3](#0-2) [4](#0-3) 

`process_initialize2` requires only that `user_wallet_info` is a signer — there is no check that the caller is authorized in relation to `market_info`, nor that the coin/pc mints or amounts match anything committed to on-chain beforehand: [5](#0-4) 

Because the PDAs derived for the pool's core accounts depend solely on the `market` pubkey, an attacker can:
1. Observe a legitimate `Initialize2` transaction in the mempool targeting a specific `market_info`.
2. Submit their own `Initialize2` transaction with the identical `market_info` account (and any attacker-controlled coin/pc mints, config, and even trivial `init_coin_amount`/`init_pc_amount`) and their own wallet as `user_wallet_info`.
3. Have their transaction land first, permanently allocating the AMM/target-orders/LP-mint/vault PDAs for that market to the attacker's pool.
4. The legitimate creator's transaction then fails at `generate_amm_associated_account`/`generate_amm_associated_spl_token` with `AmmError::RepeatCreateAmm`, since the owner of those PDAs is no longer the System Program.

This mirrors the referenced bug class: the "existence key" (here, the PDA derivation) omits parameters that should differentiate one legitimate pool creation from another (the actual mints/config/amounts), allowing a cheap front-run to permanently squat on the identity and block the intended operation.

### Impact Explanation
Any specific `market` account (e.g., an OpenBook/Serum market) can be permanently prevented from ever backing a legitimate Raydium pool by a griefer who spends only transaction fees. Since the market account itself is often externally created and costly (market creation on OpenBook/Serum requires significant rent for the order book, event queue, bids/asks), the victim's sunk cost in creating that market is wasted once the attacker claims the market-derived PDAs with worthless parameters. This is a targeted, permanent denial-of-service against specific pool creators/projects, satisfying the "permanent freezing" bar (freezing the ability to ever complete a legitimate pool launch for that market/creator) rather than merely a temporary inconvenience.

### Likelihood Explanation
The attack is trivially executable by any unprivileged actor: it requires no special accounts, no elevated privileges, and only mempool visibility plus normal transaction fees to win the race by paying a higher priority fee or simply resubmitting instantly. `Initialize2` is a fully permissionless, unprivileged-user-reachable instruction, matching the in-scope surfaces.

### Recommendation
Bind the PDA derivation (and/or add an explicit authorization check) to more than just the `market` pubkey so that an attacker cannot preempt a specific creator's intended pool parameters:
- Include the intended `coin_mint`, `pc_mint`, and/or the `user_wallet` (creator) pubkey in the seed derivation used by `get_associated_address_and_bump_seed`, so a front-runner cannot produce the same PDA with different mints.
- Alternatively/additionally, require the `market_info` account to prove some binding to the caller (e.g., verify the market's quote/base mints match `amm_coin_mint_info`/`amm_pc_mint_info` before allocating), and/or have callers pre-commit (e.g., via a nonce/salt supplied by the true creator) so that front-running with mismatched parameters cannot succeed.
- At minimum, treat `RepeatCreateAmm` collisions with different mint arguments as a signal to reject and refund rather than let the earliest transaction silently win with arbitrary parameters.

### Proof of Concept
1. Alice creates an OpenBook `market` account for token pair (X, Y) and prepares an `Initialize2` transaction using `initialize2(...)` with `amm_coin_mint = X`, `amm_pc_mint = Y`, and broadcasts it. [6](#0-5) 
2. Mallory observes Alice's pending transaction, extracts `market_info = Alice's market pubkey`, and submits her own `Initialize2` transaction using the same `market_info`, but with arbitrary mints she controls (or even a trivial/no-op mint pair) and minimal `init_coin_amount`/`init_pc_amount`, signed by her own wallet.
3. Because `get_associated_address_and_bump_seed` derives the AMM/target-orders/LP-mint/vault PDAs solely from `program_id` + `market_info.key` + seed suffix, Mallory's transaction — if it lands first — successfully allocates and initializes all associated accounts for that market: [1](#0-0) 
4. Alice's original transaction now fails: `generate_amm_associated_account`/`generate_amm_associated_spl_token` find the PDAs already owned by the program (not the System Program) and return `AmmError::RepeatCreateAmm`: [7](#0-6) 
5. Alice can never create the intended pool for that market again; the market account and any rent spent creating it are permanently unusable for their intended purpose.

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

**File:** program/src/processor.rs (L684-687)
```rust
        msg!(arrform!(LOG_SIZE, "initialize2: {:?}", init).as_str());
        if !user_wallet_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
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

**File:** program/src/instruction.rs (L664-729)
```rust
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
