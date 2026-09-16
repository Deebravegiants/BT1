### Title
Bid selection between USDC/USDT solver bids treats both stablecoins as always worth exactly $1, letting a depegged-stable bid win over a genuinely higher-value bid - (File: sdk/packages/sdk/src/protocols/intents/BidManager.ts)

### Summary
`BidManager.sortAllStables` (and its helper `computeStablesUsdValue`) ranks competing solver bids for an order whose required outputs are entirely USDC/USDT by summing "normalised USD values" while treating each stable **as $1**, exactly the flawed assumption the external report flags for `EthPeggedOracle`/frxETH: a token that is only "loosely pegged" gets hard-coded 1:1 accounting.

### Finding Description
`sortAllStables` computes `requiredUsd` and each bid's `bidUsd` via `computeStablesUsdValue`, which the surrounding comment states explicitly treats USDC/USDT as $1 each: [1](#0-0) 

Bids are then ranked purely by this synthetic USD total: [2](#0-1) 

This same $1-pin pattern is used elsewhere in the intent-solver stack — e.g. `USD_STABLE_SYMBOLS` in the Simplex filler explicitly documents that stables are "pinned at $1 and never re-priced through a curve" for anchor/confirmation-depth sizing: [3](#0-2) 
and `ContractInteractionService.getInputUsdValue` sums stable inputs 1:1 with no external price check: [4](#0-3) 

In `BidManager`, unlike the Simplex filler's anchor graph (which only affects reorg-confirmation depth, not trade pricing), the $1 pin directly decides **which solver bid is selected as the winner** in the on-chain-facing bid auction (`selectAndExecuteBest` → `sortBids` → `sortAllStables`). If USDC and USDT are not perfectly interchangeable (e.g., during a depeg event like the March 2023 USDC de-peg to ~$0.88, or any future USDT stress event), a bid denominated in the depegged/weaker stablecoin can out-rank a bid denominated in the stronger stablecoin purely because the code assumes both are worth $1, even though the actual redeemable/market value differs.

### Impact Explanation
Because bid selection is what determines which solver's fill transaction the taker/relayer executes, a distorted ranking directly changes which assets and how much value the order originator ends up receiving. During a depeg event, the auction could select a bid that nominally sums to the same or higher "USD" total under the 1:1 assumption but is actually worth materially less in real market value, causing the order taker to receive less value than a correctly-priced comparison would have delivered. This is a direct economic loss to the party relying on bid selection, mirroring the "vaults overvalued/undervalued... loss of assets" impact described in the original frxETH report.

### Likelihood Explanation
Likelihood is **low-to-medium**: USDC/USDT are highly liquid and normally track $1 closely, so under ordinary conditions the mis-pricing is negligible (a few basis points). However, both assets have depegged materially in the past (USDC to ~$0.88 in March 2023; USDT has had smaller depegs), and the code path is reachable by any bidder in the permissionless solver-bid auction — no privileged action is required to trigger the flawed comparison, only market conditions plus normal bid submission.

### Recommendation
Do not hard-code a $1 price for USDC/USDT in `computeStablesUsdValue`/`sortAllStables`. Either route stable-pair comparisons through the same on-chain DEX/oracle pricing used in `sortMixedOutputs` (`computeOutputsUsdValue`), or add a live price/peg-deviation check (e.g., from a Chainlink feed or DEX pool) and fall back to raw-amount comparison when the deviation exceeds a safety threshold, consistent with the recommendation in the referenced report to avoid pegged-oracle assumptions for assets that can depeg.

### Proof of Concept
1. An order requires USDC/USDT outputs valued nominally at $1000.
2. Bid A offers 1000 USDT while USDT is depegged to $0.97 (real value ≈ $970).
3. Bid B offers 985 USDC at par (real value ≈ $985), i.e. genuinely more valuable than Bid A.
4. `computeStablesUsdValue` scores Bid A as 1000 "USD" (both stables at $1) and Bid B as 985 "USD".
5. `sortAllStables` ranks Bid A above Bid B, and the auction selects the less valuable bid, causing the order originator to receive a worse real-value fill than available.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L352-386)
```typescript
	/**
	 * Case B: all outputs are USDC/USDT.
	 * Sum normalised USD values (treating each stable as $1) and sort descending.
	 * Partial fill bids are allowed.
	 */
	private sortAllStables(bids: Bid[], orderOutputs: TokenInfo[], chainId: string): Bid[] {
		const requiredUsd = this.computeStablesUsdValue(orderOutputs, chainId)
		console.log(`[BidManager] sortAllStables: required USD value=${requiredUsd.toString()}`)

		const validBids: { bid: Bid; usdValue: Decimal }[] = []

		for (const bid of bids) {
			const bidUsd = this.computeStablesUsdValue(bid.outputs, chainId)

			if (bidUsd === null) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED: unable to compute USD value`)
				continue
			}

			if (bidUsd.lt(requiredUsd)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate ` +
						`(bid=${bidUsd.toString()}, required=${requiredUsd.toString()}, ` +
						`covers=${bidUsd.div(requiredUsd).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED: USD value=${bidUsd.toString()}`)
			}

			validBids.push({ bid, usdValue: bidUsd })
		}

		validBids.sort((a, b) => b.usdValue.comparedTo(a.usdValue))
		return validBids.map(({ bid }) => bid)
	}
```

**File:** sdk/packages/simplex/src/config/asset-registry.ts (L53-61)
```typescript
/**
 * Symbols pegged to 1 USD. Two roles: gating Uniswap venue pricing (a pool's
 * USD-per-token quote only inverts into a pair rate when token0 is a dollar),
 * and seeding the USD anchor graph at $1 — the roots from which every pair's
 * token0 must be reachable so confirmation depth can be sized in USD (see
 * `unanchoredToken0Symbols` and `FXFiller.usdFactors`). Trade pricing never
 * uses this as a price.
 */
export const USD_STABLE_SYMBOLS: ReadonlySet<string> = new Set(["USDC", "USDT", "DAI"])
```

**File:** sdk/packages/simplex/src/services/ContractInteractionService.ts (L465-488)
```typescript
	/**
	 * Calculates the total USD value of an order's inputs.
	 * Only stable (USDC/USDT) inputs contribute; non-stables contribute 0.
	 *
	 * @param order - The order to calculate input value for
	 * @returns The total USD value of inputs (sum of normalized stable amounts, or 0 if none)
	 */
	async getInputUsdValue(order: Order): Promise<Decimal> {
		let inputUsdValue = new Decimal(0)
		const inputs = order.inputs
		const sourceUsdc = this.configService.getUsdcAsset(order.source).toLowerCase()
		const sourceUsdt = this.configService.getUsdtAsset(order.source).toLowerCase()

		for (const input of inputs) {
			const tokenAddress = bytes32ToBytes20(input.token)
			const addr = tokenAddress.toLowerCase()
			if (addr !== sourceUsdc && addr !== sourceUsdt) continue
			const decimals = await this.getTokenDecimals(tokenAddress, order.source)
			const tokenAmount = new Decimal(formatUnits(input.amount, decimals))
			inputUsdValue = inputUsdValue.plus(tokenAmount)
		}

		return inputUsdValue
	}
```
