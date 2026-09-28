### Title
Bad-debt supply-index floor leaves wiped suppliers a phantom claim that drains later deposits - ([File: contracts/pool/src/interest.rs])

### Summary

The ClamAV report's bug class is use-after-free: a dangling reference to memory that was logically released is dereferenced later. The lending analog is a **stale-claim-after-write-down**: when bad debt is socialized, `apply_bad_debt_to_supply_index` writes down the supply index but clamps it at `SUPPLY_INDEX_FLOOR_RAW` instead of letting it reach zero, so wiped supply shares remain dereferenceable ("freed" claims still usable) and later resolve to real token withdrawals paid from new suppliers' cash.

### Finding Description

`apply_bad_debt_to_supply_index` in `contracts/pool/src/interest.rs:73-89` computes `new_supply_index = supply_index * (total_supplied_value - capped_bad_debt) / total_supplied_value` and then applies `new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))`. When `bad_debt >= total_supplied_value` (a complete wipeout), `reduction_factor` should be zero, but the floor forces the index up to `SUPPLY_INDEX_FLOOR_RAW` (RAY/1000). Every supplier's scaled shares — which economically were just socialized to zero — still unscale to a positive amount via `unscale_supply_floor` / `resolve_withdrawal` (`contracts/pool/src/cache/scale.rs:50-67`).

The pool's own test suite proves the consequence. `test_raw_cache_floor_residual_can_consume_fresh_cash_without_supply_guard` and `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:317-428`) show that after the floor clamp, `unscale_supply_floor(old_scaled) > 0`, and a subsequent `resolve_withdrawal(i128::MAX, old_scaled)` pays out `gross == fresh_cash`, draining exactly a fresh deposit and leaving `cash < fresh_claim` — i.e., the honest new supplier can no longer be made whole.

The path is reachable by any unprivileged address: `process_clean_bad_debt` (`contracts/controller/src/positions/liquidation/mod.rs:196-200`) only requires `caller.require_auth()` and admits the call whenever `is_socializable_bad_debt(total_debt, total_collateral)` holds (dust-capped collateral, open debt) via `BadDebtGate::DustCapped`. `execute_bad_debt_cleanup` drives the pool-side write-down that lands in `apply_bad_debt_to_supply_index`. Post-cleanup, the wiped suppliers' share positions and the floored index persist, and normal `withdraw` resolves those shares against the floored index and pays out of `cash`.

### Impact Explanation

Theft of user funds. After a wipeout, suppliers whose claims were socialized retain a residual claim of up to ~1/1000 of the wiped supply (index floor). The first wiped supplier to withdraw converts that phantom claim into real tokens taken from whoever supplies liquidity afterward; the fresh supplier is left with an unbacked position (`cash < fresh_claim`), which is a localized insolvency. For a large wiped market the residual can be economically meaningful, and it is extractable repeatedly across all pre-wipe share holders until cash is exhausted.

### Likelihood Explanation

Triggering requires a bad-debt cleanup on a market where `bad_debt >= total_supplied_value` (or close enough that the proportional index falls below the floor) plus a subsequent fresh deposit. Permissionless `clean_bad_debt` makes the write-down step attacker-invocable once an insolvent dust-collateral account exists, which is a normal end-state of crashed markets. The attacker's own wiped shares then withdraw against the floored index. No privileged role, oracle manipulation, or reentrancy is needed. The main constraint is that an attacker must hold wiped supply shares (or acquire them cheaply post-wipe) and wait for a victim deposit — both feasible for an unprivileged address.

### Recommendation

When `bad_debt >= total_supplied_value`, do not floor the index back up: either zero out supplier shares explicitly (write `supplied = 0` and set `supply_index` to the floor only as a bookkeeping base for *future* deposits, paired with marking existing scaled shares as void) or block withdrawals of pre-wipe share positions in the same epoch. At minimum, distinguish "index floor for new share issuance" from "existing claims": `calculate_scaled_supply` may keep the floor for new deposits, but `unscale_supply_floor` / `resolve_withdrawal` for shares minted before the wipe should resolve to zero when the proportional write-down reached zero. Alternatively, burn/reset all supply positions as part of `execute_bad_debt_cleanup` so no stale claim remains dereferenceable.

### Proof of Concept

Conceptual sequence (all entrypoints are permissionless; the pool-level arithmetic is already demonstrated by `contracts/pool/tests/interest.rs:317-428`):

1. Market (hub H, asset A) accumulates an insolvent borrower account with collateral at or below the dust threshold and debt exceeding it, e.g. after a price move where liquidation leaves residual debt.
2. Attacker calls controller `clean_bad_debt(caller, account_id)` — admitted under `BadDebtGate::DustCapped` (`liquidation/mod.rs:229-235`).
3. `execute_bad_debt_cleanup` socializes the debt; the pool runs `apply_bad_debt_to_supply_index` with `bad_debt >= total_supplied_value`, so `reduction_factor = 0` but `supply_index` is clamped to `SUPPLY_INDEX_FLOOR_RAW` (`interest.rs:88`).
4. Every pre-existing scaled supply position still satisfies `unscale_supply_floor(scaled) > 0` — a claim that should have been destroyed.
5. Victim calls `supply` for amount `c`; pool mints shares at the floored index and credits cash `c`.
6. Attacker (holder of wiped shares) calls `withdraw`/`resolve_withdrawal(i128::MAX, old_scaled)`; `require_reserves(gross)` passes against the fresh cash and `transfer_out` pays `gross == c`.
7. Victim's subsequent withdrawal fails `require_reserves` — their claim exceeds remaining cash.

The pool unit test at `contracts/pool/tests/interest.rs:317-369` executes steps 3-7 directly against `Cache` and asserts `cash == 0` with `cash < fresh_claim`, confirming the drain and the stranded honest supplier.

One caveat on full verification: I confirmed the permissionless controller gate and the pool floor-clamp arithmetic, but did not trace the exact call inside `bad_debt::execute_bad_debt_cleanup` to the pool entrypoint that invokes `apply_bad_debt_to_supply_index` (the README and certora summaries indicate it is reached via the seize/net-settle path during cleanup). The mechanism and the exploitable end-state are nevertheless established by the in-repo test.