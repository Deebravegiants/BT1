## Title
Permanent Freezing of Pool Funds via LP Token Burn Bypassing `amm.lp_amount` Accounting - (File: `program/src/processor.rs`)

## Summary
The AMM tracks total LP supply internally in `AmmInfo.lp_amount`, which is only ever decremented inside `process_withdraw` after the program itself burns the caller's LP tokens. [1](#0-0)  Because LP tokens are ordinary SPL tokens with no freeze authority (`InitializeInstruction2` explicitly requires `lp_mint.freeze_authority.is_some()` to be false) [2](#0-1) , any LP holder can call the standard SPL Token `Burn` instruction directly on their own LP token account, completely bypassing the Raydium program. This decreases the real on-chain `lp_mint.supply` without ever touching `amm.lp_amount`, permanently desynchronizing the AMM's internal accounting from reality — the exact "griefing via a path that doesn't update the tracked total" bug class described in the reference report (`totalSupply()` desync in `BridgedERC20`).

## Finding Description
`amm.lp_amount` is the AMM's internal book-keeping of "total LP supply" and is used as the denominator for all pro-rata withdraw math: [3](#0-2) 

It is only mutated in two places:
- Incremented in `process_deposit` after minting new LP tokens: [4](#0-3) 
- Decremented in `process_withdraw` after the program itself burns the withdrawn amount: [1](#0-0) 

Because the SPL Token Program has no transfer/burn hooks (unlike the `_beforeTokenTransfer` callback in the referenced ERC20 report), a holder can invoke `spl_token::instruction::burn` on their own LP token account directly, with no interaction with the Raydium AMM program whatsoever, and no way for `amm.lp_amount` to observe or react to it. This immediately creates a state where `lp_mint.supply < amm.lp_amount` by more than the intended minimum-liquidity gap.

Note that a deliberate offset between `amm.lp_amount` and the actual minted supply already exists by design: at pool init, `amm.lp_amount` is set to the full `liquidity` (`sqrt(x*y)`) while only `liquidity - 10^decimals` is actually minted to the depositor, permanently reserving `10^decimals` worth of "phantom" LP as an anti-first-depositor-donation safeguard: [5](#0-4) [6](#0-5) 

An externally-triggered direct burn simply widens this gap arbitrarily and irreversibly, beyond the intentional minimum-liquidity buffer.

## Impact Explanation
Once `amm.lp_amount` is inflated relative to the real circulating `lp_mint.supply`, every subsequent withdrawal computes its share using the inflated denominator: [7](#0-6)  This means the sum of coin/pc redeemable by all remaining real LP holders (whose balances sum to the deflated real supply) will always be strictly less than `total_coin_without_take_pnl` / `total_pc_without_take_pnl`. The residual portion of vault funds — proportional to the amount directly burned — becomes permanently stranded in the coin/pc vaults with no LP tokens left in existence to ever redeem it. This is a permanent freezing of a portion of LP/pool funds, satisfying the funds-freezing impact bar. The attack costs the griefer only their own LP tokens (self-destructive for the attacker but damaging for all other current and future LPs, since the pool's real backing ratio no longer aligns with its internal `lp_amount` bookkeeping used for every future deposit and withdraw calculation).

## Likelihood Explanation
Any LP holder can execute this in a single transaction using only the standard SPL Token program, targeting their own token account and the pool's `lp_mint` — no privileged role, no cooperation from Raydium, and no protection exists since the mint has no freeze authority. Likelihood is high given how trivial and permissionless the action is; the only friction is that the attacker sacrifices their own LP position, which limits (but does not eliminate) the incentive — a market competitor seeking to permanently degrade a specific pool's integrity, or a user exploiting airdrops/points programs tied to LP burns, would have direct motive.

## Recommendation
Reconcile `amm.lp_amount` against the true on-chain `lp_mint.supply` rather than trusting an internally tracked counter: before every deposit/withdraw calculation, re-read `lp_mint.supply` from the mint account (already unpacked via `Self::unpack_mint`) and use it as the denominator for pro-rata math instead of (or in addition to, taking the minimum of) `amm.lp_amount`. Alternatively, use `Mint` extensions or a delegate-transfer/freeze mechanism so LP tokens cannot be burned outside the program's own withdraw path.

## Proof of Concept
1. Alice deposits liquidity and receives LP tokens; `amm.lp_amount` is incremented accordingly via `process_deposit` at [4](#0-3) .
2. Alice, instead of calling Raydium's `Withdraw` instruction, submits a standalone transaction invoking `spl_token::instruction::burn` directly on her own LP token account and the pool's `lp_mint`, burning e.g. 1,000 LP tokens.
3. `lp_mint.supply` on-chain decreases by 1,000, but `amm.lp_amount` (only touched inside `process_withdraw`, see [8](#0-7) ) is unchanged.
4. All subsequent `Withdraw` calls compute `coin_amount`/`pc_amount` using the now-inflated `amm.lp_amount` as denominator [7](#0-6) , so the sum of all future withdrawals by remaining LPs will fall short of the pool's real backing by an amount proportional to the 1,000 burned tokens, leaving that portion of coin/pc permanently stuck in the vaults.

### Citations

**File:** program/src/processor.rs (L904-906)
```rust
        if lp_mint.freeze_authority.is_some() {
            return Err(AmmError::InvalidFreezeAuthority.into());
        }
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

**File:** program/src/processor.rs (L977-977)
```rust
        amm.lp_amount = liquidity;
```

**File:** program/src/processor.rs (L1341-1350)
```rust
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_dest_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            amm.nonce as u8,
            mint_lp_amount,
        )?;
        amm.lp_amount = amm.lp_amount.checked_add(mint_lp_amount).unwrap();
```

**File:** program/src/processor.rs (L1751-1761)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1805-1812)
```rust
            Invokers::token_burn(
                token_program_info.clone(),
                user_source_lp_info.clone(),
                amm_lp_mint_info.clone(),
                source_lp_owner_info.clone(),
                withdraw.amount,
            )?;
            amm.lp_amount = amm.lp_amount.checked_sub(withdraw.amount).unwrap();
```
