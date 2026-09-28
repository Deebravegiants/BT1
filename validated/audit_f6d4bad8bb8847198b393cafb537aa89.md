### Title
Unpriced stale dust collateral leg permanently bricks liquidation and bad-debt cleanup of the attacker's own account - ([File: contracts/controller/src/positions/supply.rs](contracts/controller/src/positions/supply.rs))

### Summary
The BIND analog is "a malformed record crashes the service": here the "malformed record" is a supply-position leg that carries no validated price. `process_supply` never reads the oracle for the supplied asset — `process_deposit` only calls `validate_position_entry_gates`, measures the token receipt, and credits pool shares — so a borrower can plant a dust supply leg in an asset whose feed is already stale or permanently dead. Every risk-dependent path (`liquidate`, `clean_bad_debt`, `withdraw`, `repay_debt_with_collateral`, `swap_collateral`) must obtain *every* required price in the account context under the fail-closed rule, so the single poisoned leg aborts them all with `PriceFeedStale`. The result is an underwater account no liquidator can touch and no keeper can socialize while the feed stays broken.

### Finding Description
`process_supply` at `contracts/controller/src/positions/supply.rs:40-74` performs caller auth, third-party slot checks, and `process_deposit`, which iterates legs calling `transfer_amount_measured` and `get_or_create_supply_position` without any price read (`supply.rs:100-136`). Tests confirm this is intentional behavior: `test_stale_price_allows_supply_without_price_read` in `tests/test-harness/tests/oracle/tolerance/staleness.rs` and `audit_supply_setup_blocks_liquidation_via_stale_dust_leg` in `tests/test-harness/tests/controller/audit_supply_stale_shield.rs` both assert supply succeeds on a stale feed.

Conversely, `process_liquidation` (`positions/liquidation/mod.rs:36`) and `socialize_bad_debt` (`mod.rs:212-238`) build risk totals via `risk::calculate_account_risk_totals`, which prices *all* supply and borrow positions through `Context::cached_price`; the strict read panics on staleness per INV-ORACLE-01/ADR-0005 fail-closed valuation. The audit test demonstrates the full kill chain:

- attacker supplies a 0.001 WBTC leg while its Reflector timestamp is 3600s old — accepted (`audit_supply_stale_shield.rs:26-35`)
- after USDC crashes 50%, `try_liquidate` reverts `PRICE_FEED_STALE` (`:51-52`)
- permissionless `try_clean_bad_debt` reverts `PRICE_FEED_STALE` (`:54-55`)
- even the attacker cannot `withdraw` the leg (`:57-58`), so the poison is unremovable while the feed is dead.

There is no permissionless path that skips pricing for a supply leg: cleanup requires "valid required prices" per INV-LIQ-04, and `no_seize`/listing-flag bypasses do not waive pricing (`force-socialize-bad-debt.md:34-35`). Only governance-timelocked `force_socialize_bad_debt` helps, and it *also* requires valid prices, so it cannot rescue the account either.

### Impact Explanation
Temporary freezing of funds escalating to protocol insolvency. While the feed is stale, every liquidation reverts before moving a token, so the attacker rides an underwater position indefinitely, accruing borrow interest the protocol can never collect. If the feed never recovers (delisted asset, dead provider — realistic for long-tail collateral), the account becomes permanently unliquidatable and uncleanable: its debt is trapped in the borrow index while collateral cannot be seized or written off, producing realized bad debt borne by suppliers. The attacker's own collateral is also frozen, but a rational attacker sizes the dust leg (sub-cent value) so the poisoned collateral is negligible relative to the avoided liquidation. This qualifies as "temporary freezing of funds" at minimum and "protocol insolvency" in the permanent-feed-death case.

### Likelihood Explanation
Requires only: a listed collateral asset with a feed that goes stale (ordinary oracle outages happen regularly), plus a sub-dust deposit the attacker places either speculatively on any account with debt (defense-in-depth planting costs nothing once the position slot exists) or reactively the moment staleness begins. The attacker must time the plant to a stale window since supply itself doesn't check price, but staleness is publicly observable and predictable (heartbeat-based feeds go stale on a known schedule if updates stop). No privileged access, no flash loan, no capital at risk beyond the dust deposit. Rated Medium likelihood: contingent on an oracle outage, but the protocol explicitly accepts feeds that can go stale.

### Recommendation
Price the new leg at entry, or at least bound the damage:

1. In `process_deposit`/`validate_position_entry_gates`, call `cache.cached_price(&hub_asset.asset)` (or a strict `fetch_prices` for newly created supply positions) so a stale-priced asset cannot enter a supply book. This closes the plant at zero cost to normal users.
2. Alternatively/additionally, make the liquidation plan skip zero-valued or unpriceable *dust* supply legs: when a supply position's cached raw amount is below the market dust floor, treat its collateral contribution as zero instead of demanding a valid price, so one dead feed cannot veto the whole pro-rata liquidation and `clean_bad_debt`.
3. Ensure `withdraw` of a debt-free-position leg (account has other collateral backing its debt) doesn't need that leg's price, letting the poisoned leg be removed.

### Proof of Concept
Reproduced by the existing harness test `audit_supply_setup_blocks_liquidation_via_stale_dust_leg` (`tests/test-harness/tests/controller/audit_supply_stale_shield.rs`):

```rust
t.set_oracle_single_spot("WBTC");               // WBTC uses a Reflector leg
t.supply(ALICE, "USDC", 10_000.0);              // attacker collateral
t.borrow(ALICE, "ETH", 3.0);                    // attacker debt

t.advance_time(5_000);
t.mock_reflector_client()
    .set_price_at(&wbtc, &usd(60_000), &(now - 3_600));  // stale WBTC feed

t.try_supply(ALICE, "WBTC", 0.001).unwrap();    // poison leg accepted, no price read

t.set_price("USDC", usd_cents(50));             // collateral crashes; HF < 1

try_liquidate(..)      -> Err(PRICE_FEED_STALE)  // liquidation bricked
try_clean_bad_debt(..) -> Err(PRICE_FEED_STALE)  // socialization bricked
try_withdraw("WBTC")   -> Err(PRICE_FEED_STALE)  // poison unremovable
```

A twin account (BOB) with identical risk but no WBTC leg liquidates normally (`:43-47`), isolating the stale dust leg as the sole blocker.