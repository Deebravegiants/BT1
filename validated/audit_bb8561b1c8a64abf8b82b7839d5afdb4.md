### Title
Vault/LP Inflation via Direct Token Donation to AMM Vaults - ([File: program/src/processor.rs])

### Summary
`process_deposit` computes the amount of LP tokens minted to a depositor using `total_coin_without_take_pnl` / `total_pc_without_take_pnl`, which are derived directly from the **live SPL token balances** of `amm_coin_vault` / `amm_pc_vault` (via `Calculator::calc_total_without_take_pnl_no_orderbook`), not from an independently-tracked internal accounting variable. [1](#0-0) . Because a swapper/attacker can create a pool with the minimum viable liquidity and then transfer ("donate") extra coin/pc tokens directly into the vault token accounts, they can inflate this exchange-rate denominator without minting any corresponding LP shares, reproducing the classic ERC4626-style vault/share inflation attack described in the FlatCoin report.

### Finding Description
`process_initialize2` requires `sqrt(pc_amount * coin_amount) > 10**decimals` and subtracts a fixed `10**decimals` "dead share" amount from what is actually minted to the creator (`user_lp_amount = liquidity - 10**decimals`), while `amm.lp_amount` (the internal share-total denominator) is set to the full, un-subtracted `liquidity` value. [2](#0-1) . This creates a "phantom" locked-share floor similar to Uniswap V2's dead-address burn, but the pool creator can still choose values just barely above the `InitLpAmountTooLess` threshold, ending up owning essentially the entire *real* (mintable/transferable) LP supply immediately after `Initialize2` (`user_lp_amount` can be as small as 1).

Subsequently, in `process_deposit`, the exchange rate used to compute `mint_lp_amount` is based on `total_coin_without_take_pnl`/`total_pc_without_take_pnl`, obtained from `amm_coin_vault.amount` / `amm_pc_vault.amount` — i.e., the actual current token balances of the vault accounts — combined with a PnL adjustment via `calc_take_pnl`. [1](#0-0) [3](#0-2) . Because these vault accounts are ordinary SPL token accounts, any unprivileged actor can perform a plain `spl_token::transfer` into `amm_coin_vault`/`amm_pc_vault` (which are just PDAs owned by the AMM authority, with no code path preventing incoming transfers) to increase `amm_coin_vault.amount`/`amm_pc_vault.amount` without invoking `Deposit` and therefore without any corresponding increase to `amm.lp_amount`.

Once the attacker is the dominant real LP holder (from the minimal `Initialize2`) and has donated a large amount to the vault, a victim's subsequent `Deposit` computes:
```
mint_lp_amount = deduct_coin_amount / total_coin_without_take_pnl * amm.lp_amount
``` [4](#0-3) 
Since `total_coin_without_take_pnl` has been artificially inflated by the donation while `amm.lp_amount` was not, the victim receives disproportionately few LP shares for their contribution (rounding heavily in the attacker's favor, though an exact zero-mint reverts via the explicit `mint_lp_amount == 0` check). [5](#0-4) . The attacker, holding nearly all real LP supply, can then withdraw and capture the vast majority of the vault's value — including the victim's newly deposited funds and the attacker's own earlier donation — via `Withdraw`, which similarly bases the coin/pc payout on the current live vault balances proportional to `amm.lp_amount`.

### Impact Explanation
This is a Medium/High-severity accounting flaw: unlike the acknowledged FlatCoin issue, the explicit `mint_lp_amount == 0` guard in `process_deposit` prevents the most severe "silent total loss on zero-share mint" case, but it does not prevent the attacker from capturing a disproportionate share of a victim's deposit by manipulating the vault-balance-based exchange rate through direct token donation while controlling almost the entire real LP supply. This can result in real, unauthorized value transfer from a liquidity-providing victim to the attacker, i.e., theft of LP funds.

### Likelihood Explanation
Reachable purely through unprivileged, single-transaction paths: an attacker calls `Initialize2` with a minimal, barely-passing amount to create a pool (or targets a freshly-created low-liquidity pool), then performs an ordinary SPL token transfer directly to `amm_coin_vault`/`amm_pc_vault`, and finally calls `Withdraw` after a victim's `Deposit`. No privileged signer, off-chain component, or validator collusion is required — only timing relative to the victim's deposit, similar to the accepted "Medium, requires prior setup / guessed timing" characterization in the underlying report's judged resolution.

### Recommendation
Do not derive the AMM's internal-vs-external exchange rate purely from live token-account balances without reconciling them against `amm.lp_amount` and a separately tracked expected balance; consider tracking coin/pc "owned" totals as state fields updated only through `Deposit`/`Withdraw`/`Swap`, and treat unexpected excess vault balance as protocol-owned or handled by an explicit "skim"/"sync" instruction rather than silently feeding into share-minting math. Additionally, consider requiring a substantially larger, non-attacker-controllable minimum locked liquidity at `Initialize2` (or minting a fixed dead-share amount to a burn address, matching the mint's actual `totalSupply` including the dead shares) so a single account can never economically dominate the real LP supply of a freshly created pool.

### Proof of Concept
1. Attacker calls `Initialize2` for a new coin/pc pair with `init_coin_amount`/`init_pc_amount` chosen so `sqrt(pc*coin)` is just above `10**lp_decimals` (e.g., `10**lp_decimals + 1`), receiving `user_lp_amount = 1` LP token while `amm.lp_amount = 10**lp_decimals + 1`. [6](#0-5) 
2. Attacker performs a plain SPL `Transfer` of a large amount of coin/pc tokens directly into `amm_coin_vault`/`amm_pc_vault` (bypassing the `Deposit` instruction entirely).
3. Victim calls `Deposit` with their intended amount; `mint_lp_amount` is computed against the now-inflated `total_coin_without_take_pnl`/`total_pc_without_take_pnl`, yielding far fewer LP shares than the victim's proportional contribution warrants. [4](#0-3) 
4. Attacker calls `Withdraw` for their LP tokens, receiving a share of the vault (computed from the same live-balance-based formula) that includes most of both their own donation and the victim's deposited funds, extracting disproportionate value.

### Citations

**File:** program/src/processor.rs (L908-938)
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

**File:** program/src/processor.rs (L1243-1302)
```rust
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
        } else {
            // base pc
            deduct_coin_amount = invariant
                .exchange_pc_to_coin(deposit.max_pc_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_pc_amount = deposit.max_pc_amount;
            if deduct_coin_amount > deposit.max_coin_amount {
                encode_ray_log(DepositLog {
                    log_type: LogType::Deposit.into_u8(),
                    max_coin: deposit.max_coin_amount,
                    max_pc: deposit.max_pc_amount,
                    base: deposit.base_side,
                    pool_coin: total_coin_without_take_pnl,
                    pool_pc: total_pc_without_take_pnl,
                    pool_lp: amm.lp_amount,
                    calc_pnl_x: target_orders.calc_pnl_x,
                    calc_pnl_y: target_orders.calc_pnl_y,
                    deduct_coin: deduct_coin_amount,
                    deduct_pc: deduct_pc_amount,
                    mint_lp: 0,
                });
                return Err(AmmError::ExceededSlippage.into());
            }
            // base pc, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_coin_amount < deposit.other_amount_min.unwrap() {
                    encode_ray_log(DepositLog {
                        log_type: LogType::Deposit.into_u8(),
                        max_coin: deposit.max_coin_amount,
                        max_pc: deposit.max_pc_amount,
                        base: deposit.base_side,
                        pool_coin: total_coin_without_take_pnl,
                        pool_pc: total_pc_without_take_pnl,
                        pool_lp: amm.lp_amount,
                        calc_pnl_x: target_orders.calc_pnl_x,
                        calc_pnl_y: target_orders.calc_pnl_y,
                        deduct_coin: deduct_coin_amount,
                        deduct_pc: deduct_pc_amount,
                        mint_lp: 0,
                    });
                    return Err(AmmError::ExceededSlippage.into());
                }
            }

            let invariant_pc = InvariantPool {
                token_input: deduct_pc_amount,
                token_total: total_pc_without_take_pnl,
            };
            // pc_amount/ (total_pc_amount + pc_amount)  = output / (lp_mint.supply + output) =>  output = pc_amount / total_pc_amount * lp_mint.supply
            mint_lp_amount = invariant_pc
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
