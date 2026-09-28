### Title
Unhandled arithmetic overflow in accrual permanently freezes a market — all repay/withdraw/liquidate paths panic in `scaled_to_original` - ([File: common/src/rates/scaling.rs](common/src/rates/scaling.rs))

### Summary
The external report describes an unhandled exception crashing a server. In XOXNO Lending the analog is an unhandled `i128`/`Ray` overflow panic inside interest accrual: `scaled_to_original(scaled, index)` multiplies scaled debt by the borrow index with no headroom guard, and this runs inside `global_sync`, which every state-changing pool entrypoint executes first. Once total debt value approaches the representable RAY ceiling, accrual panics before the `MAX_BORROW_INDEX_RAY` index cap can engage, permanently bricking the market.

### Finding Description
- `common/src/rates/scaling.rs:14-16` — `scaled_to_original` is a plain `scaled.mul(env, index)`; overflow raises `MathOverflow` with no clamping.
- `common/src/rates/simulate.rs:51-94` — `accrue_step` calls `scaled_to_original(env, borrowed, borrow_index)` on every chunk to compute utilization.
- `contracts/pool/src/interest.rs:20-53` — `global_sync` runs `accrue_chunk` unconditionally at the top of every market mutation (deposit, withdraw, borrow, repay, seize, flash, revenue claim), per the documented flow "entrypoint → Cache::load → interest::global_sync → mutate → guards".
- `contracts/pool/README.md:187` and `common/src/constants/pool.rs:18-22` — `update_borrow_index` is the sole borrow-index writer and caps the *index* at `10^36` raw RAY, but nothing caps the *value* `borrowed_scaled × index`; the value overflows the `i128` fast path (and even the `I256` intermediate eventually) well before the index cap.
- `docs/reference/invariants.md:235-236` (INV-IDX-01) concedes: "Debt-value overflow can still revert accrual before that ceiling is reached."
- `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360` is a live proof: a whale market at 98% sustained utilization panics inside `scaled_to_original` with `MATH_OVERFLOW`, `borrow_index < MAX_BORROW_INDEX_RAY` (the cap never engages), and subsequent `withdraw` and `repay` calls panic identically — "the market is frozen: no repay, no withdraw, no liquidation."

Because `global_sync` panics on *every* entrypoint for that market, the failure is not a per-call revert: it is a permanent liveness failure. `clean_bad_debt`, `recapitalize`, and `liquidate` all accrue first, so no recovery path exists short of a contract upgrade.

### Impact Explanation
Permanent freezing of all funds in the affected (hub, token) market — supplier deposits cannot be withdrawn, debt cannot be repaid, bad debt cannot be cleaned, liquidations cannot execute. Collateral in other markets held by accounts with frozen-market debt is also effectively trapped, since `liquidate`/`repay` touch the poisoned market book. This maps to the accepted impact class "permanent freezing of funds" / "protocol insolvency" (unpayable, unseizable debt plus unrecoverable supply).

### Likelihood Explanation
Reachable entirely by unprivileged addresses via `supply`, `borrow`, and the permissionless `update_indexes` (which itself performs accrual). The attacker only needs capital: supply a very large principal to a high-decimals asset, drive utilization into the steep segment of the rate curve (e.g., the XLM-style curve where rate rises sharply near max utilization), and wait — or simply keep `update_indexes` calls flowing so chunks accrue. Caveats reducing likelihood: it requires whale-scale liquidity (the demonstrated setup is ~10^9 × 10^18 units) and sustained high utilization over a long horizon; governance-set `supply_cap`/`borrow_cap` (`contracts/controller/src/config/asset.rs:89-90`, validated by `require_cap_within_asset_domain`) can bound total size — but caps are per-spoke config, `0` disables them, and multiple spokes share one physical pool book, so caps do not reliably bound aggregate scaled shares. Once the condition exists, exploitation is deterministic and irreversible.

### Recommendation
- Bound the product, not just the index: in `update_borrow_index`/`accrue_step`, clamp or saturate the computed debt value (`scaled_to_original(borrowed, new_borrow_index)`) before it can overflow — e.g., detect the unrepresentable case and freeze the index at the last representable value, letting the market continue operating with interest stopped (fail-open for liveness) rather than panicking.
- Alternatively, enforce a protocol-wide scaled-share/value ceiling (analogous to `MAX_BORROW_INDEX_RAY`) checked at borrow/debt-mint time in the pool guards, and validate `supply_cap`/`borrow_cap` against it at listing time (`require_cap_within_asset_domain` currently only validates the asset-decimal domain).
- Add a regression test inverting `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` to assert the market remains operable at the ceiling rather than reverting.

### Proof of Concept
The in-repo test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361` already demonstrates the exploit end-to-end:

1. Attacker supplies `principal = 10^9 × 10^18` of an 18-decimal asset (`t.supply_raw(BOB, "BIG18", principal)`).
2. Attacker supplies collateral and borrows 98% of it (`t.borrow_raw(ALICE, "BIG18", principal/100*98)`).
3. Time advances year-by-year; at some point `update_indexes` (permissionless) fails inside accrual: `assert_contract_error(failed, errors::MATH_OVERFLOW)`.
4. `last.borrow_index < MAX_BORROW_INDEX_RAY` — the intended cap never engaged.
5. `try_withdraw_raw` and `try_repay` for *any* amount now revert with `MATH_OVERFLOW`; the same panic hits `liquidate`, `clean_bad_debt`, `recapitalize`, and `claim_revenue`, since all run `global_sync` first. No code path escapes the panic.