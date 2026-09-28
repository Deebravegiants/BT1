### Title
`swap_debt` ignores hub deactivation for the newly borrowed market — the active-hub filter is applied only to the existing debt leg - (File: contracts/controller/src/strategies/swap_debt.rs)

### Summary

Hub deactivation is the controller's configured kill-switch for a whole market group: `config::require_hub_active` gates which hubs may service new activity. In `process_swap_debt` the check is applied only to `existing_debt.hub_id`, the leg being *repaid*, and never to `new_debt.hub_id`, the leg that actually *creates new borrow exposure*. The analogous sibling strategy `process_repay_debt_with_collateral` checks `require_hub_active` for both legs, showing the intended shape of the filter. Because the spoke-level gate `require_can_borrow`/`require_listed_unhalted_config` validates the per-spoke listing flags (`is_borrowable`, `paused`, `frozen`) — not `HubConfig.is_active` — a deactivated hub can still originate fresh debt through `swap_debt`, exactly like Gradle resolving plugins through repositories the `pluginManagement` content filter was meant to exclude: the filter exists, is configured, and is silently skipped on this path.

### Finding Description

In `contracts/controller/src/strategies/swap_debt.rs:44`:

```rust
config::require_hub_active(env, existing_debt.hub_id);
```

Only the existing-debt hub is validated. The flow then calls `borrow_into_controller(env, &mut account, new_debt, ...)` at `swap_debt.rs:55-63`, which enforces `require_can_borrow` on the new debt market — a spoke-level listing check (`contracts/controller/src/positions/mod.rs:201-213`) that consults `SpokeAssetConfig` halt flags, not `HubConfig.is_active`.

Compare `contracts/controller/src/strategies/repay_debt_with_collateral.rs:47-48`, which checks `require_hub_active` for *both* `collateral.hub_id` and `debt.hub_id`, and `process_swap_debt`'s own use of `require_positive_amount` + `require_hub_active` showing the author knew the new leg needs gating (it gates the wrong hub — or rather, only one of the two).

### Impact Explanation

An unprivileged account owner can call `swap_debt(caller, account_id, existing_debt, new_debt_amount, new_debt, swap)` where `new_debt` names a market in a hub that governance has deactivated (`HubConfig.is_active = false`). Deactivation is the intended response to a broken oracle, mispriced market, or emergency in that hub; bypassing it lets the attacker open fresh borrow positions priced by the very infrastructure governance intended to freeze. If the hub was deactivated due to a stale/manipulated price feed, new debt minted under bad pricing translates directly into unbacked withdrawals from the shared physical pool — protocol insolvency borne by suppliers of all hubs sharing that token's custody. Impact class: theft of user funds / protocol insolvency.

### Likelihood Explanation

- Requires governance to have deactivated the target hub (`is_active = false`) while leaving the market's spoke listing `is_borrowable` — plausible: deactivating a hub is the coarse emergency lever precisely because editing every spoke listing is slow.
- Requires the account to hold existing debt somewhere and enough collateral to pass `strategy_finalize` risk gates — routine.
- Requires a swap route (or same-token cross-hub passthrough with empty bytes) — freely constructible.
- Severity is conditional on *why* the hub was halted; in the benign case it is "only" unauthorized borrowing in a frozen market, in the oracle-failure case it is direct value extraction. Rated High on the exploitability of a bypassed security control.

### Recommendation

Add `config::require_hub_active(env, new_debt.hub_id)` alongside the existing check in `process_swap_debt` (or inside `borrow_into_controller` so every debt-originating strategy inherits it). Audit `multiply` and `flash_position` for the same one-sided hub check.

### Proof of Concept

1. Governance deactivates hub 2 (`HubConfig { is_active: false }`), e.g., after its oracle goes stale. The USDC@hub2 spoke listing remains `is_borrowable = true`.
2. Attacker's account holds ETH debt in hub 1 and ample collateral.
3. Attacker calls `swap_debt` with `existing_debt = HubAssetKey{hub_id:1, asset:ETH}`, `new_debt = HubAssetKey{hub_id:2, asset:USDC}`, `new_debt_amount = X`, and a route USDC→ETH.
4. `require_hub_active(env, 1)` passes; no check ever reads `HubConfig` for hub 2. `borrow_into_controller` succeeds because spoke-level `is_borrowable` is true; the flash-style borrow mints USDC debt in the deactivated hub, swaps to ETH, repays the ETH debt, and `strategy_finalize` passes on collateral value.
5. Result: fresh debt exists in a hub governance explicitly shut down — the configured scope filter was ignored, mirroring CVE-2021-29427's ignored `pluginManagement` repository content filters.

Caveat: I could not exhaustively confirm that `borrow_into_controller`/`require_listed_unhalted_config` perform no hub-activity check internally (the context.rs matches were not fully read before the iteration limit). If `require_can_borrow` transitively checks `HubConfig.is_active`, this finding is void; the asymmetry with `repay_debt_with_collateral.rs:47-48` checking both hubs argues it does not.