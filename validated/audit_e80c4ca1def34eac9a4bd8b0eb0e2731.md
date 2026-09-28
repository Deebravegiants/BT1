### Title
Supply-index floor clamp after bad-debt cleanup leaves phantom shares that drain a later depositor's cash - (File: contracts/pool/src/interest.rs, contracts/pool/src/cache/scale.rs)

### Summary
`apply_bad_debt_to_supply_index` (called by the permissionless `clean_bad_debt` flow via `check_bad_debt_after_liquidation` / `bad_debt::execute_bad_debt_cleanup`) writes the loss down by clamping `supply_index` up to `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing or burning residual scaled shares. The pool's own test `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs:317-369`) proves the consequence: the clamped residual `scaled_a` retains a positive `unscale_supply_floor` claim ("stranded") despite zero backing, and a subsequent withdraw resolves that phantom claim against real cash.

### Finding Description
The bug class from CVE-2020-0182 — a missing bounds check on a value later trusted — maps directly here: after the write-down, no invariant enforces `unscale_supply_floor(scaled) ≤ backing cash` per position. The sequence:

1. An insolvent account leaves socializable bad debt; anyone calls `clean_bad_debt`. `apply_bad_debt_to_supply_index` clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`, leaving existing `scaled_amount` shares with a non-zero `unscale_supply_floor` valuation (`contracts/pool/tests/interest.rs:332-340`).
2. An honest user supplies `c` tokens via `supply`; `calculate_scaled_supply(c)` mints shares priced at the floored index, so the victim's claim equals the deposit while cash equals `c` (`interest.rs:343-349`).
3. The holder of residual shares calls `withdraw` with `i128::MAX` (the documented withdraw-all sentinel); `resolve_withdrawal` computes `gross = stranded = c`, `require_reserves` passes against the fresh cash, and the pool debits `c` to the attacker (`interest.rs:351-360`).
4. `cache.cash() == 0` while the honest depositor's claim `b_claim == c` is now unpayable (`interest.rs:362-368`).

### Impact Explanation
Theft of user funds / protocol insolvency: the stranded share holder extracts 100% of a subsequent supplier's principal from a wiped-out market that had zero backing. The victim's book claim stays positive but the pool's cash is gone — permanent loss for the honest supplier, denominated in the real token.

### Likelihood Explanation
Reachable by a single unprivileged address. Preconditions: a market where `clean_bad_debt` clamps the index to the floor while a supplier still holds residual scaled shares — i.e., the attacker only needs a pre-existing (even dust) supply position in that market, since any residual `scaled_amount` gains a floor-valued claim. The attacker then needs a victim to re-supply the dead market. The exploit path is two ordinary calls: `clean_bad_debt` then `withdraw(i128::MAX)`; the victim's `supply` is a normal unprivileged action. No privileged role, oracle manipulation, or flash capital is required.

### Recommendation
On bad-debt write-down, reconcile residual shares: either burn/reset scaled positions whose claims are being written to the floor, or guard `resolve_withdrawal`/`require_reserves` so a withdrawal cannot pay out against cash contributed after the write-down epoch. Alternatively, compute the supply-index write-down so that `unscale_supply_floor(residual) == 0` (i.e., floor the unscaled residual, not the index) when the wipeout exceeds total supplied.

### Proof of Concept
The protocol's own unit test demonstrates the drain end-to-end:

```rust
// contracts/pool/tests/interest.rs:317-369
apply_bad_debt_to_supply_index(&mut cache, Ray::from(2_000_000 * RAY));
assert_eq!(cache.supply_index().raw(), SUPPLY_INDEX_FLOOR_RAW);

let stranded = cache.unscale_supply_floor(scaled_a);   // phantom claim > 0
// victim supplies c; pool cash = c
let scaled_b = cache.calculate_scaled_supply(c);
cache.mint_supply(scaled_b);
cache.credit_cash(c);

// attacker withdraws all: resolve_withdrawal pays gross == c
let (burn, gross) = cache.resolve_withdrawal(i128::MAX, scaled_a);
cache.require_reserves(gross);
cache.burn_supply(burn);
cache.debit_cash(gross);

assert_eq!(gross, c);        // drains victim's deposit exactly
assert_eq!(cache.cash(), 0); // victim's claim now unpayable
```

Controller-level path: `liquidate`/`clean_bad_debt` (permissionless) triggers `bad_debt::execute_bad_debt_cleanup` → `apply_bad_debt_to_supply_index`; victim calls `supply(caller, 0, spoke, [(hub_asset, c)])`; attacker calls `withdraw(caller, account_id, [(hub_asset, i128::MAX)])`.