## Analog Found

### Title
`sortByRawAmountFallback` sums raw amounts of different tokens without decimal normalization, causing incorrect bid selection - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortByRawAmountFallback` ranks competing solver bids for a mixed-output order by summing each bid's raw `output.amount` values across all its output tokens into a single `Decimal` total, without ever converting amounts by each token's decimals. This mirrors the reported `getCategoryBalance` bug class: unrelated token quantities (potentially with different decimal precisions, e.g., 6-decimal vs 18-decimal tokens) are added together as if they were comparable units.

### Finding Description
`sortByRawAmountFallback` is invoked from `sortMixedOutputs` whenever on-chain DEX pricing (`computeOutputsUsdValue`) fails to price the order's output tokens [1](#0-0) . In the fallback, for each candidate bid it accumulates `totalOffered` by summing `matching.amount` for every required output token directly, with no decimals lookup or scaling applied: [2](#0-1) 

The required total is computed the same unnormalized way: [3](#0-2) 

Both totals mix raw base-unit amounts of arbitrary, unrelated ERC-20 tokens (which can have 6, 18, or other decimals, as seen in the pool token registry with USDC=6, DAI=18, etc. [4](#0-3) ) into one number and then compares/sorts bids by that number: [5](#0-4) 

This is functionally identical to the reported `getCategoryBalance` issue: quantities of tokens with different decimal bases are aggregated as a single scalar without any normalization to a common unit, so 1 unit of an 18-decimal token is treated as worth vastly more than 1 unit of a 6-decimal token in the comparison, regardless of actual economic value.

### Impact Explanation
When DEX pricing is unavailable for a mixed-output order, this fallback becomes the sole mechanism deciding which solver's bid is treated as "best" and gets selected/executed via `selectAndExecuteBest`/`sortBids`. Because the ranking metric is decimal-unaware, a solver offering a small amount of a high-decimal token can outrank a solver offering a genuinely higher-value bid priced in low-decimal tokens (or vice versa). A malicious or opportunistic solver can exploit this to have an economically inferior bid selected as the winning fill, causing the order beneficiary to receive less value than an available competing bid would have provided — a direct value-loss to the counterparty relying on the comparison to pick the best available offer.

### Likelihood Explanation
This path only triggers in the pricing-fallback branch (`sortMixedOutputs` → `sortByRawAmountFallback`), i.e., when on-chain DEX quoting for one or more output tokens fails [1](#0-0) . This is a realistic and solver-triggerable condition (e.g., no liquidity pool/route for a token pair), and any competing solver can then submit bids denominated in tokens of differing decimals to skew the raw-amount comparison in their favor — requiring no privileged access, only submitting a normal bid as an unprivileged filler.

### Recommendation
Normalize every token amount to a common decimal base (e.g., 18 decimals, similar to `_normalizeAmount` already implemented in `VWAPOracle.sol` [6](#0-5) ) before summing in `sortByRawAmountFallback`, using each token's actual `decimals()` value, so bid comparisons reflect true relative quantities rather than raw base-unit counts.

### Proof of Concept
1. An order requests mixed outputs where DEX pricing fails for at least one output token, forcing `sortMixedOutputs` to fall back to `sortByRawAmountFallback`.
2. Solver A bids `1_000_000` units of a 6-decimal token (worth $1.00) for the required output.
3. Solver B bids `1_000_000` units of an 18-decimal token (worth $0.000000000001) for the same required output slot.
4. `sortByRawAmountFallback` sums both bids' raw amounts as `1_000_000` each and treats them as equal/comparable, potentially ranking Solver B's near-worthless bid above or equal to a legitimately higher-value bid from another solver, causing the wrong (lower-value) bid to be selected as "best."

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

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L437-466)
```typescript
	private sortByRawAmountFallback(bids: Bid[], orderOutputs: TokenInfo[]): Bid[] {
		console.log(
			`[BidManager] sortByRawAmountFallback: checking ${bids.length} bid(s) against ${orderOutputs.length} required output(s)`,
		)
		const validBids: { bid: Bid; totalOffered: Decimal }[] = []

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

**File:** sdk/packages/indexer/src/addresses/pool-tokens.generated.ts (L14-17)
```typescript
		"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": { symbol: "USDC", decimals: 6 },
		"0xdac17f958d2ee523a2206206994597c13d831ec7": { symbol: "USDT", decimals: 6 },
		"0x9623dfb044d5612ce0c0f1606973ccaefd03cd05": { symbol: "USDR", decimals: 6 },
		"0x6b175474e89094c44da98b954eedeac495271d0f": { symbol: "DAI", decimals: 18 },
```

**File:** evm/src/utils/VWAPOracle.sol (L240-248)
```text
    function _normalizeAmount(uint256 amount, uint8 _decimals) private pure returns (uint256 normalized) {
        if (_decimals == 18) {
            return amount;
        } else if (_decimals < 18) {
            return amount * (10 ** (18 - _decimals));
        } else {
            return amount / (10 ** (_decimals - 18));
        }
    }
```
