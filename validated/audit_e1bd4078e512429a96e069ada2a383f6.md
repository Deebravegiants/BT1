### Title
Unhandled arithmetic underflow panic in `calc_take_pnl` can permanently freeze pool withdrawals - (File: `program/src/processor.rs`)

### Summary
The CVE describes a MySQL optimizer bug where a normal (if privileged) query causes the server to hang or crash — a computation-driven denial of service. The reachable analog in this AMM program is `Processor::calc_take_pnl`, which performs an integer-sqrt/rounding computation with `unwrap()`-only subtraction. If reserve/PnL state ever drifts such that the rounded "after-pnl" value exceeds the "before" value, the subtraction panics, and because this function runs unconditionally on the withdraw path, the panic recurs on every future call — a persistent, program-level DoS of LP fund withdrawal rather than a one-off failed transaction.

### Finding Description
`calc_take_pnl` computes `x2` (the coin/pc reserve after PnL is skimmed) via a chained fixed-point calculation using `integer_sqrt()` and floor/ceil integer division, then does: [1](#0-0) 

`x1`/`y1` come from `Calculator::normalize_decimal_v2`, which itself performs `checked_mul`/`checked_div` floor rounding, and `target.calc_pnl_x`/`calc_pnl_y` are persisted on-chain state updated after every withdraw using the same style of chained rounding: [2](#0-1) 

The guard at line 190 only checks that `pool_pc * pool_coin >= calc_pc * calc_coin` using the *raw* (non-decimal-normalized) reserve amounts, not the normalized/rounded `x1`/`y1` values actually used to compute `x2`/`y2`: [3](#0-2) 

Because `x1` and `x2` are derived through independent, multi-step, lossy integer arithmetic (decimal normalization, `U256` multiply/divide, integer square root), there is no algebraic guarantee that `x2 <= x1` in all cases the line-190 check permits — only that the *unnormalized* invariant holds. When `x2` (or `y2`) ends up marginally larger than `x1` (or `y1`) due to rounding drift, `x1.checked_sub(x2).unwrap()` (or the `y1` analog) panics: [4](#0-3) 

`calc_take_pnl` is invoked unconditionally by `process_withdraw` whenever `amm.status != AmmStatus::WithdrawOnly`, using the pool's persisted `target_orders.calc_pnl_x/y` and current vault balances — state that any subsequent LP holder's withdraw call will re-derive identically: [5](#0-4) 

Once the on-chain state reaches a configuration that triggers this panic, **every** future `Withdraw` instruction against that pool will deterministically panic and abort, because the inputs (`amm` reserves, `target_orders.calc_pnl_x/y`) are unchanged by the failed transaction and cannot be corrected by any unprivileged instruction.

### Impact Explanation
A panic inside an instruction handler aborts only that single transaction on Solana, so on its own this is not equivalent to crashing a shared server process. However, because the panicking computation is deterministic and depends only on persisted pool state that ordinary swap/deposit/withdraw activity mutates over time, reaching the bad state makes withdrawal permanently and unconditionally unavailable for that pool — a `permanent freezing of user or LP funds`, which is explicitly in the accepted impact set for this scan.

### Likelihood Explanation
The precondition is a sequence of normal swaps/deposits/withdraws that drift `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and the persisted `calc_pnl_x`/`calc_pnl_y` such that the decimal-normalized `x2 > x1` (or `y2 > y1`) despite the raw-reserve invariant check at line 190 passing. This depends on the specific decimals/fee configuration of a pool and on many repeated operations to accumulate rounding drift; I could not execute the arithmetic to produce a concrete numeric trigger with the tools available, so likelihood should be treated as plausible-but-unconfirmed rather than proven with a working exploit trace.

### Recommendation
Replace the bare `.unwrap()` calls on `x1.checked_sub(x2)` / `y1.checked_sub(y2)` in `calc_take_pnl` with saturating subtraction or an explicit `x2.min(x1)` clamp (and equivalent for `y`), returning zero PnL delta instead of panicking when rounding makes the after-pnl value exceed the before-pnl value. Additionally, perform the invariant check used to decide whether to take PnL using the same normalized (`x1`,`y1`) values that are later subtracted, not the raw un-normalized reserve amounts.

### Proof of Concept
Concrete PoC values (mint decimals, fee numerator/denominator, and a specific sequence of swap/deposit/withdraw amounts) that force `x2 > x1` after normalization could not be derived without executing the fixed-point arithmetic in `Calculator::normalize_decimal_v2`, `calc_x_power`, and `integer_sqrt`. This would require running the program's math functions (e.g., in a Rust unit test or with the actual crate compiled) to enumerate a reserve/decimals/fee combination that passes the raw-reserve check at `program/src/processor.rs:190-192` yet yields `x2 > x1` at `program/src/processor.rs:213`. I was not able to execute code with the tools available in this session, so this PoC step remains conceptual rather than empirically verified.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
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

**File:** program/src/processor.rs (L1740-1749)
```rust
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

**File:** program/src/processor.rs (L1818-1838)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```
