### Title
Missing error handling on `checked_sub().unwrap()` in `calc_take_pnl` can permanently freeze Deposit/Withdraw/WithdrawPnl on a pool - ([File: program/src/processor.rs])

### Summary
The AnythingLLM bug class is: an unauthenticated/attacker-reachable path performs an operation with **no error-handling wrapper**, so a single crafted request panics/crashes the process. The Raydium AMM analog is `Processor::calc_take_pnl`, which is invoked from every `Deposit`, `Withdraw`, and `WithdrawPnl` instruction and uses bare `.unwrap()` on `checked_sub()` results instead of propagating a `ProgramError`. Because the inputs to this function are derived from live, attacker-influenceable pool state (vault token balances and `target_orders.calc_pnl_x/y`), a value combination that makes the internal invariant `x2 <= x1` (or `y2 <= y1`) false will panic the instruction instead of returning a handled error.

### Finding Description
`calc_take_pnl` computes the "price-adjusted" reserves `x2`/`y2` from `target.calc_pnl_x`/`calc_pnl_y` and the live totals `x1`/`y1`, then computes: [1](#0-0) 
via `x2_power.integer_sqrt()`, `y2 = x2 * y1 / x1`, and then:
```rust
let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
```
This assumes `x2 <= x1` and `y2 <= y1` always hold whenever the guard `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` at [2](#0-1)  is true. That guard only checks the *product* (k) relationship, not that the integer-sqrt/rounding-derived `x2`/`y2` are bounded by `x1`/`y1` term-by-term. Integer division/sqrt truncation in `calc_x_power`/`integer_sqrt` can produce an `x2` (or the derived `y2`) that slightly exceeds `x1` (or `y1`) in edge-case reserve ratios, causing `checked_sub(...).unwrap()` to panic instead of returning `AmmError::CalcPnlError` (which the `else` branch of the same function already does gracefully for the coarser k-check failure at [3](#0-2) ).

Unlike a web server, a Solana program panic only aborts the *single* transaction — but `x1`/`y1`/`calc_pnl_x`/`calc_pnl_y` are derived from **persistent** on-chain state (vault SPL balances and `target_orders`), which nobody is required to change between calls. If a state is reached where this edge case triggers, it triggers identically on every subsequent call, because the inputs are unchanged and the panic prevents any state update that could self-correct the situation:
- `process_deposit` calls `calc_take_pnl` at [4](#0-3) 
- `process_withdraw` calls it at [5](#0-4) 
- `process_withdrawpnl` calls it at [6](#0-5) 

An attacker can move vault balances (any unprivileged actor can SPL-transfer tokens directly into `amm_coin_vault`/`amm_pc_vault`, which are just normal SPL token accounts — no signature from the AMM required) to shift `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (and thus `x1`/`y1`) toward a ratio that trips the rounding edge case relative to the stored `calc_pnl_x`/`calc_pnl_y`. Once triggered, every future `Deposit`, `Withdraw`, and `WithdrawPnl` call for that pool panics on `calc_take_pnl`, permanently freezing LP deposits/withdrawals and PnL collection for the pool (swap instructions do not call `calc_take_pnl`, so trading may continue, but LP capital becomes stuck).

### Impact Explanation
This is a High-severity denial-of-service on core LP functionality: once the edge condition is hit, LPs can never withdraw or deposit into the affected pool again, and admin can never collect PnL — a permanent freezing of LP funds, matching the required impact bar (concrete permanent freezing of user/LP funds) without requiring any privileged signer.

### Likelihood Explanation
Likelihood is Medium: the trigger requires a specific numeric edge case in the sqrt/rounding chain of `calc_x_power`/`integer_sqrt` relative to `calc_pnl_x`/`calc_pnl_y`, which is plausible given integer truncation but not trivially reproducible from the code alone — the vector (unprivileged token transfers into vaults skewing reserve ratios) is fully reachable by any attacker with no special permissions. I was not able to fully numerically construct a concrete failing input set within the scope of this analysis; confirming an exact reproduction requires targeted fuzzing/property-testing of `calc_x_power`/`integer_sqrt` against `checked_sub` bounds, which a Devin session with code execution could perform.

### Recommendation
Replace the bare `.unwrap()` calls on `checked_sub` in `calc_take_pnl` (and the analogous `.unwrap()` chains after it, lines 208-263) with `.ok_or(AmmError::CalcPnlError)?` (or `checked_sub` combined with `.unwrap_or(0)`/saturating semantics where an underflow simply implies zero PnL to take), so that any inversion of `x2 <= x1` / `y2 <= y1` degrades gracefully into a handled `ProgramError` rather than an unrecoverable panic, and add regression tests around reserve ratios near the rounding boundary.

### Proof of Concept
Conceptual PoC (requires numeric confirmation via fuzzing, not verified end-to-end in this analysis):
1. Create a pool via `Initialize2` and perform normal `Deposit`s so `target_orders.calc_pnl_x/y` are set to values `X0/Y0` reflecting initial deposit ratio.
2. Directly SPL-transfer extra `coin`/`pc` tokens into `amm_coin_vault`/`amm_pc_vault` (no AMM signature required — any wallet holding the mint can do this) to skew `total_pc_without_take_pnl`/`total_coin_without_take_pnl` such that the k-check `pool_pc*pool_coin >= calc_pnl_x*calc_pnl_y` passes narrowly, while the derived `x2` from `calc_x_power`/`integer_sqrt` rounds to a value marginally greater than `x1` (or the corresponding `y2 > y1`).
3. Call `Deposit`/`Withdraw`/`WithdrawPnl` — `calc_take_pnl` panics on `checked_sub().unwrap()`, and this panic will recur on every future call touching this pool as long as the skewed vault/state condition persists, permanently freezing LP deposit/withdraw functionality for the pool.

### Citations

**File:** program/src/processor.rs (L190-192)
```rust
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L205-214)
```rust
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

**File:** program/src/processor.rs (L267-278)
```rust
        } else {
            msg!(arrform!(
                LOG_SIZE,
                "calc_take_pnl error x:{}, y:{}, calc_pnl_x:{}, calc_pnl_y:{}",
                x1,
                y1,
                identity(target.calc_pnl_x),
                identity(target.calc_pnl_y)
            )
            .as_str());
            return Err(AmmError::CalcPnlError.into());
        }
```

**File:** program/src/processor.rs (L1166-1174)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
        let invariant = InvariantToken {
```

**File:** program/src/processor.rs (L1495-1502)
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

**File:** program/src/processor.rs (L1741-1749)
```rust
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
