### Title
A single unavailable collateral price poisons liquidation and bad-debt cleanup - ([File: contracts/controller/src/risk/totals.rs](contracts/controller/src/risk/totals.rs))

### Summary
The controller values **every** supply and borrow leg before it can liquidate or socialize an account. `calculate_account_risk_totals` loads prices for the complete portfolio, and the price aggregator resolves those prices strictly: one unusable `PriceKey` causes the entire `prices` call to revert. Consequently, an account containing even a dust-sized collateral position in an Aquarius LP whose configured `min_pool_value_wad` is not met cannot be liquidated or cleaned up until that LP price resolves again.

### Finding Description
`liquidate` calls `build_liquidation_plan`, which calls `calculate_account_risk_totals` before checking the account health factor. That function calls `Context::load_markets` over the union of all supply and borrow position keys. `load_markets` fetches every unique token price through the aggregator's strict `prices` entry point.

The aggregator's `prices` implementation resolves each requested key and panics if any key is unusable. For an Aquarius LP source, `read` returns `InsufficientAquariusLiquidity` whenever the calculated pool value is below `min_pool_value_wad`. That error therefore aborts the whole controller transaction, including repayment and seizure of otherwise healthy, priced collateral.

The same all-portfolio valuation is also used by permissionless `clean_bad_debt` and owner-gated bad-debt cleanup, so the unavailable collateral leg blocks both liquidation and residual-debt socialization.

### Impact Explanation
An unprivileged borrower can hold a listed Aquarius LP token as one collateral leg. If that pool's fair value falls below the configured liquidity floor, every call to `liquidate`, `clean_bad_debt`, or `force_socialize_bad_debt` for the account reverts while attempting to price that leg, regardless of the size of the LP position or the value of the other collateral.

During the outage, the borrower's debt cannot be removed even when the remaining collateral legs have valid prices and sufficient value to satisfy a partial liquidation. Interest continues accruing against suppliers, and residual bad debt cannot be socialized. This can convert a temporary market disruption into delayed loss allocation and protocol insolvency.

### Likelihood Explanation
The borrower only needs an ordinary account with:

1. debt in a listed asset;
2. at least one listed Aquarius LP collateral position;
3. the LP pool's reported fair value below its configured `min_pool_value_wad`; and
4. a health factor below `1e18`.

The first two conditions are reachable through the normal unprivileged `supply` and `borrow` entry points. The third can occur without governance or contract privileges when liquidity leaves the referenced Aquarius pool. No compromised oracle signer, privileged flag, malformed token, or upgrade is required.

### Recommendation
Do not require a valid price for collateral legs that cannot materially affect the liquidation decision. At minimum:

- price liquidation inputs and debt legs strictly;
- isolate collateral-leg valuation failures;
- treat an unpriceable leg as zero-value collateral after bounding its effect, or permit a mode that seizes only validly priced legs;
- ensure `clean_bad_debt` retains a path for accounts whose unpriceable collateral is below the configured dust threshold; and
- consider a conservative emergency plan that excludes an unavailable collateral leg rather than aborting the entire liquidation transaction.

Any such change must preserve the pro-rata economics and prevent borrowers from profitably hiding valuable collateral behind an intentionally unavailable price.

### Proof of Concept
1. Create a controller account by calling `supply` with two listed collateral assets: a normally priced asset `C` and a listed Aquarius LP token `L`.
2. Call `borrow` for debt asset `D`, keeping the account healthy.
3. Reduce the referenced Aquarius pool's value below `AquariusLpSource::min_pool_value_wad` by withdrawing liquidity from that pool.
4. Move the account below `HF = 1e18` through ordinary price movement or interest accrual.
5. As any liquidator, call `liquidate(liquidator, account_id, debt_payments, SeizeMode::Credit(0))`.

`build_liquidation_plan` calls `calculate_account_risk_totals`, which calls `Context::load_markets` for both `C` and `L`. `fetch_prices` invokes `PriceAggregator::prices`; resolving `L` reaches `aquarius::read`, which returns `InsufficientAquariusLiquidity`, and `engine::force` reverts. The entire liquidation therefore fails before repayment or seizure.

A subsequent permissionless `clean_bad_debt(caller, account_id)` fails for the same reason in `socialize_bad_debt`, even if all non-LP prices are valid and the account otherwise satisfies the bad-debt gate.