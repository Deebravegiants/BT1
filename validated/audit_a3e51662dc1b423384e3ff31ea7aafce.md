### Title
`swap_debt` omits the hub-active check for the new debt market, allowing borrowing from a disabled hub - (File: contracts/controller/src/strategies/swap_debt.rs)

### Summary
`process_swap_debt` validates `config::require_hub_active` only for `existing_debt.hub_id`, while the sibling strategy `process_repay_debt_with_collateral` enforces `require_hub_active` on *both* involved markets. The missing check is the classic "incomplete fix" shape of CVE-2026-32990: the guard exists in the codebase and was applied to the analogous entrypoint, but the `new_debt` leg of `swap_debt` was left unguarded.

### Finding Description
In `contracts/controller/src/strategies/swap_debt.rs`, the entrypoint checks: [1](#0-0) 

Only `existing_debt.hub_id` is required to be active before `borrow_into_controller` mints new debt on `new_debt` and the pool transfers `new_debt_amount` of underlying to the controller [2](#0-1) .

Contrast with `contracts/controller/src/strategies/repay_debt_with_collateral.rs`, which enforces the check on both legs: [3](#0-2) 

The pattern in `repay_debt_with_collateral` proves the intended invariant — every market leg touched by a multi-market strategy must belong to an active hub. `swap_debt` implements the fix only on the repay side and leaves the borrow side reachable on a paused/disabled hub.

Note (uncertainty): I could not fully verify in this pass whether `borrow_into_controller` or `strategy_finalize` re-checks hub status through `enforce_spoke_asset_flags`/`FreezePolicy`; if spoke-asset flags are set independently of `hub_active`, this may partially mitigate but still leaves the hub-level guard bypassed, since `require_hub_active` is explicitly the control the codebase applies to strategy entrypoints.

### Impact Explanation
An unprivileged account owner (or delegate) can call `swap_debt(account_id, existing_debt, new_debt_amount, new_debt, swap)` with `new_debt` on an inactive/frozen hub. The pool pays out `new_debt_amount` of real underlying via `borrow_into_controller`, the swap leg converts it to `existing_debt.asset`, and the proceeds repay old debt. When a hub is disabled — e.g., in response to an oracle failure, depeg, or insolvency event — this lets a user pull fresh liquidity out of a market the protocol explicitly froze, draining cash reserves precisely when the disable flag is meant to stop outflows. Impact: theft of funds / protocol insolvency via liquidity extraction from a frozen market.

### Likelihood Explanation
Requires only an existing debt position on an active hub and one disabled hub with a listed `(hub, token)` market — conditions that arise exactly when governance pauses a hub during an incident, which is when the bypass does the most damage. Medium likelihood, Medium impact → Medium.

### Recommendation
Add `config::require_hub_active(env, new_debt.hub_id)` in `process_swap_debt` alongside the existing check (and audit `multiply`, `swap_collateral`, `flash_position`, `migrate_from_blend` for the same asymmetric coverage of `require_hub_active`/`require_spoke_asset_flags` across all market legs).

### Proof of Concept
```rust
// Precondition: hub H_old active (holds account debt), hub H_new disabled.
// account has debt in (H_old, X).

controller.swap_debt(
    SwapDebtArgs {
        account_id,
        existing_debt: HubAssetKey { hub_id: H_old, asset: X },
        new_debt_amount: 1_000_000,
        new_debt: HubAssetKey { hub_id: H_new, asset: Y }, // disabled hub — unchecked
        swap: route_y_to_x,
    },
);
// Pool pays out Y from the frozen hub; swap repays X debt.
// Expected: panic like direct borrow on H_new; Actual: succeeds.
```
Contrast: `repay_debt_with_collateral` with the same disabled-hub asset panics at `require_hub_active`, confirming the intended behavior.

### Citations

**File:** contracts/controller/src/strategies/swap_debt.rs (L44-45)
```rust
    config::require_hub_active(env, existing_debt.hub_id);
    require_positive_amount(env, new_debt_amount);
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L55-63)
```rust
    let amount_received = borrow_into_controller(
        env,
        &mut account,
        new_debt,
        new_debt_amount,
        true,
        PositionAction::SwDebtR,
        &mut cache,
    );
```

**File:** contracts/controller/src/strategies/repay_debt_with_collateral.rs (L46-48)
```rust
    require_positive_amount(env, collateral_amount);
    config::require_hub_active(env, collateral.hub_id);
    config::require_hub_active(env, debt.hub_id);
```
