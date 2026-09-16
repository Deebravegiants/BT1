I found the exact analog: `BidManager.sortByRawAmountFallback` in the SDK's bid-selection path sums raw token amounts across an order's multiple output legs (a "set" of `TokenInfo`s) without any decimal normalization — directly mirroring the MetaVesT bug class where mixing items of different decimals in one aggregated sum/comparison gives an exponential advantage to the higher-decimal asset.

### Title
Bid ranking sums raw amounts of tokens with different decimals, letting a high-decimal-token bid win the auction regardless of true value - (File: sdk/packages/sdk/src/protocols/intents/BidManager.ts)

### Summary
`sortByRawAmountFallback`, the fallback path used whenever DEX pricing is unavailable for a mixed-output order, adds together the raw `amount` fields of every output token in the order and in each competing bid, then ranks bids purely by that sum. Because `TokenInfo.amount` is expressed in each token's own smallest unit, and no decimal normalization is applied before summing, tokens with more decimals dominate the sum by orders of magnitude — the same "different decimals in the same set" flaw described in the reference report, here applied to bid/output-token aggregation instead of governance-power aggregation.

### Finding Description
`sortMixedOutputs` calls `sortByRawAmountFallback` whenever `computeOutputsUsdValue` cannot price the order's outputs (any RPC/DEX-quote failure, unsupported token, etc.) — a condition fully reachable by an unprivileged actor since it depends only on order composition and external quote availability: [1](#0-0) 

Inside the fallback, both the order's required outputs and each bid's outputs are summed as raw `Decimal` amounts with no decimals lookup or scaling: [2](#0-1) 

and bids are ranked strictly by that unnormalized total: [3](#0-2) 

Contrast this with the properly decimals-aware paths in the same file (`computeStablesUsdValue`, `computeOutputsUsdValue`), which explicitly divide by `10 ** decimals` before summing/comparing: [4](#0-3) [5](#0-4) 

This is the exact bug class from the report: a "set" (here, a multi-output order's `TokenInfo[]`) mixes items whose decimals differ, and the aggregation routine treats every unit identically instead of normalizing, so tokens with higher decimals (e.g., an 18-decimal token next to a 6-decimal USDC/USDT-style token) get an exponential (10^12-scale) numerical advantage in the resulting sum — mirroring the linked MetaVesTController governing-power miscalculation.

### Impact Explanation
When the fallback path is taken, a solver can win the user-facing bid auction (`selectAndExecuteBest`/`sortBids`) by offering a trivial amount of a high-decimal token instead of genuinely competitive value, because its raw amount inflates the "total offered" sum far beyond bids that are actually worth more in USD terms. The order's user ends up selecting and executing the objectively worse bid, receiving far less real value than a rationally-sorted bid would have offered — a direct value-manipulation of intent settlement reachable from a single order/bid submission, i.e., unauthorized/incorrect app-level selection akin to a route/logic failure rather than pure UI cosmetics, since `selectAndExecuteBest` actually executes the chosen bid on-chain.

### Likelihood Explanation
The fallback triggers whenever `computeOutputsUsdValue` returns `null` — e.g., a token pair with no direct/${WETH} Uniswap route, a temporary RPC/quote failure, or any output token the config service cannot price. Any solver can construct an order/bid pair using such a token to hit this path deliberately, making exploitation straightforward and requiring no privileged access — only crafting order outputs that mix a low-decimal token (e.g. 6-decimal USDC-like) with a high-decimal, hard-to-price token.

### Recommendation
In `sortByRawAmountFallback`, resolve each token's `decimals` (the same helper `getTokenDecimals`/`getStableDecimals` pattern already used elsewhere) and normalize every amount (e.g., to 18 decimals) before summing or comparing, exactly as `computeStablesUsdValue`/`computeOutputsUsdValue` already do. Alternatively, refuse to rank/select bids via the raw-amount fallback entirely when outputs cannot be priced, and instead require per-token minimum-amount checks (compare each output token independently against its own required amount) rather than a cross-token raw sum.

### Proof of Concept
1. Construct an order with two output legs: `Leg A` = 1 unit of `TokenX` (18 decimals, e.g. a token with no configured DEX route so `computeOutputsUsdValue` returns `null`), `Leg B` = 1000 USDC (6 decimals) — required amounts: `TokenX.amount = 1e18` (1 whole token), `USDC.amount = 1000e6` (1000 USDC).
2. Solver "cheap" bids: `TokenX.amount = 1e18` (worth ~$0), `USDC.amount = 1000e6` (worth $1000) → raw sum ≈ `1e18 + 1000e6 ≈ 1.000001e18`.
3. Solver "generous" bids: `TokenX.amount = 2e18` (still worthless), `USDC.amount = 2000e6` (worth $2000) → raw sum ≈ `2.000002e18`.
4. Solver "attacker" bids: `TokenX.amount = 1e21` (1000 TokenX, still economically worthless since unpriceable/illiquid), `USDC.amount = 1e6` (only $1) → raw sum ≈ `1.000001e21`, which dwarfs both legitimate bids purely because `TokenX`'s 18-decimal raw units vastly outweigh USDC's 6-decimal raw units in the naive sum in `sortByRawAmountFallback` (lines 443-466), even though the attacker's bid delivers far less real value.
5. `sortByRawAmountFallback` ranks "attacker" first; `selectAndExecuteBest` executes it, and the user receives a bid worth a fraction of the alternatives despite having "won" the sort.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L393-399)
```typescript
	private async sortMixedOutputs(bids: Bid[], orderOutputs: TokenInfo[], chainId: string): Promise<Bid[]> {
		const requiredUsd = await this.computeOutputsUsdValue(orderOutputs, chainId)

		if (requiredUsd === null) {
			console.warn("[BidManager] sortMixedOutputs: output tokens unpriceable, falling back to raw-amount sort")
			return this.sortByRawAmountFallback(bids, orderOutputs)
		}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L443-466)
```typescript
		for (const bid of bids) {
			let valid = true
			let totalOffered = new Decimal(0)
			let rejectReason = ""

			for (const required of orderOutputs) {
				const matching = bid.outputs.find((o) => o.token.toLowerCase() === required.token.toLowerCase())
				if (!matching) {
					valid = false
					rejectReason = `missing output token=${required.token}`
					break
				}
				totalOffered = totalOffered.plus(new Decimal(matching.amount.toString()))
			}

			if (!valid) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED (fallback): ${rejectReason}`)
				continue
			}

			const totalRequired = orderOutputs.reduce(
				(acc, o) => acc.plus(new Decimal(o.amount.toString())),
				new Decimal(0),
			)
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L468-484)
```typescript
			if (totalOffered.lt(totalRequired)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate (fallback) ` +
						`(offered=${totalOffered.toString()}, required=${totalRequired.toString()}, ` +
						`covers=${totalOffered.div(totalRequired).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED (fallback): totalOffered=${totalOffered.toString()}`,
				)
			}

			validBids.push({ bid, totalOffered })
		}

		validBids.sort((a, b) => b.totalOffered.comparedTo(a.totalOffered))
		return validBids.map(({ bid }) => bid)
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L529-537)
```typescript
	private computeStablesUsdValue(outputs: TokenInfo[], chainId: string): Decimal {
		let total = new Decimal(0)
		for (const output of outputs) {
			const tokenAddr = bytes32ToBytes20(output.token)
			const decimals = this.getStableDecimals(tokenAddr, chainId)
			total = total.plus(new Decimal(output.amount.toString()).div(new Decimal(10).pow(decimals)))
		}
		return total
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L561-575)
```typescript
				const decimals = this.getStableDecimals(tokenAddr, chainId)
				totalUsd = totalUsd.plus(new Decimal(output.amount.toString()).div(new Decimal(10).pow(decimals)))
				continue
			}

			try {
				const usdcAmount = await this.quoteTokenToUsdc(
					tokenAddr,
					output.amount,
					wethAddr,
					usdcAddr,
					chainId,
					client,
				)
				totalUsd = totalUsd.plus(new Decimal(usdcAmount.toString()).div(new Decimal(10).pow(usdcDecimals)))
```
