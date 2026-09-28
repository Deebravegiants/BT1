### Title
Aquarius LP collateral price is derived from live pool reserves and can be inflated by a same-transaction token donation, enabling under-collateralized borrows - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
The price aggregator prices Aquarius LP share collateral by reading the pool's `get_reserves` and `get_total_shares` at read time and combining the legs through `fair_lp_price_wad` (`2 * sqrt(value_a * value_b) / share_supply`). Because reserves are read from raw pool balances inside the same transaction, an unprivileged attacker can inflate the reported LP price by donating one pool token directly to the Aquarius pool (or via an imbalanced `deposit`), then borrow against LP collateral at the inflated valuation and abandon the debt. The production `AQUAUSDC_LP` market is priced by exactly this single `AquariusLp` source with a sanity band wide enough (~10x) to absorb a large inflation.

### Finding Description
`read` in `contracts/price-aggregator/src/providers/aquarius.rs:69-131` calls `aquarius_pool_reserves_call` (`common/src/oracle/providers/aquarius.rs:45-57`), which proxies the AMM's `get_reserves` — a live balance read with no smoothing, no TWAP, and no comparison against a reference reserve. The fair-value formula in `common/src/oracle/lp.rs:57-87` computes `2 * sqrt(va * vb) / shares`. Donating `d` units of token A directly to the pool raises `va` to `va * (1 + d/ra)` with `vb` and `total_shares` unchanged, so the reported LP price scales by `sqrt(1 + d/ra)` — quadratic cost for linear price gain, but the ~10x configured sanity band (`min_sanity_price_wad` 1.28e16 to `max_sanity_price_wad` 1.28e17 for AQUAUSDC_LP, `configs/mainnet/markets.json:1651-1652`) permits up to ~10x inflation, which costs ~99x reserve A as a donation, or far less if the attacker is a dominant LP holder whose inflated collateral value exceeds the donation.

The controller consumes this price through the Context-cached oracle during `supply`/`borrow`/strategy entrypoints. A single unprivileged transaction (or a flash-position-funded sequence) can: acquire or already hold LP shares, supply them as collateral, donate token A to the Aquarius pool to push the reported LP price up, then `borrow` the maximum against the inflated `min_borrow_collateral_usd`/LTV check, and leave the position to `liquidate`/`clean_bad_debt`. The pool's real redeemable value never changed; the protocol books debt exceeding collateral value and the loss is socialized to suppliers via the supply-index write-down (`docs/reference/formulas.md:386-395`).

The threat model's band-safety argument (`LT < 1/u` prevents bad debt) only holds when `u = max/min` is small; for the LP market `u ≈ 10` so `1/u ≈ 0.1`, well below any plausible liquidation threshold — the band does not protect this market.

### Impact Explanation
Protocol insolvency / theft of user funds: borrowed assets are paid out of the shared pool balance at an artificially inflated collateral valuation. The resulting bad debt is written down on the debt market's supply index, transferring the loss to unrelated suppliers of that market.

### Likelihood Explanation
Medium. The attack needs the attacker's donation cost to be recovered by the extra borrow capacity: profitable when the attacker holds a large fraction of the LP supply, when reserve A is thin relative to the band width, or when combined with a buyback-style own-trade on the venue. It requires no privilege, no oracle compromise, and no code change — only `supply`, direct token transfer to the pool, and `borrow`. Capital cost bounds it to Medium rather than High.

### Recommendation
Do not derive collateral value from raw manipulable reserves. Bound reserves against a recorded/TWAP reference (e.g., Aquarius's own reserve history or a `min(reserve_now, reserve_ref)` per leg), or price LP shares as `min(claimable value, band-relative reference)`. Alternatively tighten `min_sanity_price_wad`/`max_sanity_price_wad` for LP markets so `u` stays below `1/LT`, restoring the invariant the threat model assumes.

### Proof of Concept
1. Attacker holds `N` shares of Aquarius pool P (token A/token B), supplied as collateral via `controller.supply(account, [(hub, P_share, N)])`.
2. In the same transaction (fundable through `flash_position`/`flash_loan`), attacker transfers `d` units of token A directly to P's address. `get_reserves` now returns `(ra + d, rb)`; `get_total_shares` is unchanged.
3. Attacker calls `controller.borrow`. `engine::resolve_nested` prices the collateral legs, `fair_lp_price_wad` returns `fair * sqrt(1 + d/ra)`, within the ~10x sanity band, so the read succeeds.
4. Borrow proceeds are withdrawn; the position's real collateral value is `fair * N` but booked debt is up to `LT * N * sqrt(1 + d/ra)`. The position goes bad; `clean_bad_debt`/`force_socialize_bad_debt` writes the loss into the debt market's supply index, paid by suppliers.

Supporting code: `contracts/price-aggregator/src/providers/aquarius.rs:88-122` (live reserve read + fair price + only a `min_pool_value_wad` floor), `common/src/oracle/lp.rs:57-87` (sqrt formula symmetric in donations), `common/src/oracle/providers/aquarius.rs:45-57` (raw `get_reserves`), `configs/mainnet/markets.json:1628-1652` (single-source LP oracle, ~10x band).