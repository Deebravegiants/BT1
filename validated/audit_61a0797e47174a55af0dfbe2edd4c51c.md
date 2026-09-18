This confirms the analog. The `market_info` account in `process_initialize2` is explicitly documented as "Just a seed for AMM account. Can be any account" — it is not validated to be an actual OpenBook/Serum market, nor is its ownership or content checked at all in either the 19-account or legacy branch.

### Title
Front-runnable pool creation causes permanent DoS of `Initialize2` via attacker-controlled `market_info` seed - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives all of the pool's core PDAs — LP mint, target orders, coin vault, and pc vault — deterministically from `market_info.key` combined with fixed seed constants, using `get_associated_address_and_bump_seed`. Because `market_info` is accepted as an arbitrary, unchecked account (explicitly commented as "Can be any account"), and the coin/pc mints and market are all public information visible in a pending transaction, an attacker can observe a legitimate user's `Initialize2` transaction in the mempool and front-run it with the identical `market_info`, `amm_coin_mint`, and `amm_pc_mint` accounts.

### Finding Description
The associated addresses are computed via: [1](#0-0) 
and consumed in `generate_amm_associated_spl_mint` / `generate_amm_associated_account`, which fail with `AmmError::RepeatCreateAmm` once those PDAs already have data/ownership other than the system program: [2](#0-1) [3](#0-2) 

The `market_info` account used as one of the PDA seeds is explicitly documented as unchecked/arbitrary in both account-parsing branches of `process_initialize2`: [4](#0-3) [5](#0-4) 

Since `amm_coin_mint`, `amm_pc_mint`, and `market_info` are all attacker-visible in the pending transaction (or even pre-known, since token mints for a to-be-launched pair are typically public ahead of pool creation), an attacker can submit their own `Initialize2` with the same three seed accounts first. This is the exact bug class described in the reference report: the deterministic address (here, the PDA set derived from `market_info` + fixed seed) is derived purely from front-runnable, attacker-visible input, with no `msg.sender`/submitter-binding component in the seed derivation.

### Impact Explanation
Once the attacker's `Initialize2` lands first, the LP mint, target-orders, coin-vault, and pc-vault PDAs for that `(market_info, seed)` combination become permanently owned/initialized by the program (or by the attacker with garbage state, e.g., a dust pool with 1 lamport of liquidity and near-zero mints). The legitimate creator's subsequent `Initialize2` call for the intended token pair permanently reverts with `RepeatCreateAmm`, since the PDAs are deterministically fixed and cannot be re-derived with a different, unblockable value. This is a permanent denial-of-service against a specific coin/pc pair, preventing the legitimate project team or LP from creating a normal pool for their token — a similar-shaped impact to the referenced `LeapFactory.createDrop()` finding, though here it manifests only as DoS rather than fund loss (the pool state itself is protected from more severe corruption by the subsequent liquidity/mint-authority checks in `process_initialize2`).

### Likelihood Explanation
Any transaction calling `Initialize2` is visible in the mempool before confirmation, and the three seed-relevant accounts (`market_info`, `amm_coin_mint`, `amm_pc_mint`) are copyable by an observer with no special privilege — no signature over these fields is required from the legitimate caller. Front-running a `Initialize2` transaction requires only submitting a higher-priority-fee transaction with the same account list before the victim's transaction executes.

### Recommendation
Incorporate the pool creator (`user_wallet_info.key`) or another submitter-bound, non-front-runnable value into the associated-address seed derivation in `get_associated_address_and_bump_seed`, e.g., add `user_wallet_info.key` to the seed set for the LP mint, vault, and target-orders PDAs so that a griefer cannot pre-empt the deterministic addresses intended for a specific creator. Alternatively, require `market_info` to be validated as an actual owned market account (as originally intended before OpenBook was decoupled), removing the "any account" acceptance that enables cheap, permission-less front-running of the seed.

### Proof of Concept
1. Victim broadcasts `Initialize2(nonce, open_time, init_pc_amount, init_coin_amount)` with `amm_coin_mint = M_coin`, `amm_pc_mint = M_pc`, `market_info = X`, and computed PDAs for `amm_lp_mint`, `amm_target_orders`, `amm_coin_vault`, `amm_pc_vault` derived per `get_associated_address_and_bump_seed(program_id, X, SEED, program_id)`.
2. Attacker observes the pending transaction, copies `M_coin`, `M_pc`, `X`, and the same derived PDA addresses, and submits their own `Initialize2` with a higher priority fee (attacker supplies their own dust `user_token_coin`/`user_token_pc` and any valid `user_wallet_info` signer).
3. Attacker's transaction lands first; `generate_amm_associated_spl_mint`/`generate_amm_associated_account` allocate and assign the PDAs to the program, completing pool initialization, per [6](#0-5) .
4. Victim's transaction now hits `associated_token_account.owner == system_program_account.key` as false for the same PDAs, returning `AmmError::RepeatCreateAmm` and permanently blocking the victim from creating a pool for `(M_coin, M_pc)` under that `market_info` seed.

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

**File:** program/src/processor.rs (L405-474)
```rust
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
```

**File:** program/src/processor.rs (L489-544)
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
```

**File:** program/src/processor.rs (L592-594)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L643-646)
```rust
            let _market_program_info = next_account_info(account_info_iter)?;
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L760-802)
```rust
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
```
