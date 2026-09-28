### Title
Supply-index floor clamp resurrects wiped-out supplier claims that drain future deposits - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` socializes bad debt by scaling the supply index down, but clamps the result up to `SUPPLY_INDEX_FLOOR_RAW` (`10^24`) instead of zeroing claims when the write-down exceeds total supplied value. Because positions store `scaled_amount` shares, every pre-wipeout supplier retains a nonzero claim `unscale_supply_floor(scaled) = scaled * 10^24 / 10^27` that is entirely unbacked. Any later deposit recreates cash in the market, and the wiped-out shareholder can `withdraw` that phantom claim first, stealing real tokens and permanently freezing the honest depositor's funds behind `PoolInsolvent`/liquidity checks.

### Finding Description
In `apply_bad_debt_to_supply_index` (`contracts/pool/src/interest.rs:73-89`):

- `bad_debt` is capped at `total_supplied_value`, so a full wipeout yields `remaining = 0` and `reduction_factor = 0`.
- `new_supply_index = supply_index * 0 = 0`, then line 88 clamps it up: `new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))`.
- Shares are never burned. Old suppliers keep `scaled_amount`; their floor-valued claim is `scaled * 10^24`, strictly positive, backed by nothing.

The pool's own test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:372-427`) demonstrates the exploit shape at cache level: after the clamp, `resolve_withdrawal(i128::MAX, old_scaled)` returns `gross > 0`, a fresh deposit of exactly that amount is fully drained by the wiped position (`S_old drains exactly the fresh deposit`), and the fresh supplier's claim can no longer be covered (`cache.cash() < fresh_claim`). `require_reserves` only masks this when cash happens to be absent — it does not prevent the phantom payout once any new liquidity exists.

Bad debt itself is reachable by an unprivileged user through the ordinary path: supply collateral in asset A, `borrow` asset B up to the LTV limit (the 200 BPS liquidation buffer in `INV-ACCT-07` only restricts the draw, not subsequent insolvency), wait for a collateral price move or interest accrual to push the account insolvent, then either let liquidations seize all collateral or call the permissionless `clean_bad_debt` once residual collateral is ≤ `BAD_DEBT_USD_THRESHOLD` ($5). `clean_bad_debt` invokes `apply_bad_debt_to_supply_index` per debt market; when the written-off debt approaches or exceeds `supplied * supply_index` (attainable when the attacker is the dominant borrower and the debt grew via accrued interest or when few suppliers remain), the index hits the floor clamp and phantom claims are born. This is a real reachable state, not a hypothetical: INV-IDX-02/03 (`docs/reference/invariants.md:240-260`) explicitly acknowledge the clamp "can preserve an unbacked residual claim" and "an index already at its floor need not decrease" — but no mechanism removes the now-permanently-unbacked shares, and `recapitalize` pays the shortfall without deleting them, so each recapitalization is itself immediately drainable by phantom holders.

### Impact Explanation
Theft of user funds and permanent freezing of funds. A wiped-out supplier (or the attacker themselves, who can hold wiped supply shares before triggering the socialization) can withdraw a positive phantom claim against any cash later entering the market — new `supply` deposits or `recapitalize` payments — stealing those tokens. The legitimate new depositor's position is then unbacked and their `withdraw`/`net_settle`/`claim_revenue` reverts on the cash and solvency checks, i.e. their funds are both stolen and frozen. This repeats every time the market is recapitalized, making the market a permanent value sink.

### Likelihood Explanation
Requires a market to suffer bad debt at or near the scale of total supplied value, which needs a severe collateral move plus liquidation/cleanup lag. Not trivial, but fully permissionless once market conditions produce insolvency: `clean_bad_debt` is keeper-callable by anyone, the clamp triggers deterministically on a wipeout, and the attacker can pre-position wiped shares and be first to withdraw after any recapitalization or new supply. Cost to the attacker is limited to the collateral lost in the engineered bad-debt position, while the payoff is bounded by future deposits into the market.

### Recommendation
When `reduction_factor` would drive the index below `SUPPLY_INDEX_FLOOR_RAW`, do not clamp the index upward while leaving shares outstanding. Instead, treat the market as wiped: burn/void the residual supply claims (e.g., record a wipeout flag or set supplied shares' redeemable value to zero via an explicit shortfall ledger) so `unscale_supply_floor` returns 0 for pre-wipeout shares, and track the unmet remainder as a recapitalization target. At minimum, gate withdrawals and claims on the market with `supply_index == SUPPLY_INDEX_FLOOR_RAW && cumulative_bad_debt >= supplied_value` so phantom claims cannot pay out against fresh cash, and make `recapitalize` cancel residual claims before crediting.

### Proof of Concept
1. Attacker supplies collateral (asset A) and calls `borrow` to draw the maximum of asset B; other suppliers hold `supplied` shares of B.
2. Collateral A's price falls (or interest accrues) until the account's debt exceeds its collateral; liquidations reduce collateral to ≤ $5 dust.
3. Any address calls `clean_bad_debt(caller, account_id)`. The controller writes off the remaining B debt via `apply_bad_debt_to_supply_index`; since `bad_debt ≈ supplied * supply_index`, `reduction_factor → 0` and `supply_index` clamps up to `10^24` (`contracts/pool/src/interest.rs:80-88`).
4. A victim supplies B (or calls `recapitalize`), crediting real `cash`.
5. The attacker, holding wiped `scaled_amount` shares of B, calls `withdraw(account_id, [(hubB, 0)], ...)` (withdraw-all sentinel). `resolve_withdrawal` unscales `scaled * 10^24 > 0`, `require_reserves` passes against the victim's cash, and the pool transfers real tokens for a claim backed by nothing — matching the cache-level proof in `contracts/pool/tests/interest.rs:395-425`.
6. The victim's `withdraw` then reverts (`InsufficientLiquidity`/`PoolInsolvent`); their deposit is permanently frozen/lost.