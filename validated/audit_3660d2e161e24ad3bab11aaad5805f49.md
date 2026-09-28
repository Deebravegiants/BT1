### Title
Bad-debt cleanup supply-index floor leaves a withdrawable phantom claim that drains later depositors' cash — permanent loss masked as solvency - (File: contracts/pool/src/interest.rs)

### Summary
The bug class in CVE-2024-31029 is a crafted input driving the service into a state where it can no longer serve legitimate requests. The XOXNO Lending analog is the bad-debt write-down path: `clean_bad_debt` / `execute_bad_debt_cleanup` is permissionless, and when the written-down debt exceeds what the market's supply index can absorb, `apply_bad_debt_to_supply_index` clamps the supply index UP to `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing the residual claims. Suppliers' stored `scaled_amount` shares are unchanged, so `unscale_supply_floor` still computes a positive token claim against the floor index. The pool's `cash` book is never debited for the shortfall, so `require_reserves` admits the phantom withdrawal, which then pays out of the next depositor's principal.

### Finding Description
`execute_bad_debt_cleanup` (`contracts/controller/src/positions/liquidation/bad_debt.rs:14-60`) is reachable via the permissionless `clean_bad_debt` entrypoint whenever `is_socializable_bad_debt(totals.total_debt, totals.total_collateral)` holds (ceil risk debt > half-up unweighted collateral, collateral ≤ the $5 dust threshold — `contracts/controller/src/positions/liquidation/apply.rs:313` and docs `docs/reference/invariants.md` INV-LIQ-04). It pushes every supply and debt position to `pool_seize_positions_call`, which drives `apply_bad_debt_to_supply_index` in `contracts/pool/src/interest.rs`.

That pool function reduces `supply_index` by `bad_debt / total_supplied`, but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` (`RAY / 1000`). The dedicated test pins the consequence exactly (`contracts/pool/tests/interest.rs:317-369`):

- A 2,000,000-unit write-down on a 1,000,000-unit book clamps the index to the floor rather than zero.
- `cache.unscale_supply_floor(scaled_a)` returns `stranded > 0` — the wiped-out supplier keeps a positive claim.
- After userB deposits `c`, userA's `resolve_withdrawal(i128::MAX, scaled_a)` + `require_reserves(gross)` + `debit_cash(gross)` pays out `gross == c` — exactly userB's fresh deposit — leaving `cache.cash() == 0 < b_claim`.

Because the `cash` book is not adjusted downward for the residual (unlike the `recapitalize` refund asymmetry pinned in `contracts/pool/tests/flows.rs:3328-3406`, where the same cash-vs-custody divergence is shown to make the market "report itself solvent and cannot pay"), the floor residual is indistinguishable from honest backing to `require_reserves`. The stranded holder can withdraw it the moment any new liquidity enters the market.

Attack path for a single unprivileged address:

1. Supply token B into a thin `(hub, B)` book so the attacker's shares dominate `supplied` (the write-down denominator).
2. Supply collateral in asset C on the same account and `borrow` B.
3. Let the collateral price fall (or borrow maximally and let interest accrue) until HF < 1 and the collateral value is ≤ $5 — e.g., withdraw most collateral while still solvent, leaving a dust leg.
4. Any party — including the attacker — calls `clean_bad_debt(account_id)`; `build_liquidation_plan`'s flags do not gate standalone cleanup (INV-LIQ-04: "Listing flags and global pause do not block standalone cleanup").
5. The B-market write-down exceeds the book and the index clamps at the floor; the attacker's B supply position retains its `scaled_amount` and now has a floor-denominated claim with no backing.
6. When an honest user supplies B, the attacker calls `withdraw(..., i128::MAX, ...)` and receives the victim's deposit through the normal `apply` → `transfer_out` path (`contracts/pool/src/ops/withdraw.rs:30-50`), since `require_reserves` reads the overstated `cash` book.

### Impact Explanation
Theft of user funds and permanent market insolvency: the stranded supplier extracts subsequent depositors' principal through the standard `withdraw` entrypoint, and the `cash` ledger continues to overstate custody so the pool keeps admitting withdrawals it cannot honor — the contract is effectively unable to operate for the drained market (fail-open rather than fail-closed, so it does not hit the fail-closed-DoS exclusion).

### Likelihood Explanation
All steps use only in-scope unprivileged entrypoints (`supply`, `borrow`, `withdraw`, permissionless `clean_bad_debt`). The precondition is an insolvent account with ≤ $5 residual collateral in a book small relative to the bad debt — most naturally in a thin market the attacker themselves seeded, which requires no privileged action. The one exogenous element is the price move that creates the bad debt; however the floor residual is also reachable whenever aggregate write-downs in any market exceed `999/1000` of the index base, independent of who engineered the insolvency. Note the threat model acknowledges the index floor "can leave material unpaid backing" (`docs/explanation/threat-model.md:305-308`), which documents the *existence* of a shortfall — it does not document that the residual remains withdrawable against future deposits, which is the loss mechanism shown by the test.

### Recommendation
In `apply_bad_debt_to_supply_index` (`contracts/pool/src/interest.rs`), when the write-down exceeds the index base, burn or zero the residual scaled supply of the affected book (or record an explicit per-market "unbacked scaled supply" figure) instead of clamping at `SUPPLY_INDEX_FLOOR_RAW` while leaving claims intact. Alternatively, debit `cash` by the stranded claim's floor value or gate `withdraw`/`require_reserves` on a backing check that accounts for floor residuals, so a wiped-out claim cannot consume fresh deposits. `recapitalize` already repairs measured shortfall without minting shares; extend that accounting to cover floor-residual claims.

### Proof of Concept
The behavior is already pinned by the unit test `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs:317-369`), which drives the production `Cache` functions in the same order `withdraw` does:

```rust
// contracts/pool/tests/interest.rs (excerpt)
apply_bad_debt_to_supply_index(&mut cache, Ray::from(2_000_000 * RAY));
assert_eq!(cache.supply_index().raw(), SUPPLY_INDEX_FLOOR_RAW);

let stranded = cache.unscale_supply_floor(scaled_a);
assert!(stranded > 0);                       // phantom claim survives wipeout

// userB deposits c
let scaled_b = cache.calculate_scaled_supply(c);
cache.mint_supply(scaled_b);
cache.credit_cash(c);

// userA withdraws via the same calls withdraw::accounting makes
let (burn, gross) = cache.resolve_withdrawal(i128::MAX, scaled_a);
cache.require_reserves(gross);
cache.burn_supply(burn);
cache.debit_cash(gross);

assert_eq!(gross, c);                        // drains userB's entire deposit
assert_eq!(cache.cash(), 0);                 // pool empty; userB's claim unpayable
```

End-to-end, the attacker path is: `supply` thin book → `borrow` against other collateral → collateral price drop → permissionless `clean_bad_debt` → victim `supply` of the written-down asset → attacker `withdraw` for `i128::MAX` pays out the victim's principal via `transfer_out` (`contracts/pool/src/ops/withdraw.rs:48`).