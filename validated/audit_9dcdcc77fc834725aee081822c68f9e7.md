### Title
Bad-debt write-off clamps `supply_index` at `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing wiped positions, leaving stranded claims that drain future depositors' cash - (File: contracts/pool/src/interest.rs)

### Summary
Analogous to CVE-2015-8367's "memory object initialization" bug class, `apply_bad_debt_to_supply_index` fails to fully zero-out supplier claims when bad debt exceeds total supplied value. Instead of resetting `supplied` shares or pinning the index to zero, it clamps the new supply index to a hardcoded floor (`SUPPLY_INDEX_FLOOR_RAW = RAY/1000`). Every pre-wipeout scaled supply share therefore retains a residual claim of ~0.1% of its nominal value that is no longer backed by anything — an "uninitialized/stale state" analog where wiped accounting objects keep being read as live claims.

### Finding Description
In `contracts/pool/src/interest.rs:73-89`, `apply_bad_debt_to_supply_index` computes:

```rust
let capped = bad_debt.min(total_supplied_value);
let remaining = total_supplied_value.checked_sub(cache.env(), capped);
let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
let new_supply_index = cache.supply_index().mul_floor(cache.env(), reduction_factor);
cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

When `bad_debt >= total_supplied_value` (a full wipeout of the (hub, token) book), `reduction_factor = 0`, so `new_supply_index = 0`, but the `.max(SUPPLY_INDEX_FLOOR_RAW)` clamp resurrects it to `RAY/1000`. The old scaled supply shares (`supplied`) are never burned or reset, so each unit still unscale to `scaled × (RAY/1000) / RAY = scaled/1000` asset units via `unscale_supply_floor`/`resolve_withdrawal` in `contracts/pool/src/cache/scale.rs:50-105`.

This is reachable unprivileged through the seize path: `pool::seize` → `ops::seize::apply` (`contracts/pool/src/ops/seize.rs:24-28`) calls `apply_bad_debt_to_supply_index` for `AccountPositionType::Borrow` entries, which the controller emits from `liquidate`/`clean_bad_debt` when a position's debt cannot be covered.

The only pool-side guards are `require_reserves` (cash sufficiency) and `require_supply_for_debt` in `contracts/pool/src/guards.rs:69-73`, which only panics when `supplied == ZERO && borrowed != ZERO` — it does not detect the clamped-index phantom claims. The pool's own test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:372-427`) demonstrates the full exploit: after a wipeout clamp, a fresh deposit of `stranded` tokens lets the wiped position withdraw `gross == fresh_cash`, leaving `cash < fresh_claim` — i.e., the fresh supplier's funds are stolen by the stale claim. `docs/reference/invariants.md` INV-IDX-02 acknowledges the floor "can preserve an unbacked residual claim," confirming the design leaves the wiped object alive.

### Impact Explanation
Theft of user funds / protocol insolvency. After a market suffers bad debt exceeding its supplied value, all pre-existing suppliers retain phantom claims worth `scaled_amount / 1000` each. Once any new liquidity enters the market (fresh `supply`, `recapitalize`, or routed deposits), wiped-out suppliers — including the attacker's own deliberately created dust supply — can withdraw real tokens backed by the new depositors' cash. The pool's books still report the stranded claims as live supply, so this is a direct transfer of new depositors' funds to accounts that should have been zeroed.

### Likelihood Explanation
Likelihood is moderate but requires no privilege:

1. Attacker supplies a large nominal amount early (or any supplier simply exists) in a (hub, token) book.
2. A borrow position accrues unrecoverable debt until `bad_debt >= total_supplied_value`. Anyone can drive this via `update_indexes` (permissionless) and then trigger `liquidate` or `clean_bad_debt` — both listed permissionless entrypoints — which emit `PoolSeizeEntry{side: Borrow}` and hit the clamp.
3. Wait for (or self-provide) fresh deposits, then call `withdraw` on the stranded scaled position; only `require_reserves` (cash presence) gates it, and fresh deposits satisfy that.

The precondition is a genuine bad-debt wipeout event, which is the tail-risk scenario the socialize path is designed for — exactly when correctness matters most.

### Recommendation
When `capped == total_supplied_value` (full wipeout), reset `supplied` (and `revenue`) scaled shares to zero and pin `supply_index` to `RAY` (or a defined restart index) rather than clamping the reduced index at `SUPPLY_INDEX_FLOOR_RAW`. Alternatively, burn the stranded shares proportionally so that `floor(scaled × new_index / RAY) == 0` for every surviving position, or record wiped positions in a tombstone state so `resolve_withdrawal`/`unscale_supply_floor` return zero for pre-wipeout scaled balances. The index floor should only apply to partial write-downs, not to total socialization.

### Proof of Concept
The scenario is already encoded in `contracts/pool/tests/interest.rs:372-427` (`test_raw_cache_floor_clamp_strands_claim_without_supply_guard`):

1. `PoolStateRaw { supplied: 1000·RAY scaled, supply_index: RAY, cash: 0 }`.
2. `apply_bad_debt_to_supply_index(&mut cache, 5000·RAY)` — bad debt exceeds total supply value → `supply_index` becomes `SUPPLY_INDEX_FLOOR_RAW`, not zero.
3. `unscale_supply_floor(old_scaled) > 0` — the wiped supplier still holds a claim of `stranded` units.
4. A new supplier deposits `stranded` tokens (`mint_supply` + `credit_cash`).
5. The wiped position calls `resolve_withdrawal(i128::MAX, old_scaled)` → `gross == stranded`; `require_reserves` passes; `debit_cash(gross)` pays out the entire fresh deposit.
6. Final: `cache.cash() < fresh_claim` — the honest new supplier's claim is unbacked; funds are lost.

On-chain, steps 2–3 map to `controller.liquidate`/`clean_bad_debt` → `pool.seize(Borrow)`; step 5 maps to `controller.withdraw` on the stale position. No privileged call is involved.

Note: I could not fully trace the production `withdraw` op's guard ordering (`contracts/pool/src/ops/withdraw.rs` references `require_supply_for_debt`, which only fires when `supplied == 0`), but the guard as written cannot block this path since `supplied` remains non-zero after the clamp — consistent with the test's demonstration of the drain.