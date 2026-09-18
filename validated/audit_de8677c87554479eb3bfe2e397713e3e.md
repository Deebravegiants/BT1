### Title
Attacker-controlled `coin_mint` decimals let a pool creator trivially bypass the initial-liquidity lock, enabling a share-inflation (donation) attack on `Initialize2`/`Deposit` — ([File: program/src/processor.rs])

### Summary
Raydium's `process_initialize2` derives the LP mint's decimals — and therefore the size of the permanent "dead" liquidity lock that is supposed to prevent first-depositor share-inflation attacks — directly and unconditionally from the attacker-supplied `coin_mint` account, with no floor, no relation to the actual value/precision of the pool, and no consideration of `pc_mint`'s decimals. Since `Initialize2` is a fully permissionless instruction where the caller supplies both `coin_mint` and `pc_mint` (freshly created SPL mints under their control), an attacker can trivially set `coin_mint.decimals = 0` (or 1), reducing Raydium's MINIMUM_LIQUIDITY-equivalent lock to `10^0 = 1` unit — effectively defeating the mechanism designed to make first-depositor inflation attacks economically infeasible.

### Finding Description
In `process_initialize2`, the LP mint is created with decimals taken straight from the coin mint: [1](#0-0) 

That `lp_mint.decimals` value is then used as the anti-inflation lock amount subtracted from the geometric-mean initial liquidity before minting to the pool creator — this is Raydium's analog of Uniswap V2's `MINIMUM_LIQUIDITY`: [2](#0-1) 

Both `amm_coin_mint_info` and `amm_pc_mint_info` are attacker-supplied, unprivileged accounts passed into `Initialize2` — there is no restriction requiring a specific mint, decimals value, or well-known token: [3](#0-2) 

Because `lp_decimals` is taken only from `coin_mint` (not `min(coin_decimals, pc_decimals)`, and not tied to any fixed, non-attacker-controlled floor as Uniswap's constant `1000` is), a pool creator can mint their own zero/low-decimal SPL token as `coin_mint`, pair it with a valuable `pc_mint` (e.g., a real 6/9-decimal token), and reduce the lock to as little as `10^0 = 1` raw unit. This is functionally the same bug class as the reported "hardcoded/mis-derived decimals" issue: a decimals-dependent security invariant (there, `IncentivizedERC20` decimals feeding external integrations and `MINIMUM_LIQUIDITY`; here, `lp_mint.decimals` feeding the initial-liquidity lock) is derived incorrectly and is fully controllable by an unprivileged actor, breaking the intended protection.

With the lock reduced to a negligible amount, `amm.lp_amount` after initialization can be made tiny (e.g., a handful of units) while the actual vault balances (`amm_coin_vault`/`amm_pc_vault`) can subsequently be inflated by directly transferring additional SPL tokens into the vault token accounts (a plain SPL `Transfer` requires no cooperation from the AMM program and is not reflected in `amm.lp_amount`). Downstream accounting in `process_deposit` computes newly minted LP as a ratio of the deposited amount to the *current vault balance*, using the *tiny* `amm.lp_amount` as the total-supply reference: [4](#0-3) 

Because the "total supply" side of that ratio (`amm.lp_amount`) was allowed to be near-zero due to the negligible lock, and the "total pool value" side (`total_coin_without_take_pnl`/`total_pc_without_take_pnl`) can be independently inflated via direct token transfers to the vaults, a subsequent depositor's minted LP share can be made disproportionately small relative to the value they contribute, while the attacker — holding effectively all of the (tiny) LP supply — can later withdraw and claim a share of the inflated vault balances that includes the victim's contribution.

### Impact Explanation
This breaks the core economic safety invariant of the AMM: unbacked/disproportionate LP share allocation and insolvent pool accounting for any pool the attacker creates with a purpose-built low-decimal `coin_mint`. Victims who deposit into such a pool (which looks like any other newly created Raydium pool from the outside, since `coin_mint`/`pc_mint` are legitimate SPL mints) can have their deposited value effectively transferred to the pool creator through share-price manipulation, matching the "concrete theft ... of user or LP funds" / "unbacked LP minting" / "insolvent pool accounting" impact classes.

### Likelihood Explanation
Likelihood is high: creating an SPL mint with 0 or 1 decimals costs nothing and requires no special privilege, `Initialize2` is fully permissionless and reachable from a single transaction with attacker-chosen accounts (`amm_coin_mint_info`, `amm_pc_mint_info`), and directly transferring tokens into an already-known vault ATA is a standard, permissionless SPL `Transfer` instruction. No validator or off-chain assumptions are required.

### Recommendation
Do not let the initial-liquidity lock size (`lp_mint.decimals`-derived) be solely determined by an attacker-chosen `coin_mint`. Use a fixed, protocol-defined minimum-liquidity constant (independent of any external mint's decimals, similar to Uniswap V2's `MINIMUM_LIQUIDITY = 1000` fixed units) or, if decimal-scaling is desired, derive the LP mint decimals/lock from `max(coin_decimals, pc_decimals)`/`sys_decimal_value` rather than `coin_mint.decimals` alone, and enforce a hard minimum absolute lock value so it cannot be trivially reduced to `1`.

### Proof of Concept
1. Attacker creates SPL mint `M0` with `decimals = 0` and mints themselves a small supply.
2. Attacker calls `Initialize2` with `coin_mint = M0`, `pc_mint = <valuable token, e.g. USDC>`, `init_coin_amount`/`init_pc_amount` chosen so `liquidity = sqrt(init_coin_amount * init_pc_amount)` is just above `1` (the lock amount, since `lp_decimals = coin_mint.decimals = 0` ⇒ `10^0 = 1`), per program/src/processor.rs:761 and :908-917.
3. `amm.lp_amount` is now tiny (e.g., `liquidity - 1`).
4. Attacker performs a raw SPL `Transfer` (not via the AMM program) of a large amount of `pc_mint`/`coin_mint` directly into `amm_pc_vault`/`amm_coin_vault`, inflating `total_pc_without_take_pnl`/`total_coin_without_take_pnl` without changing `amm.lp_amount`.
5. A victim calls `Deposit`; `mint_lp_amount` is computed via `InvariantPool::exchange_token_to_pool` against the now-inflated vault balance and the still-tiny `amm.lp_amount` (program/src/processor.rs:1243-1250), yielding a disproportionately small LP allocation relative to the value the victim deposits into the vault.
6. Attacker withdraws using their share of `amm.lp_amount`, claiming a proportional share of the vault that includes the victim's deposited value.

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

**File:** program/src/instruction.rs (L142-165)
```rust
    ///   Initializes a new AMM pool.
    ///
    ///   0. `[]` Spl Token program id
    ///   1. `[]` Associated Token program id
    ///   2. `[]` Sys program id
    ///   3. `[]` Rent program id
    ///   4. `[writable]` New AMM Account to create.
    ///   5. `[]` $authority derived from `create_program_address(&[AUTHORITY_AMM, &[nonce]])`.
    ///   6. `[writable]` AMM open orders Account
    ///   7. `[writable]` AMM lp mint Account
    ///   8. `[]` AMM coin mint Account
    ///   9. `[]` AMM pc mint Account
    ///   10. `[writable]` AMM coin vault Account. Must be non zero, owned by $authority.
    ///   11. `[writable]` AMM pc vault Account. Must be non zero, owned by $authority.
    ///   12. `[writable]` AMM target orders Account. To store plan orders informations.
    ///   13. `[]` AMM config Account, derived from `find_program_address(&[&&AMM_CONFIG_SEED])`.
    ///   14. `[]` AMM create pool fee destination Account
    ///   15. `[]` Market program id
    ///   16. `[writable]` Market Account. Market program is the owner.
    ///   17. `[writable, signer]` User wallet Account
    ///   18. `[]` User token coin Account
    ///   19. '[]` User token pc Account
    ///   20. `[writable]` User destination lp token ATA Account
    Initialize2(InitializeInstruction2),
```
