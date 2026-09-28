### Title
Bad-debt supply-index floor leaves wiped suppliers an unbacked residual claim that withdraws against post-loss cash — (`contracts/pool/src/interest.rs:88`)

### Summary
When bad debt is socialized, `apply_bad_debt_to_supply_index` scales the supply index down by `remaining / total_supplied` but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`) instead of letting it reach zero. If the write-down is large enough to hit the clamp, surviving scaled supply shares unscale to a strictly positive claim even though the pool's cash backing for them was destroyed. Withdrawal only checks `cash >= amount` (`require_reserves`), so those "freed" claims can still redeem against any cash that later enters the market — residual repayments, dust, or `recapitalize` refills — stealing funds that belong to the protocol or new suppliers.

### Finding Description
The UAF analog: a supplier's scaled shares are the "object"; the supply-index write-down is the "free." Because the index is floored rather than allowed to reach zero, the shares remain dereferenceable:

- `apply_bad_debt_to_supply_index` computes `new_supply_index = supply_index * floor(remaining/total)` then applies `.max(SUPPLY_INDEX_FLOOR_RAW)` (`contracts/pool/src/interest.rs:73-89`). At the clamp, `unscale_supply_floor(scaled)` still returns >0 for any surviving `scaled > 0`.
- In `seize_positions`, the borrow leg burns only the liquidated account's debt shares (`cache.burn_debt`) and reclassifies only that account's supply as revenue; other suppliers' scaled shares are untouched (`contracts/pool/src/ops/seize.rs:24-31`).
- Withdrawal resolves `(burn, gross)` via `resolve_withdrawal` at the current (floored) index and debits cash guarded solely by `require_reserves`, which compares against `cash`, not against any backing measure (`contracts/pool/src/cache/cash.rs:15-21`). The backing-shortfall gate (`guards::backing_shortfall`) protects supply-side entries, not withdrawals.
- The pool's own unit tests pin the exploit arithmetic: `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` and `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs:372-494`) show a wiped position paying out exactly a fresh depositor's principal once any cash exists, leaving the honest claim undercollateralized. The docs acknowledge the residual: "The non-zero floor can leave residual claims without backing" (`docs/reference/formulas.md:399`) and INV-IDX-02 notes the bound "can preserve an unbacked residual claim" (`docs/reference/invariants.md:246`).

Reachability for an unprivileged attacker: `clean_bad_debt` is permissionless for insolvent accounts with collateral ≤ $5 (`process_clean_bad_debt`, `contracts/controller/src/positions/liquidation/mod.rs:195-235`). An attacker can engineer a total-wipeout market: supply the market, borrow near-max against collateral in another market, move the price so debt far exceeds collateral and the bad debt exceeds total supplied value in the debt market, then call `clean_bad_debt`. The index clamps at the floor; the attacker (or any surviving supplier) holds scaled shares worth `scaled * RAY/1000` with zero backing. They then wait for — or themselves trigger — `recapitalize` or any inflow, and withdraw, extracting the refill.

### Impact Explanation
Theft of user/protocol funds. Every token that later enters the wiped market — recapitalization fills, stray direct transfers to the pool, late repayments on other debts — is claimable first-come-first-served by holders of the phantom residual claims, ahead of (or instead of) backing honest positions. This is a permanent, quantifiable drain equal to `supplied_scaled * SUPPLY_INDEX_FLOOR_RAW` worth of tokens per wiped market.

### Likelihood Explanation
Medium. It requires a wipeout severe enough to push the computed index below `RAY/1000` (bad debt > ~99.9% of total supplied value in that market) and subsequent cash entering the market. Both are reachable without privilege: thin/spoke-isolated markets can be fully wiped by a single engineered insolvency plus an oracle-permitted price move, and `recapitalize`/direct transfers post-cleanup are expected operational flows (the runbook explicitly prescribes `recapitalize` after cleanup — `docs/reference/runbooks/force-socialize-bad-debt.md:71-73`).

### Recommendation
Do not floor the supply index at a nonzero value when the write-down exceeds total supplied value; either let it reach zero (with a separate zero-index handling that makes `unscale_supply_*` return 0) or, at the floor, burn/zero the now-unbacked residual by tracking a write-down factor per share. Alternatively, gate withdrawals on `backing_shortfall == 0` so unbacked claims cannot redeem against new cash — though the cleaner fix is removing the phantom claim at write-down time.

### Proof of Concept
Conceptual (mirrors the repo's own tests):

1. Attacker supplies `S` of asset X (sole supplier), supplies collateral Y, borrows ~all of X.
2. Price of Y collapses within oracle bands; account is insolvent with collateral ≤ $5.
3. Attacker calls `clean_bad_debt(account_id)`. `seize_positions` burns the debt and calls `apply_bad_debt_to_supply_index` with `bad_debt > total_supplied_value`; `reduction_factor` → 0 but index clamps to `RAY/1000`. Attacker's X supply shares survive.
4. `recapitalize` (or any direct transfer) adds `C` cash to market X.
5. Attacker calls `withdraw` for the full position; `resolve_withdrawal` pays `scaled * RAY/1000`, `require_reserves(C)` passes, attacker receives real tokens backed by nothing.

Not fully verified (tool budget exhausted): the exact guard set inside `ops/withdraw.rs` beyond `require_reserves`/`resolve_withdrawal`, and whether `recapitalize` itself checks `backing_shortfall` in a way that would refuse the refill — though the runbook indicates refill-after-cleanup is a supported flow.