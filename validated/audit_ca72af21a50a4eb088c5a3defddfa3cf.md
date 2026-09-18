### Title
Stale cached `amm.lp_amount` diverges from the true SPL LP mint supply, permanently misallocating pool reserves - ([File: program/src/processor.rs])

### Summary
`AmmInfo.lp_amount` is a program-maintained "shadow" counter of total LP supply that is only incremented/decremented inside `process_deposit`/`process_withdraw`, while the actual source of truth for outstanding LP tokens is the SPL Token `lp_mint.supply`. Exactly like the `LivenessModule.THRESHOLD_PERCENTAGE` that is derived/cached separately from the `SAFE`'s real threshold and gets silently overwritten once the real value is changed by another path, `amm.lp_amount` can silently diverge from `lp_mint.supply` whenever LP tokens are moved by a path the AMM program does not observe (e.g. an LP holder directly invokes the SPL Token program's `Burn` instruction on their own LP token account instead of going through `Withdraw`). Because all deposit/withdraw pro‑rata math uses `amm.lp_amount` as the denominator instead of `lp_mint.supply`, this cached value becoming stale corrupts the pool's accounting permanently.

### Finding Description
`AmmInfo` stores `lp_amount`, described as "pool lp amount" [1](#0-0) . It is set once at pool creation to the initial minted liquidity [2](#0-1) , then only ever updated inside the program's own deposit and withdraw handlers:

- On deposit: `amm.lp_amount = amm.lp_amount.checked_add(mint_lp_amount).unwrap();` [3](#0-2) 
- On withdraw: `amm.lp_amount = amm.lp_amount.checked_sub(withdraw.amount).unwrap();` [4](#0-3) 

Both the deposit-side mint calculation and the withdraw-side redemption calculation use this cached `amm.lp_amount` as the pool-share denominator instead of the real, verifiable `lp_mint.supply`:

- Deposit mint sizing: `mint_lp_amount = invariant_coin.exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)` [5](#0-4) 
- Withdraw redemption sizing: `let invariant = InvariantPool { token_input: withdraw.amount, token_total: amm.lp_amount };` [6](#0-5) 

The only cross-check against the real mint is `if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount { return Err(...) }` [7](#0-6) , which merely bounds a single withdrawal — it never reconciles or resets `amm.lp_amount` to `lp_mint.supply`.

Because an LP token holder legitimately owns their LP token account, they can call the SPL Token program's `Burn` instruction directly on their own LP tokens (a normal, unprivileged SPL Token operation), reducing `lp_mint.supply` without ever going through the Raydium `Withdraw` instruction. `amm.lp_amount` is never told about this and remains inflated relative to the real circulating supply — exactly the same class of bug as the `LivenessModule` continuing to trust its cached `THRESHOLD_PERCENTAGE`-derived value after the `SAFE`'s real threshold changed out from under it via an independent path.

### Impact Explanation
Once `amm.lp_amount` (cache) > `lp_mint.supply` (truth), every subsequent deposit and withdraw miscalculates shares against the inflated denominator. Withdrawers permanently redeem less than their true pro-rata share of coin/pc reserves, and new depositors are minted LP amounts sized against the inflated total. The residual value corresponding to the phantom (externally burned) LP supply becomes permanently stuck/unattributable in the vaults, because no code path ever true-ups `amm.lp_amount` to `lp_mint.supply` — this is a permanent freezing/misallocation of LP funds, reachable purely by an ordinary, unprivileged LP holder performing a standard SPL Token action.

### Likelihood Explanation
Likelihood is high: any LP holder can trigger the divergence with a single, permissionless SPL Token `Burn` instruction on their own token account in the same or a separate transaction — no admin signature, no special accounts, and no interaction with the Raydium program is required to create the mismatch. From that point forward, every ordinary `Deposit`/`Withdraw` transaction (fully in-scope, unprivileged instructions) computes incorrect shares.

### Recommendation
Stop treating `amm.lp_amount` as an independently maintained source of truth. Either:
1. Remove the cached `lp_amount` field entirely and always use `lp_mint.supply` (read from the SPL Mint account) as the denominator in `InvariantPool` calculations for both `process_deposit` and `process_withdraw`, or
2. If `lp_amount` must be kept for compatibility, refresh/reconcile it from `lp_mint.supply` at the start of every `process_deposit`/`process_withdraw` call before it is used in any exchange-rate math.

### Proof of Concept
1. Pool is initialized normally via `Initialize2`; `amm.lp_amount == lp_mint.supply == S`.
2. An LP holder who owns LP tokens (from a prior `Deposit`) submits a standalone transaction invoking the SPL Token program's `Burn` instruction on their own LP token account for amount `B`, bypassing Raydium's `Withdraw` entirely. Now `lp_mint.supply = S - B`, but `amm.lp_amount` is still `S`.
3. Any subsequent `Withdraw` call computes `coin_amount`/`pc_amount` using `InvariantPool { token_input: withdraw.amount, token_total: amm.lp_amount }` with the stale, inflated `S` as denominator (processor.rs:1751-1758), so every remaining LP holder permanently redeems less than their real share of pool reserves versus what `lp_mint.supply` (`S-B`) implies; the corresponding coin/pc value is never recoverable by anyone through the program's normal instructions.

### Citations

**File:** program/src/state.rs (L666-667)
```rust
    /// pool lp amount
    pub lp_amount: u64,
```

**File:** program/src/processor.rs (L976-977)
```rust
        amm.amm_owner = config_feature::amm_owner::ID;
        amm.lp_amount = liquidity;
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

**File:** program/src/processor.rs (L1713-1718)
```rust
        if withdraw.amount > user_source_lp.amount {
            return Err(AmmError::InsufficientFunds.into());
        }
        if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
            return Err(AmmError::NotAllowZeroLP.into());
        }
```

**File:** program/src/processor.rs (L1751-1758)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
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
