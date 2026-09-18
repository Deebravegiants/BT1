### Title
Zero/low-decimal coin mints allow the Initialize2 minimum-liquidity lock to be bypassed, enabling a donation-based LP-share inflation attack - (File: program/src/processor.rs)

### Summary
`process_initialize2` mimics Uniswap V2's `MINIMUM_LIQUIDITY` mechanism by withholding `10^lp_decimals` units of LP from the pool creator while still counting the full `sqrt(x*y)` in `amm.lp_amount` (the internal LP-supply accounting used for every subsequent deposit/withdraw ratio calculation). Because `lp_decimals` is taken directly from the attacker-controlled `coin_mint`'s decimals field, and pool creation via `Initialize2` is fully permissionless, an attacker can create a pool with a coin mint that has 0 (or very low) decimals, reducing the "locked" minimum liquidity to a negligible amount (as low as 1). This defeats the protection and reopens the classic ERC4626-style donation/inflation attack that the lock is meant to prevent.

### Finding Description
At pool creation, `lp_decimals` is set from the coin mint's decimals: [1](#0-0) 

The initial liquidity/lock computation then subtracts `10^lp_decimals` from the amount actually minted to the creator, while `amm.lp_amount` (the pool's internal total-supply accounting used for all future deposit/withdraw share math) is set to the *full*, un-reduced `liquidity` value: [2](#0-1) [3](#0-2) 

If `lp_decimals` is 0, the effective lock is only 1 unit, meaning `amm.lp_amount` (the virtual total supply) can be as small as 2 for a minimal initial deposit (e.g., `init_coin_amount = init_pc_amount = 2`), with only 1 unit of LP actually minted to the attacker.

Subsequent deposits compute minted shares purely from live vault balances vs. `amm.lp_amount`, using floor rounding in the attacker's favor: [4](#0-3) [5](#0-4) 

Because `amm_coin_vault_info` / `amm_pc_vault_info` are ordinary SPL token accounts owned by the AMM authority PDA, any third party can transfer ("donate") tokens directly into them via a standard SPL `Transfer` instruction without going through the AMM program at all — this inflates `total_coin_without_take_pnl` / `total_pc_without_take_pnl` without touching `amm.lp_amount`. With `amm.lp_amount` artificially small (2), a subsequent victim `Deposit` will receive a rounded-down number of LP shares relative to the value they contributed (per the floor-rounded `exchange_token_to_pool` math), while the attacker's pre-existing 1 LP share now represents a disproportionately large claim on the post-donation pool. The deposit path only rejects the transaction if `mint_lp_amount == 0`: [6](#0-5) 
but does not reject a merely *disproportionate*, non-zero share count — so the core rounding-based value transfer from victim to attacker is not blocked.

### Impact Explanation
This is a value-theft primitive against liquidity providers: the attacker (as pool creator) can capture a share of a victim's deposit disproportionate to their real economic contribution, effectively stealing LP value once they withdraw. It also causes insolvent/incorrect pool accounting, since `amm.lp_amount` no longer accurately represents proportional ownership of the vault balances relative to donated funds.

### Likelihood Explanation
Exploitability depends entirely on the attacker being able to create a pool whose `coin_mint` has 0 (or very low) decimals — this is fully permissioned to the attacker since `Initialize2` accepts arbitrary mint accounts and is callable by anyone. Since most production Raydium pools pair well-known tokens with 6–9 decimals (SOL/USDC/USDT etc.), the practical likelihood is limited to pools involving custom/malicious low-decimal SPL tokens, but nothing in `process_initialize2` prevents such a pool from being created and listed, and a victim depositor has no on-chain signal distinguishing a maliciously configured low-decimal pool from a legitimate one.

### Recommendation
Do not rely solely on `10^lp_decimals` as the minimum-liquidity lock, since `lp_decimals` is derived from an attacker-controlled mint. Instead enforce a fixed, protocol-defined minimum absolute value for the initial lock (independent of token decimals), and/or enforce a minimum decimals requirement on `coin_mint`/`pc_mint` at `Initialize2` time (e.g., reject mints with `decimals == 0` or below some threshold), and consider basing deposit share calculations on a reconciled/tracked internal balance rather than raw, externally-donatable vault balances where feasible.

### Proof of Concept
1. Attacker calls `Initialize2` with a custom `coin_mint` configured with `decimals = 0` and a normal `pc_mint`, using `init_coin_amount = init_pc_amount = 2`. `liquidity = sqrt(2*2) = 2`; `user_lp_amount = 2 - 10^0 = 1` LP minted to attacker; `amm.lp_amount = 2` (full liquidity) is stored in `AmmInfo` (program/src/processor.rs:908-917, 977).
2. Attacker sends a plain SPL `Transfer` (outside the AMM program) of a large amount of `coin`/`pc` tokens directly into `amm_coin_vault`/`amm_pc_vault`, inflating `total_coin_without_take_pnl`/`total_pc_without_take_pnl` without changing `amm.lp_amount`.
3. Victim calls `Deposit` with a reasonable amount; `mint_lp_amount` is computed via floor-rounded `exchange_token_to_pool` against the now-inflated vault balances and the still-tiny `amm.lp_amount = 2` denominator (program/src/processor.rs:1147-1250), producing a rounded-down share count that undervalues the victim's real contribution.
4. Attacker calls `Withdraw` with their 1 LP share; since `amm.lp_amount` is small, the attacker's share of `total_coin_without_take_pnl`/`total_pc_without_take_pnl` (which now includes both the donation and part of the victim's deposit) is disproportionately large, extracting value contributed by the victim.

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

**File:** program/src/processor.rs (L967-977)
```rust
        amm.coin_vault = *amm_coin_vault_info.key;
        amm.pc_vault = *amm_pc_vault_info.key;
        amm.coin_vault_mint = *amm_coin_mint_info.key;
        amm.pc_vault_mint = *amm_pc_mint_info.key;
        amm.lp_mint = *amm_lp_mint_info.key;
        amm.open_orders = Pubkey::default();
        amm.market = *market_info.key;
        amm.market_program = Pubkey::default();
        amm.target_orders = *amm_target_orders_info.key;
        amm.amm_owner = config_feature::amm_owner::ID;
        amm.lp_amount = liquidity;
```

**File:** program/src/processor.rs (L1147-1153)
```rust
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

**File:** program/src/processor.rs (L1319-1325)
```rust
        if deduct_coin_amount > user_source_coin.amount || deduct_pc_amount > user_source_pc.amount
        {
            return Err(AmmError::InsufficientFunds.into());
        }
        if mint_lp_amount == 0 || deduct_coin_amount == 0 || deduct_pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```
