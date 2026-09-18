### Title
Permanent freezing of LP funds via unhandled negative-PnL (`k`-decrease) revert in `calc_take_pnl` - (File: `program/src/processor.rs`)

### Summary
The external report describes a Yearn-style vault where losses on the underlying asset are not fairly distributed: instead of spreading a permanent loss across all LPs, the accounting only realizes the loss lazily on withdrawal, so the first withdrawer(s) exit unaffected while whoever withdraws later is forced to absorb the whole loss. The closest reachable analog in this AMM is `Processor::calc_take_pnl`, which snapshots pool value (`target_orders.calc_pnl_x`/`calc_pnl_y`) and only knows how to handle the case where the pool's current invariant (`x1 * y1`) is **greater than or equal to** the last recorded snapshot. If the current invariant ever falls below the snapshot — i.e. the pool has suffered a "loss" relative to the last recorded state — the function does not distribute or account for that loss at all; it simply returns `AmmError::CalcPnlError` and aborts the transaction.

### Finding Description
`calc_take_pnl` compares `pool_pc_amount * pool_coin_amount` (current normalized reserves) against `calc_pc_amount * calc_coin_amount` (the last snapshot taken in `TargetOrders`): [1](#0-0) 

When the current product is smaller than the snapshot (i.e. pool value decreased since the last snapshot was taken), the function has no loss-handling branch — it logs and returns an error, aborting the whole instruction: [2](#0-1) 

This function is invoked unconditionally inside `process_deposit`: [3](#0-2) 

and inside `process_withdraw` for every status except `WithdrawOnly`: [4](#0-3) 

and inside `process_withdrawpnl` (the admin PnL-collection path): [5](#0-4) 

By contrast, the swap paths (`process_swap_base_in_v2`, `process_swap_base_out_v2`) never call `calc_take_pnl` — they compute reserves via `calc_total_without_take_pnl_no_orderbook` directly and proceed with the trade regardless of the snapshot: [6](#0-5) [7](#0-6) 

So once the invariant check trips, `Deposit` and `Withdraw` (outside `WithdrawOnly` status) become permanently unusable for that pool until the pool's reserves recover to at least the old snapshot value — something that, by definition of a "loss," may never happen. This mirrors the report's core defect: the protocol's PnL/loss accounting mechanism has only a "gain" code path and no mechanism to fairly recognize/redistribute a decrease in pool value across LP holders; instead of socializing the loss, it blocks exits/entries outright.

### Impact Explanation
If pool reserves ever drop below the last recorded `calc_pnl_x`/`calc_pnl_y` snapshot (any event that decreases the raw token balances of `amm_coin_vault`/`amm_pc_vault` without a matching decrease being reflected first via `withdrawpnl`, e.g. externally-caused balance reduction on the underlying SPL token accounts, or accumulated precision-related asymmetries between the normalize/restore-decimal round trips used to store/compare the snapshot), every subsequent `Deposit` and `Withdraw` call reverts with `AmmError::CalcPnlError`. LP token holders lose the ability to add or remove liquidity from the pool — a permanent freeze of LP funds for that pool, since there is no recovery instruction that lets the protocol re-baseline the snapshot to the new (lower) value except through admin-only levers, and even `WithdrawOnly` status is a privileged/admin-set state, not something an LP can trigger themselves.

### Likelihood Explanation
The check is reached on every single `Deposit`/`Withdraw` call, with no privileged signer required — any user submitting a normal deposit or withdraw transaction hits this code path. What is uncertain (and could not be fully verified from the indexed portion of the repository) is the exact concrete mechanism by which the underlying vault balance could organically fall below the recorded snapshot in this specific AMM design, since ordinary swap fees are designed to make `k` monotonically non-decreasing and floor-rounded withdrawals also favor remaining LPs. Establishing a fully deterministic single-transaction trigger (e.g., confirming whether `Initialize2` allows fee-on-transfer/rebasing SPL mints, or whether the `restore_decimal`/`normalize_decimal_v2` round trip can itself introduce a spurious decrease) would require further verification with full file access; this could not be conclusively confirmed within the indexed context.

### Recommendation
Add a loss-handling branch to `calc_take_pnl` (or callers) so that when the current invariant is below the last snapshot, the function re-baselines `target_orders.calc_pnl_x`/`calc_pnl_y` to the new, lower reserves (effectively recognizing and socializing the loss across all current LP holders proportionally) instead of hard-erroring, so `Deposit`/`Withdraw` remain available. Alternatively, gate this failure so it only blocks the admin `WithdrawPnl` instruction (where no loss should be paid out) while allowing `Deposit`/`Withdraw` to proceed by treating "no positive PnL to skim" as a no-op rather than a fatal error.

### Proof of Concept
Not able to construct a fully deterministic, single-transaction PoC from the indexed code alone, because the concrete external trigger that reduces `amm_coin_vault`/`amm_pc_vault` balances below the recorded `target_orders.calc_pnl_x * calc_pnl_y` snapshot (e.g., pool creation with a non-standard/fee-bearing SPL mint via `Initialize2`, or accumulated decimal round-trip drift in `normalize_decimal_v2`/`restore_decimal`) could not be conclusively confirmed with the available context. The code-level defect itself — `calc_take_pnl` unconditionally erroring instead of handling a `k`-decrease, and that error path being reachable from unprivileged `Deposit`/`Withdraw` — is directly demonstrated by the cited lines above.

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

**File:** program/src/processor.rs (L1165-1173)
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

**File:** program/src/processor.rs (L2154-2159)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
