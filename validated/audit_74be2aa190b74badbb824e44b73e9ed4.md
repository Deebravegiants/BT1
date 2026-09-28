### Title
Bad-debt supply-index floor leaves stranded supply claims that drain subsequent deposits - (File: contracts/pool/src/interest.rs)

### Summary
CVE-2014-9837's class is "malformed edge-case input drives the code into a state it fails to fully handle." In XOXNO Lending the analog is the bad-debt write-down path: `apply_bad_debt_to_supply_index` socializes bad debt by deflating the supply index, but clamps it at `SUPPLY_INDEX_FLOOR_RAW` (RAY/1000) instead of zeroing or burning the residual supply. After a wipeout, unburned supply shares keep a positive floored claim (`unscale_supply_floor` > 0) that is only masked while pool cash is zero. When any new depositor supplies the market — including via `supply` or `recapitalize` — the stranded position can `withdraw` and extract the fresh cash, stealing the honest depositor's funds.

### Finding Description
- `contracts/pool/src/ops/seize.rs` lines 24-27: the borrow-side seize computes `bad_debt = unscale_borrow_ceil_ray(position)`, calls `interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt)`, then `cache.burn_debt(position)`. No supply shares are burned and no guard ensures the write-down fully cancels outstanding supply claims.
- `apply_bad_debt_to_supply_index` (called from `seize.rs`; exercised in `contracts/pool/tests/interest.rs` lines 299-313) clamps the supply index to `SUPPLY_INDEX_FLOOR_RAW` on a wipeout rather than resetting or zeroing supply. The floor exists to keep `calculate_scaled_supply` division defined, but it leaves pre-write-down shares with a stranded claim: `unscale_supply_floor(scaled_at_floor) > 0`.
- Withdrawal settlement (`resolve_withdrawal` + `require_reserves` + `debit_cash`, `contracts/pool/src/cache/scale.rs` 97-105, `contracts/pool/src/cache/cash.rs` 34-41) pays the floored claim against whatever cash exists. `require_supply_for_debt` (`guards.rs` 69-73) is only invoked in `net_settle`, not in `seize`, so nothing blocks the wipeout residual.

The repo's own characterization tests prove the exploit chain at cache level:
- `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs` 316-369): after `apply_bad_debt_to_supply_index` exceeds total supplied, the index clamps to the floor, user A's shares retain a `stranded > 0` claim, user B deposits `c`, and user A withdraws exactly `c`, draining the pool to zero while B's claim remains unpaid.
- `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs` 430-495): same outcome via the real seize sequence (`unscale_borrow_ceil_ray` → `apply_bad_debt_to_supply_index` → `burn_debt`).

### Impact Explanation
Theft of user funds / protocol insolvency. Any supplier who deposits into a written-down market — or any recapitalizer injecting cash — funds the payout of phantom claims held by wiped-out positions. An unprivileged attacker can reach this by calling `clean_bad_debt` on an account that produces a full write-down of a market where other supply shares exist, then becoming (or waiting for) the residual claimant's counterparty: the first new deposit is drained by the stranded holder's `withdraw`. The books are left insolvent (`total_owed > cash`), so honest suppliers permanently lose funds.

### Likelihood Explanation
- Reachable unprivileged: `clean_bad_debt` triggers the borrow-side seize; `supply`/`withdraw` are permissionless.
- Preconditions: a market that suffers bad debt large enough to drive the supply index to the floor while unburned supply shares remain (the natural outcome of a wipeout liquidation), followed by any fresh deposit. Bad-debt events are inherent to undercollateralized lending; once one occurs, the vulnerability is deterministic — the residual claim always exists and always converts against fresh cash.
- No privileged action, oracle honesty assumption, or timing dependency is required; the stranded claim persists indefinitely until it finds cash.

### Recommendation
When the write-down exceeds the value that total supply can absorb (i.e., the clamp to `SUPPLY_INDEX_FLOOR_RAW` binds), burn or zero the residual scaled supply — or equivalently account the written-down supply explicitly (e.g., convert survivors to revenue or a flagged stranded-claim register) — so no `unscale_supply_floor` claim survives a wipeout. Alternatively, gate `withdraw`/`transfer_out` behind `require_backed_market` or a `stranded_shares` flag set when the floor clamps, so stranded claims can never be settled against post-wipeout cash. Regression tests already exist as raw-cache demonstrations; promote them to end-to-end `clean_bad_debt` → `supply` → `withdraw` tests asserting the stranded holder cannot withdraw.

### Proof of Concept
Mirroring `contracts/pool/tests/interest.rs` 430-495 through real entrypoints:

1. Market (hub, T) has Alice supplying and a borrower whose collateral collapses so `clean_bad_debt(borrower)` executes the borrow-side seize in `seize.rs`: `bad_debt = unscale_borrow_ceil_ray(position)`; `apply_bad_debt_to_supply_index` clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW`; `burn_debt` removes the debt. Alice's supply shares are never burned.
2. `unscale_supply_floor(alice_scaled)` now returns `stranded > 0` (index floor guarantees a positive floored claim), but `cash == 0`, so `require_reserves` masks it.
3. Bob calls `supply(hub, T, c)`; pool credits `c` cash and mints Bob shares at the floored index.
4. Alice calls `withdraw` with `WITHDRAW_ALL_SENTINEL`; `resolve_withdrawal` pays `gross == c`; `debit_cash(c)` drains the pool.
5. Bob's `unscale_supply_floor(bob_scaled) == c` remains, but `cash == 0` — Bob cannot withdraw; the market is insolvent (`owed > cash`).