### Title
Permissionless, front-runnable `Initialize2` allows a malicious actor to seize deterministic pool PDAs and set an arbitrary initial price, permanently DoS-ing the legitimate pool creator - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives the AMM account, LP mint, coin/pc vaults and target-orders account deterministically from the caller-supplied `market_info` pubkey using `get_associated_address_and_bump_seed` [1](#0-0) , and mints the very first LP supply based purely on whatever `init_coin_amount`/`init_pc_amount` the caller funds the vaults with [2](#0-1) . Nothing in the instruction restricts who may call `Initialize2` for a given market, nor validates that `market_info` is a genuine OpenBook/Serum market matching the given `coin_mint`/`pc_mint` — the account is explicitly documented as "Just a seed for AMM account. Can be any account." [3](#0-2) . Any address can therefore be raced to initialize the deterministic pool PDA before the intended creator, exactly analogous to the referenced Morpho report where a market can be irreversibly created (and blocked from re-creation) by whoever gets there first with attacker-chosen parameters.

### Finding Description
`process_initialize2` computes the pool's associated accounts from `market_account.key` alone: [4](#0-3) 

These derived accounts (`amm_info`, `amm_lp_mint_info`, `amm_coin_vault_info`, `amm_pc_vault_info`, `amm_target_orders_info`) are created via `generate_amm_associated_*` helpers, which only fail with `RepeatCreateAmm` if the target address is *already* owned by something other than the system program [5](#0-4) . The instruction is permissionless: `user_wallet_info` merely needs to be a signer, with no check that it is the "legitimate" pool creator for that market [6](#0-5) . The `market_info` account is not validated against any real market state (no check that its registered base/quote mints equal `amm_coin_mint_info`/`amm_pc_mint_info`), so an attacker can pick the exact same `market_info`, `coin_mint`, and `pc_mint` that a legitimate creator intends to use.

Because the pool's initial price and LP allocation is derived solely from the caller-funded amounts: [2](#0-1) 

a malicious actor monitoring the network for a pending legitimate `Initialize2` transaction (or simply pre-emptively targeting a known upcoming market) can submit their own `Initialize2` with the same `market_info`/mint pair first, funding the vaults with minimal, arbitrarily skewed amounts (e.g. `init_pc_amount = 1`, `init_coin_amount = huge`, or vice versa). This:
1. Sets a manipulated initial price for the pool that the front-runner controls, letting them mint themselves the entire first LP supply at a favorable ratio and immediately extract value from any subsequent deposits/swaps at the corrected market price.
2. Permanently occupies the deterministic PDA set for that market. Since `amm_info`/vaults/mint accounts are now owned by the program (or otherwise non-system-owned), the legitimate creator's follow-up `Initialize2` call for the same market will always fail with `RepeatCreateAmm`/`AlreadyInUse` [7](#0-6) , permanently denying that market/mint pair from ever being paired with a fairly-priced Raydium pool.

This mirrors the Morpho Blue analog: a permissionless "create" entrypoint whose target identity (there: `id = hash(marketParams)`; here: PDA derived from `market_info`) can be claimed by any front-runner before the legitimate party, embedding attacker-chosen parameters (there: oracle; here: initial coin/pc ratio and vault funding) and making the operation un-repeatable, thus a durable DoS plus an economic manipulation vector.

### Impact Explanation
Impact is Medium-High: legitimate market creators are permanently blocked from creating a correctly-priced pool for that market/mint pair (fund-affecting DoS), and the attacker can capture the entire first-LP-mint economics of the pool by setting the skewed price themselves, which enables extraction of value from any later liquidity added at the "corrected" price — this is a fund-impacting vulnerability, not merely a griefing/compute issue.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to observe/predict a target `market_info`/mint pair before the legitimate creator's `Initialize2` transaction lands (mempool front-running or simply racing a known upcoming market), which is realistic given Solana's public transaction visibility and the fully deterministic PDA derivation.

### Recommendation
Add an explicit whitelist/authorization check restricting who may call `Initialize2` for a given market (e.g., requiring a signer bound to the market's real base/quote mint authority, or a permissioned "pool creator" registry), and/or validate `market_info` against genuine OpenBook/Serum market state (verifying its registered base/quote mint match the supplied `amm_coin_mint_info`/`amm_pc_mint_info`) before allowing account creation, so that only the intended creator's transaction for a specific market can ever succeed.

### Proof of Concept
1. Legitimate user A prepares an `Initialize2` transaction for market `M` with mints `(C, P)` intending to deposit a fair-value ratio of `init_coin_amount`/`init_pc_amount`.
2. Attacker observes transaction `A` (or predicts market `M` will be used), and submits their own `Initialize2` for the same `market_info = M`, `amm_coin_mint_info = C`, `amm_pc_mint_info = P`, but with a heavily skewed `init_coin_amount`/`init_pc_amount` ratio, funded from the attacker's own token accounts, with higher priority fee to land first.
3. Attacker's transaction succeeds: PDAs for `amm_info`, `amm_lp_mint_info`, vaults, `target_orders` are created and owned by the program at `process_initialize2` lines [8](#0-7) ; attacker receives the full first LP mint at the skewed ratio via `Invokers::token_mint_to` [9](#0-8) .
4. User A's original transaction now fails at `RepeatCreateAmm` (accounts no longer system-owned) or `AlreadyInUse` [7](#0-6) , permanently preventing A from creating the intended fairly-priced pool for market `M`.

### Citations

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

**File:** program/src/processor.rs (L592-594)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L685-687)
```rust
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

**File:** program/src/processor.rs (L844-847)
```rust
        let mut amm = AmmInfo::load_mut(&amm_info)?;
        if amm.status != AmmStatus::Uninitialized.into_u64() {
            return Err(AmmError::AlreadyInUse.into());
        }
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

**File:** program/src/processor.rs (L921-929)
```rust
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
