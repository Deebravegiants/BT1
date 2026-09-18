### Title
Reachable integer overflow panic in `Calculator::calc_x_power` permanently freezes LP deposit/withdraw/pnl paths - ([File: program/src/math.rs])

### Summary
The reported swift-nio-http2 bug class is a mishandled variable-length integer computation that panics/crashes instead of gracefully erroring when values grow too large. The Raydium AMM program has an analogous pattern: nearly all arithmetic in `Calculator` (program/src/math.rs) uses `checked_mul()/checked_pow()/checked_div().unwrap()` chains rather than propagating an error. In `Calculator::calc_x_power`, three large `U256` values are multiplied together before dividing, and this function is invoked from `Processor::calc_take_pnl`, which itself is called on every `Deposit`, `Withdraw`, and `WithdrawPnl` instruction. If the multiplication overflows `U256`, the `.unwrap()` panics, aborting the transaction — and because the inputs are derived from persistent, attacker-influenced pool state (`TargetOrders.calc_pnl_x/y` and normalized vault balances), the overflow condition can become permanent, i.e. every future `Deposit`/`Withdraw`/`WithdrawPnl` call on that pool panics forever, freezing LP funds and any withdrawable PnL in the pool while `Initialize2` accepted attacker-supplied decimals with no cross-mint sanity bound.

### Finding Description
`Calculator::calc_x_power` (program/src/math.rs:50-60) computes:
```
let x_power = last_x.checked_mul(last_y).unwrap()
    .checked_mul(current_x).unwrap()
    .checked_div(current_y).unwrap();
``` [1](#0-0) 

This is called from `Processor::calc_take_pnl` (program/src/processor.rs:167-281), passing `target.calc_pnl_x`, `target.calc_pnl_y` (persisted pool state from `TargetOrders`) and `x1`, `y1` (the currently normalized pc/coin vault totals): [2](#0-1) 

`calc_take_pnl` is invoked unconditionally on `process_deposit` (processor.rs:1166), `process_withdraw` (processor.rs:1741, unless status is `WithdrawOnly`), and `process_withdrawpnl` (processor.rs:1495) — all reachable by any unprivileged LP/swapper/withdrawer with a single transaction: [3](#0-2) [4](#0-3) 

`x1`/`y1` and `target.calc_pnl_x/y` are produced by `Calculator::normalize_decimal_v2` (math.rs:106-116), which multiplies the raw token amount by `amm.sys_decimal_value` (up to `10^19`, since `sys_decimal_value = 10^max(pc_decimals, coin_decimals)` set at `AmmInfo::initialize`, state.rs:737-745) and divides by `10^native_decimal`: [5](#0-4) [6](#0-5) 

Because `Initialize2` accepts arbitrary SPL mints supplied by the pool creator (an unprivileged action) with no restriction that decimals be low/typical, and vault balances can approach `u64::MAX`, `normalize_decimal_v2` outputs can approach the top of the `U128` range (~1.8×10¹⁹ × 10¹⁹ ≈ 1.8×10³⁸, close to `U128::MAX` ≈ 3.4×10³⁸). When these near-maximal `x1`/`y1` values (and the correspondingly large stored `calc_pnl_x`/`calc_pnl_y`) are widened to `U256` and multiplied twice in `calc_x_power` (`last_x * last_y * current_x`), the intermediate product can exceed `U256::MAX` (~1.15×10⁷⁷), causing `checked_mul` to return `None` and the subsequent `.unwrap()` to panic.

Because `calc_pnl_x`/`calc_pnl_y` are pool state that persists between transactions and grows through ordinary deposit/withdraw activity (and can be driven toward the overflow boundary via a pool created with low-decimal, high-supply mints and large deposits — all reachable through `Initialize2` + `Deposit`, both unprivileged), once the overflow threshold is crossed the panic recurs on every subsequent `Deposit`/`Withdraw`/`WithdrawPnl` call for that pool, since `calc_take_pnl` runs unconditionally at the start of those handlers with the same growing state. This is a durable failure, not a one-off — analogous to the swift-nio HPACK bug where a specially crafted (here: dimensioned) input causes the parser/calculator to crash instead of returning a checked error.

### Impact Explanation
If triggered, `calc_take_pnl` panics for every future `Deposit`, `Withdraw`, and `WithdrawPnl` call on the affected pool (Solana `SwapBaseIn`/`SwapBaseOut`, whose code paths inspected do not call `calc_take_pnl`, would continue to succeed, letting the pool balance drift further while LP/PnL functions remain permanently unusable). This permanently freezes LP principal (no LP can withdraw their share via `Withdraw`) and admin PnL (`WithdrawPnl` also broken), matching the "permanent freezing of user or LP funds" acceptance criterion.

### Likelihood Explanation
Triggering the exact overflow boundary requires careful selection of mint decimals (both attacker-controlled via a self-created pool at `Initialize2`) and sizable deposits growing `calc_pnl_x`/`calc_pnl_y` toward the `U256` overflow threshold; this needs several transactions (pool creation + deposits) rather than a single crafted transaction, and precise numeric conditions are not proven end-to-end without running the arithmetic (I could not execute code to confirm the exact overflow threshold is reachable using realistic `u64` vault balances). This uncertainty lowers confidence versus a directly provable single-transaction exploit, but the code path itself (unchecked-then-unwrap arithmetic on attacker-influenced state, reachable purely through unprivileged instructions) is real and matches the reported bug class.

### Recommendation
- Replace `.unwrap()` calls in `Calculator::calc_x_power` (and the broader `Calculator`/`InvariantToken`/`InvariantPool` arithmetic in program/src/math.rs) with proper `checked_*` propagation returning `AmmError` instead of panicking.
- Bound `sys_decimal_value`/decimals accepted at `Initialize2` to a safe range, and/or use wider intermediate types (e.g. `U512`) or rescale before multiplying three large factors together in `calc_x_power`.
- Add regression tests exercising near-`u64::MAX` vault balances combined with extreme (0 and high) decimals to ensure `calc_take_pnl` degrades gracefully (returns an error) rather than panicking.

### Proof of Concept
Not independently executed. Conceptual construction: create a pool via `Initialize2` using coin/pc mints with decimals chosen to maximize `sys_decimal_value` (e.g., one mint at 0 decimals, other at 19) and deposit amounts approaching `u64::MAX`; repeat `Deposit` calls to grow `TargetOrders.calc_pnl_x/y` toward the `U256` overflow boundary in `Calculator::calc_x_power`; once crossed, any subsequent `Deposit`/`Withdraw`/`WithdrawPnl` call panics inside `Processor::calc_take_pnl`, permanently blocking those instructions for the pool. Precise numeric parameters to guarantee overflow were not verified by execution and would need to be validated with a local test harness (e.g., the existing `test_calc_take_pnl`/`test_calc_pnl_precision` tests in processor.rs as a starting point).

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

**File:** program/src/math.rs (L106-116)
```rust
    pub fn normalize_decimal_v2(val: u64, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = ret_mut
            .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        ret
    }
```

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

**File:** program/src/state.rs (L737-745)
```rust
        if pc_decimals > coin_decimals {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(pc_decimals.try_into().unwrap())
                .unwrap();
        } else {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(coin_decimals.try_into().unwrap())
                .unwrap();
        }
```
