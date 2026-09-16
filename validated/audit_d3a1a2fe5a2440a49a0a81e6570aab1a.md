### Title
Uniswap V4 venue pricing ignores pool fee tier and price impact, letting solvers be drained by orders sized against thin exotic-token pools - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
Simplex's Uniswap-V4 "venue pricing" path (used to price and fund cross-asset intent-gateway orders with an exotic token like cNGN, e.g. `USDC/cNGN`) prices a fill purely from the pool's raw mid price (`sqrtPriceX96`), never applying the pool's own fee tier and never accounting for size/price-impact, before extending that mid linearly across the whole order notional. This is the same bug class as M-18: a swap/price route is priced against a hardcoded/selected pool without regard to that pool's real depth or fee, so as soon as real liquidity is thin (or an order is large relative to depth), the counterparty absorbing the difference (here, the solver funding the fill) suffers unbounded loss instead of the on-chain execution cost being reflected in the quote.

### Finding Description
When a trading pair has no static bid/ask curves and `[vault.uniswapV4]` positions are configured, Simplex derives its quoted price for the pair from the "most-liquid qualifying" Uniswap V4 position rather than from static curves: [1](#0-0) 

The actual pricing implementation, `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, reads the pool's `sqrtPriceX96` and returns `sdkPool.token0Price`/`token1Price` directly as the USD price of the exotic token: [2](#0-1) 

As documented in the project's own analysis of this flow, this price is the **raw pool mid**, the pool's fee tier is read and stored on the hydrated position but **never applied to the price**, there is **no size or price-impact term**, and `computeLegPolicyOutput` extends this mid **linearly** across the entire notional being priced: [3](#0-2) 

The only safeguard on this path, `checkPriceGuard`, only rejects a fill if the pool quote deviates from a static `referencePrice` by more than `maxDeviationBps` — it protects against a stale/manipulated *price*, not against *execution cost*: [4](#0-3) 

Because the same code path is used both to quote intent-gateway orders and to size withdrawals from the V4 position when the solver has to top up destination-chain inventory (`[vault.uniswapV4]` withdrawal/funding), a pair whose configured position is thin — or that thins out over time exactly as in the sDAI/sUSDe case — causes the solver's actual swap cost through that same pool to exceed what was quoted to the user. This is the identical root cause pattern as M-18: a fixed swap/price venue is trusted for pricing without regard to its live depth or fee, and the deficit is unrecoverable slippage borne by whoever executes against real liquidity. Here that party is Simplex, the intent solver explicitly listed as an in-scope actor for this analog scan.

### Impact Explanation
An order submitter (an unprivileged actor placing an IntentGateway order) can size an order against a venue-priced pair whose configured Uniswap V4 position has thin liquidity relative to the order notional. Because the quote never reflects the fee tier or the price impact of executing that size, the solver is forced to fill at the quoted (near-mid) price while its actual swap through the same pool realizes a materially worse rate. Repeated or size-optimized orders against a thinning pool extract solver funds order after order, a "loss of funds due to unnecessary slippage" mirroring the External Report's characterization, except the funds lost belong to the solver funding fills on Hyperbridge's IntentGateway rather than a Notional vault. If the position is drained over time (analogous to sDAI/sUSDe's declining balance), the miscalibration only worsens, since `checkPriceGuard`'s static reference check does not track depth degradation.

### Likelihood Explanation
Any user can place an IntentGateway order for a venue-priced pair; no privileged role is required. The pricing code path is exercised on every fill of a curveless, pool-priced pair, and the fee/impact omission is confirmed directly in the project's own documentation of the flow, not speculation. The main constraint is operator configuration (an LP must have chosen pool-based pricing without curves for a given pair), but this is a documented, supported configuration, not a misconfiguration.

### Recommendation
`computeDirectPoolPriceUsd`/`computeLegPolicyOutput` should incorporate the pool's fee tier and an on-chain price-impact/quote-for-size calculation (e.g., using the V4 quoter against the leg's actual notional) rather than linearly extending the raw mid price, and `checkPriceGuard` should additionally bound the pool's available depth at the requested size, not just its mid-price deviation from a static reference.

### Proof of Concept
Not applicable — this is a documented pricing/architecture gap (`sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md`) rather than a runnable exploit found in this scan; a concrete PoC would require standing up a Simplex instance with a `[vault.uniswapV4]` position on a thin pool and submitting a sized order, which exceeds what static code review here can execute.

### Citations

**File:** docs/content/developers/evm/simplex/pricing.mdx (L40-46)
```text
## Pool-Based Pricing

When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.

With Uniswap V4 positions configured, you can **omit** `bidPriceCurve` and `askPriceCurve` on the pair. Pool pricing requires the pair's `token0` to be a USD stablecoin, and same-token pairs always need their curve. The optional **`spreadBps`** field (basis points) sets the slippage tolerance for on-chain LP redemptions; defaults to `50` (0.50%).

Uniswap V4 venue pricing uses pools that pair the exotic token with **USDC or USDT** (addresses from your chain config). When multiple positions exist for the same exotic token on a chain, the most-liquid qualifying pool's price is used.
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-84)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.

```toml lineNumbers
[vault.uniswapV4]
# referencePrice is the expected cNGN per USD;
# reject if the quote is more than 2% off.
# The two go together — one without the other is rejected.
[[vault.uniswapV4.positions]]
chain           = "EVM-8453"
tokenId         = "2087350"
referencePrice  = "1575"
maxDeviationBps = 200
```
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-275)
```typescript
	private computeDirectPoolPriceUsd(
		pos: HydratedV4Position,
		sdkPool: V4Pool,
		chain: string,
	): { exoticToken: string; priceUsd: Decimal } | null {
		const usdc = this.configService.getUsdcAsset(chain).toLowerCase()
		const usdt = this.configService.getUsdtAsset(chain).toLowerCase()
		const c0 = pos.currency0.toLowerCase()
		const c1 = pos.currency1.toLowerCase()

		if (c0 === usdc || c0 === usdt) {
			// currency0 is stable → exotic is currency1
			// token1Price = "token0 per token1" = USD per exotic
			return {
				exoticToken: c1,
				priceUsd: new Decimal(sdkPool.token1Price.toFixed(18)),
			}
		}

		if (c1 === usdc || c1 === usdt) {
			// currency1 is stable → exotic is currency0
			// token0Price = "token1 per token0" = USD per exotic
			return {
				exoticToken: c0,
				priceUsd: new Decimal(sdkPool.token0Price.toFixed(18)),
			}
		}

		return null
	}
```

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
