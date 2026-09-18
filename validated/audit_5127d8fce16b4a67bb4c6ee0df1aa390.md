Based on my analysis of the FRR `ospf_te.c` `get_edge()` bug class (a value returned by an internal calculation is consumed by a caller without any validation, leading to an unhandled crash reachable from network input), I looked for the closest analog in `raydium-amm--013`: paths where an internal helper computes a value that is *not* guaranteed by its caller's precondition to be safe, and the result is fed into an unchecked `.unwrap()`/panicking operation, reachable from unprivileged instructions (`Deposit`/`Withdraw`/`WithdrawPnl`).

### Title
Unchecked arithmetic in `calc_take_pnl` can panic and permanently freeze Deposit/Withdraw/WithdrawPnl on unprivileged, attacker-influenced pool state - (File: `program/src/processor.rs`)

### Summary
`Processor::calc_take_pnl` computes a "post-pnl" reserve pair `(x2, y2)` from the pool's stored `TargetOrders.calc_pnl_x/calc_pnl_y` and the current normalized reserves `(x1, y1)`, then immediately does `x1.checked_sub(x2).unwrap()` and `y1.checked_sub(y2).unwrap()` [1](#0-0)  without verifying that `x2 <= x1` and `y2 <= y1` actually hold. The single guard that exists before this computation only checks the *raw native-unit* product `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` [2](#0-1) , whereas `x2` is derived via `Calculator::calc_x_power` and an integer square root operating on decimal-normalized values [3](#0-2) . Integer-sqrt truncation combined with independently-chosen per-token decimal normalization (`sys_decimal_value`, `pc_decimals`, `coin_decimals`) means the native-unit guard does not strictly guarantee `x2 <= x1` / `y2 <= y1` in the normalized domain used for the subtraction.

### Finding Description
`calc_take_pnl` is called from every state-mutating, unprivileged liquidity path: `process_deposit` [4](#0-3) , `process_withdraw`, and `process_withdrawpnl` [5](#0-4) . In each case, `x1`/`y1` are recomputed from the *live* vault balances (`amm_pc_vault.amount`, `amm_coin_vault.amount`) via `calc_total_without_take_pnl_no_orderbook` [6](#0-5) , which any unprivileged swapper directly influences through the four swap instructions (`process_swap_base_in`, `process_swap_base_in_v2`, `process_swap_base_out`, `process_swap_base_out_v2`). Because swaps change the coin/pc ratio while `TargetOrders.calc_pnl_x/calc_pnl_y` is only updated when `calc_take_pnl` *succeeds*, an attacker can drive the pool into a reserve ratio where the sqrt-based `x2`/`y2` estimate exceeds the corresponding `x1`/`y1` in the normalized domain, triggering the `unwrap()` panic on `checked_sub`. Because the on-chain state that produced the panic (vault balances, `TargetOrders`) is unchanged by a reverted/panicking transaction, every subsequent `Deposit`, `Withdraw`, or `WithdrawPnl` call recomputes the identical inputs and panics identically — the failure is not self-healing, it will persist until reserves happen to shift back (which normal trading may never do, and which nothing in the program forces).

This mirrors the CVE-2024-34088 bug class: an internal function (`get_edge()` in FRR / `calc_x_power`+`integer_sqrt` here) produces a value the caller trusts without validating against the true precondition, and the unhandled failure path (NULL deref in FRR / `unwrap()` panic here) is reachable from ordinary, unprivileged traffic (an OSPF LSA / a submitted swap+deposit transaction).

### Impact Explanation
If triggered, `Deposit`, `Withdraw`, and `WithdrawPnl` all become permanently unusable for the affected pool once the qualifying ratio is reached, since they all route through `calc_take_pnl` with the same live-vault-derived inputs. This constitutes permanent freezing of LP funds (LPs cannot withdraw) and of user deposits, and blocks the protocol's own pnl withdrawal mechanism — satisfying the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
Reaching the vulnerable state requires only unprivileged swap transactions (no special signer, no privileged account) to shift the coin/pc ratio, followed by a normal `Deposit`/`Withdraw`/`WithdrawPnl` call — all within the in-scope instruction set. The precise numeric conditions required to make integer-sqrt truncation exceed `x1`/`y1` depend on decimal configuration and reserve magnitudes and were not empirically reproduced here; this reduces confidence that the condition is trivially/always reachable versus reachable only under specific decimal/reserve combinations.

### Recommendation
Replace the `.unwrap()` calls at `x1.checked_sub(x2)` / `y1.checked_sub(y2)` in `calc_take_pnl` with `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?` (consistent with the pattern already used in `calc_total_without_take_pnl_no_orderbook`), and additionally clamp/saturate `x2`/`y2` to be no greater than `x1`/`y1` before computing the pnl delta, so that decimal-normalization/sqrt-truncation discrepancies degrade to "no pnl taken this call" rather than aborting the entire instruction.

### Proof of Concept
1. Attacker (or anyone) executes a sequence of `SwapBaseIn`/`SwapBaseOut` transactions to skew the pool's coin/pc reserve ratio relative to the last-recorded `TargetOrders.calc_pnl_x/calc_pnl_y`, while keeping the raw product check `pool_pc_amount*pool_coin_amount >= calc_pc_amount*calc_coin_amount` satisfied.
2. Attacker (or any user) submits a `Deposit`, `Withdraw`, or `WithdrawPnl` instruction; `calc_take_pnl` computes `x2`/`y2` via `calc_x_power`/`integer_sqrt` in the sys-decimal-normalized domain.
3. Due to normalization/sqrt truncation, `x2 > x1` or `y2 > y1` in the normalized domain even though the native-unit guard passed; `checked_sub(...).unwrap()` panics, reverting the instruction.
4. Because on-chain state is unchanged by the revert, step 2 repeats identically for any future caller, permanently blocking `Deposit`/`Withdraw`/`WithdrawPnl` for the pool.

### Citations

**File:** program/src/processor.rs (L188-192)
```rust
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
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

**File:** program/src/processor.rs (L1494-1495)
```rust
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
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
