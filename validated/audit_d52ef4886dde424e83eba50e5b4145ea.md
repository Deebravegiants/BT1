### Title
Unprivileged dust-supply griefing permanently blocks permissionless bad-debt socialization in `clean_bad_debt` - (File: contracts/controller/src/positions/supply.rs)

### Summary
The permissionless bad-debt cleanup path `clean_bad_debt` only admits accounts whose remaining collateral is at or below `BAD_DEBT_USD_THRESHOLD` (`BadDebtGate::DustCapped`). However, `process_supply` explicitly permits any third party to add tokens to an account's *existing* supply positions. Any unprivileged address can therefore keep an insolvent account's collateral pinned just above the dust threshold with cheap top-ups, permanently reverting `clean_bad_debt` with `CannotCleanBadDebt`. This is the protocol-level analog of CVE-2016-8626: a single crafted unprivileged request (a dust `supply` call) denial-of-services a permissionless administrative operation, and unlike a mere fail-closed revert, the consequence is that insolvent debt is never written down — it keeps accruing against suppliers, freezing their funds.

### Finding Description
- `clean_bad_debt` → `process_clean_bad_debt` → `socialize_bad_debt(env, account_id, BadDebtGate::DustCapped)` at `contracts/controller/src/positions/liquidation/mod.rs:196-243`.
- The gate is `is_socializable_bad_debt(total_debt, total_collateral)`, which requires `total_debt > total_collateral && total_collateral <= BAD_DEBT_USD_THRESHOLD` at `contracts/controller/src/positions/liquidation/curve.rs:25-27`. If collateral is even slightly above the threshold, `socialize_bad_debt` asserts `admits` and reverts (`mod.rs:235`).
- `process_supply` allows anyone to top up *existing* supply positions on any account: `require_third_party_existing_supply` only rejects legs for hub assets the account does **not** already supply; for existing positions the caller need not be owner or delegate (`contracts/controller/src/positions/supply.rs:61, 86-97`).
- `total_collateral` is computed from `account.supply_positions` via `risk::calculate_account_risk_totals` (`mod.rs:222-227`), so the attacker's dust top-up directly raises the denominator of the gate.

Attack sequence (single unprivileged address):
1. An account becomes insolvent with remaining collateral just under `BAD_DEBT_USD_THRESHOLD` — the exact state `clean_bad_debt` exists for.
2. Attacker calls `supply(account_id = victim_id, spoke_id, assets = [(hub, token) already in victim's supply_positions], amount = dust)` where dust pushes `total_collateral` above the threshold. `require_third_party_existing_supply` passes because the position exists.
3. Every subsequent `clean_bad_debt(victim_id)` reverts at `assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt)`.
4. As prices/indexes drift and collateral falls back below the threshold, the attacker repeats the dust top-up at negligible marginal cost, indefinitely.

The owner-only escape (`process_force_socialize_bad_debt`, `mod.rs:246-249`) requires the insolvent account's owner to voluntarily socialize their own loss and is not a permissionless mitigation; the third-party-supply vector lets an *unrelated* attacker hold the gate shut.

### Impact Explanation
Bad debt that is never socialized keeps its borrow positions open, accruing interest against a pool whose collateral backing is already insufficient. Suppliers' underlying tokens remain lent to a position that can never be resolved through the permissionless path: withdrawals from that market are increasingly under-collateralized, and the protocol's documented resolution mechanism (`clean_bad_debt`) is permanently DoS-able for the cost of ~`BAD_DEBT_USD_THRESHOLD` per top-up round. This qualifies as temporary-to-permanent freezing of supplier funds and growing protocol insolvency, not a mere fail-closed revert.

### Likelihood Explanation
- Reachability: `supply` and `clean_bad_debt` are both callable by any unprivileged address; no delegate relationship is needed once the victim account already holds the targeted supply position.
- Cost: one dust transfer roughly equal to `BAD_DEBT_USD_THRESHOLD` minus current collateral per refresh — small if the threshold is configured in the cents/dollars range, and the donated tokens may even be partially recoverable to the attacker only if the account is eventually cleaned (which the attacker prevents). The grief is asymmetric: attacker cost is bounded by the dust threshold; supplier exposure is the full underwater debt.
- One uncertainty I could not fully verify in this pass: whether `validate_position_entry_gates` (`supply.rs:107-113`) enforces a minimum supply amount. Even if a minimum exists, it only raises the attacker's per-round cost; it does not close the vector, since the gate compares USD collateral and the attacker can top up any existing position by at most that amount.

### Recommendation
Do not let unsolicited third-party supply reset the bad-debt clock. Options:
- In `require_third_party_existing_supply`, additionally reject third-party supply when `account.borrow_positions` is non-empty and the account is insolvent (or simply when `account.borrow_positions` is non-empty — third parties have no legitimate reason to collateralize someone else's debt).
- Alternatively, base `BadDebtGate::DustCapped` on the collateral the account held when it first became eligible, or snapshot eligibility: once `is_socializable_bad_debt` has been observed true for an account, record a flag in storage so later dust deposits cannot un-admit it.
- At minimum, exclude positions deposited by non-owners after insolvency from `total_collateral` in the cleanup gate.

### Proof of Concept
```rust
// Preconditions: account V is insolvent with total_collateral <= BAD_DEBT_USD_THRESHOLD
// and holds at least one supply position in (hub, token T).
// Attacker A has no delegate relationship with V.

// 1) Sanity: permissionless cleanup would succeed now.
controller.clean_bad_debt(&keeper, &V);            // would socialize — do not execute

// 2) Attacker dust top-up on V's EXISTING position (passes require_third_party_existing_supply).
let dust = threshold_tokens_plus_epsilon(&controller, V, T); // ~$1 scaled to T's units
controller.supply(&attacker, &V, &spoke_id, &vec![&env, HubPayment{ hub, asset: T, amount: dust }]);

// 3) Cleanup is now permanently bricked while A keeps topping up.
let res = controller.try_clean_bad_debt(&keeper, &V);
assert_eq!(res, Err(Ok(CollateralError::CannotCleanBadDebt)));

// 4) Repeat step 2 whenever collateral drifts below the threshold.
// V's debt keeps accruing; suppliers in (hub, T) cannot be made whole via clean_bad_debt.
```