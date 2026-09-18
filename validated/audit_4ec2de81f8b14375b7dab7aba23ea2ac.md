### Title
Spot-price-based PnL split in `calc_take_pnl()` is manipulatable via same-transaction swaps before `Withdraw` - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
`Processor::calc_take_pnl()` determines how much of the pool's accumulated invariant growth (trading-fee revenue) is booked as protocol PnL (`need_take_pnl_pc` / `need_take_pnl_coin`) versus how much remains in the pool backing LP token value. This split is derived directly from the pool's instantaneous spot reserve ratio (`current_x`/`current_y`), read fresh from the AMM vault balances at call time, with no time-weighted average or manipulation resistance. Since this function is invoked as part of the unprivileged `Withdraw` instruction, any liquidity provider can, within a single atomic transaction, execute a swap that skews the pool's reserve ratio, immediately call `Withdraw`, and optionally reverse the swap afterward — biasing the PnL split in their own favor and extracting more value from the pool than their true share.

### Finding Description
`calc_take_pnl()` computes the post-take-pnl invariant point using: [1](#0-0) 

This directly consumes `current_x`/`current_y` (i.e., `x1`, `y1`), which are the *live* normalized vault balances passed in from `process_withdraw`: [2](#0-1) 

`x1`/`y1` are computed from `amm_pc_vault.amount` / `amm_coin_vault.amount` — the actual current token balances of the pool, i.e., the pool's spot price — with no TWAP or staleness/deviation check: [3](#0-2) 

Inside `calc_take_pnl`, `x2 = sqrt(last_x*last_y*current_x/current_y)` is computed directly from this spot ratio, and the amount attributed to protocol PnL (`pc_pnl_amount`/`coin_pnl_amount`, which is subtracted from the pool balance that backs LP shares) is a function of `diff_x = x1 - x2` and `diff_y = y1 - y2`: [4](#0-3) 

Because `Withdraw` is reachable by any unprivileged LP holder in a single transaction (unlike `WithdrawPnl`, which requires the privileged `pnl_owner` signer), and Solana transactions can bundle a `SwapBaseIn`/`SwapBaseOut` instruction immediately before a `Withdraw` instruction against the same pool with attacker-chosen amounts, an attacker fully controls `current_x`/`current_y` at the moment `calc_take_pnl` executes. This lets the attacker bias how much of the accumulated invariant growth is booked as `need_take_pnl_*` (owed to the protocol) versus how much remains in `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, which is what determines the withdrawing LP's `coin_amount`/`pc_amount` payout: [5](#0-4) 

### Impact Explanation
By manipulating the spot ratio right before withdrawing, an LP can shrink the amount attributed to protocol PnL and correspondingly inflate the reserve pool used to compute their own withdrawal proceeds, extracting real vault funds (SPL token transfers of coin/pc) beyond their legitimate share. This directly misallocates real, already-deposited user/protocol funds — a fund-theft/insolvency-class impact, since the protocol's `need_take_pnl_pc`/`need_take_pnl_coin` accounting becomes permanently understated relative to actual value extracted, and other LPs' remaining share of the pool is diluted.

### Likelihood Explanation
The attack requires only a single self-submitted transaction bundling a swap instruction (`SwapBaseIn`/`SwapBaseOut`/`_v2` variants) and a `Withdraw` instruction against accounts the attacker already controls (their own LP tokens, source/destination token accounts) — no privileged signer, no special timing beyond intra-transaction ordering, and no reliance on other actors. This is fully within reach of any LP holder with capital to move the pool's reserve ratio momentarily.

### Recommendation
Do not derive the PnL/pool split from the instantaneous vault balances captured within the same instruction as the withdrawal. Use a time-weighted or checkpointed reserve ratio (or restrict the invariant-growth split calculation to only reflect fee-driven growth measured independent of any single-transaction reserve skew), and/or disallow combining swap and withdraw instructions against the same pool within one transaction/slot to prevent atomic price manipulation of `calc_take_pnl`.

### Proof of Concept
1. Attacker holds LP tokens for pool P (coin/pc reserves `Cx`, `Cy`) and knows the AMM's stored `target_orders.calc_pnl_x/calc_pnl_y` snapshot (public account data).
2. In one transaction, attacker submits:
   a. `SwapBaseIn` (or `SwapBaseOut`) with a large `amount_in`, skewing `Cx`/`Cy` sharply in the attacker's chosen direction (paying only the swap fee).
   b. `Withdraw` for the attacker's LP tokens — this calls `calc_take_pnl` using the now-skewed `Cx`/`Cy` as `current_x`/`current_y`, computing `x2`/`y2` and thus `diff_x`/`diff_y` biased by the attacker's chosen ratio, minimizing `pc_pnl_amount`/`coin_pnl_amount` booked to the protocol and maximizing `total_pc_without_take_pnl`/`total_coin_without_take_pnl` used for the attacker's `coin_amount`/`pc_amount` payout.
   c. (Optional) a second swap reversing step (a) to restore the pool price, leaving the attacker with a net gain equal to the value shifted away from `need_take_pnl_*` accounting, minus swap fees.
3. Compare the attacker's payout to the payout computed with an un-manipulated spot price at the pre-transaction reserve ratio — the difference is value extracted at the expense of the protocol's PnL accounting / other LPs.

### Citations

**File:** program/src/math.rs (L50-60)
```rust
    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }
```

**File:** program/src/processor.rs (L196-262)
```rust
            // let current_k: u128 = (x1 as u128).checked_mul(y1 as u128).unwrap();
            // current p is
            // let current_p: u128 = (x1 as u128).checked_div(y1 as u128).unwrap();
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
            // let x2 = Calculator::sqrt(x2_power).unwrap();
            let x2 = x2_power.integer_sqrt();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl x2_power:{}, x2:{}", x2_power, x2).as_str());
            let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl y2:{}", y2).as_str());

            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
            delta_x = diff_x
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
            delta_y = diff_y
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();

            let diff_pc_pnl_amount =
                Calculator::restore_decimal(diff_x, amm.pc_decimals, amm.sys_decimal_value);
            let diff_coin_pnl_amount =
                Calculator::restore_decimal(diff_y, amm.coin_decimals, amm.sys_decimal_value);
            let pc_pnl_amount = diff_pc_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            let coin_pnl_amount = diff_coin_pnl_amount
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u64();
            if pc_pnl_amount != 0 && coin_pnl_amount != 0 {
                amm.state_data.need_take_pnl_pc = amm
                    .state_data
                    .need_take_pnl_pc
                    .checked_add(pc_pnl_amount)
                    .unwrap();
                amm.state_data.need_take_pnl_coin = amm
                    .state_data
                    .need_take_pnl_coin
                    .checked_add(coin_pnl_amount)
                    .unwrap();

                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
```

**File:** program/src/processor.rs (L1459-1464)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1719-1748)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );

        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
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
