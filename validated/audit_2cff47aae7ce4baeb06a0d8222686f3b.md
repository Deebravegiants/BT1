## Title
Front-running `Initialize2` Pool Creation Squats the Deterministic AMM PDA Cluster and Permanently DoSes Legitimate Pool Creation for a Given Market - (File: `program/src/processor.rs`)

### Summary
`AmmInstruction::Initialize2` derives every account of a new pool (AMM state account, LP mint, coin/pc vaults, target orders) from a PDA seeded **only** by the `market_info` account key and a fixed associated-seed constant — not by the coin/pc mints or the creator. Since `market_info` is explicitly documented as "Just a seed for AMM account. Can be any account," and is never validated against an actual OpenBook/Serum market's registered mints, an attacker can observe a pending legitimate `Initialize2` transaction in the mempool (which necessarily reveals the `market` pubkey the victim intends to use), front-run it with the same `market` account but attacker-chosen (worthless) mints and minimal amounts, and permanently occupy the entire PDA cluster for that market. This is directly analogous to the reported `createNewTask()` DoS: an unauthenticated creation entrypoint keyed by a value the victim must reveal in advance, exploitable with minimal funds, causing irreversible squatting/blocking of the legitimate resource.

### Finding Description
`process_initialize2` computes the pool's associated addresses via `get_associated_address_and_bump_seed`, which hashes only `program_id`, `market_account.key`, and a constant seed suffix (`AMM_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, `PC_VAULT_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`): [1](#0-0) 

The instruction documentation itself states the market account can be arbitrary: [2](#0-1) [3](#0-2) 

`process_initialize2` never validates that `market_info` corresponds to a real OpenBook/Serum market whose registered base/quote mints match `amm_coin_mint_info`/`amm_pc_mint_info` — it only checks that the two mints differ from each other: [4](#0-3) 

Each associated-account helper (`generate_amm_associated_account`, `generate_amm_associated_spl_token`, `generate_amm_associated_spl_mint`) checks whether the derived PDA is still owned by the system program; if it is not (i.e., someone already created it), the call returns `AmmError::RepeatCreateAmm` instead of proceeding: [5](#0-4) [6](#0-5) 

Because the derivation depends only on the `market` key, an attacker who sees a victim's pending `Initialize2` transaction (the `market` pubkey is plaintext in the transaction) can submit their own `Initialize2` with the same `market` account, but with attacker-supplied/worthless coin and pc mints and the minimum non-zero vault amounts required to pass the `amount == 0` checks: [7](#0-6) 

If the attacker's transaction lands first, the AMM account, LP mint, coin/pc vaults, and target orders for that `market` key are permanently created and owned by the program. The victim's subsequent legitimate `Initialize2` call for the same `market` (with the real mints and real liquidity) will hit `RepeatCreateAmm`/`AlreadyInUse` and fail forever — the canonical pool address tied to that `market` account can never be legitimately initialized again, exactly mirroring the reported bug class where a malicious actor "preempts legitimate ... submissions by setting themselves as [creator] ... with minimal funds."

### Impact Explanation
This permanently blocks legitimate pool creation for the targeted market: the deterministic AMM/vault/LP-mint/target-orders addresses become forever squatted by an attacker-controlled, worthless pool, and no retry with the correct mints/liquidity is possible once front-run. This is a direct, low-cost griefing/DoS vector against any prospective pool creator, and can be used for extortion (attacker can demand payment to "release" a market key they've already squatted with negligible capital) — matching the "extortion or DoS conditions" and "front-running" impact called out in the analogous report.

### Likelihood Explanation
Exploitation only requires observing a public mempool transaction (or even predicting a well-known market account ahead of time) and submitting a competing transaction with a higher priority fee — no privileged role, no leaked keys, and minimal token/lamport cost (a single unit of two throwaway mints) are needed. Any unprivileged actor watching the network can execute this against any user attempting to create a pool via `Initialize2`, making likelihood high whenever pool creation is anticipated (e.g., new token listings).

### Recommendation
Bind the derived PDA seeds to the actual coin/pc mints (and/or the creator's pubkey) rather than solely to an arbitrary `market` account, so that squatting a `market` key cannot preempt the correct mint pair. Additionally, validate that `market_info` corresponds to a genuine market whose registered base/quote mints match the supplied `amm_coin_mint_info`/`amm_pc_mint_info` before using it as a seed, and/or require a meaningful minimum initial liquidity threshold so trivial squats are not economically viable.

### Proof of Concept
1. Victim broadcasts an `Initialize2` transaction specifying real `market`, `coin_mint`, `pc_mint`, and real initial liquidity amounts (public in mempool).
2. Attacker copies the transaction's `market` pubkey, builds their own `Initialize2` instruction using the same `market` account but two throwaway SPL mints they control and `init_coin_amount = init_pc_amount = 1`.
3. Attacker submits with a higher fee/priority so it lands first; `generate_amm_associated_account`/`generate_amm_associated_spl_token`/`generate_amm_associated_spl_mint` succeed since the PDAs (seeded only by `market_info.key`) are still system-owned, and the pool is created with worthless mints.
4. Victim's original transaction now fails at `generate_amm_associated_*` with `AmmError::RepeatCreateAmm` (system-program-owner check fails) — the intended pool for that `market` can never be created with the correct mints again. [6](#0-5)

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

**File:** program/src/processor.rs (L313-317)
```rust
        if associated_token_address != *associated_token_account.key {
            msg!("Error: Associated token address does not match seed derivation");
            return Err(AmmError::ExpectedAccount.into());
        }
        if associated_token_account.owner == system_program_account.key {
```

**File:** program/src/processor.rs (L499-544)
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

**File:** program/src/processor.rs (L680-682)
```rust
        if *amm_coin_mint_info.key == *amm_pc_mint_info.key {
            return Err(AmmError::InvalidCoinMint.into());
        }
```

**File:** program/src/processor.rs (L858-860)
```rust
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
```
