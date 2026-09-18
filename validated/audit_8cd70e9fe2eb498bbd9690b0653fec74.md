### Title
Direct-transfer ("donation") vault inflation breaks LP share calculation in `Deposit`, allowing rounding-down theft from later depositors - (File: `program/src/processor.rs`)

### Summary
Raydium's `Deposit` instruction computes the amount of LP tokens to mint using the *live token balances* of the coin/pc vaults rather than a value that is exclusively updated through instruction-gated accounting. Because an attacker can transfer SPL tokens directly to `amm_coin_vault`/`amm_pc_vault` with a plain SPL Token `Transfer` (no Raydium instruction required), they can desynchronize the internal LP-share counter (`amm.lp_amount`) from the actual vault balances used in the share-price calculation — the same asset/share mismatch root cause described in the referenced ERC4626 "first depositor" report.

### Finding Description
`process_deposit` computes the pool's real balances via `Calculator::calc_total_without_take_pnl_no_orderbook`, fed with the *actual* unpacked vault token amounts: [1](#0-0) 

The number of LP tokens minted for a deposit is then derived from the ratio of the deposited amount to this live vault balance, multiplied by `amm.lp_amount` (the pool's internally tracked LP-share counter), rounded down: [2](#0-1) [3](#0-2) 

`amm.lp_amount` is only ever incremented when the program itself mints LP tokens (in `Initialize2` and `Deposit`): [4](#0-3) 

However, nothing prevents an unprivileged attacker from sending extra coin or pc tokens directly to `amm_coin_vault_info`/`amm_pc_vault_info` via a standalone SPL Token `Transfer` instruction (these are just ordinary token accounts owned by the pool `$authority`). This inflates `amm_coin_vault.amount`/`amm_pc_vault.amount` — and therefore `total_coin_without_take_pnl`/`total_pc_without_take_pnl` — without any corresponding increase to `amm.lp_amount`. The result is the exact same "assets per share" inflation described in the ERC4626 report: `mint_lp_amount = deduct_X_amount * amm.lp_amount / total_X_without_take_pnl` now rounds far more aggressively downward for the next depositor, while the extra (undercounted) value accrues proportionally to existing LP holders — including the attacker, who can hold LP tokens from before the donation and withdraw them afterward at an inflated redemption rate.

Raydium does mitigate the classic "1-wei-first-deposit" variant at pool creation time: `Initialize2` requires `liquidity = sqrt(pc_amount * coin_amount)` to exceed `10^lp_decimals`, and only mints `liquidity - 10^lp_decimals` LP tokens to the creator, permanently under-crediting a "floor" amount of LP supply relative to the tracked liquidity value: [5](#0-4) 

This prevents an attacker from owning nearly all shares immediately after `Initialize2` with a negligible deposit. However, this protection only guards the *initialization* step — it does nothing to prevent a subsequent direct-transfer donation to the vaults at any later point, which still desynchronizes `amm.lp_amount` from real vault balances for every `Deposit` call thereafter.

### Impact Explanation
Any depositor who deposits into a pool shortly after an attacker's donation will have their `mint_lp_amount` rounded down more than intended by the AMM's ratio invariant, transferring value to existing LP holders (i.e., the attacker, if they hold LP tokens from before the donation). If the rounding pushes `mint_lp_amount` to exactly `0`, the deposit instead reverts (`AmmError::InvalidInput`) rather than silently minting nothing, which caps the most extreme form of the attack (unlike some ERC4626 vaults that don't check for a zero-share mint) — but any non-zero-but-disproportionately-small mint still results in a real economic loss transferred to existing LP holders, which is a fund-safety issue for LP depositors.

### Likelihood Explanation
The attack is reachable by any unprivileged actor: it requires only (1) holding some LP tokens in the target pool (which can be acquired via a normal, small `Deposit`) and (2) issuing a standard SPL Token `Transfer` directly to the pool's coin or pc vault account, both public/known PDAs once a pool exists. No privileged signer, off-chain component, or non-default build is needed. However, the practical severity is constrained because vaults typically already hold significant liquidity in an actively used pool (making an attacker's donation an economically costly way to skew ratios only slightly), and because the `mint_lp_amount == 0` check prevents the most severe zero-share exploitation vector seen in the referenced report.

### Recommendation
Track pool liquidity strictly through the program's own internal accounting (e.g., cached/synced vault balances updated only via program-controlled paths) rather than trusting the live SPL token account balance directly in the LP mint-ratio calculation, or explicitly reconcile/reject deposits where the vault balance deviates from the last-known internally tracked balance beyond expected swap/fee movements. Alternatively, require `mint_lp_amount` to not fall below a configurable minimum proportional threshold instead of only checking for exact zero, to reduce the reward from ratio-skewing donations.

### Proof of Concept
1. Attacker calls `Deposit` normally with a small amount right after pool creation, receiving some LP tokens (`amm.lp_amount` increases proportionally, tracked in `program/src/processor.rs:1341-1350`).
2. Attacker issues a plain SPL Token `Transfer` instruction (outside of the Raydium program) sending a large amount of the coin token directly to `amm.coin_vault`. This is a valid SPL token operation on a normal token account and requires no interaction with the Raydium AMM program.
3. `amm_coin_vault.amount` (read in `process_deposit` at `program/src/processor.rs:1138-1153`) is now inflated, but `amm.lp_amount` is unchanged.
4. A victim calls `Deposit` with `base_side = 0`; `mint_lp_amount` is computed as `deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` (`program/src/processor.rs:1243-1250`), which now rounds down disproportionately versus the victim's real economic contribution.
5. The attacker later calls `Withdraw`, redeeming their earlier LP tokens at the new, donation-inflated exchange rate, capturing a share of the victim's under-credited deposit value.

### Citations

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

**File:** program/src/processor.rs (L1138-1153)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_source_coin =
            Self::unpack_token_account(&user_source_coin_info, spl_token_program_id)?;
        let user_source_pc =
            Self::unpack_token_account(&user_source_pc_info, spl_token_program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1243-1250)
```rust
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1295-1302)
```rust
            let invariant_pc = InvariantPool {
                token_input: deduct_pc_amount,
                token_total: total_pc_without_take_pnl,
            };
            // pc_amount/ (total_pc_amount + pc_amount)  = output / (lp_mint.supply + output) =>  output = pc_amount / total_pc_amount * lp_mint.supply
            mint_lp_amount = invariant_pc
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
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
