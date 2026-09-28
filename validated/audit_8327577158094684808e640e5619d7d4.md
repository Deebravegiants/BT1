### Title
Mixed-nature oracle legs bypass timestamp-spread check and inflate borrow capacity - (File: contracts/price-aggregator/src/engine.rs)

### Summary
The price aggregator bounds the timestamp gap between two blended legs only when both legs are `FeedNature::Market`; a `Fundamental` leg can be arbitrarily older than the fresh leg as long as it remains inside its own `max_stale_seconds` and the pair stays inside the tolerance band. [1](#0-0) [2](#0-1)  Production configs combine Reflector market/TWAP legs with RedStone `Fundamental` legs with much larger staleness budgets, so the spread guard is not applied to real mixed-nature markets. [3](#0-2) 

### Finding Description
`Controller::borrow` is callable by an account owner or delegate and ends in post-pool solvency checks that value collateral and debt through `Context`-cached aggregator prices. [4](#0-3) [5](#0-4) [6](#0-5)  In `engine::blend`, `stale` is `primary.stale || anchor.stale || (spread_bounded && age_spread > MAX_LEG_AGE_SPREAD_SECONDS)`, where `spread_bounded` requires both legs to be `FeedNature::Market`, and the accepted price is the leg midpoint. [7](#0-6)  Therefore a stale-but-not-expired `Fundamental` anchor can pull the midpoint away from the fresh market leg while still passing staleness, deviation, and sanity checks. [8](#0-7) 

### Impact Explanation
An attacker can supply the affected collateral and call `borrow` to draw more debt than the fresh fair value permits, creating debt backed by overvalued collateral; when the stale leg catches up or the market moves, the residual loss can become bad debt that is socialized through `clean_bad_debt`. [9](#0-8)  The checked-in audit test demonstrates this shape: with the anchor lagging by 82,800 seconds under an 86,400-second staleness budget and a 1,000 bps tolerance, collateral valuation is inflated by more than 4% versus a fresh-anchor control and the oversized borrow succeeds while the control reverts with `InsufficientCollateral`. [10](#0-9) [11](#0-10) [12](#0-11) 

### Likelihood Explanation
The path is unprivileged: supply collateral, then call `Controller::borrow`; no upgrade, leaked key, or privileged oracle write is required. [4](#0-3)  Likelihood depends on a real feed delaying within its configured `max_stale_seconds`, which mainnet settings already allow for `Fundamental` RedStone legs paired with fresher Reflector legs. [13](#0-12)  This is not third-party oracle dishonesty within bands: both feeds can be individually valid, non-future, non-stale by their own budgets, and within tolerance, while their observation times are materially misaligned. [14](#0-13) [15](#0-14) 

### Recommendation
Apply an explicit cross-leg observation-time bound to every two-source blend, including Market/Fundamental pairs, instead of gating `MAX_LEG_AGE_SPREAD_SECONDS` on `spread_bounded`. [16](#0-15)  A safer rule is to reject or mark stale when `primary.timestamp.abs_diff(anchor.timestamp)` exceeds a configured maximum for the asset, or to make `Fundamental` anchors use a staleness budget comparable to the market leg when they are used in risk gates. [2](#0-1)  For scaled or LP compositions, propagate the oldest constituent timestamp into the leg timestamp so the same spread bound cannot be bypassed by nesting. [17](#0-16) 

### Proof of Concept
Use a dual oracle with a fresh Reflector market/TWAP leg at the true price and a RedStone `Fundamental` leg still inside a much larger `max_stale_seconds`; keep the two prices within the configured tolerance so `deviation` remains false. [18](#0-17) [19](#0-18)  Set the fresh leg to the post-move price and set the anchor timestamp near the edge of its staleness window with the pre-move price; `engine::blend` accepts the midpoint because the mixed natures make `spread_bounded` false. [20](#0-19) [7](#0-6)  Call `supply` on the inflated collateral asset and then `borrow` against it; the post-borrow gate uses the blended cached price, so it passes even though the same borrow fails under a fresh-anchor control. [21](#0-20) [22](#0-21)

### Citations

**File:** contracts/price-aggregator/src/engine.rs (L20-28)
```rust
/// A single source's resolved value: price, observation timestamp, whether it
/// is considered stale, and the feed nature used to decide whether the two-leg
/// age-spread bound applies.
struct Reading {
    price_wad: i128,
    timestamp: u64,
    stale: bool,
    nature: FeedNature,
}
```

**File:** contracts/price-aggregator/src/engine.rs (L122-147)
```rust
    /// Returns the error that makes this outcome unusable against `oracle`, if
    /// any. Checks, in order: an error already carried on the outcome, a missing
    /// oracle, staleness, deviation, a non-positive price, and the oracle's
    /// sanity price bounds. Returns `None` when none of these apply.
    fn failure(&self, oracle: Option<&AssetOracle>) -> Option<OracleError> {
        if let Some(err) = self.err {
            return Some(err);
        }
        let Some(oracle) = oracle else {
            return Some(OracleError::OracleNotConfigured);
        };
        if self.stale {
            return Some(OracleError::PriceFeedStale);
        }
        if self.deviation {
            return Some(OracleError::UnsafePriceNotAllowed);
        }
        if self.price_wad <= 0 {
            return Some(OracleError::InvalidPrice);
        }
        if self.price_wad < oracle.min_sanity_price_wad
            || self.price_wad > oracle.max_sanity_price_wad
        {
            return Some(OracleError::SanityBoundViolated);
        }
        None
```

**File:** contracts/price-aggregator/src/engine.rs (L420-438)
```rust
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
            Outcome {
                price_wad,
                timestamp: ts,
                first_wad: primary.price_wad,
                second_wad: anchor.price_wad,
                stale,
                deviation,
                err: None,
```

**File:** common/src/oracle/observation.rs (L30-34)
```rust
/// Largest timestamp gap between two market-nature legs of a blended price
/// before the blend is marked stale.
///
/// A TWAP leg carries the timestamp of the oldest sample in its window.
pub const MAX_LEG_AGE_SPREAD_SECONDS: u64 = 3_600;
```

**File:** configs/ops/mainnet/a69eb3dd2e905dd42025a393b11fe41b0ea99f3c710f9594a1610e8f394a7f1b.json (L20-55)
```json
        "sources": [
          {
            "Feed": {
              "provider": {
                "Reflector": {
                  "contract": "CAFJZQWSED6YAWZU3GWRTOCNPPCGBN32L7QV43XX5LZLFTK6JLN34DLN",
                  "asset": {
                    "Symbol": "BTC"
                  },
                  "read_mode": {
                    "Twap": 3
                  }
                }
              },
              "decimals": 14,
              "max_stale_seconds": 3600
            }
          },
          {
            "Feed": {
              "provider": {
                "RedStone": {
                  "contract": "CA526Y2NQWGWVVQ7RFFPGAZMU66PSYJ3UC2MTVAV4ZU7OM5BOPHDXUSG",
                  "feed_id": "BTC",
                  "nature": "Fundamental"
                }
              },
              "decimals": 8,
              "max_stale_seconds": 46800
            }
          }
        ],
        "tolerance": {
          "upper_ratio_bps": 11000,
          "lower_ratio_bps": 9091
        },
```

**File:** contracts/controller/src/lib.rs (L104-115)
```rust
    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
    }
```

**File:** contracts/controller/src/lib.rs (L160-165)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
    }
```

**File:** contracts/controller/src/risk/validation.rs (L29-57)
```rust
pub(crate) fn require_post_pool_risk_gates(env: &Env, cache: &mut Context, account: &Account) {
    if account.debt_free() {
        return;
    }

    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    assert_with_error!(
        env,
        totals.ltv_collateral >= totals.total_debt,
        CollateralError::InsufficientCollateral
    );

    spec_hooks::solvency_gate_checked(account);

    assert_with_error!(
        env,
        totals.health_factor >= Wad::ONE,
        CollateralError::InsufficientCollateral
    );

    let floor = storage::get_min_borrow_collateral_usd_wad(env);
    if floor != 0 && totals.ltv_collateral.raw() < floor {
        panic_with_error!(env, CollateralError::MinBorrowCollateralNotMet);
```

**File:** contracts/controller/src/context.rs (L141-160)
```rust
    /// Fetches missing prices in one aggregator call; retains cached prices.
    pub(crate) fn fetch_prices(&mut self, assets: &Vec<Address>) {
        let missing = collect_uncached_keys(&self.env, assets, &self.token_prices);
        if missing.is_empty() {
            return;
        }
        let fetched = external::price_aggregator::fetch_prices(&self.env, &missing);
        for (asset, feed) in fetched.iter() {
            self.token_prices.set(asset, feed);
        }
    }

    /// Returns a previously loaded price; fails if the cache has no entry.
    pub(crate) fn cached_price(&mut self, asset: &Address) -> PriceFeed {
        let raw = self
            .token_prices
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(&self.env, OracleError::OracleNotConfigured));
        (&raw).into()
    }
```

**File:** tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blend.rs (L5-13)
```rust
const ANCHOR_FROZEN_PRICE: i128 = usd(1);
const TRUE_FRESH_PRICE: i128 = usd_cents(91);
const XLM_TOLERANCE_BPS: u32 = 1000;
const ANCHOR_MAX_STALE_SECONDS: u64 = 86_400;
const ANCHOR_LAG_SECONDS: u64 = 82_800;

const XLM_SUPPLY: f64 = 100_000.0;

const TARGET_BORROW: f64 = 70_000.0;
```

**File:** tests/test-harness/tests/controller/audit_borrow_withdraw_liquidate_stale_anchor_blend.rs (L45-63)
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

    t.supply(BOB, "USDC", 500_000.0);

    t.supply(ALICE, "XLM", XLM_SUPPLY);

    let collateral_usd = t.total_collateral(ALICE);
    let borrow = t.try_borrow(ALICE, "USDC", TARGET_BORROW);

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

**File:** configs/ops/mainnet/e34577c8ccfd6564e31da2b42a78fc278e5d63264644b5c1734b632d1e5082a8.json (L20-55)
```json
        "sources": [
          {
            "Feed": {
              "provider": {
                "Reflector": {
                  "contract": "CAFJZQWSED6YAWZU3GWRTOCNPPCGBN32L7QV43XX5LZLFTK6JLN34DLN",
                  "asset": {
                    "Symbol": "USDC"
                  },
                  "read_mode": {
                    "Twap": 3
                  }
                }
              },
              "decimals": 14,
              "max_stale_seconds": 3600
            }
          },
          {
            "Feed": {
              "provider": {
                "RedStone": {
                  "contract": "CA526Y2NQWGWVVQ7RFFPGAZMU66PSYJ3UC2MTVAV4ZU7OM5BOPHDXUSG",
                  "feed_id": "USDC",
                  "nature": "Fundamental"
                }
              },
              "decimals": 8,
              "max_stale_seconds": 57600
            }
          }
        ],
        "tolerance": {
          "upper_ratio_bps": 10500,
          "lower_ratio_bps": 9524
        },
```

**File:** contracts/price-aggregator/src/observation.rs (L25-56)
```rust
    pub(crate) fn from_multi_feed(
        now_secs: u64,
        price_data: &RedStonePriceData,
        decimals: u32,
    ) -> Option<Self> {
        let package_ts = millis_to_seconds(price_data.package_timestamp);
        let write_ts = millis_to_seconds(price_data.write_timestamp);
        if is_future_at(now_secs, package_ts) || is_future_at(now_secs, write_ts) {
            return None;
        }
        let raw_price = try_u256_to_i128(&price_data.price)?;
        Some(OracleObservation {
            price_wad: try_normalize_positive_price(raw_price, decimals)?,
            timestamp: write_ts.min(package_ts),
        })
    }

    /// Builds an observation from a Reflector price payload. Rejects the
    /// observation if its timestamp exceeds `now_secs + MAX_FUTURE_SKEW_SECONDS`
    /// or if the price fails decimal normalization.
    pub(crate) fn from_reflector(
        now_secs: u64,
        price_data: &ReflectorPriceData,
        decimals: u32,
    ) -> Option<Self> {
        if is_future_at(now_secs, price_data.timestamp) {
            return None;
        }
        Some(OracleObservation {
            price_wad: try_normalize_positive_price(price_data.price, decimals)?,
            timestamp: price_data.timestamp,
        })
```

**File:** tests/test-harness/src/oracle/config.rs (L34-69)
```rust
pub fn redstone_source_with_max_stale(
    contract: &Address,
    feed_id: &String,
    max_stale_seconds: u64,
) -> PriceSource {
    multi_feed_source(
        ProviderRef::RedStone(multi_feed_ref(contract, feed_id)),
        max_stale_seconds,
    )
}

fn xoxno_source_with_decimals(contract: &Address, feed_id: &String, decimals: u32) -> PriceSource {
    let mut source = multi_feed_source(
        ProviderRef::Xoxno(multi_feed_ref(contract, feed_id)),
        DEFAULT_REDSTONE_MAX_STALE_SECONDS,
    );
    if let PriceSource::Feed(feed) = &mut source {
        feed.decimals = decimals;
    }
    source
}

fn multi_feed_source(provider: ProviderRef, max_stale_seconds: u64) -> PriceSource {
    PriceSource::Feed(FeedSource {
        provider,
        decimals: MULTI_FEED_DECIMALS,
        max_stale_seconds,
    })
}

fn multi_feed_ref(contract: &Address, feed_id: &String) -> MultiFeedRef {
    MultiFeedRef {
        contract: contract.clone(),
        feed_id: feed_id.clone(),
        nature: FeedNature::Fundamental,
    }
```

**File:** tests/test-harness/src/oracle/config.rs (L191-207)
```rust
fn oracle(
    env: &Env,
    items: &[PriceSource],
    tolerance_bps: u32,
    min_sanity_price_wad: i128,
    max_sanity_price_wad: i128,
) -> AssetOracle {
    let sources = sources(env, items);
    AssetOracle {
        asset_decimals: 7,
        max_price_stale_seconds: stale_ceiling(&sources),
        sources,
        tolerance: tolerance_band(env, tolerance_bps),
        independence: IndependencePolicy::RequireDisjoint,
        min_sanity_price_wad,
        max_sanity_price_wad,
    }
```
