### Title
`swap_debt` validates the repaid market's hub instead of the borrowed market's hub — `require_hub_active` checks `existing_debt.hub_id` while debt is minted against `new_debt.hub_id` - (File: contracts/controller/src/strategies/swap_debt.rs)

### Summary
In `process_swap_debt`, the hub-active gate is applied to the wrong `HubAssetKey`. The entrypoint checks `config::require_hub_active(env, existing_debt.hub_id)` (the market being repaid) but never checks `new_debt.hub_id` (the market it borrows from via `borrow_into_controller`). This mirrors CVE-2024-50158: the guard tests a field that exists on the object at hand (`existing_debt`) while the dangerous action consumes a different object (`new_debt`), so a deactivated hub can still originate new debt.

### Finding Description
`process_swap_debt` lets an account owner or delegate refinance debt: it borrows `new_debt_amount` of `new_debt` into the controller, swaps it into `existing_debt.asset`, and repays the old position. Its only hub-liveness check is:

```rust
// contracts/controller/src/strategies/swap_debt.rs:44
config::require_hub_active(env, existing_debt.hub_id);
```

followed by the actual borrow on the *other* key:

```rust
// contracts/controller/src/strategies/swap_debt.rs:55-63
let amount_received = borrow_into_controller(
    env, &mut account, new_debt, new_debt_amount, true,
    PositionAction::SwDebtR, &mut cache,
);
```

`new_debt.hub_id` is never passed to `require_hub_active`. The sibling entrypoint `repay_debt_with_collateral` demonstrates the intended convention — it activates-checks **both** hubs it touches:

```rust
// contracts/controller/src/strategies/repay_debt_with_collateral.rs:47-48
config::require_hub_active(env, collateral.hub_id);
config::require_hub_active(env, debt.hub_id);
```

Likewise, `flash_position` checks the hub of the asset it actually mints debt in (`config::require_hub_active(env, debt.hub_id)` at `contracts/controller/src/strategies/flash_position.rs:60`), and `flash_loan` checks the borrowed asset's hub (`contracts/controller/src/strategies/flash_loan.rs:24`). The `require_hub_active` call inside `swap_debt` is therefore caller-side and targets the wrong key: the repaid leg (`existing_debt`) is an exit-side action that legitimately does not need an active hub — exits are supposed to remain available during a halt — while the entry-side borrow leg goes ungated.

### Impact Explanation
Deactivating a hub is the governance control that stops new risk origination in that hub's markets while keeping withdrawals/repayments open. An unprivileged account holder can keep minting fresh borrows in a deactivated hub by routing the borrow through `swap_debt` with any `existing_debt` in an active hub. Repeated calls compound unbounded new debt on a market governance froze precisely to stop exposure growth — e.g., a market halted because its oracle or liquidity is deteriorating — directly producing protocol insolvency risk. The attacker needs only an account with collateral and any existing (or co-created) debt position in an active hub; `require_owner_or_delegate` is satisfied by acting on their own account.

### Likelihood Explanation
Reachable whenever governance deactivates a hub that still has liquidity and collateral-enabled counterparts. No privileged role, no price manipulation, and no flash mechanics are needed — one `swap_debt` call with `existing_debt.hub_id` active and `new_debt.hub_id` inactive bypasses the halt. It is not a default-state bug, which caps severity at Medium: the window opens only after an operator halts a hub, and each borrow still passes the post-action risk gates (`strategy_finalize` runs health checks), so the attacker must keep the account solvent — but refinancing into a frozen market indefinitely is exactly the exposure the halt was meant to deny, and spoke-level paused/frozen flags (`FreezePolicy`) do not substitute for the hub-level check.

### Recommendation
In `process_swap_debt`, replace or supplement the existing check so the borrowed leg is gated: `config::require_hub_active(env, new_debt.hub_id)`. The check on `existing_debt.hub_id` should be dropped (repaying into a halted hub must stay possible, consistent with the "exits remain callable under their separate gates" invariant in `docs/reference/invariants.md` INV-HALT-01). Mirror the same audit to `process_swap_collateral` (`contracts/controller/src/strategies/swap_collateral.rs:43`), which checks `current.hub_id` but never `new.hub_id` — `require_can_supply` covers spoke listing/pause but not hub activation.

### Proof of Concept
1. Hub H0 is active with markets for USDC (borrowable) and XLM (collateral). Hub H1 has market USDC.
2. Alice supplies XLM collateral in H0 and borrows a small amount of USDC in H0 (`existing_debt = (H0, USDC)`).
3. Governance deactivates H1 (`require_hub_active` now fails for H1) to stop new H1 exposure.
4. Alice calls `swap_debt` with `existing_debt = (H0, USDC)`, `new_debt = (H1, USDC)` — same asset across hubs passes the `existing_debt != new_debt` check and the swap is a passthrough. The only hub check targets `H0` and passes; `borrow_into_controller` mints `new_debt_amount` of `(H1, USDC)` debt and `repay_debt_from_controller` retires the `(H0, USDC)` position.
5. Net effect: Alice's debt is now parked (and can be grown over repeated calls up to her collateral limit) in the halted hub H1, defeating the activation gate.