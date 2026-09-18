### Title
Reachable panic (unwrap-on-None) via division-by-zero in `Processor::calc_take_pnl` / `Calculator::calc_x_power` can permanently brick Deposit, Withdraw and WithdrawPnl for a pool - (File: `program/src/processor.rs`)

### Summary
The external report describes a NULL-pointer dereference in Open Babel's `CacaoFormat::SetHilderbrandt` caused by an unguarded dereference reachable from crafted input (CWE-404/476 — improper resource handling leading to a crash). The closest reachable analog in this Solana program is the same bug *class* — an unguarded, panicking operation on attacker-influenceable state — manifested as `.unwrap()` calls on `checked_div`/`checked_sub` results inside the pnl-accounting path that is invoked from `Deposit`, `Withdraw`, and `WithdrawPnl`, all of which are reachable by any unprivileged liquidity provider or swapper in a single transaction.

### Finding Description
`Processor::calc_take_pnl` (`program/src/processor.rs:167-281`) computes: [1](#0-0) 
which calls `Calculator::calc_x_power` (`program/src/math.rs:50-60`): [2](#0-1) 
and then computes `y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` at [3](#0-2) 

`x1` and `y1` are the normalized total pc/coin reserves passed in by the caller (`x1 = normalize_decimal_v2(total_pc_without_take_pnl, ...)`), and `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are derived from live vault balances minus `need_take_pnl_pc`/`need_take_pnl_coin`: [4](#0-3) 

Both `checked_div` and `checked_mul` return `Option`, and every arithmetic step here is `.unwrap()`ed with no error propagation — an exact `x1 == 0` state causes `checked_div(x1)` to return `None`, and `.unwrap()` on `None` panics (`Some`/`None` here plays the analogous role of Open Babel's null-checked pointer that is dereferenced without validation). The branch guard that decides whether to enter this code path, [5](#0-4) 
only compares `pool_pc_amount * pool_coin_amount` against `calc_pc_amount * calc_coin_amount`; it does not check that `x1`/`y1` (used later as divisors) are non-zero. Because `target.calc_pnl_x`/`calc_pnl_y` (the `calc_pc_amount`/`calc_coin_amount` terms) are zero-initialized on `TargetOrders::default()` / at pool creation (uninitialized account data), and can also be driven toward zero over the life of a pool via repeated pnl-taking/withdraw cycles, the guard `0 >= 0` is satisfiable while `x1` (pc reserves net of un-swept pnl) is simultaneously zero — leading straight into the `checked_div(x1)` panic.

This same `calc_take_pnl` function is invoked from three unprivileged, permissionless entry points:
- `process_deposit` (`program/src/processor.rs:1166-1173`) [6](#0-5) 
- `process_withdrawpnl` (`program/src/processor.rs:1494-1502`) [7](#0-6) 
- `process_withdraw` (`program/src/processor.rs:1737-1749`) [8](#0-7) 

Because `total_pc_without_take_pnl`/`total_coin_without_take_pnl` reflect the AMM's *persistent on-chain state* (vault balances vs. accrued `need_take_pnl_*`), once a pool reaches the zero-reserve-net-of-pnl condition, every subsequent call to Deposit/Withdraw/WithdrawPnl against that pool will deterministically panic and abort — this is not a one-off failed transaction but a state-dependent, repeatable crash for as long as the pool remains in that state.

### Impact Explanation
A Solana program panic aborts only the offending transaction (the runtime does not "crash," unlike the Open Babel process-level NULL deref), so this does not directly enable fund theft. However, if a pool's vaults reach the described state (net pc or coin reserves equal to the currently un-swept `need_take_pnl_*` amount, while `target.calc_pnl_x`/`calc_pnl_y` are simultaneously zero or otherwise satisfy the guard), Deposit, Withdraw, and WithdrawPnl for that pool become permanently unusable — a persistent denial of service that freezes LP funds already deposited in the pool (they can no longer be withdrawn through the normal instruction path). This matches the "permanent freezing of user or LP funds" impact bar in scope.

### Likelihood Explanation
The precise state required (`x1 == 0` while the pnl-guard is satisfied) is a narrow, pool-lifecycle-dependent condition rather than something a single crafted instruction can trivially force in isolation — it depends on the pool's `TargetOrders.calc_pnl_x/calc_pnl_y` and `AmmInfo.state_data.need_take_pnl_*` bookkeeping converging with vault balances over a sequence of trades/deposits/withdrawals. I was not able to fully enumerate, within the available analysis, a guaranteed single-transaction sequence of Swap/Deposit/Withdraw calls that forces this exact convergence (this would require deeper simulation of the pnl accounting across multiple state transitions than is feasible from static code review alone). This is best treated as a plausible but unconfirmed likelihood — the root-cause defect (unchecked `unwrap()` on `checked_div`/`checked_mul` in `calc_take_pnl`/`calc_x_power` with reserve-derived divisors) is concretely present and reachable from unprivileged instructions, but a fully worked, deterministic PoC transaction sequence could not be constructed with confidence in this pass.

### Recommendation
Replace the chained `.unwrap()` calls in `Calculator::calc_x_power` and in `Processor::calc_take_pnl`'s `y2`/`delta_x`/`delta_y` computation with `checked_*` combinators that propagate `AmmError::CheckedDivOverflow`/`CheckedMulOverflow` instead of panicking, and add an explicit guard rejecting the pnl-take path (returning a defined error) when `x1 == 0` or `y1 == 0`, mirroring the existing `checked_sub` guards already used elsewhere in `calc_total_without_take_pnl_no_orderbook`.

### Proof of Concept
Not constructed with confidence — deriving a concrete, minimal transaction sequence that drives a pool into the `x1 == 0`-with-satisfied-guard state requires simulating the pnl bookkeeping (`need_take_pnl_pc/coin`, `target.calc_pnl_x/y`) across multiple Swap/Deposit/Withdraw calls, which exceeds what could be verified from static code reading alone in this pass. The root-cause line-level defect is cited above; a background engineering/fuzzing session against the program's Deposit/Withdraw/WithdrawPnl/Swap state machine would be needed to confirm reachability with concrete numeric parameters.

### Citations

**File:** program/src/processor.rs (L190-192)
```rust
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L199-208)
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

**File:** program/src/processor.rs (L1737-1749)
```rust
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

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```
