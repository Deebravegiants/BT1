### Title
Front-running `Initialize2` lets an attacker permanently hijack a target OpenBook market's pool address and seed it with a manipulated initial price - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every pool-related account (AMM account, LP mint, coin/pc vaults, target-orders account) deterministically from the `market_info` pubkey via `get_associated_address_and_bump_seed(program_id, &market_account.key, associated_seed, program_id)`, and the instruction is fully permissionless — any signer can call it for any market. Because the resulting addresses depend only on the market key (never on the caller), an attacker can observe a pending legitimate `Initialize2` transaction in the mempool and front-run it with their own `Initialize2` call for the *same market/mint pair*, consuming the deterministic PDAs first. [1](#0-0) [2](#0-1) 

### Finding Description
`generate_amm_associated_account`, `generate_amm_associated_spl_token`, and `generate_amm_associated_spl_mint` all gate creation on `associated_token_account.owner == system_program_account.key`; if the account has already been allocated/assigned (owner not System), they return `AmmError::RepeatCreateAmm` instead of proceeding. [3](#0-2) [4](#0-3) [5](#0-4) 

Since `Initialize2` performs no check that the calling `user_wallet_info` is any particular authorized creator, and the target PDAs are derived solely from `market_info.key` (a value the attacker can read directly out of the victim's unconfirmed transaction), an attacker can:
1. Copy the victim's `market_info`, `amm_coin_mint_info`, `amm_pc_mint_info` accounts from the pending transaction.
2. Submit their own `Initialize2` with the same market/mints but attacker-chosen `init_coin_amount`/`init_pc_amount` (as small as allowed) and their own `user_wallet_info`/token accounts, with a higher priority fee to land first.
3. Because `Initialize2` finishes fully (creates AMM account, LP mint, vaults, mints LP to the attacker) in one transaction, the pool for that market now exists, owned by the program, with a price ratio the attacker fully controls.
4. The victim's original `Initialize2` transaction then reverts permanently with `AmmError::RepeatCreateAmm` (during `generate_amm_associated_account`) — there is no way to retry for that same market, since the addresses are immutably tied to the market pubkey.

This mirrors the InstaDApp `build`/`setOwner` bug class: an attacker uses a permissionless "create" entrypoint keyed on a value the victim will also use, to pre-empt and permanently block the victim's legitimate state-establishing transaction, while simultaneously seizing control of the resulting privileged state (here, the pool's initial LP supply and price).

The initial liquidity check only requires `liquidity > 10^lp_decimals` [6](#0-5) , so an attacker can create the pool with a heavily skewed coin:pc ratio using minimal capital, e.g. depositing 1 unit of one side and a large amount of the other, establishing an extreme initial price that later legitimate LPs/swappers interact with, and mint themselves the entire initial LP supply.

### Impact Explanation
- Permanent denial of service: the intended pool creator can never initialize the pool for that specific OpenBook market once the attacker's transaction lands first — the deterministic PDA is consumed and `RepeatCreateAmm`/`AlreadyInUse` will fire on every retry.
- Insolvent/manipulated pool accounting: the attacker fully controls the coin/pc ratio and LP mint amount at genesis (`Invokers::token_mint_to` mints `user_lp_amount` only to the attacker's `user_token_lp_info`) [7](#0-6) , letting them set an arbitrary skewed initial price with minimal capital, which later depositors/swappers interact with at a disadvantage.

### Likelihood Explanation
`Initialize2` is a standard, unprivileged instruction reachable in a single transaction with attacker-chosen accounts and data; any observer of the mempool (or of an announced pool-creation event) can construct a competing transaction using the same market/mint accounts. No signer/owner check restricts who may call `Initialize2` for a given market, so the attack requires only normal transaction front-running capability.

### Recommendation
Restrict pool creation for a given market to a designated/whitelisted creator (or require a two-step commit/reveal or minimum-liquidity/ratio bound enforced against an oracle/market reference price), and/or bind the derived AMM PDAs to the actual first-mover's intended parameters (e.g., require `market_info` to already reference the coin/pc mints being initialized, and add a minimum liquidity floor plus slippage/ratio bounds) so that a front-runner cannot cheaply seize a specific market's pool address with an arbitrary skewed price.

### Proof of Concept
1. Victim broadcasts `Initialize2` for market `M` with mints `coin`/`pc`, depositing balanced liquidity.
2. Attacker observes the pending transaction, extracts `market_info = M`, `amm_coin_mint_info`, `amm_pc_mint_info`.
3. Attacker submits their own `Initialize2` instruction (same market/mints, their own wallet/token accounts, minimal `init_coin_amount`/`init_pc_amount` skewed heavily to one side) with a higher fee so it lands first.
4. Attacker's transaction succeeds: PDAs for AMM/vaults/LP mint/target-orders for market `M` are created and assigned to the program [8](#0-7) ; LP tokens are minted entirely to the attacker.
5. Victim's original transaction now fails in `generate_amm_associated_account`/`generate_amm_associated_spl_mint` with `AmmError::RepeatCreateAmm` because the PDAs are no longer owned by the System Program [9](#0-8) , permanently preventing the victim from creating the intended pool for market `M`, while the attacker holds a pool with a price ratio they chose.

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

**File:** program/src/processor.rs (L317-383)
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
    }
```

**File:** program/src/processor.rs (L470-475)
```rust
        } else {
            associated_token_address.log();
            return Err(AmmError::RepeatCreateAmm.into());
        }
        Ok(())
    }
```

**File:** program/src/processor.rs (L541-546)
```rust
        } else {
            associated_token_address.log();
            return Err(AmmError::RepeatCreateAmm.into());
        }
        Ok(())
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
