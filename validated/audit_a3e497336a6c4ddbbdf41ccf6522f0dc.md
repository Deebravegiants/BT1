## Analog Found

### Title
Front-running/squatting the deterministic per-market AMM pool PDA lets any user permanently DOS a market's "real" pool creation for minimal cost — (File: `program/src/processor.rs`, function `process_initialize2`)

### Summary
`Initialize2` derives every pool-related account (`AmmInfo`, `TargetOrders`, LP mint, coin/pc vaults) deterministically from the OpenBook `market_info.key` via `generate_amm_associated_account` / `generate_amm_associated_spl_mint` / `generate_amm_associated_spl_token`, each keyed off a fixed seed (`AMM_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, etc.) and the market pubkey. Because the resulting addresses are 1:1 with the market, and Solana account creation fails once an account exists at that address, the *first* successful `Initialize2` call for a given market permanently claims that address space — regardless of how small the `init_coin_amount`/`init_pc_amount` are.

### Finding Description
`process_initialize2` accepts any caller (only requires `user_wallet_info.is_signer`), and enforces only that the deposited vault amounts are non-zero and that the resulting geometric-mean liquidity exceeds `10^lp_decimals` (`InitLpAmountTooLess`) — there is no minimum economically meaningful liquidity requirement tied to the actual market/token value: [1](#0-0) 

All the pool accounts for that market (`AmmInfo`, `TargetOrders`, LP mint, coin vault, pc vault) are created via PDA derivation seeded by `market_info.key`, not by the caller's own keys: [2](#0-1) 

Since these are `create_account`-style associated accounts tied only to `market_info.key` and `program_id`, once created for a market they cannot be created again — any subsequent legitimate `Initialize2` attempt for the *same* market (e.g. by the actual project team wanting to bootstrap a properly-funded pool) will fail at account creation, well before the `AlreadyInUse` status check is even reached: [3](#0-2) 

This mirrors the Tessera `[H-05]` pattern exactly: a low-value, minimally-priced action (there, a `_collateral = 1` proposal; here, `init_coin_amount`/`init_pc_amount` set to the smallest values that clear `InitLpAmountTooLess`) permanently occupies a scarce, deterministically-addressed resource slot and blocks the legitimate/economically meaningful action from ever being performed for that market.

### Impact Explanation
Any unprivileged user can pay only the rent for a handful of small accounts plus a negligible amount of the two mints (just above `10^decimals` combined liquidity) to squat the PDA-derived pool for any OpenBook market before the legitimate market maker/project does. Because the pool address space is permanently consumed, the real pool for that market can never be created through this program instance — a persistent denial of service against pool creation for that market, and by extension against all downstream deposit/withdraw/swap functionality that depends on a properly-funded pool existing at that canonical address.

### Likelihood Explanation
High: `Initialize2` is a fully permissionless, single-transaction instruction reachable by anyone; the attacker only needs to know the target market pubkey (public in OpenBook) and race (or simply precede) the legitimate creator. No privileged signer, leaked key, or off-chain condition is required.

### Recommendation
Enforce a meaningful minimum notional value for `init_coin_amount`/`init_pc_amount` (or require permissioned/whitelisted pool creation per market), and/or allow an authorized re-initialization/migration path for a market whose pool was created with dust liquidity, so that a trivially-funded pool cannot permanently block a properly-funded one for the same market.

### Proof of Concept
1. Attacker observes a new OpenBook market about to be paired with a Raydium pool.
2. Attacker calls `Initialize2` for that `market_info` with `init_coin_amount` and `init_pc_amount` set to the minimum values that satisfy `liquidity.checked_sub(10^lp_decimals)` in `process_initialize2` (program/src/processor.rs:908-917), e.g. amounts producing `liquidity = 10^lp_decimals + 1`.
3. This creates the deterministic `AmmInfo`, `TargetOrders`, LP mint, coin vault, and pc vault PDAs for that market (program/src/processor.rs:748-804), each seeded solely by `market_info.key`.
4. The legitimate team subsequently attempts `Initialize2` for the same market with real liquidity; the account-creation calls for the same PDAs fail because the accounts already exist, before the `AlreadyInUse` status check at program/src/processor.rs:845-847 is even reached.
5. The market is permanently stuck with a dust-liquidity pool that no one can replace via this instruction path.

### Citations

**File:** program/src/processor.rs (L748-804)
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
```

**File:** program/src/processor.rs (L843-847)
```rust
        // load AmmInfo
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
