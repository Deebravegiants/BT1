### Title
Unchecked division by zero in `calc_take_pnl`/`calc_x_power` causes panic-based permanent freeze of pool funds - ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl` and its helper `Calculator::calc_x_power` perform `checked_div(...).unwrap()` operations on pool-derived values (`x1`, `y1`) without first validating that these values are non-zero, mirroring the TensorFlow `SparseFillEmptyRows` pattern of skipping validation of a tensor/value that can legitimately be empty/zero before dereferencing/dividing by it. Because `calc_take_pnl` is invoked from every unprivileged, fund-moving instruction (`Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn`, `SwapBaseOut`, and their V2 variants), a pool state where one side's normalized vault balance (`x1` or `y1`) becomes `0` will make every subsequent call panic, aborting all transactions against that pool.

### Finding Description
`calc_take_pnl` computes `x1`/`y1` from `Calculator::normalize_decimal_v2(total_pc_without_take_pnl, ...)` / `normalize_decimal_v2(total_coin_without_take_pnl, ...)`, which are derived directly from live SPL token vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook` [1](#0-0) . These values are passed unchecked into `calc_take_pnl`: [2](#0-1) 

`Calculator::calc_x_power` divides by `current_y` with `checked_div(current_y).unwrap()`, and immediately after, `calc_take_pnl` computes `y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` — dividing by `x1` with no zero-check [3](#0-2) . If either `x1` (normalized pc vault total) or `y1` (normalized coin vault total) is `0`, the `checked_div` returns `None` and the subsequent `.unwrap()` panics, aborting the instruction with no recoverable `ProgramError`.

This function is reachable from every fund-moving, unprivileged instruction: `process_deposit` [4](#0-3) , `process_withdraw` [5](#0-4) , `process_withdrawpnl` [6](#0-5) , and swap paths such as `process_swap_base_in_v2` which computes totals via the same no-checked-zero pipeline [7](#0-6) . None of these entry points validate that the resulting `total_pc_without_take_pnl` / `total_coin_without_take_pnl` (and therefore `x1`/`y1`) are non-zero before calling `calc_take_pnl`.

### Impact Explanation
If a pool's vault balance on one side is ever driven down to `0` (e.g., through repeated legitimate swaps that asymptotically drain one side, or through `WithdrawExcessLamports`/other legitimate operations reducing vault token amounts to the floor), any subsequent call into `Deposit`, `Withdraw`, `WithdrawPnl`, or any swap instruction will panic inside `calc_take_pnl`/`calc_x_power`. Because a Solana program panic aborts the transaction without a graceful `ProgramError`, and because every fund-moving instruction routes through this same function, this creates a permanent inability for LPs to withdraw liquidity or for the pool to process any further deposits/swaps/pnl-withdrawals — i.e., a permanent freeze of user and LP funds locked in the AMM vaults, satisfying the "permanent freezing of funds" impact bar.

### Likelihood Explanation
No privileged signer is required to trigger this: it depends purely on the pool reaching a state where the normalized total on one side is `0`, which can be approached through ordinary swap activity against a pool with skewed reserves or extreme decimal/precision combinations (the AMM math floors amounts, and precision loss through `normalize_decimal_v2`/`restore_decimal` conversions between `sys_decimal_value` and token decimals can round a side to zero even when raw vault balance is nonzero in some decimal configurations). All reachable entry points (Deposit, Withdraw, WithdrawPnl, all four swap variants) funnel into the same unguarded arithmetic, making the surface broad, though the precise reserve/decimal combination needed to hit an exact zero requires specific pool parameters and trade sequencing.

### Recommendation
Add explicit checks before performing division in `calc_take_pnl` and `Calculator::calc_x_power`: if `x1 == 0` or `y1 == 0` (or `current_y == 0` in `calc_x_power`), return a proper `AmmError` (e.g., `AmmError::CalcPnlError`) instead of allowing `checked_div(...).unwrap()` to panic. This converts a program panic (which can permanently brick the pool) into a graceful, recoverable error path, consistent with how `CalcPnlError` is already used elsewhere in the same function for the `k`-invariant check.

### Proof of Concept
1. An attacker (or natural pool activity) drives `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) for a given AMM pool down toward its minimum via a sequence of ordinary `SwapBaseIn`/`SwapBaseOut` calls, exploiting decimal normalization rounding in `normalize_decimal_v2` so that the normalized `x1` (or `y1`) value used internally becomes exactly `0` even though the raw vault balance is nonzero (`program/src/math.rs` lines 106-116).
2. Any subsequent submitted transaction calling `Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn/Out`, or `SwapBaseInV2/OutV2` on this pool invokes `Processor::calc_take_pnl` with the zeroed `x1`/`y1` (`program/src/processor.rs` lines 1166-1173, 1494-1502, 1741-1748, 2342-2347).
3. Inside `calc_take_pnl`, `Calculator::calc_x_power` and the subsequent `y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` line divide by the zeroed value, causing `checked_div` to return `None` and the `.unwrap()` to panic (`program/src/processor.rs` line 208, `program/src/math.rs` lines 50-60).
4. The transaction aborts; because every fund-moving instruction for this pool depends on this same code path, no further deposits, withdrawals, or swaps can ever succeed against the pool, permanently locking all funds held in its vaults.

### Citations

**File:** program/src/processor.rs (L199-209)
```rust
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
```

**File:** program/src/processor.rs (L1148-1153)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1166-1173)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1494-1502)
```rust
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

**File:** program/src/processor.rs (L1741-1748)
```rust
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
```

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

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
