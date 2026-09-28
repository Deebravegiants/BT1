### Title
Leg age-spread bound applies only to Market/Market pairs, letting a stale Fundamental anchor blend into the valuation midpoint - (File: contracts/price-aggregator/src/engine.rs)

### Summary
The dual-leg blend in `blend()` bounds the timestamp gap between the two configured sources with `MAX_LEG_AGE_SPREAD_SECONDS` (3,600 s) only when **both** legs have `FeedNature::Market`. For the configuration actually deployed on mainnet — a Reflector `Market` leg plus a RedStone `Fundamental` leg — no age-spread bound applies at all. A Fundamental anchor up to `max_stale_seconds` old (up to 26 h, per `MAX_PRICE_STALE_SECONDS`) still counts as "fresh" and is averaged into the midpoint used for LTV-weighted collateral valuation. The harness test `audit_borrow_withdraw_liquidate_stale_anchor_blends_5pct_skew_into_ltv` demonstrates the exploit end to end.

### Finding Description
In `engine.rs::blend`, the staleness flag is computed as:

```rust
let spread_bounded =
    primary.nature == FeedNature::Market && anchor.nature == FeedNature::Market;
let age_spread = primary.timestamp.abs_diff(anchor.timestamp);
let stale = primary.stale
    || anchor.stale
    || (spread_bounded && age_spread > MAX_LEG_AGE_SPREAD_SECONDS);
let price_wad = midpoint_price_or_zero(anchor.price_wad, primary.price_wad);
``` [1](#0-0) 

Per-leg staleness is only checked against each feed's own `feed.max_stale_seconds` (`read_feed`, engine.rs:613-617) and the asset-level `oracle.max_price_stale_seconds` (`read_source`, engine.rs:555-560), which may legally be as large as `MAX_PRICE_STALE_SECONDS = 93_600` s (common/src/oracle/observation.rs:21). Deployed mainnet oracles use exactly this asymmetric shape: a Market Reflector leg with `max_stale_seconds: 3600` and a `Fundamental` RedStone leg with `max_stale_seconds: 46800`–`57600` (e.g., `configs/ops/mainnet/d107945413c34e38a186e50f4ae6077df37495c9ed9b2671688774aceded9816.json`, XLM oracle).

Because the Fundamental leg is exempt from the leg-age-spread bound, a RedStone anchor that stopped updating up to ~13–16 h ago remains "fresh" to the aggregator. Its frozen price is midpoint-averaged with the true fresh market price, and the result passes `failure()` (not stale, within the ±5–10% tolerance band, inside sanity bounds) and is returned by `prices()` to the controller's `Context::fetch_prices` / `cached_price` for health-factor and LTV valuation (contracts/controller/src/external/price_aggregator.rs:18-29).

This is the XOXNO Lending analog of the reported class — freshness enforcement exists but is applied inconsistently: the cross-leg staleness guard silently does not bind for the dominant deployed configuration.

### Impact Explanation
An attacker holds collateral priced by a dual-leg oracle whose Fundamental anchor is frozen at a higher price than the live market leg. The midpoint blends up to half of the stale-vs-true skew into the accepted price (bounded only by the tolerance band), inflating LTV-weighted collateral. The attacker calls `borrow` and extracts debt they could not obtain under an honest valuation; when the anchor finally updates or the position is liquidated, the realized collateral value is lower, leaving bad debt / protocol insolvency borne by suppliers. The direction is symmetric: a stale-low anchor also suppresses measured collateral, blocking legitimate borrows or triggering unwarranted liquidation of other users.

### Likelihood Explanation
Requires only that a `Fundamental` feed halts updates within its configured `max_stale_seconds` window — a signer/relayer outage, not misbehavior — while the Market leg keeps updating. Long-anchor staleness budgets (13–26 h) are deliberate in the deployed configs, so the window is wide. Any unprivileged account can then borrow against the skewed midpoint in a single transaction via `Controller::borrow` (or amplify it via `multiply`). Exploitation is bounded by the tolerance band (≤ ~5% midpoint error at a 10% band), matching Medium severity: conditional external trigger, bounded but real insolvency impact.

### Recommendation
Apply `MAX_LEG_AGE_SPREAD_SECONDS` (or a configurable per-oracle leg-spread bound) to all two-leg blends, not just Market/Market pairs — or at minimum cap the anchor leg's contribution when `age_spread` exceeds a fraction of `feed.max_stale_seconds`, e.g., fall back to the fresh market leg (deviation-flagged) instead of midpointing a day-old value. Alternatively, tighten `max_stale_seconds` on Fundamental legs to something on the order of the leg-spread constant so "fresh" cannot mean "many hours old."

### Proof of Concept
The repository's own harness proves the path (`tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blends_5pct_skew_into_ltv.rs`):

1. XLM is configured with a Reflector primary (fresh, $0.91) and a RedStone `Fundamental` anchor frozen at $1.00 with timestamp `now - 82_800` s — inside its `ANCHOR_MAX_STALE_SECONDS = 86_400` window, so `read_feed` marks it not stale.
2. Because the anchor's nature is `Fundamental`, `spread_bounded` is false and the 82,800 s leg-age gap does not trip `stale` in `blend`.
3. The accepted price is the midpoint ≈ $0.955, inflating measured collateral > 4% versus the control run where the anchor is fresh at $0.91.
4. `try_borrow(ALICE, "USDC", 70_000)` succeeds in the exploit run while the honest-fresh control reverts with `INSUFFICIENT_COLLATERAL` — one unprivileged `borrow` call extracting debt backed by overvalued collateral. [2](#0-1)

### Citations

**File:** contracts/price-aggregator/src/engine.rs (L419-430)
```rust
        Legs::Two { primary, anchor } => {
            let spread_bounded =
                primary.nature == FeedNature::Market && anchor.nature == FeedNature::Market;
            let age_spread = primary.timestamp.abs_diff(anchor.timestamp);
            let stale = primary.stale
                || anchor.stale
                || (spread_bounded && age_spread > MAX_LEG_AGE_SPREAD_SECONDS);
            let ts = primary.timestamp.min(anchor.timestamp);
            let deviation =
                !within_tolerance_band(env, anchor.price_wad, primary.price_wad, &oracle.tolerance);

            let price_wad = midpoint_price_or_zero(anchor.price_wad, primary.price_wad);
```
