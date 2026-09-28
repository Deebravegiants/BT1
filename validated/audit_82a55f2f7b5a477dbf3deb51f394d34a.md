### Title
Deposits accepted on a stale-priced asset are trapped — every exit path reverts `PriceFeedStale` - (File: contracts/controller/src/positions/supply.rs)

### Summary
`supply` admits a new collateral leg for an asset whose oracle feed is stale, because the entry path never resolves a price for the supplied asset. Every exit path — `withdraw`, `liquidate`, and `clean_bad_debt` — runs `enforce_post_pool_solvency`, which resolves strict prices for **all** of the account's legs and reverts with `PriceFeedStale` while any leg is stale. A user who supplies after the feed's freshness window lapses cannot take the funds back out; if the feed never recovers, the freeze is permanent — the exact analog of "deposit after `endTime` → withdraw blocked forever".

### Finding Description
- `process_supply` in `contracts/controller/src/positions/supply.rs:40-74` calls `process_deposit` (`supply.rs:100-136`), which only runs `validate_position_entry_gates`, measures the token transfer, and merges pool share mutations. No price resolution and no post-pool solvency check are performed for a pure supply, so a stale/dead feed on the supplied asset does not block entry.
- `process_withdraw` (`supply.rs:140-169`) calls `enforce_post_pool_solvency` at `supply.rs:157-158` after `settle_withdraw`; the solvency check in `positions/mod.rs` prices every supply and debt leg via the Context-cached strict oracle, and a stale observation on any leg panics with `PriceFeedStale` (error 206), reverting the whole withdrawal including legs with fresh feeds.
- The same strict pricing gates `liquidate` and `clean_bad_debt`, so neither the owner nor a liquidator can unwind the position while the feed is stale.
- This is confirmed by the existing test `audit_supply_setup_blocks_liquidation_via_stale_dust_leg` in `tests/test-harness/tests/controller/audit_supply_stale_shield.rs:26-58`: `t.try_supply(ALICE, "WBTC", 0.001)` succeeds while WBTC's feed is stale, and subsequently `try_liquidate`, `try_clean_bad_debt_by_id`, and `try_withdraw` all revert with `PRICE_FEED_STALE` until the feed is refreshed.
- The asymmetry is the bug: entry uses no price at all for the supplied asset, while exit requires a fresh price for it. The deposit is committed to the pool before any freshness requirement is enforced.

### Impact Explanation
Temporary freezing of user funds in the ordinary case (the leg cannot be withdrawn until the feed resumes), and permanent freezing if the feed is abandoned or permanently stale — the user-supplied tokens sit in the pool with no reachable exit path (`withdraw`, `swap_collateral`, `repay_debt_with_collateral`, `flash_position`-driven exits all hit the same solvency price check). The freeze also propagates: the trapped stale leg blocks liquidation and `clean_bad_debt` of the entire account, and can poison a multi-asset withdrawal batch since `enforce_post_pool_solvency` prices all legs atomically.

### Likelihood Explanation
Any unprivileged user can trigger this by calling `supply(account_id, spoke_id, [(hub_asset, amount)])` for an asset whose feed is older than the configured staleness bound — reachable by the owner or a delegate, and by any third party topping up an existing leg (`supply.rs:78-97`). Staleness requires only oracle downtime or a stopped provider round, not manipulation. Because supply is the only unrestricted entry and there is no freshness gate on it, the trap is reachable whenever a feed lapses; recovery depends on the provider, which may never resume.

### Recommendation
Reject supply of an asset whose strict price cannot be resolved: resolve and cache the supplied asset's price inside `validate_position_entry_gates` (or `process_deposit`) before transferring tokens, so entry fails with `PriceFeedStale` instead of admitting an unpriceable leg. Alternatively, exempt the withdrawn leg's own price from `enforce_post_pool_solvency` when reducing a supply position cannot worsen health — but the simpler fix matching the report's recommendation is a freshness `require` at deposit time.

### Proof of Concept
The behavior is already demonstrated by `tests/test-harness/tests/controller/audit_supply_stale_shield.rs`:

```rust
// WBTC feed is set stale (timestamp now - 3600)
t.mock_reflector_client().set_price_at(&wbtc, &usd(60_000), &(now - 3_600));

// Entry succeeds despite the dead feed — the analog of deposit() after endTime
let plant = t.try_supply(ALICE, "WBTC", 0.001);
assert!(plant.is_ok());
t.assert_position_exists(ALICE, "WBTC", PositionType::Supply);

// Every exit path reverts while the feed is stale
assert_contract_error(t.try_withdraw(ALICE, "WBTC", 0.0001), errors::PRICE_FEED_STALE);
assert_contract_error(t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0), errors::PRICE_FEED_STALE);
assert_contract_error(t.try_clean_bad_debt_by_id(alice_id), errors::PRICE_FEED_STALE);
```

Root cause: `process_deposit` never prices the incoming leg (`contracts/controller/src/positions/supply.rs:107-135`), while `process_withdraw` unconditionally runs `enforce_post_pool_solvency` over all legs (`supply.rs:157-158`), so the deposited funds are committed before the freshness condition that governs their release is ever checked.