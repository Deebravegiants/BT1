### Title
Front-runnable, market-key-only PDA derivation for pool accounts lets an attacker squat the canonical AMM pool for any market, blocking legitimate creation and seeding a manipulated pool - ([File: program/src/processor.rs])

### Summary
The original report's root cause is that `GovernorAlpha`'s `proposalId` is a bare, content-independent counter, so an attacker can front-run a `propose` call and cause a victim's `castVote` to bind to an unrelated proposal with the same ID. The analogous root cause exists in `AmmInstruction::Initialize2` processing: the addresses of the AMM account, its LP mint, target-orders account, and both vaults are derived *solely* from the public `market_info.key`, with no dependence on the creator, on transaction-specific salt, or on the pool’s actual content/parameters. Anyone who observes a pending `Initialize2` transaction for a given market can pre-compute these same PDAs and front-run the transaction, claiming the "canonical" pool identity for that market with attacker-chosen (and adversarial) parameters.

### Finding Description
In `process_initialize2`, the AMM account itself, the LP mint, the target-orders account, and the coin/pc vaults are all created via `generate_amm_associated_account` / `generate_amm_associated_spl_mint` / `generate_amm_associated_spl_token`, each of which derives its expected address purely from `market_info.key` and a fixed seed string: [1](#0-0) 

The underlying derivation helper computes the PDA using only the program id, the market pubkey, and the fixed associated seed — nothing tied to the submitter, to the pool's initial reserves, or to any other content that would make each proposal/pool unique: [2](#0-1) [3](#0-2) 

Because these accounts must not already be owned by the SPL Token / AMM program (`generate_amm_associated_spl_token`/`generate_amm_associated_account` check `associated_token_account.owner == system_program_account.key` and error with `AmmError::RepeatCreateAmm` otherwise), only the **first** `Initialize2` transaction to land for a given `market_info.key` can ever succeed: [4](#0-3) 

This is the direct analog of the incrementing/predictable `proposalId`: exactly as `castVote(proposalId)` binds to whatever content ends up at that ID first, any downstream consumer that resolves "the AMM pool for market M" via this deterministic derivation binds to whichever `Initialize2` transaction lands first — regardless of who submitted it or what initial reserve ratio/parameters it used. An attacker (Mallory) observing a legitimate creator's (Bob's) pending `Initialize2` transaction for market `M` in the mempool can:
1. Compute the same deterministic `amm_info`, `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault` addresses from the public `market_info.key`.
2. Submit her own `Initialize2` for the same `market_info.key` with a higher fee, funding only the minimal amount required to pass `InitLpAmountTooLess`, using an arbitrary/skewed coin:pc ratio she controls: [5](#0-4) 
3. Her transaction claims all of the market-keyed PDAs first; Bob's now-conflicting `Initialize2` reverts entirely with `AmmError::RepeatCreateAmm` when it tries to initialize the same accounts.

### Impact Explanation
This meets the Medium bar for concrete harm to unprivileged users, analogous to the incorrect-binding impact in the source report:
- **Permanent squatting / freezing of pool creation for a market**: because the addresses are uniquely and deterministically tied to `market_info.key`, once Mallory's transaction lands, no legitimate `Initialize2` for that market can ever succeed again — this is a permanent denial of the intended pool for that trading pair.
- **Fund loss via a manipulated "canonical" pool**: since any client, aggregator, or user that resolves "the Raydium pool for market M" by recomputing this deterministic derivation will find Mallory's pool (not Bob's), unsuspecting LPs/swappers who deposit or swap against it interact with a pool whose initial coin:pc ratio and reserve mix were entirely chosen by the attacker, exposing them to a skewed price at pool "genesis" that Mallory can exploit immediately with follow-up swaps once real capital flows in.

### Likelihood Explanation
Any pool creation is inherently a public transaction (market pubkey, mint pubkeys are plaintext in the instruction), and the derivation seeds (`AMM_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, `PC_VAULT_ASSOCIATED_SEED`) are fixed program constants, so anyone monitoring the mempool for a specific market's first `Initialize2` can trivially reconstruct the exact target addresses and front-run with a higher priority fee — no special access or privileged role is required, matching the "reachable by unprivileged pool creator" criterion.

### Recommendation
Bind the derived AMM/PDA addresses to content that a front-runner cannot control or predict in advance — e.g., include the intended creator's pubkey, a user-chosen nonce/salt, or a hash of the intended initial parameters (mints, initial ratio) in the seed used for `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token`, so that a race on the same `market_info.key` cannot let an unrelated party claim the canonical pool identity ahead of the intended creator.

### Proof of Concept
1. Bob broadcasts `Initialize2` for market `M` with legitimate mints, real initial liquidity, and his wallet as `user_wallet_info`. The `amm_info`/`amm_target_orders`/`amm_lp_mint`/vault addresses he supplies are the PDAs derived only from `M` via `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token` (program/src/processor.rs:747-814).
2. Mallory observes this pending transaction, extracts `market_info.key = M` (public), and independently recomputes the identical PDAs using the same fixed seeds.
3. Mallory submits her own `Initialize2` for the same `market_info.key = M`, using her own mints/token accounts and a minimal, heavily skewed init_coin_amount/init_pc_amount just above the `InitLpAmountTooLess` threshold (program/src/processor.rs:908-917), with a higher priority fee so it lands first.
4. Mallory's transaction succeeds, initializing the market-M-keyed `amm_info`, `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, and `amm_pc_vault` with her attacker-chosen parameters.
5. Bob's transaction then executes and fails at `generate_amm_associated_spl_token`/`generate_amm_associated_account` with `AmmError::RepeatCreateAmm` (program/src/processor.rs:378-381), because those accounts are already owned by the token/AMM program — Bob can never create the legitimate pool for market `M`.
6. Any user or integrator resolving "the pool for market M" via the same deterministic derivation lands on Mallory's pool and trades against her manipulated initial ratio, exposing them to loss.

### Citations

**File:** program/src/processor.rs (L294-316)
```rust
    fn generate_amm_associated_spl_token<'a, 'b: 'a>(
        program_id: &Pubkey,
        spl_token_program_id: &Pubkey,
        market_account: &'a AccountInfo<'b>,
        associated_token_account: &'a AccountInfo<'b>,
        token_mint_account: &'a AccountInfo<'b>,
        user_wallet_account: &'a AccountInfo<'b>,
        system_program_account: &'a AccountInfo<'b>,
        rent_sysvar_account: &'a AccountInfo<'b>,
        spl_token_program_account: &'a AccountInfo<'b>,
        associated_owner_account: &'a AccountInfo<'b>,
        associated_seed: &[u8],
    ) -> ProgramResult {
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

**File:** program/src/processor.rs (L386-408)
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

**File:** program/src/processor.rs (L908-917)
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
```
