## Title
Direct token donation to `amm_coin_vault`/`amm_pc_vault` causes arithmetic-underflow panic in `calc_take_pnl`, DOSing Deposit/Withdraw/WithdrawPnl - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
`Processor::calc_take_pnl` (called from `process_deposit`, `process_withdraw`, and `process_withdrawpnl`) recomputes a "post-pnl" invariant point (`x2`, `y2`) from the pool's **live SPL token vault balances** (`amm_coin_vault.amount`, `amm_pc_vault.amount`) compared against a stale, previously-stored reference point (`target_orders.calc_pnl_x`/`calc_pnl_y`). Because the live vault balances can be inflated by a completely unprivileged, single-sided SPL token transfer directly into `amm_coin_vault` or `amm_pc_vault` (a plain SPL Token `Transfer`, not routed through the Raydium program at all), an attacker can push the current coin:pc ratio far away from the stored reference ratio. This makes `x2` (or `y2`) exceed the live vault balance, and the `checked_sub(...).unwrap()` calls in `calc_take_pnl` panic, aborting every transaction that reaches this code path. This mirrors the Ethos report's root cause: an attacker directly transferring assets into a vault/pool account breaks an internal accounting invariant that other code paths assume holds, causing a `checked_sub` underflow that DOSes core protocol functionality (deposit/withdraw).

### Finding Description
`calc_take_pnl` reconstructs the "price-adjusted" invariant point using the stored `target.calc_pnl_x`/`target.calc_pnl_y` (last snapshot) and the current pool amounts `x1`, `y1` derived from live vault balances:

<cite repo="AYontt/raydium-amm--024" path="program/src/processor.rs" start="199="209" /> [1](#0-0) 

```
let x2_power = Calculator::calc_x_power(target.calc_pnl_x, target.calc_pnl_y, x1, y1);
let x2 = x2_power.integer_sqrt();
let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
```

`x1`/`y1` are derived directly from the **actual SPL token balances** in `amm_coin_vault`/`amm_pc_vault` (via `calc_total_without_take_pnl_no_orderbook`), not from an internally-tracked ledger: [2](#0-1) 

The only guard before the subtraction is `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` (i.e. k must not have decreased), which is trivially satisfied by *any* one-sided donation into either vault (donations only increase k, never decrease it). However, satisfying that guard does **not** guarantee `x2 <= x1` and `y2 <= y1` — `x2 = sqrt(last_k * current_price)`, and if `current_price = x1/y1` is pushed far away from the stored reference ratio (which is exactly what a one-sided direct transfer does, since it changes only one side of the pool with no corresponding trade), `x2` can exceed `x1` (or symmetrically `y2` can exceed `y1`), causing `checked_sub(...).unwrap()` to panic.

An attacker needs only to issue a standard SPL Token `Transfer` instruction (no signer authority over the AMM, no privileged role) sending a large amount of coin or pc token directly to the pool's `amm_coin_vault`/`amm_pc_vault` token account — these are just regular SPL token accounts owned by the AMM authority PDA, and any wallet can transfer tokens into them. This single transaction:
1. Skews `x1`/`y1` (the current, live vault-balance-derived amounts) relative to the stale `target.calc_pnl_x`/`calc_pnl_y` reference stored in the `TargetOrders` account.
2. Any subsequent `Deposit`, `Withdraw` (unless status is administratively set to `WithdrawOnly`, bypassing `calc_take_pnl`), or `WithdrawPnl` call recomputes `calc_take_pnl` using the now-skewed ratio, triggering the underflow panic.

This is functionally identical to the Ethos-Core bug: a direct, unprivileged transfer into a vault account corrupts an accounting relationship that a `checked_sub`/underflow-prone calculation assumes holds, permanently reverting (until the price ratio is restored, e.g. by arbitrage swaps or admin intervention) the affected instructions.

### Impact Explanation
While the price ratio remains skewed, `process_deposit` and `process_withdrawpnl` unconditionally call `calc_take_pnl` and will panic/revert on every invocation: [3](#0-2) [4](#0-3) 

`process_withdraw` also calls it unless the pool status is `WithdrawOnly`: [5](#0-4) 

This means LPs are unable to deposit or withdraw liquidity, and the protocol operator cannot withdraw accrued PnL, for as long as the ratio remains skewed relative to the stale target snapshot — a freeze of LP funds and protocol-owned PnL. An attacker can repeat the donation after any corrective swap activity to keep re-triggering the condition, sustaining the DOS, exactly as described in the referenced report ("the attacker can repeat the attack to keep the protocol unusable").

### Likelihood Explanation
The attack requires only a single, unprivileged SPL token transfer of the attacker's own tokens into a publicly-known, non-signer-gated token account (the AMM's `coin_vault`/`pc_vault`), which is trivially discoverable from the `AmmInfo` account. No special timing, market conditions, or elevated privileges are needed beyond having tokens of one side of the pool and paying for the transfer — the more imbalanced the donation relative to pool size, the more likely `x2`/`y2` exceeds the live balance and panics.

### Recommendation
- Avoid deriving `x1`/`y1` (and the "current price") directly from raw, attacker-influenceable SPL vault balances when comparing against the stored `target.calc_pnl_x/y` snapshot; instead validate/clamp so that `x2`/`y2` can never exceed `x1`/`y1` before subtracting (e.g. use `checked_sub` with graceful `min(x1, x2)` clamping or `saturating_sub` combined with treating the excess as zero delta, and return a typed error instead of relying on `.unwrap()` panics).
- Replace the `.unwrap()` calls in `calc_take_pnl` (`checked_sub`, `checked_div`) with proper error propagation so pathological ratios return an `AmmError` (already partially done via `AmmError::CalcPnlError`) rather than causing a raw panic on every subsequent instruction.
- Consider tracking the previous invariant point using solely program-controlled internal accounting rather than instantaneous token account balances, so an unrelated external transfer cannot corrupt the comparison basis used by `calc_take_pnl`.

### Proof of Concept
1. Pool exists with normal coin/pc reserves and a `TargetOrders.calc_pnl_x/calc_pnl_y` snapshot from the last Deposit/Withdraw.
2. Attacker issues a standard SPL Token `Transfer` instruction sending a large amount of coin token directly to `amm_coin_vault` (no interaction with the Raydium program required).
3. Victim (or attacker) calls `Deposit`, `Withdraw`, or `WithdrawPnl`.
4. `calc_total_without_take_pnl_no_orderbook` reads the now-inflated `amm_coin_vault.amount`, producing a skewed `x1` relative to `y1`.
5. `calc_take_pnl` computes `x2 = sqrt(target.calc_pnl_x * target.calc_pnl_y * x1 / y1)`; because `x1` was artificially inflated, `x2 > x1`, and `x1.checked_sub(x2).unwrap()` panics, aborting the transaction.
6. All subsequent Deposit/Withdraw/WithdrawPnl calls fail identically until the ratio is restored (e.g., by arbitrage swap activity or an admin setting `WithdrawOnly` status), and the attacker can repeat the donation to re-trigger the condition.

### Citations

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
