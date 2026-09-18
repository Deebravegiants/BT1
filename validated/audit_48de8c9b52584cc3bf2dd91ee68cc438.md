### Title
`calc_take_pnl` panics on unsigned subtraction underflow when normalized/restored decimal rounding causes computed PnL "value-preserving" amounts to exceed current pool amounts, freezing deposit/withdraw operations - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` guards its PnL computation with a k-value comparison performed in *native* (restored) decimal units, but then computes the value-preserving reference amounts `x2`/`y2` and subtracts them from the *normalized* (`sys_decimal_value`-scaled) current amounts `x1`/`y1` using `checked_sub(...).unwrap()`. Because `normalize_decimal_v2`/`restore_decimal` truncate on integer division, the two unit systems can diverge at the margin, allowing the guard to pass while `x2 > x1` or `y2 > y1` in the normalized space, causing an `unwrap()` panic that reverts the transaction — exactly the "value decreases → unsigned subtraction underflow → operation reverts" bug class described in the external report.

### Finding Description
`calc_take_pnl` is called from `process_deposit`, `process_withdraw`, and `process_withdrawpnl` — all reachable by ordinary users via a single instruction with no special privileges. [1](#0-0) 

The function first checks whether the current pool value (in native/restored decimal units) is at least the previously recorded value: [2](#0-1) 

If that check passes, it computes `x2` (a value-preserving reference amount at the current price, using `last_k`) and its counterpart `y2`, purely in the *normalized* `sys_decimal_value` unit space (`x1`, `y1`, `target.calc_pnl_x`, `target.calc_pnl_y`): [3](#0-2) 

It then subtracts these using unchecked-panic `unwrap()` on `checked_sub`:

```
let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
``` [4](#0-3) 

Mathematically, `x2 <= x1` and `y2 <= y1` follow algebraically only if the *same* current/last k values (in the *same* unit basis) used in the guard are the ones used to derive `x2`/`y2`. But the guard operates on `calc_pc_amount`/`calc_coin_amount` (obtained via `Calculator::restore_decimal`, which multiplies by `10^native_decimal` then integer-divides by `sys_decimal_value`) compared against native `pool_pc_amount`/`pool_coin_amount`, while `x2`/`y2` are derived directly from the normalized `target.calc_pnl_x`/`calc_pnl_y` and `x1`/`y1` via `Calculator::calc_x_power` (a separate integer-truncating computation: `last_x*last_y*current_x/current_y`). Both `normalize_decimal_v2` and `restore_decimal` truncate on division: [5](#0-4) 

Because two independently-truncated decimal conversions are compared and mixed across two different code paths (one for the guard, one for the actual sqrt/subtraction math), rounding at the margins of legitimate pool-state transitions (e.g., after a swap shifts the coin/pc ratio, or repeated small deposits/withdraws) can make the guard's inequality technically hold while the normalized-unit `x2`/`y2` slightly exceed `x1`/`y1`. This precisely mirrors the reported bug class: a legitimate state transition (a decreasing/shifting exchange-rate-like ratio) causes an unsigned subtraction to underflow, and since Rust's `unwrap()` on `None` panics (aborting the transaction, unlike Solidity's `revert` this still fails the entire instruction), every subsequent deposit/withdraw call on that pool would panic until the on-chain state realigns — if it ever does, since the same non-monotonic-truncation condition can recur every time the code path executes.

Notably, elsewhere in the same file the developers were aware of exactly this underflow risk and used `saturating_sub` defensively (`get_max_buy_size_at_price`, `get_max_sell_size_at_price`): [6](#0-5) 

but the equivalent protection is missing from `calc_take_pnl`'s `x1`/`y1` subtraction.

### Impact Explanation
A panic in `calc_take_pnl` aborts the entire `deposit`/`withdraw`/`withdrawpnl` instruction. Since this function is invoked on every deposit and withdraw, once the pool enters a state where the normalized-vs-restored decimal rounding causes `x2 > x1` or `y2 > y1`, all subsequent deposits and withdrawals for that pool will revert, permanently freezing LP funds in the vault (until/unless external factors happen to shift the ratio back), which matches the "permanent freezing of user or LP funds" impact criterion.

### Likelihood Explanation
This requires no attacker privilege — any user's deposit, withdraw, or swap sequence that shifts the coin/pc ratio and decimal-normalization rounding at the margin can trigger it. It is more likely with tokens that have differing/large decimal counts (`pc_decimals`/`coin_decimals` far from `sys_decimal_value`'s implied scale), where the truncation gap between `normalize_decimal_v2`/`restore_decimal` conversions is largest. It is a rounding-edge-case bug rather than a directly and deterministically attacker-triggerable-in-one-tx exploit, so likelihood is low-to-moderate, consistent with Medium severity classification in the referenced analog report.

### Recommendation
Replace the unchecked `unwrap()` subtractions in `calc_take_pnl` with saturating or checked-with-graceful-fallback arithmetic (e.g., `saturating_sub`, mirroring `get_max_buy_size_at_price`/`get_max_sell_size_at_price`), and/or unify the unit basis used for the guard comparison and the `x2`/`y2` derivation so that the mathematical invariant `x2 <= x1`, `y2 <= y1` is guaranteed to hold in the same decimal space before the subtraction is performed.

### Proof of Concept
Conceptually:
1. A pool has `target.calc_pnl_x`/`calc_pnl_y` recorded from a prior deposit/withdraw at one native-decimal ratio.
2. A subsequent swap (`process_swap_base_in`/`_out`) shifts `total_pc_without_take_pnl`/`total_coin_without_take_pnl` such that, after `normalize_decimal_v2` truncation, the guard `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` (computed via `restore_decimal`) passes.
3. A user then calls `deposit` or `withdraw`, invoking `calc_take_pnl`; `Calculator::calc_x_power` and `integer_sqrt()` compute `x2` in the normalized unit space using truncated inputs, producing `x2` slightly larger than `x1` (or `y2` slightly larger than `y1`) due to the independent truncation paths.
4. `x1.checked_sub(x2).unwrap()` (or the `y1` equivalent) panics, aborting the deposit/withdraw instruction, and every future deposit/withdraw on the same pool state repeats the same panic, freezing the vault.

### Citations

**File:** program/src/processor.rs (L167-214)
```rust
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
        // calc pnl
        let mut delta_x: u128;
        let mut delta_y: u128;
        let calc_pc_amount = Calculator::restore_decimal(
            target.calc_pnl_x.into(),
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let calc_coin_amount = Calculator::restore_decimal(
            target.calc_pnl_y.into(),
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
            // last k is
            // let last_k: u128 = (target.calc_pnl_x as u128).checked_mul(target.calc_pnl_y as u128).unwrap();
            // current k is
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
```

**File:** program/src/math.rs (L96-116)
```rust
    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }

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

**File:** program/src/math.rs (L252-267)
```rust
    pub fn get_max_buy_size_at_price(price: u64, x: u128, y: u128, amm: &AmmInfo) -> u64 {
        // max_size = x / (1.0025 * price) - y
        let price_with_fee = U128::from(price)
            .checked_mul(U128::from(
                amm.fees.trade_fee_denominator + amm.fees.trade_fee_numerator,
            ))
            .unwrap()
            .checked_div(U128::from(amm.fees.trade_fee_denominator))
            .unwrap();
        let mut max_size = U128::from(x)
            .checked_mul(amm.sys_decimal_value.into())
            .unwrap()
            .checked_div(price_with_fee)
            .unwrap();
        max_size = max_size.saturating_sub(y.into());
        Self::to_u64(max_size.as_u128()).unwrap()
```
