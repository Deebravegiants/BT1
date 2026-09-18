## Analog Found

### Title
Front-runnable, unauthenticated pool creation via deterministic PDA seeding on an unchecked `market_info` account allows permanent hijacking of a market's canonical AMM pool - (File: `program/src/processor.rs`)

### Summary
`process_initialize2` derives every pool PDA (`amm_info`, `target_orders`, `lp_mint`, `coin_vault`, `pc_vault`) deterministically from `(program_id, market_info.key, seed)` via `get_associated_address_and_bump_seed`, but never validates that `market_info` is a genuine, unused OpenBook market or that the supplied `amm_coin_mint`/`amm_pc_mint` actually belong to that market. Anyone can call the public `Initialize2` instruction first for a target market, permanently occupying its canonical pool addresses before the legitimate deployer, exactly analogous to the CREATE2 front-running bug in the referenced report.

### Finding Description
`Initialize2` is a fully public, unprivileged instruction. Its account-derivation helper explicitly treats `market_info` as attacker-controlled input: [1](#0-0) 

The PDA addresses for the pool's core accounts are derived solely from `market_info.key` and fixed seeds, with no signer or ownership check tying `market_info` to a real, unused OpenBook market: [2](#0-1) 

Each helper (`generate_amm_associated_account`, `generate_amm_associated_spl_mint`, `generate_amm_associated_spl_token`) only checks that the derived address is currently owned by the System Program; if it is not (i.e., someone already initialized it), it reverts with `RepeatCreateAmm`: [3](#0-2) 

Because the seeds do not include the caller (`user_wallet_info`) or any nonce/salt chosen by the legitimate deployer, and because `coin_mint`/`pc_mint` are never cross-checked against the actual mints registered on the OpenBook market, an attacker who knows (or predicts) the target market's pubkey can submit their own `Initialize2` transaction first — using arbitrary self-chosen `coin_mint`/`pc_mint` amounts and quantities — and become the first (and only) initializer for that market's deterministic pool address. The legitimate project's subsequent `Initialize2` call for the same market will then unconditionally fail with `AmmError::RepeatCreateAmm`, because the PDAs are already owned by the program from the attacker's earlier call.

This mirrors the report's root cause precisely: a public, deterministic-address-creating entrypoint is called before an authorization/idempotency check is meaningfully scoped to the intended caller, so a front-runner can consume the one-time creation slot.

### Impact Explanation
The attacker becomes the sole/first liquidity provider of the canonical pool for that market, seeding it with a self-chosen, arbitrarily skewed `init_coin_amount`/`init_pc_amount` ratio: [4](#0-3) 

Because `amm.lp_amount` is fixed at pool creation to the initial `liquidity = sqrt(x*y)` while later swaps/deposits price strictly against the manipulated initial ratio, any user or protocol that subsequently deposits into or swaps against what they believe is the official pool for that market is trading against an attacker-controlled initial price/reserve ratio. The legitimate project can never re-create the intended, properly-funded pool at the expected deterministic address for that market (`AmmError::RepeatCreateAmm` permanently blocks it), permanently freezing the market's canonical pool slot and exposing subsequent depositors/swappers to loss from the attacker's chosen skewed reserves — an economically damaging, not merely DoS-only, outcome.

### Likelihood Explanation
`Initialize2` requires only a signer wallet and no special privilege; `market_info` is explicitly documented as usable with "any account," and no check ties the provided mints to the actual OpenBook market or to a specific expected caller. Any attacker monitoring the mempool/market-creation activity for a soon-to-launch token can submit this transaction ahead of the legitimate deployer with minimal cost (rent + optional `create_pool_fee`), making this a straightforward, single-transaction front-run.

### Recommendation
Bind pool creation to the actual market instead of an arbitrary account: validate that `market_info` is owned by the expected market/DEX program and that its serialized base/quote mints equal `amm_coin_mint_info.key`/`amm_pc_mint_info.key` before deriving/creating any PDA. Additionally, consider incorporating the intended creator (e.g., a DAO/admin-approved allowlist, or a `create_pool_fee_address`-gated flow) into the derivation/authorization so an unrelated party cannot pre-empt a market's canonical pool slot.

### Proof of Concept
1. Attacker observes an OpenBook market `M` about to be paired with an official Raydium pool by a project team.
2. Attacker submits `Initialize2` with `market_info = M`, `amm_coin_mint`/`amm_pc_mint` set to `M`'s real mints (or any two arbitrary mints, since they aren't validated against `M`), and `init_coin_amount`/`init_pc_amount` chosen to create a heavily skewed price.
3. `generate_amm_associated_account`/`generate_amm_associated_spl_mint` succeed since the PDAs derived from `M` are still owned by the System Program; attacker's pool is created and becomes the sole LP.
4. The legitimate deployer's later `Initialize2(M, ...)` call derives the identical PDAs, finds them already owned by the program, and reverts with `AmmError::RepeatCreateAmm`, permanently preventing creation of the intended, properly-funded pool for market `M`.

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

**File:** program/src/processor.rs (L592-594)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L908-929)
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

        // liquidity is measured in terms of token_a's value since both sides of
        // the pool are equal
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
