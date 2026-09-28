### Title
Bad-debt cleanup books the defaulter's remaining collateral as protocol revenue instead of covering the socialized loss - (File: contracts/pool/src/ops/seize.rs)

### Summary
`seize_positions` handles the two sides of a bad-debt cleanup asymmetrically: the defaulted borrow is socialized onto the supply index (suppliers absorb the loss via `apply_bad_debt_to_supply_index`), while the defaulted account's remaining deposit collateral is reclassified as protocol revenue (`absorb_supply_as_revenue`), which is later swept to the accumulator by `claim_revenue`. Suppliers pay for the bad debt, and the collateral that should compensate them is diverted to the revenue destination.

### Finding Description
This mirrors the reported Reserve bug class: funds seized to cover a loss are routed to revenue destinations rather than to the party that bore the loss.

- In `contracts/controller/src/positions/liquidation/bad_debt.rs:21-49`, `execute_bad_debt_cleanup` emits one `PoolSeizeEntry` per supply position with `side: Deposit` and one per borrow position with `side: Borrow`, then calls `pool_seize_positions_call`.
- In `contracts/pool/src/ops/seize.rs:23-32`, the `Borrow` side calls `interest::apply_bad_debt_to_supply_index` (a supply-index write-down borne by all suppliers) and burns the debt, while the `Deposit` side calls `cache.absorb_supply_as_revenue(position)`, which in `contracts/pool/src/cache/shares.rs:45-48` increases `revenue` with total supply unchanged.
- That revenue is later claimed by anyone via controller `claim_revenue` (`contracts/controller/src/markets.rs:129-138`) and forwarded to the `accumulator` (`markets.rs:174-196`).

The economically correct routing for a bad-debt cleanup is to use the defaulted account's remaining collateral to offset the bad debt being socialized — i.e., the seized deposit should compensate the suppliers whose supply index is being written down (or at minimum reduce the write-down). Instead the collateral becomes a windfall to the accumulator while suppliers still absorb the full loss. The same `Deposit`-side seize path is also used for liquidation protocol fees (`apply.rs:191-211`), where revenue booking is correct — the bug is that `execute_bad_debt_cleanup` reuses it for collateral that exists to back the defaulted debt.

### Impact Explanation
Theft of user funds / protocol insolvency pressure: suppliers suffer the full supply-index write-down from bad debt, while the defaulter's residual collateral — the only asset available to offset that loss — is permanently redirected to the accumulator. The loss is bounded by the dust threshold (cleanup only runs under the collateral dust cap per `is_socializable_bad_debt`), but is a systematic transfer from suppliers to the protocol on every bad-debt cleanup.

### Likelihood Explanation
Reachable by any unprivileged address: once a position's debt qualifies as socializable bad debt, any caller can invoke `liquidate` / `clean_bad_debt`, which unconditionally calls `execute_bad_debt_cleanup` and triggers the misrouting. No admin action or privileged state is required; it only needs a defaulted account with residual dust collateral.

### Recommendation
On the `Deposit` side of a bad-debt cleanup, burn the seized supply shares (or transfer their underlying to the pool as cash) to offset the socialized debt, rather than reclassifying them as revenue. Concretely, `seize_positions` needs a third path — or the controller must distinguish fee seizure from bad-debt collateral seizure — so that residual collateral reduces `apply_bad_debt_to_supply_index`'s write-down instead of accruing to `revenue`. I could not fully verify `apply_bad_debt_to_supply_index`'s internals in `contracts/pool/src/interest.rs`, so the exact offset mechanism should be confirmed there; additionally, this behavior is described in the pool README, so the finding should be weighed against whether the diversion is an intentional documented design choice.

### Proof of Concept
1. Alice supplies collateral and borrows; a price move makes her account deeply insolvent with a small residual supply position (under the dust cap).
2. Any caller invokes `liquidate`/`clean_bad_debt`; `check_bad_debt_after_liquidation` (`apply.rs:313-315`) detects socializable bad debt and runs `execute_bad_debt_cleanup`.
3. The pool socializes the unpaid debt onto the supply index (suppliers lose `bad_debt` worth of underlying) and books Alice's residual deposit shares as `revenue`.
4. Anyone calls `claim_revenue`; the seized collateral value is transferred to the accumulator. Net effect: suppliers absorbed 100% of the loss while the collateral that could have covered it went to the accumulator.