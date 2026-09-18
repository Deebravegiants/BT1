Found a legitimate analog. In Raydium's `process_initialize2`, the pool-creation minimum liquidity is derived directly from the coin mint's decimals rather than a small decimal-independent constant, which can force the pool creator to permanently forfeit a large, unpredictable amount of value — the same underlying bug class as the reported "hardcoded MINIMUM_AMOUNT too costly for some tokens" issue, but here the forfeited amount is *worse than fixed* because it scales exponentially with decimals.

### Title
Decimals-dependent locked minimum liquidity in `process_initialize2` can force pool creators to permanently forfeit outsized value - (File: program/src/processor.rs)

### Summary
`process_initialize2` computes the initial pool liquidity as `sqrt(coin_amount * pc_amount)` and then permanently withholds `10^lp_mint.decimals` units of it from the creator's minted LP tokens, where `lp_mint.decimals` is set equal to `coin_mint.decimals`. Unlike Uniswap V2's fixed, decimals-independent `MINIMUM_LIQUIDITY` constant, this locked amount is not calibrated to real-world token value and can represent a very large, unrecoverable forfeiture for tokens whose "1 unit" (10^decimals) has high value or whose decimals differ significantly from the paired mint's decimals — mirroring the reported class of "minimum amount too costly for the user" but manifesting as a mandatory unrecoverable loss rather than a mere UX inconvenience.

### Finding Description
During pool creation the code sets the LP mint's decimals to the coin mint's decimals: [1](#0-0) 

Then, at initialization, the liquidity (geometric mean of the two vault balances) is computed and a fixed `10^lp_mint.decimals` slice of it is subtracted and never minted to anyone — it is simply excluded from `user_lp_amount` while the full `liquidity` value is still recorded as `amm.lp_amount`: [2](#0-1) 

This means the pool creator's minted LP tokens are always `sqrt(coin_amount * pc_amount) - 10^coin_decimals` (in raw geometric-mean units), and the withheld `10^coin_decimals` slice of pool value is never credited to any account — it is permanently and unrecoverably locked in the pool's accounting (`amm.lp_amount` includes it, but no LP tokens exist to redeem it), functioning as dead/frozen value. If this subtraction underflows (deposit too small relative to decimals), pool creation reverts entirely: [3](#0-2) 

Because the withheld amount is `10^coin_decimals` (i.e., exactly "1 whole coin token" in the coin's own units) rather than a small fixed constant, the real economic cost of this permanently-frozen slice depends entirely on the coin token's per-unit market value — exactly the failure mode described in the source report about WBTC-like tokens, where "1 unit" of value is large. For any coin mint whose native "1 token" unit carries substantial value (e.g., a wrapped high-value asset with modest decimals), a pool creator is forced to forfeit that entire unit's worth of value permanently just to bootstrap the pool, with no way for anyone to reclaim it.

### Impact Explanation
This is a permanent, protocol-enforced freezing of a determinate portion of the pool creator's deposited funds on every `Initialize2` call: the value corresponding to `10^coin_decimals` in the geometric-mean liquidity metric is never mintable to any party, and no path exists for the pool creator or anyone else to redeem it. For higher-value coin mints this forfeiture can be economically significant and unpredictable at pool-creation time. This satisfies the "permanent freezing of user/LP funds" criterion.

### Likelihood Explanation
Every legitimate, unprivileged pool creation via `Initialize2` triggers this deduction — it is not a rare edge case but the default behavior for all new pools, so it is deterministically reachable with normal parameters and attacker/creator-chosen mints and amounts.

### Recommendation
Decouple the locked minimum-liquidity amount from the coin mint's raw decimal count. Use a fixed, decimal-independent constant (normalized via `Calculator::normalize_decimal_v2`/`sys_decimal_value`, similar to how PnL and swap math already normalize decimals) so that the forfeited amount is a small, predictable, low-value quantity regardless of which mint is used as the "coin" side, rather than scaling with `10^coin_decimals`.

### Proof of Concept
1. Attacker/creator calls `Initialize2` for a pool where `coin_mint` is a token with decimals set such that `10^coin_decimals` represents a large real-world value share of the initial deposit (e.g., a wrapped high-value asset).
2. `process_initialize2` sets `lp_decimals = coin_mint.decimals` [4](#0-3)  and computes `liquidity = sqrt(coin_amount * pc_amount)`.
3. `user_lp_amount = liquidity - 10^lp_mint.decimals` is minted to the creator [5](#0-4) , while `amm.lp_amount = liquidity` (the full, undiscounted value) is stored [6](#0-5) .
4. The `10^coin_decimals` gap between `amm.lp_amount` and total minted LP supply is permanently unredeemable by any party, representing a forced, unrecoverable loss proportional to the coin mint's per-unit value.

### Citations

**File:** program/src/processor.rs (L760-774)
```rust
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
