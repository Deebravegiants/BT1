### Title
Supply-index floor clamp resurrects wiped-out supplier claims that drain fresh deposits - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` socializes bad debt by scaling the supply index down pro-rata, capping the write-down at total supplied value. However, the resulting index is floored at `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`), so when bad debt meets or exceeds total supplied value — which should zero out every supplier claim — the clamp lifts the index back up and leaves every existing scaled share with a positive, unbacked token claim. A subsequent deposit then creates real cash, and the stranded holder can withdraw real tokens backed only by the fresh deposit. This is the direct analog of CVE-2024-48958's "src moves beyond dst" bound violation: the write-down arithmetic is correctly capped at `total_supplied_value`, but a downstream clamp moves the effective claim bound past the backing bound, producing claims beyond what exists.

### Finding Description
In `contracts/pool/src/interest.rs:73-89`:

```rust
let capped = bad_debt.min(total_supplied_value);
let remaining = total_supplied_value.checked_sub(cache.env(), capped);
let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
let new_supply_index = cache.supply_index().mul_floor(cache.env(), reduction_factor);
cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

When `bad_debt >= total_supplied_value`, `remaining = 0`, `reduction_factor = 0`, and `new_supply_index = 0`. The `.max(SUPPLY_INDEX_FLOOR_RAW)` then sets the index to `RAY/1000` instead. Crucially, the function never zeroes or reduces `cache.supplied()` scaled shares — every holder's `scaled_amount` is untouched. Unscaling via `unscale_supply_floor` (`contracts/pool/src/cache/scale.rs:60-67`) now yields `scaled * RAY/1000` tokens of claim against `cash = 0`.

The repo's own test proves the end state: `contracts/pool/tests/interest.rs:372-427` (`test_raw_cache_floor_clamp_strands_claim_without_supply_guard`) shows that after a full wipeout the clamp leaves `S_old` a "phantom claim", a fresh deposit of `fresh_cash` credits real cash, and `resolve_withdrawal(i128::MAX, old_scaled)` pays out `gross == fresh_cash` — draining exactly the new depositor's funds while the fresh supplier's claim remains unpaid.

Reachability: `apply_bad_debt_to_supply_index` is invoked from the liquidation/bad-debt socialization path driven by the unprivileged `liquidate` and `clean_bad_debt` entrypoints (`contracts/controller/src/positions/liquidation/mod.rs`, `bad_debt.rs`). An unprivileged attacker can manufacture bad debt exceeding total supply in a thin/spoke market (borrow against collateral, let the collateral price move or structure dust residual debt), then trigger socialization so the index clamps at the floor. The clamp's stated purpose is only to "avoid a zero index"; there is no corresponding burn of `supplied` shares or guard that blocks withdrawals once backing is gone — the only mitigation is `require_reserves`, which passes the moment any fresh cash lands.

### Impact Explanation
Theft of user funds / protocol insolvency. Any supplier holding scaled shares through a full socialization retains a claim worth `scaled * RAY/1000` tokens despite the backing having been written down to zero. The first deposits after the event are drained by these resurrected claims. Per the test, the drained amount equals the fresh deposit exactly, and pool cash ends below the fresh supplier's claim — the protocol is instantly insolvent on the new money.

### Likelihood Explanation
Requires a market where socializable bad debt reaches total supplied value — plausible in small/new spoke markets, dust-threshold cleanup (`clean_bad_debt`), or collateral crashes where the liquidation bonus cannot cover the gap. The attacker needs no privilege: `liquidate`/`clean_bad_debt` are open calls, and the attacker can hold a supply position (or acquire residual shares) before triggering the wipeout, then wait for — or sandwich — a fresh deposit to withdraw against.

### Recommendation
When `remaining == 0` (full write-down), zero or pro-rata scale the `supplied` scaled-share total together with the index clamp, or record a write-down factor so post-clamp claims are extinguished rather than revalued. Alternatively, gate withdrawals on a backing check (`floor(supply_value) <= cash + debt_value` shortfall accounting already defined in `docs/reference/formulas.md`) so stranded claims cannot pay out against unrelated deposits. The floor clamp should only apply when `remaining > 0`.

### Proof of Concept
Existing executable PoC: `contracts/pool/tests/interest.rs:372-427`. The sequence:

1. Cache seeded with `supplied = 1000 * RAY` shares, `supply_index = RAY`, `cash = 0`.
2. `apply_bad_debt_to_supply_index(&mut cache, Ray::from(5_000 * RAY))` — index clamps to `SUPPLY_INDEX_FLOOR_RAW` while old shares remain.
3. `cache.unscale_supply_floor(old_scaled) > 0` — phantom claim exists with zero cash.
4. Fresh supplier mints shares and credits `fresh_cash` tokens.
5. `resolve_withdrawal(i128::MAX, old_scaled)` returns `gross == fresh_cash`; `debit_cash` leaves `cash < fresh_claim` — the fresh deposit is fully drained by the wiped-out position.

Uncertain: whether production `ops` wrap `apply_bad_debt_to_supply_index` with an additional share-burn that the raw-cache test bypasses; the grep results show no such reduction in `interest.rs`, and the function signature only mutates the index, so the phantom-claim path appears reachable as written.