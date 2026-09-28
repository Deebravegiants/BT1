### Title
Bad-debt supply-index floor clamp resurrects wiped suppliers' claims, letting them drain fresh deposits - (File: contracts/pool/src/interest.rs)

### Summary
The kernel bug class is "a missing enforcement on a shared boundary (stack-pointer alignment) lets one party corrupt another party's state." The XOXNO analog is the missing enforcement in `apply_bad_debt_to_supply_index`: when socialized bad debt meets or exceeds the total supplied value, the write-down clamps the supply index *up* to `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`) instead of zeroing it, silently resurrecting a residual ~0.1% claim for every wiped supplier. That stranded claim is backed by nothing until anyone deposits fresh cash, at which point the wiped supplier withdraws the fresh deposit in full.

### Finding Description
In `contracts/pool/src/interest.rs`, `apply_bad_debt_to_supply_index` computes `remaining = total_supplied_value - min(bad_debt, total_supplied_value)` and scales `supply_index` by `remaining / total_supplied_value`, then applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))` (lines 73-89). When `bad_debt >= total_supplied_value`, `remaining = 0` and `reduction_factor = 0`, but the floor clamps the index to `RAY/1000`. The supply shares themselves are never burned: `seize.rs::apply` on the `Borrow` side only calls `apply_bad_debt_to_supply_index` + `burn_debt`; `supplied` is untouched (`post.supplied == pre.supplied` is asserted in `certora/pool/spec/seize_settle_accounting_rules.rs:77`).

The result is a book where `supplied * supply_index` is a positive claim with `cash = 0`. Withdrawal gating in `contracts/pool/src/ops/withdraw.rs::gate_and_debit` checks only `require_reserves` (cash ≥ payout), `require_utilization_below_max`, and `require_supply_for_debt` — none detects the unbacked residual. `docs/reference/invariants.md` explicitly notes "The index floor can leave a shortfall. Recapitalization fills that shortfall" (INV-LIQ-04), but recapitalization is optional and does not burn the phantom shares; the stranded claim stays withdrawable.

The in-repo tests `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` and `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs:317-495`) prove the exact mechanics: after the clamp, a wiped holder's `unscale_supply_floor` claim is positive, a fresh deposit credits cash, and the wiped holder's `resolve_withdrawal(i128::MAX, old_scaled)` pays out exactly the fresh deposit, leaving the honest depositor unbacked.

Reaching the wipeout state is permissionless: any account whose debt value exceeds total supplied value in a market (debt grows via `borrow_index` accrual while supply claim grows only via `supply_index`, so long accrual or a price crash can push debt past total supply value) is liquidated or cleaned via `clean_bad_debt`/`force_socialize_bad_debt` → `execute_bad_debt_cleanup` (`contracts/controller/src/positions/liquidation/bad_debt.rs:14`) → `pool_seize_positions_call` → `ops::seize::apply`. The attacker only needs to be a pre-existing supplier in that market, or buy the stranded position cheaply before fresh cash arrives.

### Impact Explanation
Theft of user funds: every token subsequently deposited into the wiped market (new `supply`, direct token transfers to the pool, or `recapitalize` funds meant to restore backing) is withdrawable by holders of the ~0.1%-of-original-value residual claims, ahead of honest depositors. The pool ends with `cash` below the fresh suppliers' claims — deterministic loss for whoever supplies next. This is exactly the corruption-by-misalignment shape of CVE-2017-17856: a boundary enforcement that was assumed (index → 0 means claims → 0) is violated, and downstream accounting consumes the corrupted state without checking it.

### Likelihood Explanation
Requires a market wipeout where ceil debt value ≥ supplied claim value at seizure time. This is reachable whenever accrued interest or a collateral crash makes a single account's bad debt exceed the market's entire supplier claims — most plausible in small/young markets or thinly-collateralized spikes, and `clean_bad_debt` is permissionless once collateral is at/below the $5 dust threshold while debt remains. After that, only one fresh deposit is needed for the stranded claim to pay out real tokens. The attacker's cost is holding any supply share in the market pre-wipeout.

### Recommendation
When `capped == total_supplied_value` (full wipeout), burn the residual: either set `supply_index` and `supplied`/`revenue` together to zero, or explicitly burn the surviving supply shares so `supplied == 0` and the stranded claim cannot exist. Alternatively, add a withdraw-time guard rejecting payouts while the market carries a write-down residual (`post.supply_index == SUPPLY_INDEX_FLOOR_RAW` with `supplied > 0` and `remaining == 0` should mark the market as defaulted rather than leaving claims live). `recapitalize` should also settle or clear the residual claim before crediting cash.

### Proof of Concept
```text
1. Market M: Alice supplies 1000 X (supplied=1000·RAY, supply_index=RAY).
   Carol supplies collateral elsewhere; borrows against M so that after
   accrual/price crash, debt_value ≥ supplied_value. Bob (attacker) holds
   any small supply share s in M.
2. Permissionless `clean_bad_debt(caller=anyone, account_id=carol)`
   → execute_bad_debt_cleanup → seize::apply(Borrow side)
   → apply_bad_debt_to_supply_index(bad_debt ≥ total_supplied_value):
       capped = total_supplied_value; remaining = 0; factor = 0
       new_supply_index = 0.max(RAY/1000) = RAY/1000   // clamped UP
   → burn_debt(position). supplied unchanged.
   State: supplied = 1000·RAY, supply_index = RAY/1000, cash = 0.
   Bob's stranded claim = s·(RAY/1000) > 0, backed by nothing.
3. Dave supplies amount C (or anyone transfers C to the pool):
   cash = C, supplied grows, index stays RAY/1000.
4. Bob calls controller withdraw(account with share s):
   resolve_withdrawal(i128::MAX, s) → gross = s·floor_index
   require_reserves(gross): C ≥ gross  → passes.
   Bob receives C (up to his residual); Dave's claim is now unbacked.
```
Mirrors `test_raw_cache_seizure_residual_would_drain_fresh_cash_without_supply_guard` (`contracts/pool/tests/interest.rs:430-495`), which demonstrates the stranded claim extracting "exactly Bob's fresh deposit" once cash exists.