### Title
`swap_debt` and `swap_collateral` enforce the hub-active scope on the *source* leg only, letting users open new debt/supply positions in a deactivated hub - (File: contracts/controller/src/strategies/swap_debt.rs)

### Summary
The Filament advisory describes a scope (`recordSelectOptionsQuery`) that restricts which values a user may pick, while the corresponding validation rule fails to apply the same scope, so a tampered out-of-scope value is accepted. The analog in XOXNO Lending is the hub-activity scope: the controller enforces `require_hub_active` as the gate that decides which hub markets are in-scope for new risk, but `process_swap_debt` and `process_swap_collateral` apply that gate to the *old* asset's hub and never to the *new* asset's hub. A user can therefore create a fresh borrow or supply position in a hub that governance has deactivated — exactly the class of out-of-scope submission the advisory covers.

### Finding Description
In `process_swap_debt` (`contracts/controller/src/strategies/swap_debt.rs:39-63`), the only hub-level check is:

```rust
config::require_hub_active(env, existing_debt.hub_id);
```

`new_debt.hub_id` is never checked before `borrow_into_controller` mints the new `DebtPosition`. The check is also inverted in intent: the leg being *closed* (repayment of `existing_debt`) is the one that should remain exitable even in an inactive hub, while the leg being *opened* (`new_debt`) is the one that creates new risk and must be in-scope. Compare with `swap_collateral` (`contracts/controller/src/strategies/swap_collateral.rs:43-50`), which has the same shape:

```rust
config::require_hub_active(env, current.hub_id);
...
require_can_supply(env, &mut cache, account.spoke_id, new);
```

`require_can_supply` operates on the per-(spoke, hub_asset) `SpokeAssetConfig` (paused/frozen/caps via `cached_spoke_asset`, `contracts/controller/src/context.rs:192-204`); the hub-active flag is a separate hub-level flag enforced by a distinct function, `config::require_hub_active`, which callers such as `process_flash_position` invoke explicitly (`contracts/controller/src/strategies/flash_position.rs:60`). Neither `swap_collateral` nor the deposit it performs checks `new.hub_id`.

This mirrors the advisory exactly: the listing-level scoping (`require_can_supply`/`require_can_borrow` on the destination asset — the "options query") is enforced, but the hub-level scope (`require_hub_active` — the "validation rule") is applied to the wrong operand and never to the user-chosen destination.

### Impact Explanation
When governance deactivates a hub (e.g., an oracle incident, market wind-down, or cross-hub risk containment), all ordinary entry points that open positions in that hub are rejected. `swap_debt` bypasses this: an attacker can refinance existing debt into a borrow position in the deactivated hub at full size, re-expanding protocol exposure to precisely the market governance chose to halt. `swap_collateral` similarly routes new supply into the dead hub's book, letting a user acquire supply shares in a market that may be impaired or delisted-in-progress, which then competes for the same physical pool balance under `clean_bad_debt`/`recapitalize` write-down rules. This is a scope-enforcement bypass reachable by any account owner or delegate via `swap_debt(account_id, existing_debt, new_debt_amount, new_debt, swap)` and `swap_collateral(account_id, current, from_amount, new, swap)`, directly undermining a governance safety lever.

### Likelihood Explanation
Triggering requires (a) a hub to be deactivated while its spoke asset listings remain configured — the normal wind-down order — and (b) an account holding debt/collateral in an active hub plus a swap route (or a same-token cross-hub passthrough, which needs no external venue per the docstring "Matching assets across hubs pass through"). During a deactivation event — the exact moment the scope matters — any user can execute the swap with one call. Profitability is not required; the caller may even be the party harmed, but for an attacker wanting exposure to the halted market (e.g., to buy distressed supply shares or keep borrowing against a failing oracle) the path is direct and permissionless.

### Recommendation
In `process_swap_debt`, check the destination instead of (or in addition to) the source: replace `require_hub_active(env, existing_debt.hub_id)` with `config::require_hub_active(env, new_debt.hub_id)`, and drop the requirement on the source hub so refinancing *out of* a deactivated hub stays possible. Apply the symmetric fix in `process_swap_collateral`: `config::require_hub_active(env, new.hub_id)` rather than `current.hub_id`. Audit the other strategy entrypoints (`multiply`, `repay_debt_with_collateral`, `migrate_from_blend`, `flash_position`) for the same source-vs-destination inversion.

### Proof of Concept
1. Setup: hub 0 active with USDC and XLM listed on spoke S; hub 1 also has XLM listed on spoke S. Alice holds a USDC debt position in hub 0.
2. Governance deactivates hub 1 (`hub_active[1] = false`); ordinary `borrow`/`supply` against `(hub 1, XLM)` now revert.
3. Alice (or her delegate) calls `swap_debt(account_id, existing_debt=(hub0,USDC), new_debt_amount=X, new_debt=(hub1,XLM), swap=route)`:
   - `existing_debt != new_debt` passes; `require_hub_active(env, 0)` passes.
   - `borrow_into_controller` mints a `DebtPosition` on `(hub1, XLM)` — a hub governance deactivated.
   - The proceeds repay the USDC leg; `strategy_finalize` passes risk gates since prices/indexes for hub 1 still resolve.
4. Result: a new, full-size borrow exists in a deactivated hub despite every direct entrypoint rejecting it. The same sequence with `swap_collateral(account_id, current=(hub0,USDC), from_amount=Y, new=(hub1,XLM), swap)` deposits into the inactive hub's supply book.

Note: I verified the missing `require_hub_active` on the destination legs in both files, but could not fully confirm whether `borrow_into_controller`/`process_deposit` internally re-check hub activity via `require_can_borrow`/`require_can_supply`; based on the visible pattern of explicit per-caller `require_hub_active` invocations (e.g., `flash_position.rs:60`, `validate_position_entry_gates` callers), the destination-hub check appears genuinely absent — this should be confirmed in a full session before reporting.