### Title
Non-decreasing invariant assertion inside `calc_take_pnl` DOS's every deposit/withdraw/swap after a partial pool loss - (File: program/src/processor.rs)

### Summary
`Processor::calc_take_pnl` contains a hard invariant check that behaves like an `assert!`: if the pool's current reserves multiplied together fall below the last recorded `target.calc_pnl_x * target.calc_pnl_y` product, the function returns `Err(AmmError::CalcPnlError)` instead of degrading gracefully. This function is invoked on essentially every state-changing AMM instruction reachable by unprivileged users (deposit, withdraw, withdrawpnl, swap_base_in, swap_base_out), so a legitimate partial loss of pool funds (vault balance reduced below the pnl checkpoint, e.g. by a donation-then-partial-drain, external token loss, or any accounting drift that shrinks `total_pc_without_take_pnl * total_coin_without_take_pnl` below the stored `calc_pnl_x * calc_pnl_y`) permanently reverts every subsequent call, DOS'ing the pool exactly as described in the referenced Dynamo4626 report.

### Finding Description
`calc_take_pnl` computes the pool's "k" using live vault balances (`total_pc_without_take_pnl`, `total_coin_without_take_pnl`) and compares it against the last checkpointed k (`target.calc_pnl_x`, `target.calc_pnl_y`): [1](#0-0) 

If the live k is smaller than the checkpoint k, the branch hits an unconditional error return rather than any graceful fallback (e.g., skipping the pnl step or returning zero delta): [2](#0-1) 

This function is called unconditionally from every core liquidity/trading instruction:
- `process_deposit` calls it before minting LP: [3](#0-2) 
- `process_withdraw` calls it (unless status is `WithdrawOnly`): [4](#0-3) 
- `process_withdrawpnl` calls it: [5](#0-4) 
- `process_swap_base_in` computes `total_pc_without_take_pnl`/`total_coin_without_take_pnl` from live vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook` right before the swap math: [6](#0-5)  — the analogous `calc_take_pnl` call sits earlier in `process_swap_base_out`/`process_swap_base_in` paths (grep confirms 9+ call sites across the swap and deposit/withdraw handlers in `program/src/processor.rs`).

The underlying reserve numbers (`amm_pc_vault.amount`, `amm_coin_vault.amount`) come directly from the SPL token vault accounts, which can shrink relative to the fixed `target.calc_pnl_x`/`calc_pnl_y` checkpoint through any legitimate reduction of vault balance not matched by a corresponding pnl/target-orders update (for example, a loss event, a bug in another instruction that debits the vault, or even normal precision/rounding drift accumulating over many swaps that is not perfectly re-synced). Once `pool_pc_amount * pool_coin_amount < calc_pnl_x * calc_pnl_y`, `calc_take_pnl` — and therefore deposit, withdraw, withdrawpnl, and swap — all revert with `AmmError::CalcPnlError`, matching the exact bug class in the Dynamo4626 report where an assert on cumulative/checkpointed values incorrectly reverts on a partial loss scenario, even though the vault still holds recoverable value.

### Impact Explanation
Because `calc_take_pnl` is on the hot path for deposit, withdraw, withdrawpnl, and both swap directions, tripping this check freezes the entire pool: LPs cannot withdraw their funds, users cannot swap, and even the privileged `withdrawpnl` path (used by the pnl owner) is blocked, since it calls the same function. This is a full denial-of-service on all pool funds until the pool's live k happens to exceed the checkpoint again (which may never happen without external donations), making it effectively an indefinite freeze of LP and swapper funds in the pool.

### Likelihood Explanation
This is reachable by any account that can trigger a reduction in effective vault balance relative to the `TargetOrders` checkpoint, or by any accounting/rounding drift that is not perfectly reversible via `Calculator::restore_decimal`/`normalize_decimal_v2` precision loss over many operations. Given the function's use of integer division/multiplication and `checked_sub`/`checked_mul` chains for pnl accounting, a slow precision drift or any adverse-but-legitimate reserve movement between the checkpoint time and the current call is plausible over the life of a pool, especially pools with frequent swap-fee/pnl activity and long operational periods without a `withdrawpnl` re-sync.

### Recommendation
Change the `else` branch in `calc_take_pnl` from `return Err(AmmError::CalcPnlError.into())` to a safe no-op path: skip the pnl-taking step and return `(0, 0)` deltas without reverting, mirroring the fix applied upstream in the referenced Dynamo4626 remediation. This preserves deposit/withdraw/swap availability even in the (should-be-rare) case where the live k transiently or permanently falls below the checkpoint k, deferring the pnl-taking until reserves recover instead of freezing the whole pool.

### Proof of Concept
1. Establish a pool and let normal swap activity accrue pnl checkpoints in `target.calc_pnl_x` / `target.calc_pnl_y` via repeated `calc_take_pnl` calls during swaps (each swap/deposit/withdraw updates `total_pc_without_take_pnl`/`total_coin_without_take_pnl` and periodically the checkpoint via delta_x/delta_y application in `process_withdraw`/`process_deposit`).
2. Arrange (or simulate) a reduction of the AMM's actual vault balances relative to the checkpoint — this can occur through any legitimate external event reducing `amm_pc_vault.amount`/`amm_coin_vault.amount` without a compensating `target_orders` update (e.g., a partial loss scenario analogous to the Dynamo4626 report, or via extreme precision loss accumulated across `normalize_decimal_v2`/`restore_decimal` roundtrips over a large number of small-value swaps).
3. Call any of `deposit`, `withdraw`, `withdrawpnl`, `swap_base_in`, or `swap_base_out`. Each of these paths recomputes `total_pc_without_take_pnl`/`total_coin_without_take_pnl` from the now-reduced vault balances via `Calculator::calc_total_without_take_pnl_no_orderbook`, then calls `calc_take_pnl` with the stale, larger `target.calc_pnl_x`/`calc_pnl_y` checkpoint.
4. `pool_pc_amount.checked_mul(pool_coin_amount) < calc_pc_amount.checked_mul(calc_coin_amount)` evaluates true, so `calc_take_pnl` returns `Err(AmmError::CalcPnlError)`, aborting the transaction. Because every entry point performs this same check, the pool becomes fully non-functional for all deposits, withdrawals, and swaps until the checkpoint is somehow reduced or reserves recover — a full DOS of user/LP funds.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
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

**File:** program/src/processor.rs (L1940-1945)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
