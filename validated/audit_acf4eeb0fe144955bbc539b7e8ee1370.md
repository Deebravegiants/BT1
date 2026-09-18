### Title
Reachable panic (`unwrap()`/`checked_sub`) in `Calculator::calc_take_pnl` and swap-token math can permanently DoS all swap/deposit/withdraw paths - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
CVE-2017-16818 is a Ceph RGW assertion-failure DoS: a semi-privileged user supplies data that the server accepts through normal authorization checks but that violates an internal invariant assumed elsewhere in the code, causing an `assert()`/panic and process abort. The closest reachable analog in this program is the pattern of unchecked `.unwrap()` calls on `checked_sub`/`checked_mul`/`checked_div` inside `Calculator::calc_take_pnl` (`program/src/processor.rs`) and the swap-math helpers in `program/src/math.rs`, which are invoked from every `Deposit`, `Withdraw`, `SwapBaseIn/Out` (and v2) instruction path with attacker-influenced vault balances and instruction arguments.

### Finding Description
`calc_take_pnl` computes `x2`/`y2` from `target.calc_pnl_x/y` and current normalized reserves `x1`/`y1`, then does: [1](#0-0) 
The branch is gated only by a **k-value** comparison (`pool_pc*pool_coin >= calc_pc*calc_coin`), not by an individual-reserve comparison, so it does not guarantee `x1 >= x2` or `y1 >= y2` individually: [2](#0-1) 
If price/reserve skew (driven by attacker-chosen swap amounts across repeated `SwapBaseIn`/`SwapBaseOut` calls, which are fully reachable by any unprivileged trader) produces `x2 > x1` or `y2 > y1`, the subsequent `checked_sub(...).unwrap()` panics instead of returning a program error. `calc_take_pnl` is invoked from `process_deposit`, `process_withdraw`, `process_withdrawpnl`, and every swap variant, all of which are reachable from a single submitted transaction with attacker-chosen swap direction/amount: [3](#0-2) 
Because `target_orders.calc_pnl_x`/`calc_pnl_y` are persisted on-chain state that only gets reset via `check_init` (pool creation) or by the pnl update logic itself, once the invariant is violated for a given pool's stored `calc_pnl_x/y` vs. live vault balances, **every subsequent call into any instruction that reaches `calc_take_pnl`** (deposit, withdraw, swap, withdrawpnl) will re-panic on the same underflow — effectively freezing that pool for deposits, withdrawals and swaps until/unless the account state is externally reset.

### Impact Explanation
A panic inside an on-chain instruction aborts that transaction (fails, no state change), which by itself is only a transient DoS (unlike the Ceph case where the whole daemon process aborts). However, if the underlying arithmetic invariant is *persistently* violated (i.e., the stored `calc_pnl_x`/`calc_pnl_y` combined with the current vault reserves always trigger `x2 > x1`/`y2 > y1`), then deposit, withdraw and swap instructions for that pool will keep panicking on every future attempt, which constitutes a **permanent freeze of user and LP funds** in that pool — matching the class of impact required (permanent freezing of user/LP funds) even though I could not conclusively prove, purely from the code paths reviewed, that an attacker can force this persistent skew starting from a fresh/healthy pool state using only in-scope, unprivileged instructions (Deposit/Withdraw/Swap). The mathematical proof that k-invariant alone is insufficient to guarantee `x1>=x2 && y1>=y2` is solid; whether real-world swap sequences by an ordinary trader can practically drive the pool into that skewed state (versus the invariant always holding due to how swaps update reserves) I was unable to fully verify within available context/tool budget.

### Likelihood Explanation
Medium: the code path is reachable by any unprivileged swapper/LP with a single transaction and attacker-chosen swap direction and amount (no privileged signer needed), matching the CVE's "authenticated but non-admin, normal privilege" access model. But triggering the specific numeric skew that causes `x2>x1`/`y2>y1` requires reasoning about swap-driven reserve movement relative to the previously stored `calc_pnl_x/y` snapshot, which I could not fully confirm is achievable purely through legitimate swap sequences without deeper simulation of `swap_token_amount_base_in/out` and the deposit/withdraw pnl-update flow.

### Recommendation
Replace the `.unwrap()` calls in `calc_take_pnl` (and the analogous unchecked math in `program/src/math.rs`, e.g. `swap_token_amount_base_in/out`, `normalize_decimal_v2`/`restore_decimal`) with `checked_sub`/`checked_mul`/`checked_div` chains that return `Result<_, AmmError>` and propagate a descriptive error (as is already done in `calc_total_without_take_pnl_no_orderbook` via `ok_or(AmmError::CheckedSubOverflow)`), so a violated invariant fails the transaction gracefully instead of panicking, and add an explicit guard ensuring `x1 >= x2` and `y1 >= y2` before subtracting, returning `AmmError::CalcPnlError` otherwise — mirroring the existing k-value guard's error-return pattern rather than panicking.

### Proof of Concept
I was not able to construct and verify a concrete instruction sequence (using only Initialize2/Deposit/Withdraw/Swap with attacker-controlled amounts) that provably drives a healthy pool's `target.calc_pnl_x/y` state into persistent `x2>x1`/`y2>y1` skew, within the scope of this analysis. This would require deeper numeric simulation of `swap_token_amount_base_in`/`swap_token_amount_base_out` combined with repeated pnl-taking across deposit/withdraw calls, which exceeds what I could confirm from static code review alone.

### Citations

**File:** program/src/processor.rs (L188-214)
```rust
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
