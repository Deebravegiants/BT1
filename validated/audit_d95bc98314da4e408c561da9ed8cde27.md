## Title
Attacker-controlled vault "donation" desynchronizes pool accounting, triggering unconditional `.unwrap()` arithmetic panics in `calc_take_pnl`/Deposit/Withdraw that permanently DoS a pool's Deposit and Withdraw instructions - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
CVE-2024-21125 describes a MySQL Server crash/hang triggerable by a supplied query hitting an unguarded internal computation. The analogous bug class here is unguarded arithmetic (`.unwrap()` on `checked_sub/checked_mul/checked_div`) in the AMM's PnL/liquidity accounting that assumes pool token totals always satisfy certain invariants. Those totals are derived directly from live SPL vault balances, which any unprivileged account can perturb with an ordinary token transfer, allowing an attacker to break the invariant and force a panic on every future `Deposit`/`Withdraw` for that pool.

### Finding Description
`Calculator::calc_total_without_take_pnl_no_orderbook` computes the pool's "real" reserves directly from the live vault SPL token balances passed in (`amm_pc_vault.amount`, `amm_coin_vault.amount`), only subtracting the internally tracked `need_take_pnl_pc/coin`: [1](#0-0) 

These vault accounts are ordinary SPL token accounts owned by the AMM PDA authority; nothing prevents an unprivileged party from sending an arbitrary extra amount of coin or pc tokens directly to `amm_coin_vault`/`amm_pc_vault` via a normal `spl_token::transfer` instruction in the same or a prior transaction, before invoking `Deposit` or `Withdraw`. This directly and permanently inflates `total_pc_without_take_pnl`/`total_coin_without_take_pnl` used by `Deposit`, `Withdraw` and `calc_take_pnl`.

`calc_take_pnl` recomputes a pnl split assuming the pool's normalized `x1`,`y1` values stay consistent with the stored `target.calc_pnl_x`/`calc_pnl_y`, using unchecked `.unwrap()` subtractions and divisions: [2](#0-1) 
and: [3](#0-2) 

`Deposit` calls `calc_take_pnl` **unconditionally** (no status gate), then unwraps further subtractions to update `target_orders.calc_pnl_x/y`: [4](#0-3) [5](#0-4) 

`Withdraw` calls `calc_take_pnl` unless `amm.status == WithdrawOnly`, and also performs unwrap-based subtractions on the result: [6](#0-5) [7](#0-6) 

Because `x1`/`y1` are recomputed from the (attacker-inflated) live vault balances on every call while `target.calc_pnl_x`/`calc_pnl_y` is state persisted from before the donation, an attacker-chosen donation size can violate the arithmetic assumptions baked into these `.unwrap()` chains (e.g. `x1.checked_sub(x2).unwrap()`, `y1.checked_sub(y2).unwrap()`, or the final `calc_pnl_x`/`calc_pnl_y` `checked_sub().unwrap()`), causing a Rust panic that aborts the transaction with `ProgramError::Custom` from the panic handler (or an unhandled panic depending on runtime). Since the donated tokens permanently remain in the vault balance (there is no reconciliation/sweep instruction that returns donated tokens or excludes them from `total_*_without_take_pnl`), the desynchronization is not self-healing: **every subsequent `Deposit` call** (which has no status bypass) will recompute the same broken invariant and panic again, permanently denying deposits to that pool. `Withdraw` is only protected if an admin proactively sets `AmmStatus::WithdrawOnly` via the privileged `SetParams` instruction - which is not automatic and requires operator intervention after the fact.

### Impact Explanation
This is a DoS/freezing bug class analogous to the referenced CVE: unprivileged, attacker-suppliable input (a token donation amount, not privileged and not a special build) crashes the affected code path deterministically and persistently. Concretely, it can permanently freeze LP `Deposit` functionality (and `Withdraw` until an admin manually flips pool status) for the targeted Raydium pool, locking already-deposited LP funds from being added to or, absent admin action, withdrawn.

### Likelihood Explanation
Reachable via a single submitted transaction (or two: a token transfer donation + a `Deposit`/`Withdraw` call) from any unprivileged account with attacker-chosen accounts (the public vault addresses) and attacker-chosen data (the donation amount, and/or the `Deposit`/`Withdraw` amounts). No signer authority over the AMM, no special build, and no off-chain component is required.

### Recommendation
- Do not derive `total_pc_without_take_pnl`/`total_coin_without_take_pnl` solely from raw vault SPL balances; track/reconcile against an internally accounted reserve, or clamp/ignore any balance surplus beyond expected deposits.
- Replace `.unwrap()` in `calc_take_pnl` and the `Deposit`/`Withdraw` pnl-update code with `checked_*` combinators returning a proper `AmmError` (e.g., `AmmError::CalcPnlError`) instead of panicking, so unexpected vault states fail gracefully rather than permanently bricking the instruction.
- Consider validating that vault balances match `amm.lp_amount`-derived expectations before running pnl math, rejecting the transaction cleanly if an unexpected surplus/deficit is detected.

### Proof of Concept
1. Attacker identifies a target Raydium AMM pool and its `amm_coin_vault` (or `amm_pc_vault`) SPL token account (public info).
2. Attacker sends an ordinary `spl_token::instruction::transfer` of a large, carefully chosen amount of the coin (or pc) mint directly into `amm_coin_vault`, from any wallet they control holding that token - no special permission required.
3. Attacker (or any subsequent user) calls `Deposit` (or `Withdraw`) on the pool.
4. `calc_total_without_take_pnl_no_orderbook` (`program/src/math.rs:238-250`) returns an inflated `total_coin_without_take_pnl` reflecting the donation.
5. `calc_take_pnl` (`program/src/processor.rs:167-281`) recomputes `x1`, `y1` from these skewed totals against the stale `target.calc_pnl_x`/`calc_pnl_y`, and the resulting `.checked_sub(...).unwrap()` calls (lines 213-214, 257-262) or the caller's post-processing unwraps (lines 1352-1371 for Deposit, 1818-1838 for Withdraw) panic due to a negative intermediate value.
6. The transaction aborts. Since the donated balance remains in the vault permanently and `Deposit` has no status bypass, every future `Deposit` transaction against this pool panics identically, permanently freezing new liquidity provisioning (and `Withdraw`, absent admin intervention via `SetParams`/`WithdrawOnly`).

### Citations

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

**File:** program/src/processor.rs (L199-226)
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
            delta_x = diff_x
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
            delta_y = diff_y
                .checked_mul(amm.fees.pnl_numerator.into())
                .unwrap()
                .checked_div(amm.fees.pnl_denominator.into())
                .unwrap()
                .as_u128();
```

**File:** program/src/processor.rs (L256-262)
```rust
                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
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

**File:** program/src/processor.rs (L1352-1371)
```rust
        target_orders.calc_pnl_x = x1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
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
