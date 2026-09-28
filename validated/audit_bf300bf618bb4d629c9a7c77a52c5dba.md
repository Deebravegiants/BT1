### Title
A borrower can permanently block liquidation and bad-debt cleanup of their own insolvent account by adding a dust Aquarius LP collateral leg and draining that LP pool below `min_pool_value_wad` - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
The Mattermost report's bug class is an unprivileged resource/read path that lets an attacker deny service. The direct analog in XOXNO Lending: every valuation-dependent controller call (health factor, liquidation, `clean_bad_debt`, threshold refresh) must resolve prices for *every* asset in the account's books through the price aggregator. An Aquarius LP share price read fails closed whenever the underlying pool's WAD value falls below the configured `min_pool_value_wad`. Because `supply` accepts a dust amount of any listed collateral without a price read, a borrower who is also an Aquarius LP can attach a dust LP leg to an indebted account, then withdraw their own liquidity from that Aquarius pool. From that point on the price read returns `InsufficientAquariusLiquidity`, the account can never be liquidated or cleaned up, and its debt accrues into protocol bad debt.

### Finding Description
`aquarius::read` in `contracts/price-aggregator/src/providers/aquarius.rs` computes `pool_value_wad = price_wad * total_shares / share_unit` and returns `Err(OracleError::InsufficientAquariusLiquidity)` when it is below `lp.min_pool_value_wad` (lines 118-122). It likewise returns `NoLastPrice` when `aquarius_pool_reserves_call`, `aquarius_total_shares_call`, or `aquarius_amp_call` fail (lines 90-110).

On the controller side, `liquidate` (and every risk-gated entrypoint) builds a `Context` and calls `risk::calculate_account_risk_totals` over *all* supply and borrow positions (`contracts/controller/src/positions/liquidation/mod.rs`, lines 105-110). Any required price that is invalid aborts the whole transaction — this is confirmed in `docs/reference/architecture.md` ("An invalid required price aborts the operation") and enumerated in the threat model (DoS.1): "an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization."

Reachable path for a single unprivileged address:
1. `supply` a dust amount of a listed Aquarius LP share token onto a borrowing account (supply does not require a valid price).
2. `borrow` against other collateral to near the limit.
3. Wait for HF < 1 (or push it below via own Aquarius trade that also crashes a leg price).
4. As an LP in that Aquarius pool, call Aquarius `withdraw` to pull reserves below the value floor.
5. Every subsequent `liquidate`, `clean_bad_debt`, `update_account_threshold` (full-risk mode), `withdraw`/`borrow` touching that account reverts inside the aggregator.

### Impact Explanation
Protocol insolvency / permanently unenforceable debt. The attacker's debt position can never be liquidated and can never be cleaned up as bad debt, so its interest accrues without bound while the collateral claim is frozen. Suppliers' claims on the affected markets remain booked, but the protocol cannot recover the underwater debt — the bad debt is permanently socialized. Cost to the attacker is one dust LP deposit plus their own LP withdrawal (which they can re-add later; the shield persists only while liquidity stays low, but they control it for free). Impact category: protocol insolvency plus permanent freezing of the seized-collateral path.

### Likelihood Explanation
High. Requires no privileged role, no leaked keys, and no oracle dishonesty: Aquarius reserves and share supply are permissionlessly mutable on-chain reads, and LP withdrawal is a normal venue operation open to anyone holding shares. The dust-leg setup is a single `supply` call. The mechanism is explicitly acknowledged as a reachable threat boundary in the repo's own threat model (DoS.1), and the price-failure branch in `aquarius::read` is a hard `Err`, not a degraded quote, so there is no degraded-liquidation path to route around it.

### Recommendation
- Do not let a single collateral leg's price outage veto the entire valuation: for liquidation eligibility, compute HF over the subset of legs with valid prices (treating unreadable collateral as zero value) so that accounts are liquidatable against their priced collateral, or allow seizure restricted to legs with valid prices.
- Alternatively, allow `clean_bad_debt` and `liquidate` to skip legs whose price read fails while still seizing/valuing the rest.
- At listing time, require `min_pool_value_wad` to be set materially above the maximum plausible borrow collateralized by that LP token, and monitor Aquarius pool TVL to pause borrowing before the floor can be crossed by ordinary withdrawals.

### Proof of Concept
1. Governance lists Aquarius LP share token `LP` in hub 1 with `min_pool_value_wad = X` via `ConfigureAssetOracle`.
2. Attacker: `controller.supply(caller, account_id=0, spoke_id, assets=[(hub(1, USDC), 100_000e6)])`; `controller.borrow(caller, acct, [(hub(1, USDT), 90_000e6)])`; then `controller.supply(caller, acct, spoke_id, [(hub(1, LP), 1)])` — a dust LP leg.
3. Price moves: HF < 1. Liquidator calls `controller.liquidate(...)` — still works.
4. Attacker calls `aquarius_pool.withdraw(...)` removing their liquidity so `pool_value_wad < X`.
5. `controller.liquidate(liquidator, acct, [(hub(1, USDT), amount)], SeizeMode::Transfer)` → aggregator `read` hits `pool_value_wad < lp.min_pool_value_wad` → `OracleError::InsufficientAquariusLiquidity` → `Context` fails → transaction aborts. Same for `clean_bad_debt(acct)` and `update_account_threshold`.
6. The account remains liquidatable-in-fact but unreachable; debt accrues at `debt_index` until socialization via governance runbook — which is also blocked per the threat model.