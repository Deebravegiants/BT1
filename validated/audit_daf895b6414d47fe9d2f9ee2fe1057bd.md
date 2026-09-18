## Title
Permissionless pool creation with attacker-chosen low/zero-decimal `coin_mint` bypasses `Initialize2`'s minimum-liquidity floor, enabling a `pricePerShare`/LP-ratio inflation ("donation") attack against subsequent depositors - (File: `program/src/processor.rs`)

## Summary
`process_initialize2` derives its anti-inflation "minimum liquidity" floor from `lp_mint.decimals`, which is set equal to `coin_mint.decimals` — a value fully controlled by the (unprivileged) pool creator. Combined with the fact that LP-share accounting (`amm.lp_amount`) is a virtual value decoupled from the real, donatable SPL vault balances used in `process_deposit`, an attacker can create a near-zero-cost pool and later dilute a victim's deposit exactly as in the referenced AaveV3YieldSource `pricePerShare` manipulation report.

## Finding Description
In `process_initialize2`, the initial LP supply is computed as:

```
liquidity = sqrt(pc_vault.amount * coin_vault.amount)
user_lp_amount = liquidity - 10^lp_mint.decimals   // errors via checked_sub if liquidity < 10^decimals
``` [1](#0-0) 

and `lp_decimals` (and therefore `lp_mint.decimals`) is taken directly from the caller-supplied `coin_mint`:

```
let lp_decimals = coin_mint.decimals;
Self::generate_amm_associated_spl_mint(..., lp_decimals);
``` [2](#0-1) 

`Initialize2` only requires the coin/pc mints to differ and the vaults to be non-zero — there is no restriction preventing the creator from using an SPL mint with `decimals = 0` (or a very low value) as `coin_mint`:

```
if *amm_coin_mint_info.key == *amm_pc_mint_info.key {
    return Err(AmmError::InvalidCoinMint.into());
}
...
if amm_coin_vault.amount == 0 { return Err(AmmError::InvalidSupply.into()); }
if amm_pc_vault.amount == 0 { return Err(AmmError::InvalidSupply.into()); }
``` [3](#0-2) [4](#0-3) 

With `decimals = 0`, the "minimum liquidity" threshold collapses to `10^0 = 1`, so an attacker can bootstrap a pool with e.g. `pc_vault.amount = 2`, `coin_vault.amount = 2` (`liquidity = 2`), receiving `user_lp_amount = 1` — an exact analog of the report's "supply 1 wei, get 1 wei of shares" first-depositor step.

The subsequent `process_deposit` math computes minted LP as a ratio of the **real, donatable** vault token balance against the **virtual** `amm.lp_amount` bookkeeping value:

```
let invariant_coin = InvariantPool { token_input: deduct_coin_amount, token_total: total_coin_without_take_pnl };
mint_lp_amount = invariant_coin.exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)...
``` [5](#0-4) 

`total_coin_without_take_pnl`/`total_pc_without_take_pnl` are derived from the actual on-chain vault token-account balances via `Calculator::calc_total_without_take_pnl_no_orderbook`, fed straight from `amm_coin_vault.amount` / `amm_pc_vault.amount` read at the start of deposit processing: [6](#0-5) 

Because these are real SPL token account balances, they can be inflated by a **plain SPL token transfer directly into the vault** — no program instruction is required, exactly mirroring the "attacker sends aToken directly to the yield source" step of the referenced report. This raises `total_coin_without_take_pnl` (the denominator/pro-rata basis) without touching `amm.lp_amount` (the numerator basis for LP minting), so a victim's subsequent deposit is minted proportionally far fewer LP tokens than their contribution is worth, while the attacker's already-minted `user_lp_amount` (and the donated tokens now embedded in the vault) capture the excess value once the attacker withdraws.

The only guardrail present is the zero-mint check:
```
if mint_lp_amount == 0 || deduct_coin_amount == 0 || deduct_pc_amount == 0 {
    return Err(AmmError::InvalidInput.into());
}
``` [7](#0-6) 
This prevents the *degenerate* free-redemption/zero-mint case from the report, but does **not** prevent the attacker from capturing a disproportionate share when `mint_lp_amount` rounds to a small nonzero value relative to the victim's real economic deposit.

## Impact Explanation
An attacker who creates a pool via `Initialize2` using a self-minted, zero/low-decimal `coin_mint` paired with a valuable `pc_mint` (or vice versa) can, for a near-zero cost (a couple of base units of each token), obtain the sole existing LP position. By subsequently transferring (donating) real value directly into the AMM's coin/pc vault token accounts, the attacker skews the ratio between the real vault balance and the virtual `amm.lp_amount` bookkeeping value. Any user who is lured into depositing into this pool via the standard `Deposit` instruction will be minted a share of LP tokens far smaller than their real contribution warrants, permitting the attacker to withdraw a disproportionate amount of the pooled value (including the victim's real deposit) via `Withdraw`. This is a direct theft of LP/user funds through insolvent/mis-proportioned pool accounting.

## Likelihood Explanation
Pool creation (`Initialize2`) is fully permissionless and reachable by any unprivileged account in a single transaction, and creating an SPL mint with `decimals = 0` and donating tokens to a vault ATA are both ordinary, unprivileged SPL Token operations. The main practical constraint is social — a victim must be induced to deposit into the attacker-created pool rather than an established, well-known pair. This is a realistic risk for permissionless AMM deployments where pools for arbitrary/new token pairs are routinely created and discovered by users (e.g., via UI pool lists, LP-farming, new-token trading), making likelihood Medium.

## Recommendation
- Decouple the "minimum liquidity" floor from attacker-controlled `coin_mint.decimals`; use a fixed, sufficiently large constant (Uniswap-V2-style `MINIMUM_LIQUIDITY`) independent of any user-supplied mint's decimals, or take the floor from `max(coin_decimals, pc_decimals)`/a program-wide constant rather than solely `coin_mint.decimals`.
- Enforce a sane minimum on `coin_mint.decimals` (and/or `pc_mint.decimals`), e.g., reject mints with decimals below a configured threshold (e.g., 6), preventing the near-zero bootstrap cost.
- Consider computing deposit LP minting against a value that also accounts for undeposited/donated balances consistently, or reconcile `amm.lp_amount` against real vault balances at deposit time to detect/neutralize unexplained balance growth (donations) before minting new LP shares.

## Proof of Concept
1. Attacker mints a custom SPL token `X` with `decimals = 0`.
2. Attacker calls `Initialize2` with `coin_mint = X`, `pc_mint = <valuable token, e.g. USDC>`, `init_coin_amount = 2`, `init_pc_amount = 2`.
   - `liquidity = sqrt(2*2) = 2`; `lp_decimals = 0` ⇒ threshold `10^0 = 1`; `user_lp_amount = 2 - 1 = 1` minted to attacker.
   - `amm.lp_amount = liquidity = 2` (virtual bookkeeping) [8](#0-7) 
3. Attacker performs a normal SPL `Transfer` sending, e.g., `1_000_000` USDC directly into `amm_pc_vault_info` (no program call required, vault is a normal token account owned by the AMM authority PDA but transfers into it require no special permission).
4. `total_pc_without_take_pnl` at next deposit now reflects the inflated real balance, while `amm.lp_amount` remains `2`. [9](#0-8) 
5. Victim calls `Deposit` intending to provide proportional liquidity (e.g., deposits real value comparable to the donated amount). Because `mint_lp_amount = deduct_amount * amm.lp_amount / total_without_take_pnl` (floor), the victim receives a minimal number of new LP tokens relative to their contribution. [10](#0-9) 
6. Attacker calls `Withdraw` with their `user_lp_amount = 1` LP token, redeeming a share of the total pool (now containing the victim's real deposit plus the attacker's original donation) disproportionate to their real contribution.

### Citations

**File:** program/src/processor.rs (L680-683)
```rust
        if *amm_coin_mint_info.key == *amm_pc_mint_info.key {
            return Err(AmmError::InvalidCoinMint.into());
        }

```

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

**File:** program/src/processor.rs (L858-883)
```rust
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_coin_mint_info.key,
            amm_coin_vault.mint,
            "coin_mint",
            AmmError::InvalidCoinMint
        );
        // unpack and check token_pc
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_pc_vault.owner,
            *amm_authority_info.key,
            "pc_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_pc_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
```

**File:** program/src/processor.rs (L908-977)
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

        amm.initialize(
            init.nonce,
            init.open_time,
            coin_mint.decimals,
            pc_mint.decimals,
            0,
            0,
        )?;
        encode_ray_log(InitLog {
            log_type: LogType::Init.into_u8(),
            time: init.open_time,
            pc_decimals: amm.pc_decimals as u8,
            coin_decimals: amm.coin_decimals as u8,
            pc_lot_size: 0,
            coin_lot_size: 0,
            pc_amount: amm_pc_vault.amount,
            coin_amount: amm_coin_vault.amount,
            market: *market_info.key,
        });
        let x = Calculator::normalize_decimal_v2(
            amm_pc_vault.amount,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y = Calculator::normalize_decimal_v2(
            amm_coin_vault.amount,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        // check and init target orders account
        if amm_target_orders_info.owner != program_id {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        let mut target_order = TargetOrders::load_mut(amm_target_orders_info)?;
        target_order.check_init(x.as_u128(), y.as_u128(), amm_info.key)?;

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

**File:** program/src/processor.rs (L1323-1325)
```rust
        if mint_lp_amount == 0 || deduct_coin_amount == 0 || deduct_pc_amount == 0 {
            return Err(AmmError::InvalidInput.into());
        }
```
