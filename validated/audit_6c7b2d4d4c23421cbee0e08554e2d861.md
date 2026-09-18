### Title
Permissionless `Initialize2` lets anyone front-run and permanently occupy the deterministic pool accounts for any market, DOSing legitimate pool creation - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives all of the AMM's core accounts (`amm_info`, `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`) as PDAs seeded solely by the caller-supplied `market_info` pubkey, with no validation that `market_info` is a genuine, owned-by-the-market-program account. Any unprivileged caller can invoke `Initialize2` with an arbitrary `market_info` pubkey (including a real, well-known market address that a legitimate project intends to use) plus attacker-chosen mints/amounts, permanently claiming those PDA slots. Because `generate_amm_associated_account` rejects account creation once the target is already program-owned, this permanently blocks any future, legitimate `Initialize2` call keyed to that same market pubkey.

### Finding Description
`process_initialize2` computes deterministic addresses for target orders, LP mint, coin/pc vaults, and the AMM account itself using `get_associated_address_and_bump_seed` / `find_program_address` keyed on `market_info.key`:

<cite repo="Alyssadaypin/raydium-amm--004" path="program/src/processor.rs" start="640="/> [1](#0-0) 

The comments in the code itself acknowledge `market_info` is not validated to be a real market: "Just a seed for AMM account. Can be any account." [2](#0-1) 

`generate_amm_associated_account` (used to create `amm_target_orders_info` and `amm_info`) only checks that the derived address is unoccupied by the system program; if it is already owned by the AMM program, it fails hard with `RepeatCreateAmm`: [3](#0-2) 

There is no signer/authority restriction tying who may call `Initialize2` for a given `market_info` seed - it is fully permissionless, and the only requirement is that `user_wallet_info` is a signer and pays for the created accounts: [4](#0-3) 

Because the PDAs are deterministic functions of `market_info.key` alone, an attacker can pre-emptively call `Initialize2` with:
- a real/foreseeable `market_info` pubkey that a legitimate team intends to use for their official pool (e.g., a known OpenBook market address, or any pubkey the attacker can predict/observe being prepared off-chain),
- throwaway/attacker-controlled coin/pc mints and minimal amounts (only constraint is `coin_mint != pc_mint` and non-zero vault balances) [5](#0-4) [6](#0-5) 

This successfully creates and assigns ownership of `amm_info`, `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, and `amm_pc_vault` for that market seed to the AMM program under the attacker's bogus pool. When the legitimate team later submits their genuine `Initialize2` for the same `market_info`, every `generate_amm_associated_account`/`generate_amm_associated_spl_*` call for that seed will see the target already owned by `program_id` and unconditionally return `AmmError::RepeatCreateAmm`, permanently blocking creation of the real pool at that deterministic address.

This is directly analogous to the reported bug class: a permissionless entry point (`passMessageToL1` / here `Initialize2`) lets an attacker inject attacker-controlled data into state that a downstream, security-critical, deterministic process (migration decode / here pool creation at a specific market-derived address) relies on being pristine, causing the legitimate process to permanently fail (DOS), with resulting reputational damage, delay, and griefing.

### Impact Explanation
The affected pool address is deterministic and public knowledge before creation. Any project/market whose PDA seed becomes known in advance can be griefed by a competitor or malicious actor who front-runs pool creation with garbage tokens, permanently preventing the legitimate token issuer from creating their official Raydium pool at that address. This causes reputational damage, forces the legitimate team to fragment liquidity to a different (undesired) address, and is a persistent (not just transaction-level) denial of service, matching the Medium severity of the analog report.

### Likelihood Explanation
The attack requires only a single permissionless transaction with attacker-chosen `market_info`, mints, and minimal token amounts - no elevated privileges, no race against validators beyond simple front-running, and no special conditions. Any market/pool that is publicly announced in advance (a very common occurrence for token launches) is a viable target, making this readily executable by any unprivileged actor.

### Recommendation
Validate that `market_info` is a genuine, program-owned market account (or otherwise enforce a stronger, harder-to-front-run binding, such as requiring the pool creator to also control/create the market, or gating `Initialize2` behind a whitelist/authority check) before deriving and creating dependent PDAs, so that arbitrary/unrelated callers cannot pre-claim the deterministic accounts tied to a specific market seed.

### Proof of Concept
1. Attacker observes/predicts the `market_info` pubkey a legitimate project will use for its official Raydium pool (e.g., a newly created OpenBook market or a pre-announced market address).
2. Attacker calls `initialize2` (`program/src/instruction.rs` `initialize2`, dispatched via `process_initialize2`) supplying that `market_info`, attacker-owned throwaway `amm_coin_mint`/`amm_pc_mint`, and minimal non-zero `init_coin_amount`/`init_pc_amount`.
3. `process_initialize2` derives `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`, `amm_info` from `market_info.key` and successfully creates/assigns them to the AMM program via `generate_amm_associated_account`/`generate_amm_associated_spl_*`.
4. Legitimate team later submits the real `Initialize2` transaction with the same `market_info` and correct mints; `generate_amm_associated_account` finds the derived accounts already owned by `program_id` and returns `AmmError::RepeatCreateAmm`, permanently blocking creation of the official pool for that market.

### Citations

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

**File:** program/src/processor.rs (L630-646)
```rust
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

**File:** program/src/processor.rs (L675-714)
```rust
        let (pda, _) = Pubkey::find_program_address(&[&AMM_CONFIG_SEED], program_id);
        if pda != *amm_config_info.key || amm_config_info.owner != program_id {
            return Err(AmmError::InvalidConfigAccount.into());
        }

        if *amm_coin_mint_info.key == *amm_pc_mint_info.key {
            return Err(AmmError::InvalidCoinMint.into());
        }

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

**File:** program/src/processor.rs (L858-866)
```rust
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
```
