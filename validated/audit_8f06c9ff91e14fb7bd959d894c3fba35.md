## Title
`Initialize2` pool creation can be front-run and permanently DoS'd because the deterministic PDA seed for AMM/vault/mint/target-orders accounts depends only on the public `market` account - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every account that defines a Raydium pool (the `AmmInfo` account, LP mint, coin/pc vaults, and target-orders account) from a PDA whose seeds are only `program_id`, the OpenBook/Serum `market` pubkey, and a fixed constant string. No account derived from `msg.sender`/the caller's wallet, the chosen coin/pc mints, or any other caller-supplied secret is included in the seed. Because `market` is a pre-existing, publicly known account (it must already exist on the market program before `Initialize2` can be called), an attacker who observes a pending `Initialize2` transaction in the mempool can compute the exact same PDAs and submit a front-running transaction that claims them first, exactly as described in the reported `Factory.createMarket` issue where the salt is derived from the public `pool` argument only.

### Finding Description
The seed-derivation helper used for every pool-defining account only takes the market account and a static seed suffix: [1](#0-0) 

This function is used to derive the `AmmInfo` account, the LP mint, the coin/pc vaults, and the target-orders account, all keyed **solely** off `market_account.key`: [2](#0-1) 

Each of the three `generate_amm_associated_*` helpers checks that the derived address is still owned by the system program (i.e., not yet created); if it is not, it fails with `AmmError::RepeatCreateAmm` instead of proceeding: [3](#0-2) [4](#0-3) 

Because these PDAs depend only on the public `market` pubkey (and not on the caller's wallet, chosen mints, or any other value only the legitimate creator would supply before broadcasting), any account watching the mempool can:
1. See a pending `Initialize2` transaction that references market `M`.
2. Immediately construct and submit their own `Initialize2` transaction using the same market `M` but attacker-chosen `amm_coin_mint`/`amm_pc_mint` and minimal `init_coin_amount`/`init_pc_amount`.
3. Get their transaction confirmed first, which permanently assigns ownership of the deterministic PDA addresses (the `AmmInfo`, LP mint, coin vault, pc vault, target-orders accounts) to the program under the attacker's pool state.
4. The legitimate creator's transaction, using the same market, now fails permanently with `RepeatCreateAmm` because the accounts already exist and are no longer owned by the system program.

The account addresses derived from `market` are also the canonical addresses users/off-chain integrations look up for "the Raydium pool for market `M`" (see `amm.market = *market_info.key;` at line 973), so once occupied by the attacker's low-liquidity/garbage-mint pool, that market's canonical pool address is permanently unusable for its intended token pair. [5](#0-4) 

### Impact Explanation
This permanently and irrecoverably freezes the ability to create the legitimate AMM pool for that market: the deterministic PDA slot is consumed forever by the attacker's pool (there is no `close`/reclaim path for these associated accounts). This is not merely a one-time revert-and-retry annoyance (as in typical front-running DoS) — because the address space is fully deterministic on `market` alone, the attacker can always win the race for any given market, permanently blocking that market from ever getting Raydium's canonical pool. This also creates a spoofing risk: users or integrators who trust "the pool at the canonical derived address for market M" could be tricked into interacting with the attacker's garbage-mint pool, believing it is the project's intended liquidity pool.

### Likelihood Explanation
`market` accounts are public on-chain state (created via the OpenBook/Serum market program) before `Initialize2` is ever called, so an attacker does not need any privileged information — only mempool visibility of the `Initialize2` transaction, or even just prior knowledge of a market's existence, to preemptively claim the PDA slot. The only cost to the attacker is the rent for the pool accounts and the `create_pool_fee`, both attacker-affordable and reusable as griefing tooling against any target project preparing to list on Raydium.

### Recommendation
Include a value only the legitimate creator controls before broadcasting (e.g., `user_wallet_info.key`, or an explicit creator-chosen nonce/salt supplied and checked in the instruction data) in the seeds used by `get_associated_address_and_bump_seed`, in addition to `market_account.key`. This removes the fully-public, single-input determinism that allows an attacker to precompute and race for the same PDAs, while still keeping `market` as part of the seed to prevent multiple pools per market from the same creator if desired.

### Proof of Concept
1. Attacker monitors the mempool (or simply knows a market `M` is about to have a Raydium pool created for it — market creation itself is a public, prior event).
2. Attacker computes, using `Pubkey::find_program_address(&[program_id, M, AMM_ASSOCIATED_SEED], program_id)` (and similarly for `LP_MINT_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, `PC_VAULT_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`), the exact same addresses the legitimate creator's transaction will target — this is deterministic and requires only `M`, which is public.
3. Attacker submits their own `Initialize2` instruction referencing market `M`, with attacker-controlled `amm_coin_mint`/`amm_pc_mint` and minimal `init_coin_amount`/`init_pc_amount`, with higher priority fee/earlier slot than the victim's transaction.
4. `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token` succeed for the attacker (system-program-owned accounts get allocated/assigned/initialized) at `program/src/processor.rs:748-814`.
5. The victim's original `Initialize2` transaction for market `M` now hits the ownership check in `generate_amm_associated_account` (`program/src/processor.rs:499-544`) and permanently fails with `AmmError::RepeatCreateAmm`, since the deterministic addresses are already owned by the program (under the attacker's pool).

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

**File:** program/src/processor.rs (L313-316)
```rust
        if associated_token_address != *associated_token_account.key {
            msg!("Error: Associated token address does not match seed derivation");
            return Err(AmmError::ExpectedAccount.into());
        }
```

**File:** program/src/processor.rs (L378-382)
```rust
        } else {
            associated_token_address.log();
            return Err(AmmError::RepeatCreateAmm.into());
        }
        Ok(())
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

**File:** program/src/processor.rs (L967-976)
```rust
        amm.coin_vault = *amm_coin_vault_info.key;
        amm.pc_vault = *amm_pc_vault_info.key;
        amm.coin_vault_mint = *amm_coin_mint_info.key;
        amm.pc_vault_mint = *amm_pc_mint_info.key;
        amm.lp_mint = *amm_lp_mint_info.key;
        amm.open_orders = Pubkey::default();
        amm.market = *market_info.key;
        amm.market_program = Pubkey::default();
        amm.target_orders = *amm_target_orders_info.key;
        amm.amm_owner = config_feature::amm_owner::ID;
```
