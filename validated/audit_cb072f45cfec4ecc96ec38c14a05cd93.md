### Title
Stale-but-accepted oracle leg inflates blended collateral price - (File: contracts/price-aggregator/src/engine.rs)

### Summary
The price aggregator rejects only observations older than their configured `max_stale_seconds`, then blends two accepted legs by midpoint. A slow-feed anchor can therefore carry an hours-old price while remaining “fresh” under its configured heartbeat. If the stale anchor diverges upward from the live market leg by less than the tolerance band, the midpoint still overvalues the asset and can increase borrowing power beyond the current market valuation.

### Finding Description
`read_feed` marks each direct source stale only when `now_secs > observation.timestamp + feed.max_stale_seconds`; an observation within the configured window is accepted regardless of whether another leg has a materially newer market observation. For two accepted legs, `blend` rejects them only if either is individually stale or if the market-nature timestamps differ by more than `MAX_LEG_AGE_SPREAD_SECONDS`; that spread check is disabled when the slower leg is `FeedNature::Fundamental`. Accepted legs are then averaged by `midpoint_price_or_zero`. [1](#0-0) [2](#0-1) [3](#0-2) 

This is not merely a third-party oracle honesty assumption: both providers can return exactly the data they honestly stored, while the aggregator combines a current market leg with a still-permitted old fundamental leg. The regression scenario uses a fresh Reflector price of `$0.91` and a RedStone fundamental anchor frozen at `$1.00` for 82,800 seconds with `max_stale_seconds = 86,400`; both legs pass and the midpoint is `$0.955`, approximately 4.95% above the live price. [4](#0-3) [5](#0-4) 

### Impact Explanation
An unprivileged borrower can supply the affected asset as collateral and call `borrow` while the blended collateral value is inflated. The protocol can issue more debt than the current market valuation supports, leaving the account closer to insolvency or immediately undercollateralized when the stale leg is refreshed. Across sufficient collateral and repeated borrowing, this can create bad debt and protocol insolvency, which the regression test demonstrates by showing that the stale-anchor borrow succeeds while the corresponding fresh-anchor borrow fails with `INSUFFICIENT_COLLATERAL`. [6](#0-5) [7](#0-6) 

### Likelihood Explanation
The condition requires only normal oracle behavior: the primary market feed moves while a slower fundamental feed remains within its explicitly allowed staleness window and within the configured ±10% tolerance. Such windows can exceed 24 hours because `MAX_PRICE_STALE_SECONDS` permits 93,600 seconds, while the leg-age spread bound does not apply unless both legs are classified as `Market`. No privileged action, oracle compromise, or malformed provider response is required. [8](#0-7) [9](#0-8) 

### Recommendation
Apply a maximum timestamp-spread check to every dual-source blend, not only pairs where both providers are declared `Market`. Alternatively, value collateral with the lower of the accepted legs rather than the midpoint when their observation ages differ materially. The stale-window policy should also distinguish publication heartbeat from maximum economic staleness: even if a fundamental feed only publishes once per day, risk-sensitive actions can require a tighter quote-age bound or use the fresh market leg instead of blending in the delayed valuation.

### Proof of Concept
1. Configure the collateral asset with a fresh Reflector market leg and a RedStone `Fundamental` leg whose `max_stale_seconds` is 86,400.
2. Set the live market price to `$0.91` and the RedStone observation to an honestly stored `$1.00` timestamped 82,800 seconds ago.
3. `read_feed` accepts the RedStone value because 82,800 seconds is below its 86,400-second bound.
4. `blend` skips `MAX_LEG_AGE_SPREAD_SECONDS` because the RedStone leg is `Fundamental`, accepts the 9.89% deviation under a 1,000-bps tolerance, and returns the `$0.955` midpoint.
5. An attacker supplies that collateral and calls `borrow`, receiving a borrow that succeeds under the inflated blend while the same borrow fails under a fresh `$0.91` anchor with `INSUFFICIENT_COLLATERAL`.

This exact scenario is encoded in `audit_borrow_withdraw_liquidate_stale_anchor_blend.rs`, which measures collateral inflation above 4% and asserts that the stale-anchor borrow succeeds while the fresh-anchor control fails. [10](#0-9) [11](#0-10)

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

**File:** contracts/price-aggregator/src/engine.rs (L613-618)
```rust
    let stale = is_stale(
        session.now_secs(),
        observation.timestamp,
        feed.max_stale_seconds,
    );
    Some((observation, stale))
```

**File:** common/src/oracle/observation.rs (L17-21)
```rust
pub const MIN_PRICE_STALE_SECONDS: u64 = 60;
/// Largest staleness budget an oracle may declare (26 h). It exceeds the 24 h
/// heartbeat of the slowest consumed feed, so a feed that publishes only on its
/// heartbeat does not read as stale.
pub const MAX_PRICE_STALE_SECONDS: u64 = 93_600;
```

**File:** common/src/oracle/observation.rs (L53-57)
```rust
/// Returns whether `feed_ts` is older than `max_stale` seconds relative to
/// `now_secs`. Returns `false` when `feed_ts` is at or after `now_secs`.
pub fn is_stale(now_secs: u64, feed_ts: u64, max_stale: u64) -> bool {
    now_secs > feed_ts && (now_secs - feed_ts) > max_stale
}
```

**File:** tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blend.rs (L5-10)
```rust
const ANCHOR_FROZEN_PRICE: i128 = usd(1);
const TRUE_FRESH_PRICE: i128 = usd_cents(91);
const XLM_TOLERANCE_BPS: u32 = 1000;
const ANCHOR_MAX_STALE_SECONDS: u64 = 86_400;
const ANCHOR_LAG_SECONDS: u64 = 82_800;

```

**File:** tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blend.rs (L45-55)
```rust
    t.set_price("XLM", TRUE_FRESH_PRICE);

    let redstone_client = MockRedStonePriceFeedClient::new(&t.env, &redstone);
    let now = t.env.ledger().timestamp();
    if anchor_stale {
        let stale_ms = now.saturating_sub(ANCHOR_LAG_SECONDS) * 1000;
        redstone_client.set_price_data(&feed_id, &ANCHOR_FROZEN_PRICE, &stale_ms, &stale_ms);
    } else {
        let fresh_ms = now * 1000;
        redstone_client.set_price_data(&feed_id, &TRUE_FRESH_PRICE, &fresh_ms, &fresh_ms);
    }
```

**File:** tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blend.rs (L57-67)
```rust
    t.supply(BOB, "USDC", 500_000.0);

    t.supply(ALICE, "XLM", XLM_SUPPLY);

    let collateral_usd = t.total_collateral(ALICE);
    let borrow = t.try_borrow(ALICE, "USDC", TARGET_BORROW);

    Outcome {
        collateral_usd,
        borrow,
    }
```

**File:** tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blend.rs (L70-93)
```rust
#[test]
fn audit_borrow_withdraw_liquidate_stale_anchor_blends_5pct_skew_into_ltv() {
    let exploit = run(true);
    let control = run(false);

    let inflation = exploit.collateral_usd / control.collateral_usd;
    assert!(
        inflation > 1.04,
        "stale-anchor blend must inflate collateral >4% vs the honest fresh-anchor \
         valuation: exploit={} control={} ratio={}",
        exploit.collateral_usd,
        control.collateral_usd,
        inflation
    );

    assert!(
        exploit.borrow.is_ok(),
        "stale-anchor skew must let the attacker borrow beyond true capacity: {:?}",
        exploit.borrow
    );

    // Pin the reason: an unrelated fixture break that reverts for any other
    // cause would otherwise "prove" the stale anchor enabled the borrow.
    assert_contract_error(control.borrow, errors::INSUFFICIENT_COLLATERAL);
```
