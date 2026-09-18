### Title
Incorrect PnL-baseline delta calculation in `calc_take_pnl` causes repeated over-extraction of LP fee growth - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` computes two related but distinct quantities from the same "diff" (the growth in pool value since the last PnL take): the amount that should actually be pulled into the `need_take_pnl_*` reserve, and the amount by which the tracked baseline (`target_orders.calc_pnl_x` / `calc_pnl_y`) should be advanced. The function's own docstring specifies that the baseline should advance by the *full* diff (`pnl_x = current_x - x_after_take_pnl`), but the code instead advances it by only the `pnl_numerator/pnl_denominator` fraction of the diff — the same fraction that is separately, and correctly, applied when computing the actual amount transferred into `need_take_pnl_pc`/`need_take_pnl_coin`. This double-application of the fee fraction (once to the tracked baseline delta, once to the extracted amount) is structurally the same class of bug as the reported `DIARewardsDistribution.updateRewardRatePerDay` issue: a rate/fraction that should be applied once to compute one downstream value is instead baked into an intermediate variable that a second calculation also multiplies by, and the wrong quantity is retained across accounting periods.

### Finding Description
`calc_take_pnl` is documented as: [1](#0-0) 

Per the docstring, step 5 defines `pnl_x = current_x - x_after_take_pnl` i.e. the full `diff_x = x1 - x2`, which should become the new `delta_x` used to roll `target_orders.calc_pnl_x` forward to the new baseline `x2`. Instead, the implementation multiplies `diff_x`/`diff_y` by `pnl_numerator/pnl_denominator` before assigning to `delta_x`/`delta_y`: [2](#0-1) 

Separately, the code correctly restores the *same* `diff_x`/`diff_y` to token decimals and again multiplies by `pnl_numerator/pnl_denominator` to compute the amount actually credited to the pnl reserve: [3](#0-2) 

Because `delta_x`/`delta_y` (the value used to update the tracked baseline) is only 12% (`pnl_numerator=12, pnl_denominator=100` per `Fees::initialize`) of the true diff instead of 100% of it, the baseline `target_orders.calc_pnl_x`/`calc_pnl_y` barely advances toward the current invariant coordinates `x2`/`y2` each time PnL is taken: [4](#0-3) 

This baseline is used on every subsequent `Deposit`/`Withdraw` call (both reachable by any unprivileged LP) to recompute `x1`, `y1`, and feed back into `calc_take_pnl`: [5](#0-4) [6](#0-5) 

Since the baseline lags far behind the real invariant growth (only 12% of the gap is closed each time instead of 100%), the "remaining gap" (`diff_x`/`diff_y`) stays large across successive deposit/withdraw calls. Each call re-extracts `pnl_numerator/pnl_denominator` (12%) of that still-large remaining gap into `need_take_pnl_pc`/`need_take_pnl_coin`: [7](#0-6) 

Over repeated deposit/withdraw cycles, this compounds into cumulative extraction far exceeding the intended 12% share of trading-fee growth, continuously siphoning value out of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (the LP-owned pool balance) and into the protocol's `need_take_pnl_*` bucket, which is only reachable to withdraw via the privileged `WithdrawPnl` instruction but whose *accrual* is driven entirely by unprivileged `Deposit`/`Withdraw` calls.

### Impact Explanation
This causes insolvent/skewed pool accounting: LP token holders' share of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` is eroded faster than the documented 12% PnL-fee design intends, because the invariant baseline used to gate future extractions never properly catches up. This is a direct, unbounded (across many deposit/withdraw calls) transfer of value from LPs to the `need_take_pnl_*` reserve, i.e., financial loss for LPs — matching the "High" severity classification of the analogous reward-miscalculation report.

### Likelihood Explanation
Any unprivileged user (a swapper is not required — any LP performing normal `Deposit` or `Withdraw` operations) triggers `calc_take_pnl` and this miscalculation on every call, with no special permissions or accounts required beyond the standard deposit/withdraw instruction accounts. The bug is deterministic and triggers on the very first non-trivial pool-growth cycle, and worsens with every subsequent deposit/withdraw, making it highly likely to manifest in normal pool operation.

### Recommendation
Set `delta_x`/`delta_y` to the raw `diff_x`/`diff_y` (matching the docstring's `pnl_x = current_x - x_after_take_pnl`), i.e. remove the `pnl_numerator`/`pnl_denominator` multiplication from the assignment at `program/src/processor.rs:215-226`, and retain the fee-fraction multiplication only for computing `pc_pnl_amount`/`coin_pnl_amount` (the actual amount routed to `need_take_pnl_*`). This ensures the baseline (`target_orders.calc_pnl_x`/`calc_pnl_y`) is properly advanced to `x2`/`y2` each cycle while only the intended 12% fraction of realized growth is extracted as protocol PnL.

### Proof of Concept
1. Pool is created and initial `target_orders.calc_pnl_x`/`calc_pnl_y` recorded via `Initialize2`.
2. Multiple swaps occur (via `SwapBaseIn`/`SwapBaseOut`, unprivileged), growing `total_pc_without_take_pnl`/`total_coin_without_take_pnl` due to trading fees, so `x1*y1 > calc_pnl_x*calc_pnl_y`.
3. Any user calls `Deposit` (unprivileged) — `calc_take_pnl` runs: it computes `diff_x = x1 - x2` correctly, extracts `pc_pnl_amount = 12% of diff_x` into `need_take_pnl_pc` (correct), but sets `target_orders.calc_pnl_x = x1 + deposit - delta_x` where `delta_x = 12% of diff_x` instead of `delta_x = diff_x` (100%). The recorded baseline should have moved to `x2`, but instead stays close to `x1`.
4. On the next `Deposit`/`Withdraw` call, `x1` (current pool value) has grown further from new trading fees, but `calc_pnl_x` (baseline) is still nearly at the old `x1`, so `diff_x` computed again is nearly as large as before rather than shrinking to reflect the prior extraction — causing another ~12% extraction of an inflated gap.
5. Repeating steps 3–4 across many deposit/withdraw cycles cumulatively extracts a share of pool growth well above the intended 12%, transferring LP-owned value into `need_take_pnl_pc`/`need_take_pnl_coin` at an accelerated, non-bounded rate — verifiable by comparing cumulative `need_take_pnl_pc`/`need_take_pnl_coin` growth against the expected `12% * total realized trading fees` over the same period.

### Citations

**File:** program/src/processor.rs (L159-166)
```rust
    /// The Detailed calculation of pnl
    /// 1. calc last_k witch dose not take pnl: last_k = calc_pnl_x * calc_pnl_y;
    /// 2. calc current price: current_price = current_x / current_y;
    /// 3. calc x after take pnl: x_after_take_pnl = sqrt(last_k * current_price);
    /// 4. calc y after take pnl: y_after_take_pnl = x_after_take_pnl / current_price;
    ///                           y_after_take_pnl = x_after_take_pnl * current_y / current_x;
    /// 5. calc pnl_x & pnl_y:  pnl_x = current_x - x_after_take_pnl;
    ///                         pnl_y = current_y - y_after_take_pnl;
```

**File:** program/src/processor.rs (L213-226)
```rust
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
```

**File:** program/src/processor.rs (L228-243)
```rust
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
```

**File:** program/src/processor.rs (L244-262)
```rust
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

**File:** program/src/processor.rs (L1145-1173)
```rust
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
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
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1719-1749)
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
        }
```

**File:** program/src/state.rs (L463-477)
```rust
    pub fn initialize(&mut self) -> Result<(), AmmError> {
        // min_separate = 5/10000
        self.min_separate_numerator = 5;
        self.min_separate_denominator = TEN_THOUSAND;
        // trade_fee = 25/10000
        self.trade_fee_numerator = 25;
        self.trade_fee_denominator = TEN_THOUSAND;
        // pnl = 12/100
        self.pnl_numerator = 12;
        self.pnl_denominator = 100;
        // swap_fee = 25 / 10000
        self.swap_fee_numerator = 25;
        self.swap_fee_denominator = TEN_THOUSAND;
        Ok(())
    }
```
