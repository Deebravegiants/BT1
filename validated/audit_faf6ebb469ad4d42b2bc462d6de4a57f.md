### Title
`Initialize2` pool derivation keyed only on the `market` account allows front-running to permanently DoS creation of the intended AMM pool - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives all of the AMM pool's core PDAs (`AmmInfo`, `TargetOrders`, LP mint, coin/pc vault) solely from the `market_info` account key, the program id, and fixed seed constants — independent of the coin/pc mint pair being configured. Because the `market_info` account is explicitly documented as "just a seed... can be any account," and there is no ownership/authority check tying it to a specific, already-existing market, any unprivileged actor can call `Initialize2` first with an arbitrary `market_info` pubkey (matching whatever address the legitimate deployer intends to use) and attacker-chosen mints/amounts, permanently occupying the derived PDAs before the legitimate initialization can occur — directly analogous to the Morpho `initializeMarket` front-running issue (M-26).

### Finding Description
In `Processor::process_initialize2` [1](#0-0) , the AMM's associated accounts are created via `generate_amm_associated_account` / `generate_amm_associated_spl_token` / `generate_amm_associated_spl_mint`, all of which derive the target PDA using:

```
get_associated_address_and_bump_seed(program_id, &market_account.key, associated_seed, program_id)
``` [2](#0-1) 

This derivation depends **only** on `program_id`, `market_account.key`, and a fixed seed constant (e.g. `AMM_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, `PC_VAULT_ASSOCIATED_SEED`) [3](#0-2)  — it does **not** incorporate `amm_coin_mint_info` or `amm_pc_mint_info`. The in-line comments confirm the `market_info` account is not validated as a genuine market: "Just a seed for AMM account. Can be any account." [4](#0-3) [5](#0-4) 

Each account-creation helper checks whether the target address is still owned by the System Program; if it has already been assigned (owner != system program), it returns `AmmError::RepeatCreateAmm` and aborts [6](#0-5) . Because the derivation is keyed only on `market_info.key`, an attacker who observes (or predicts) the `market_info` pubkey a legitimate deployer/protocol intends to use for a given pool can submit their own `Initialize2` transaction first — supplying arbitrary `amm_coin_mint_info`/`amm_pc_mint_info` (e.g., mints they freely create) and minimal `init_coin_amount`/`init_pc_amount` — to occupy the `AmmInfo`, `TargetOrders`, LP mint and vault PDAs tied to that `market_info` key. All account-creation checks (lines 748-814) occur before any real token transfer for the legitimate caller [7](#0-6) , so the legitimate caller's subsequent `Initialize2` transaction for the same `market_info` will unconditionally fail with `RepeatCreateAmm`, and can never succeed for that market key again, since Solana PDAs cannot be recreated once assigned.

### Impact Explanation
This is a griefing/denial-of-service vulnerability reachable by any unprivileged actor via a single `Initialize2` transaction with fully attacker-chosen accounts and data (no signer privilege required beyond being the `user_wallet`). It permanently prevents the intended AMM pool for a specific market key from ever being initialized with its intended coin/pc mint pair, since the underlying PDAs for that market seed are consumed. Front-ends or integrators that expect a canonical AMM address per market (derived purely from `market_info`) may also be misled into believing an attacker-seeded pool (with arbitrary, worthless mints and a hostile initial price ratio) is the legitimate pool for that market, since the address derivation gives no cryptographic assurance about which token pair is inside it. No production token transfer from the legitimate caller occurs (the entire transaction reverts atomically before transfers), so this manifests strictly as denial-of-service against pool configuration rather than direct fund loss from an already-funded pool — matching the severity profile (Medium) of the cited Morpho `initializeMarket` front-running report.

### Likelihood Explanation
Likelihood is high in adversarial/MEV environments: `market_info` pubkeys for upcoming pools are frequently observable in mempools/public announcements before the official `Initialize2` transaction lands, exactly as described in the analog report's attack path (front-running the initializer's transaction). The attack requires no special access, no privileged signer, and only minimal SPL token setup (attacker-created mints with 1 unit each) plus the (often zero, per default `AmmConfig::create_pool_fee = 0`) creation fee [8](#0-7) .

### Recommendation
Bind the derived PDAs to the actual token pair (coin/pc mint) in addition to the market key, so that front-running with unrelated mints cannot squat the seed space for a legitimate pair. Alternatively/additionally, validate that `market_info` is actually owned by the expected market program (e.g., OpenBook) with the expected base/quote mints matching `amm_coin_mint_info`/`amm_pc_mint_info`, removing the "can be any account" trust assumption, and/or gate `Initialize2` behind a privileged creator check (as is already partially done via `create_fee_destination_info` / `config_feature::create_pool_fee_address`) so arbitrary unprivileged accounts cannot consume the PDA namespace for markets they do not control.

### Proof of Concept
1. Observe (or predict) the `market_info` pubkey that a protocol/user intends to use to initialize a legitimate AMM pool for token pair (`mintA`, `mintB`) via `Initialize2`.
2. Before that transaction lands, submit an `Initialize2` transaction using the same `market_info` pubkey but attacker-created/controlled `amm_coin_mint_info`/`amm_pc_mint_info` and `init_coin_amount = init_pc_amount = 1`, computing the same derived `amm_info`, `amm_target_orders`, `amm_lp_mint`, `amm_coin_vault`, `amm_pc_vault` addresses via `get_associated_address_and_bump_seed(program_id, market_info.key, seed, program_id)` [2](#0-1) .
3. This transaction succeeds, assigning ownership of all those PDAs to the AMM program (or SPL token program for the mint/vaults).
4. The legitimate deployer's subsequent `Initialize2` transaction for the same `market_info` reaches `generate_amm_associated_account`/`generate_amm_associated_spl_token`, finds `associated_token_account.owner != system_program`, and reverts with `AmmError::RepeatCreateAmm` [9](#0-8) , permanently blocking initialization of the intended pool for that market key.

### Citations

**File:** program/src/processor.rs (L104-110)
```rust
pub const COIN_VAULT_ASSOCIATED_SEED: &'static [u8] = b"coin_vault_associated_seed";
/// Suffix for pc vault associated seed
pub const PC_VAULT_ASSOCIATED_SEED: &'static [u8] = b"pc_vault_associated_seed";
/// Suffix for lp mint associated seed
pub const LP_MINT_ASSOCIATED_SEED: &'static [u8] = b"lp_mint_associated_seed";
/// Amm config seed
pub const AMM_CONFIG_SEED: &'static [u8] = b"amm_config_account_seed";
```

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

**File:** program/src/processor.rs (L548-553)
```rust
    /// Processes an [Initialize](enum.Instruction.html).
    pub fn process_initialize2(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        init: InitializeInstruction2,
    ) -> ProgramResult {
```

**File:** program/src/processor.rs (L592-594)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L644-646)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
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

**File:** program/src/processor.rs (L2764-2767)
```rust
        let mut amm_config = AmmConfig::load_mut_checked(&amm_config_info, program_id)?;
        amm_config.pnl_owner = *pnl_owner_info.key;
        amm_config.create_pool_fee = 0;

```
