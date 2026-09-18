### Title
Attacker-Manipulated Swap Ratio Causes Unchecked Arithmetic Underflow Panic in PnL Accounting, Permanently Freezing Deposit/Withdraw - (`program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` computes the amount of accumulated PnL to "skim" from the pool on every `Deposit`, `Withdraw`, and `WithdrawPnl` call. It relies on the assumption that the newly computed geometric-mean invariant point `(x2, y2)` is always `<= (x1, y1)` (the current normalized reserves), and then does `x1.checked_sub(x2).unwrap()` / `y1.checked_sub(y2).unwrap()` without ever validating that assumption or handling the `None` case. The only upstream guard is a coarse `K_current >= K_target` invariant check, which does not guarantee `x2 <= x1` and `y2 <= y1` individually after a large one-sided price swing produced by ordinary, permissionless `SwapBaseIn`/`SwapBaseOut` calls.

### Finding Description
`calc_take_pnl` is invoked from `process_deposit`, `process_withdraw`, and `process_withdrawpnl`: [1](#0-0) [2](#0-1) 

Inside it, the geometric-mean rebalancing point is computed and then subtracted from the live normalized reserves without a bounds check: [3](#0-2) 

The only gate before entering this branch is: [4](#0-3) 

This only compares the *product* `x1*y1` against the stored target product; it says nothing about the relative magnitude of `x1` vs `x2` or `y1` vs `y2` individually. Because `x2 = sqrt(last_x*last_y*x1/y1)` and `y2 = x2*y1/x1`, a sufficiently large, legitimate, permissionless swap (`process_swap_base_in`/`process_swap_base_out`, reachable by any unprivileged trader with attacker-chosen `amount_in`/`amount_out`) that shifts the pool's price ratio far from the ratio implied by the stored `target_orders.calc_pnl_x`/`calc_pnl_y` can produce `x2 > x1` (or `y2 > y1`) even while the coarse product check still passes (e.g., fees have nudged `K` slightly above the stored target `K`, but the price ratio moved enormously). In that case `x1.checked_sub(x2)` (or `y1.checked_sub(y2)`) returns `None`, and the `.unwrap()` panics, aborting the whole transaction.

Because the panic occurs before `target_orders.calc_pnl_x`/`calc_pnl_y` is ever updated, the on-chain state that produced the panic condition (skewed reserves vs. stale `calc_pnl_x`/`calc_pnl_y`) is left completely unchanged. Every subsequent `Deposit` or `Withdraw` call re-enters the exact same code path with the exact same inputs and panics again — deterministically and permanently, since normal callers cannot alter `target_orders.calc_pnl_x`/`calc_pnl_y` except through this same code path.

### Impact Explanation
Once triggered, `process_deposit` and `process_withdraw` (and `process_withdrawpnl`) become permanently unusable for that pool because they all call `calc_take_pnl` with the same stale, non-updatable `target_orders` state. This constitutes a permanent freeze of LP funds already deposited in the pool (LPs can never redeem their LP tokens via `Withdraw` again), qualifying as High severity impact under "permanent freezing of user or LP funds."

### Likelihood Explanation
The triggering condition only requires standard `SwapBaseIn`/`SwapBaseOut`/`SwapBaseInV2`/`SwapBaseOutV2` calls with attacker-chosen amounts to push the pool's coin/pc ratio far away from the ratio recorded in `target_orders.calc_pnl_x`/`calc_pnl_y` (which is only updated on successful Deposit/Withdraw/WithdrawPnl calls, i.e., can lag well behind the live swap-driven price). No privileged signer, off-chain component, or malicious validator is required — a single unprivileged trader with a normal swap transaction can reach this condition, then any subsequent permissionless `Deposit` or `Withdraw` call panics.

### Recommendation
Replace the unchecked `.unwrap()` calls on `x1.checked_sub(x2)` and `y1.checked_sub(y2)` in `calc_take_pnl` (`program/src/processor.rs:213-214`) with explicit checks that gracefully clamp `delta_x`/`delta_y` to zero (or return a typed `AmmError`) whenever `x2 > x1` or `y2 > y1`, instead of allowing the process to panic on an unrepresentable subtraction. This prevents an attacker-influenced price ratio from permanently bricking `Deposit`/`Withdraw` for a pool.

### Proof of Concept
1. Attacker (or anyone) creates/uses an existing pool and performs a very large, one-sided `SwapBaseIn`/`SwapBaseOut` (permissionless, single transaction, attacker-chosen `amount_in`) that shifts the coin/pc reserve ratio far from the ratio encoded in `target_orders.calc_pnl_x`/`calc_pnl_y`, while keeping the pool's `K` slightly above the stored target `K` (satisfied naturally by trading fees) so the guard at `processor.rs:190-192` still passes.
2. Any user then calls `Deposit` or `Withdraw`; `calc_take_pnl` computes `x2`/`y2` via `calc_x_power`/`integer_sqrt`, and because of the skewed ratio, `x2 > x1` or `y2 > y1`.
3. `x1.checked_sub(x2).unwrap()` (or the `y` equivalent) panics, aborting the transaction. Since `target_orders` state was never persisted, the same panic recurs on every future `Deposit`/`Withdraw` attempt on that pool, permanently freezing LP funds.

### Citations

**File:** program/src/processor.rs (L190-192)
```rust
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L199-214)
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

            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
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
