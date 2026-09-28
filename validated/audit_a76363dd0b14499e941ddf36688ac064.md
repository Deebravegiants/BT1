### Title
Bad-debt write-down clamps the supply index at a floor, resurrecting wiped-out positions into phantom claims that drain fresh deposits - (File: contracts/pool/src/interest.rs)

### Summary
When `seize_positions` socializes borrow-side bad debt, `apply_bad_debt_to_supply_index` reduces the supply index by `reduction_factor = remaining / total_supplied_value`. If the write-down exceeds total supplied value, the index does not go to zero — it is clamped upward to `SUPPLY_INDEX_FLOOR_RAW`. Every supplier's pre-existing share balance then still unscales to a positive token claim against a market that should be worthless. Those stranded shares later pay out real tokens through `withdraw`, stealing cash deposited by subsequent suppliers.

### Finding Description
`contracts/pool/src/interest.rs` computes the write-down correctly up to the cap (`bad_debt.min(total_supplied_value)`, `checked_sub`), but then substitutes a nonzero floor:

```rust
let new_supply_index = cache
    .supply_index()
    .mul_floor(cache.env(), reduction_factor);
cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

When `reduction_factor` is 0 (total wipeout), `new_supply_index` is `SUPPLY_INDEX_FLOOR_RAW` instead of 0. The share total `supplied` is unchanged, so `unscale_supply_floor(old_shares, FLOOR)` > 0 — a phantom claim backed by nothing. This is the analog of the CVE's "buffer sized too small relative to what is written": the accounting index is sized to a small-but-nonzero floor while the share ledger still writes a full claim against pool cash.

Reachability: `pool::seize_positions` (`contracts/pool/src/ops/seize.rs`) is invoked by the controller's liquidation / `clean_bad_debt` path, which an unprivileged liquidator/caller reaches on an underwater account. After the wipeout, the stranded holder calls `withdraw`, which runs `resolve_withdrawal` → `require_reserves` → `debit_cash` → `transfer_out` and pays out whatever fresh cash exists.

The codebase's own tests prove the flow end-to-end: `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` and `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs`) show a wiped-out holder draining exactly a new depositor's `fresh_cash`, leaving `cash < fresh_claim` and `cash == 0`.

### Impact Explanation
Theft of user funds / protocol insolvency. A supplier whose shares were economically wiped out retains a floor-priced claim (`SUPPLY_INDEX_FLOOR_RAW` ≈ RAY/1000). As soon as any new cash enters the market (a fresh `supply`, a `recapitalize`, or a `repay`), the stranded holder withdraws and consumes it, leaving honest suppliers under-collateralized. On a large market, 0.1% of total supplied value is a material, repeatable extraction per wipeout.

### Likelihood Explanation
Requires a bad-debt event whose write-down meets or exceeds total supplied value (a wipeout of the market), i.e. a near-total default in one `(hub, asset)` book — plausible for tail-risk or thin markets, and `clean_bad_debt` exists precisely for dust/uncollateralized debt cleanup. Triggering is unprivileged: a liquidator calls the seize path; exploitation afterwards is a plain `withdraw`. The extra condition is new liquidity arriving afterward, which happens naturally via `supply`/`repay`/`recapitalize`.

### Recommendation
On a full write-down, burn the stranded supply shares (or set `supplied` and `revenue` to 0) instead of clamping the index upward — i.e., make `apply_bad_debt_to_supply_index` zero out the share ledger when `reduction_factor == 0`, or skip the `SUPPLY_INDEX_FLOOR_RAW` clamp and guard downstream unscale calls against a zero index. Alternatively, track the stranded floor-residual value as written-off debt so `resolve_withdrawal` cannot pay it out. Ensure `revenue ≤ supplied` and the zero-share withdrawal revert (`WithdrawRoundsToZeroShares`) still hold after the change.

### Proof of Concept
1. Market `(hub, X)`: supplier A holds `scaled_a` shares; borrower defaults; `clean_bad_debt`/liquidation calls `pool.seize_positions` with `side = Borrow`, `scaled_amount = debt`.
2. `bad_debt ≥ supplied × supply_index` → `reduction_factor = 0` → `supply_index` stored as `SUPPLY_INDEX_FLOOR_RAW` (`contracts/pool/src/interest.rs:88`). A's `scaled_a` unchanged.
3. Supplier B calls `supply(amount = C)`; pool `cash = C`, B's claim `= C` at the floor index.
4. A calls `withdraw` (or `0` for all): `resolve_withdrawal(i128::MAX, scaled_a)` returns `gross = unscale_supply_floor(scaled_a) > 0`; `require_reserves`/`debit_cash`/`transfer_out` send `C` to A.
5. Pool `cash = 0 < B`'s claim: B's deposit is lost — direct theft of user funds, matching the in-repo tests `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` and `test_raw_cache_floor_clamp_strands_claim_without_supply_guard`.