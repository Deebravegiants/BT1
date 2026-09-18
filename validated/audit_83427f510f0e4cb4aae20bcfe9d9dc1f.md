### Title
Permanent AMM-pool "market squatting" Denial of Service via unchecked `market_info` seed in `process_initialize2` - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every deterministic account for a pool (target orders, LP mint, coin/pc vaults, `AmmInfo`) from `market_info.key` alone, with no validation that `market_info` is an actual, legitimate Serum/OpenBook market for the intended coin/pc pair. Any unprivileged caller can call `Initialize2` with an arbitrary `market_info` pubkey (plus attacker-chosen, worthless coin/pc mints and a minimal `init_coin_amount`/`init_pc_amount`) to permanently occupy the PDA-derived addresses tied to that market key, which will make every future legitimate `Initialize2` attempt using that same market fail forever.

### Finding Description
`generate_amm_associated_account` / `generate_amm_associated_spl_mint` / `generate_amm_associated_spl_token` compute the associated address purely as: [1](#0-0) 
i.e. `create_program_address([program_id, market_account.key, seed, bump], program_id)`. If the derived address is already owned by something other than the System Program, the call fails with `AmmError::RepeatCreateAmm` rather than proceeding: [2](#0-1) 

In `process_initialize2`, the comment explicitly documents that `market_info` is **not validated** as belonging to a real market program — "Just a seed for AMM account. Can be any account.": [3](#0-2) 

The only checks performed are on the config PDA, coin/pc mint inequality, signer status of the user wallet, and the SPL/system program IDs — there is no check that `market_info.owner` equals the OpenBook/Serum market program, nor any binding of `market_info` to the specific `coin_mint`/`pc_mint` pair being initialized: [4](#0-3) 

Because the derived accounts (`amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`, `amm_info`) are all keyed only off `market_info.key`, any attacker can precompute these addresses for a market pubkey they expect a legitimate project to use, then submit their own `Initialize2` transaction first with dust liquidity and throwaway mints for that same `market_info`. Once that first transaction succeeds, the accounts at those derived addresses become permanently owned by the program (`spl_token`/AMM program) and initialized, so the legitimate team's subsequent `Initialize2` for the real coin/pc pair on that same market will always hit `RepeatCreateAmm` and can never succeed — there is no closing/reset instruction to reclaim or reassign the squatted addresses (`WithdrawPnl` and `SetParams` only operate on already-initialized state, they do not free the account for a fresh pool creation).

This is directly analogous to the reported bug class: absence of a uniqueness/ownership check on an attacker-controllable identifier (login name in RuoYi; `market_info` pubkey here) lets any unprivileged actor permanently squat the resource, denying legitimate use forever.

### Impact Explanation
This is a permanent Denial of Service against pool creation for any market of the attacker's choosing. Any project intending to launch an AMM pool tied to a specific serum/openbook market can be permanently blocked from ever creating that pool if an attacker front-runs them with a garbage `Initialize2` call using the same `market_info` key. This does not directly drain existing pool funds, but it permanently and unrecoverably denies legitimate market participants (pool creators / LPs) the ability to use that market address for an AMM pool — a lasting griefing/freezing effect reachable from a single unprivileged transaction with attacker-chosen accounts and data.

### Likelihood Explanation
High reachability: `Initialize2` is a fully public, unprivileged instruction; `market_info` accounts, coin/pc mints, vaults, and the user wallet are all attacker-supplied and require only minimal token amounts (`init_coin_amount`/`init_pc_amount` need only be non-zero) and normal SPL token/mint creation, which is cheap. An attacker can front-run any observed pending pool-creation transaction (mempool/transaction visibility) or preemptively squat popular/anticipated market pubkeys.

### Recommendation
Bind `market_info` to `coin_mint`/`pc_mint` and validate it is owned by the expected market program (or otherwise verify legitimacy) before deriving associated accounts, so that squatting an address space with unrelated garbage mints is not possible; alternatively, derive the AMM's associated PDAs from the coin/pc mint pair (or another value the legitimate creator controls, e.g., mint pair plus the true market account validated against the market program) instead of an unauthenticated arbitrary account key.

### Proof of Concept
1. Attacker observes/predicts the `market_info` pubkey a legitimate team plans to use for pool creation (e.g., a specific OpenBook market for `TOKEN/USDC`).
2. Attacker creates two throwaway SPL mints (`coin_mint`, `pc_mint`) and funds tiny token accounts.
3. Attacker calls `Initialize2` (`program/src/processor.rs:549`) with the observed `market_info`, their own throwaway mints, `init_coin_amount = 1`, `init_pc_amount = 1`; the PDA derivations for `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault`, and `amm_info` are computed solely from `market_info.key` [1](#0-0) , so these succeed and become permanently initialized and owned by the program.
4. When the legitimate team later calls `Initialize2` with the same `market_info` and their real `coin_mint`/`pc_mint`, the derived addresses match the attacker's already-initialized accounts (owner != system program), causing `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token` to return `AmmError::RepeatCreateAmm` [2](#0-1) , permanently preventing pool creation on that market.

### Citations

**File:** program/src/processor.rs (L489-498)
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
```

**File:** program/src/processor.rs (L540-546)
```rust
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
