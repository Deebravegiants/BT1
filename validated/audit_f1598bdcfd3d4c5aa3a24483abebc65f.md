## Title
Permissionless PDA-squatting of `Initialize2`-derived accounts enables pool-creation DoS - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every account it creates for a new AMM pool (`amm_info`, `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`) deterministically from `find_program_address(&[program_id, market.key, seed], program_id)`, and the instruction is fully permissionless — any signer can call `Initialize2` supplying an arbitrary `market_info` account, since the code explicitly treats it as "Just a seed for AMM account. Can be any account." An attacker can therefore pre-occupy the deterministic addresses for a market that a legitimate user is about to launch a pool for, permanently blocking that user's pool creation — the same CREATE2-address-squatting DoS class described in the referenced Yield `Join`/`Wand` report.

### Finding Description
The PDA derivation helper is: [1](#0-0) 

and is used by `generate_amm_associated_account`, `generate_amm_associated_spl_token`, and `generate_amm_associated_spl_mint`, each of which only proceeds if the target address is still system-owned, otherwise returning `RepeatCreateAmm`: [2](#0-1) 

`process_initialize2` calls these helpers keyed only on `market_info.key` (plus fixed seed constants), and the comments confirm `market_info` is not validated as belonging to a real, unique Serum/OpenBook market — it is accepted as any account: [3](#0-2) 

Because `Initialize2` itself has no access control beyond a signer wallet and a token/fee payment (checked at lines 685-714), and requires only that the caller supply non-zero coin/pc vaults and a fresh LP mint they control, an attacker can complete a full (but economically minimal) `Initialize2` call using a `market_info` pubkey equal to the one a legitimate project intends to use for their real pool. This permanently assigns the deterministic `target_orders`/`lp_mint`/`coin_vault`/`pc_vault`/`amm_info` addresses derived from that `market` key to the program (owned, non-system), so any subsequent legitimate `Initialize2` call using the same `market_info` will hit the `RepeatCreateAmm` check in `generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` and revert.

This mirrors the CVE-style CREATE2-squatting issue in the referenced Yield report: the deterministic-address creation path is open to anyone, so an attacker can occupy the address the legitimate deployer will need before they use it, causing a denial of service for that specific market/pool.

### Impact Explanation
The impact is a griefing/DoS vector rather than direct fund theft: an attacker can prevent any specific market from ever having a Raydium pool created against it through the normal permissionless path, since the target addresses are exhausted. This can be used to block a competitor's pool launch or to grief a specific expected market ahead of a public launch. It does not by itself cause fund loss or affect already-initialized pools, but it is a concrete on-chain griefing capability reachable by an ordinary signer submitting a single `Initialize2` transaction with attacker-chosen accounts and data, consistent with the scope of Initialize2 being an unprivileged, reachable instruction.

### Likelihood Explanation
Likelihood is realistic: `Initialize2` requires only a funded wallet, control over two mints, minimal token balances to seed the initial vaults, and payment of the (possibly zero) `create_pool_fee`. There is no check binding `market_info` to any real market program ownership or uniqueness constraint beyond being a `Pubkey`, so an attacker only needs to guess or observe (e.g., via mempool monitoring) the `market` pubkey a legitimate deployer plans to use and front-run with their own `Initialize2` call.

### Recommendation
Tie the derived PDAs to a value that cannot be squatted independently of a validated, program-verified market (e.g., require `market_info` to be owned by a whitelisted market program and validate its base/quote mints match `amm_coin_mint`/`amm_pc_mint` before using it as a seed), or restrict `Initialize2` execution to a privileged pool-creation authority/factory so squatting via arbitrary `market_info` values is not possible, analogous to the Yield team's recommendation to move away from open, permissionless deterministic-address creation.

### Proof of Concept
1. Attacker observes/derives the `market` pubkey a legitimate team intends to use for a new pool (e.g., the OpenBook market for TOKEN/USDC).
2. Attacker submits `Initialize2` (`program/src/instruction.rs` lines 663-729) supplying that same `market_info` pubkey, their own two token mints/vaults with a non-zero token balance, and a fresh zero-supply LP mint, satisfying all checks in `process_initialize2` (lines 675-929).
3. `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token` successfully allocate and assign the PDAs derived from `[program_id, market.key, seed]` to the AMM program, marking them as no longer system-owned.
4. When the legitimate team later calls `Initialize2` for the real pool using the same `market_info` key, every call to `generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` hits the `else` branch and returns `AmmError::RepeatCreateAmm` (`program/src/processor.rs` lines 378-381, 470-474, 541-544), permanently blocking pool creation for that market through the front door.

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

**File:** program/src/processor.rs (L495-546)
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
