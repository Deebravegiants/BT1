This confirms the analog. The `Initialize2` instruction derives every pool-defining account (`AmmInfo`, LP mint, coin/pc vaults, target orders) as a PDA seeded only by `program_id` and `market_info.key` (`get_associated_address_and_bump_seed`), with no binding to `user_wallet_info` or to the specific `init_coin_amount`/`init_pc_amount` chosen by the legitimate creator. Combined with `generate_amm_associated_account`/`generate_amm_associated_spl_token` racing on `associated_token_account.owner == system_program_account.key` (whoever gets there first "wins", others get `AmmError::RepeatCreateAmm`), this is directly analogous to the reported `proposalId` frontrunning bug: the "ID" (the pool's PDA set) is fully computable in advance from public data by any observer, and the first transaction to land claims it — permanently, since a pool for that market can never be initialized again once `RepeatCreateAmm`/`AlreadyInUse` triggers. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Title
Pool creation can be frontrun/DOS'd because Initialize2's PDAs are derived only from the public market key - (File: program/src/processor.rs)

### Summary
`process_initialize2` derives the addresses of every pool-critical account — `AmmInfo`, the LP mint, the coin/pc vaults, and the target-orders account — solely from `program_id` and the caller-supplied `market_info.key`, via `get_associated_address_and_bump_seed`. None of these seeds include the legitimate creator's wallet, a nonce chosen by them, or any value unique to their specific transaction. An attacker who observes a pending `Initialize2` transaction for a given market in the mempool can compute the exact same PDAs, submit their own `Initialize2` with the same `market_info` but attacker-controlled token accounts/amounts, and land it first.

### Finding Description
The pool account addresses are computed with `find_program_address(&[program_id, market_account.key, associated_seed], program_id)` [1](#0-0) . In `generate_amm_associated_account` and `generate_amm_associated_spl_token`, the code only checks that the derived address matches the account passed in, and that the account is still owned by the system program before assigning/allocating it to the AMM program: if it is *not* owned by system program (i.e., someone already created it), the call fails with `AmmError::RepeatCreateAmm` [2](#0-1) [3](#0-2) .

Because these PDAs depend only on the market pubkey (a public, well-known identifier) and the program id — not on `user_wallet_info`, a per-creator nonce, or the intended `init_coin_amount`/`init_pc_amount` — any two independent `Initialize2` calls targeting the same market race for the exact same set of accounts. The code even documents that `market_info` is only used "as a seed for the AMM account" and "can be any account" [4](#0-3) , further underscoring that nothing about the caller or their transaction is bound into the derived addresses.

The attacker's frontrunning transaction is fully valid: they simply need their own token-coin/token-pc accounts for the desired mints (or attacker-created mints if the mints themselves aren't fixed by protocol convention) and enough balance to satisfy `InitLpAmountTooLess` (`liquidity - 10^decimals > 0`) [5](#0-4) . Once their `Initialize2` lands, the legitimate creator's identical-looking transaction reverts with `RepeatCreateAmm`/`AlreadyInUse`, and the canonical pool address for that market is now permanently owned by the attacker with an initial price ratio and LP distribution entirely of the attacker's choosing.

### Impact Explanation
This is a direct DoS of pool creation for any specific market: once an attacker's `Initialize2` succeeds for a market, the deterministic PDA for that market can never be initialized as the "real" pool again — `AmmError::AlreadyInUse`/`RepeatCreateAmm` blocks it permanently. Beyond DoS, the attacker fully controls `init_coin_amount`/`init_pc_amount`, letting them set an arbitrary, manipulated initial price for what becomes the canonical on-chain pool for that market, and mints themselves the vast majority of the initial LP supply — analogous to the classic "pool sniping" attack but guaranteed to succeed via mempool frontrunning rather than probabilistic racing, since the accounts are 100% predictable in advance.

### Likelihood Explanation
Any unprivileged party monitoring the mempool for `Initialize2` transactions can immediately extract the `market_info` pubkey (a public value) from the pending transaction, compute the identical PDAs off-chain, and submit a higher-priority-fee transaction with their own `init_coin_amount`/`init_pc_amount` and token accounts. No special permissions, market program validation of `market_info`, or knowledge beyond public transaction data is required, making this readily and repeatably exploitable.

### Recommendation
Bind the derived pool PDAs to something unique to the legitimate creator/transaction — e.g., include `user_wallet_info.key` or a creator-chosen nonce/salt in the seed derivation for `AMM_ASSOCIATED_SEED`, `TARGET_ASSOCIATED_SEED`, `LP_MINT_ASSOCIATED_SEED`, `COIN_VAULT_ASSOCIATED_SEED`, and `PC_VAULT_ASSOCIATED_SEED`, rather than deriving them solely from the public `market_info.key`. Alternatively, require the `amm_info`/other PDAs to be pre-created via a separate, atomically-bundled create-account instruction signed by the intended creator, and validate that `market_info` is a legitimate, program-verified market account rather than an arbitrary seed value.

### Proof of Concept
1. Legitimate user Alice broadcasts an `Initialize2` transaction for market `M` with `init_coin_amount = 1_000_000`, `init_pc_amount = 1_000_000`.
2. Attacker Bob observes this pending transaction, extracts `market_info = M` (public), and computes the same PDAs via `get_associated_address_and_bump_seed(program_id, M, seed, program_id)` for `amm_info`, `amm_lp_mint`, vaults, and `target_orders`.
3. Bob submits his own `Initialize2` for market `M` with the same derived accounts but his own token accounts and `init_coin_amount = 1`, `init_pc_amount = 1_000_000_000` (or any ratio favorable to him), with a higher priority fee so it lands first.
4. Bob's transaction succeeds: the pool for market `M` is now initialized at his chosen price, and he receives the LP tokens per `Invokers::token_mint_to` [6](#0-5) .
5. Alice's original `Initialize2` for market `M` now reverts with `AmmError::RepeatCreateAmm`/`AmmError::AlreadyInUse` since the accounts are already owned by the AMM program and `amm.status != Uninitialized` [7](#0-6) , permanently blocking the legitimate pool creation for that market.

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

**File:** program/src/processor.rs (L590-594)
```rust
            let amm_config_info = next_account_info(account_info_iter)?;
            let create_fee_destination_info = next_account_info(account_info_iter)?;
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L845-847)
```rust
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

**File:** program/src/processor.rs (L921-929)
```rust
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
