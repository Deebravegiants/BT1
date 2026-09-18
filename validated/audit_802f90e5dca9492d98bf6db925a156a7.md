### Title
Front-runnable, attacker-controlled PDA seed (`market_info`) in `process_initialize2` lets pool addresses be hijacked before creation completes - ([File: program/src/processor.rs])

### Summary
`Processor::process_initialize2` derives the deterministic addresses of the AMM pool account, LP mint, coin/pc vaults, and target-orders account solely from `program_id`, the `market_info` account key, and a fixed constant seed. `market_info` is explicitly documented and treated as an arbitrary, attacker-controlled account ("Just a seed for AMM account. Can be any account."), and the derivation contains no binding to the transaction signer (`user_wallet_info`) or to the coin/pc mints. This is the on-chain analog of the CREATE2-salt issue in the external report: because the salt/seed used to compute the deterministic address does not incorporate the caller's identity, a second party can win the race to "claim" the deterministically-derived pool address with attacker-chosen initialization parameters, causing a legitimate creator's subsequent instructions (e.g. `Deposit`) to interact with a pool they do not control and did not intend to create.

### Finding Description
In `Processor::process_initialize2` (`program/src/processor.rs`), the AMM account, LP mint, coin vault, pc vault and target-orders account addresses are all computed via `get_associated_address_and_bump_seed`, which calls: [1](#0-0) 

The seed inputs are `program_id`, `market_account.key`, and a fixed constant (`AMM_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, `PC_VAULT_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`). Crucially, `market_info` is fetched with an explicit comment confirming it is unconstrained attacker-supplied data: [2](#0-1) [3](#0-2) 

No ownership check, no signer check, and no relationship to the actual OpenBook/Serum market is enforced on `market_info` before it is used to derive every associated account: [4](#0-3) 

The only replay protection is `RepeatCreateAmm`, triggered when the target address is no longer owned by the system program: [5](#0-4) 

Because the derived addresses depend only on the caller-suppliable `market_info` pubkey (not on `msg.sender`/`user_wallet_info`, and not on the coin/pc mint pair or any nonce unique to the creator's intent), this is exactly the CREATE2-salt problem from the report: the address is fully predictable off-chain, and whoever lands their `Initialize2` transaction first for a given `market_info` "wins" that deterministic address — with initialization parameters (`init_pc_amount`, `init_coin_amount`, mint pair) entirely of their own choosing. The pool's initial price ratio and first-mover LP share are also attacker-controlled at that point: [6](#0-5) 

### Impact Explanation
A user ("Bob") who computes the deterministic pool/vault/LP-mint addresses off-chain from a `market_info` account and submits `Initialize2` followed by a `Deposit` (a common batched pattern to atomically bootstrap and fund a pool) can be front-run by an attacker ("Alice") who submits her own `Initialize2` using the same `market_info` seed first. Alice's `Initialize2` succeeds, claims the deterministic addresses, and sets the initial coin/pc amounts (hence initial price) and mints herself the corresponding LP tokens. Bob's own `Initialize2` then fails with `RepeatCreateAmm`, but if Bob's bundled `Deposit` still executes against the now-existing pool at the same predictable vault/LP-mint addresses, Bob deposits real tokens into a pool whose price ratio and LP allocation were unilaterally chosen by the attacker — resulting in direct loss of value for Bob (deposited at an attacker-skewed ratio) and unearned/inflated LP ownership for the attacker. This is a concrete theft/loss-of-funds vector, not merely a best-practice concern.

### Likelihood Explanation
This is reachable by any unprivileged party through the public `Initialize2` instruction with fully attacker-chosen accounts and data (`market_info` "can be any account," per the code's own comment) and requires only observing a pending transaction (mempool/leader-relay visibility, or reconstructing predictable off-chain address computation and racing to submit first) — no privileged signer or special build is needed. The lack of any binding of the derived addresses to the creator's wallet or transaction intent makes the race trivial to execute whenever pool addresses are computed and relied upon client-side before confirmation.

### Recommendation
Bind the PDA seeds used for the AMM pool, vaults, LP mint, and target-orders accounts to inputs that cannot be front-run/predicted independent of the legitimate creator's intent, for example:
1. Require `market_info` to be validated as an actual OpenBook/Serum market account (owned by the market program, with the market's declared base/quote mints matching `amm_coin_mint_info`/`amm_pc_mint_info`), rather than accepting "any account."
2. Incorporate `user_wallet_info.key` (the signer) and/or the coin/pc mint pair into the derivation seed so that two different callers cannot collide on the same deterministic address for different intents.
3. Alternatively, require the pool-creating transaction to atomically set/verify the initial price ratio and LP allocation match caller-supplied expectations before any dependent instruction (e.g. `Deposit`) is allowed to proceed against a newly created pool, so a hijacked pool cannot silently absorb a victim's follow-up deposit.

### Proof of Concept
1. Bob selects a `market_info` account `M` and mint pair `(X, Y)`, computes the deterministic addresses for `amm_info`, `amm_lp_mint`, `coin_vault`, `pc_vault`, `target_orders` via `get_associated_address_and_bump_seed(program_id, M, seed, program_id)`, and submits a bundle: `Initialize2{nonce, open_time, init_pc_amount: 1000, init_coin_amount: 1000}` followed by `Deposit{...}` targeting those addresses.
2. Alice observes Bob's pending transaction (or independently derives the same addresses using the same public `M`), and submits her own `Initialize2` first using the same `market_info = M` (and, if she wants a different token pair to also claim the same `amm_info`/`target_orders`/`lp_mint` slot, any mint pair — since those addresses don't depend on mints at all) with `init_pc_amount`/`init_coin_amount` chosen to set an attacker-favorable price ratio, executed via `Processor::process_initialize2` (`program/src/processor.rs:549`), successfully minting herself LP tokens per the formula at `program/src/processor.rs:908-929`.
3. Bob's `Initialize2` now fails with `AmmError::RepeatCreateAmm` (`program/src/processor.rs:380`), but his bundled `Deposit` instruction, referencing the same precomputed vault/LP-mint addresses, executes against Alice's pool and its attacker-set ratio, causing Bob's tokens to be deposited at unfavorable terms determined solely by Alice.

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

**File:** program/src/processor.rs (L317-381)
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
```

**File:** program/src/processor.rs (L592-599)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;

            let user_wallet_info = next_account_info(account_info_iter)?;
            let user_token_coin_info = next_account_info(account_info_iter)?;
            let user_token_pc_info = next_account_info(account_info_iter)?;
            let user_token_lp_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L641-646)
```rust
            // Won't use.
            // Can be any account.
            let _market_program_info = next_account_info(account_info_iter)?;
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L804-814)
```rust
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
