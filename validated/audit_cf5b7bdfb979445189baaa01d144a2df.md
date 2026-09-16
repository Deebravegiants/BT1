### Title
Cross-chain confirmation depth silently defaults to $0 for non-stable order inputs, weakening reorg protection - ([File: sdk/packages/simplex/src/services/ContractInteractionService.ts])

### Summary
Analogous to the Frax `UniV3LiquidityAMO` bug where `collatDolarValue` falls back to a hard-coded $1 for tokens without an oracle (silently misrepresenting collateral value and skewing a protocol safety decision), Hyperbridge's Simplex intent filler has the same class of defect in reverse: `getInputUsdValue` values an order's inputs at $0 whenever the token is not USDC/USDT, and this $0 is the value actually used to size cross-chain reorg protection when the pair's own FX pricing strategy fails to price the order.

### Finding Description
`ContractInteractionService.getInputUsdValue` explicitly only prices USDC/USDT inputs and defaults every other token to a $0 contribution: [1](#0-0) 

This `baseInputUsd` is used in `IntentFiller`'s order-processing pipeline as the starting/fallback USD value fed to the confirmation-policy curve that decides how many source-chain block confirmations a cross-chain order must wait for before the filler commits capital on the destination chain: [2](#0-1) 

The pipeline attempts to overwrite `baseInputUsd` with a strategy-specific, properly FX-anchored value from `FXFiller.getOrderUsdValue`, but only takes that value when the strategy actually returns one; if `getOrderUsdValue` returns `null` (e.g. a leg fails to resolve to a configured pair, `sizeOrder` fails, or an anchor factor lookup misses), `inputUsdValue` silently remains at the $0-defaulted `baseInputUsd`: [3](#0-2) 

`requiredConfirmations` is then computed directly from that (possibly zero) `inputUsdValue`: [4](#0-3) 

`InterpolatedCurve.getValue` clamps at the *smallest* configured curve point when the input amount is at or below it — for every built-in and documented confirmation curve, the smallest configured point still requires nonzero confirmations only because the smallest curve point itself is nonzero (e.g. 1000 USD → 2 blocks). At an input of exactly $0, the curve still returns the first point's value (not literally zero) since `amount <= this.points[0].amount` returns `points[0].value`: [5](#0-4) 

However, this only provides a "small order" confirmation depth (e.g. 2 blocks / ~24s on Ethereum) — not a depth appropriate to the *actual* value at stake. A cross-chain order whose input is a large amount of a non-stable, non-registered-pair token (canFill=true for some strategy that doesn't implement/succeed at `getOrderUsdValue`, but a different strategy is what ultimately executes) is treated by the confirmation-sizing logic as if it were a trivial ~$0–$1000 order, when the destination-chain commitment could be arbitrarily large. This is the same root-cause pattern flagged in the Frax report: a pricing function that has no real price data quietly substitutes a fixed/default value into a decision (collateralization vs. reorg-protection depth) that is supposed to scale with real economic value.

### Impact Explanation
Confirmation depth exists specifically to protect the filler's destination-chain payout against a source-chain reorg: Simplex's own documentation states a compromised/lying RPC or reorged source event lets "the solver...be induced to pay out against events that never happened" if confirmation depth is insufficient. If the USD valuation used to size that depth is silently floored to near-zero for a large non-stable-input order, the solver may commit destination-chain funds after only the shallow "small order" confirmation wait, even though the order's real value is large. If the source-chain order is then reorged out (accidentally or via a targeted reorg/RPC-manipulation attack as described in the project's own confirmations documentation), the filler pays out on the destination chain for an order that no longer exists on the source chain — a direct loss of filler/solver funds. This maps to concrete theft of funds via a route with insufficient reorg protection, one of the accepted impact categories.

### Likelihood Explanation
This requires a specific but plausible combination: (1) a cross-chain order whose input token is not USDC/USDT, (2) at least one configured `FillerStrategy` reports `canFill=true` for it (satisfying the "some fillable strategy has a confirmationPolicy" gate) while (3) `getOrderUsdValue` fails to resolve a proper USD value for that particular order (returns `null`) — e.g., because the leg's token pair isn't priced by the FX curves/venue at that moment, or an anchor lookup misses. Given that `FXFiller.getOrderUsdValue` has multiple `return null` branches (unresolved legs, failed sizing, missing anchor factor) documented directly in the code, and operators are free to configure pairs/venues that don't cover every token a `canFill` check might pass, this is a realistic misconfiguration/edge-case rather than a purely theoretical one. It is a "Medium" likelihood because it depends on specific solver configuration/order shapes rather than being triggerable on every order.

### Recommendation
- **Short term**: Do not silently fall back to `baseInputUsd` (which floors to $0 for non-stables) when a fillable strategy's `getOrderUsdValue` returns `null`. Either reject/skip the order (fail closed, consistent with `resolveLegRates`'s existing "refuse to size" pattern) or force the maximum configured confirmation depth for that chain when the true USD value cannot be determined.
- **Long term**: Audit every place a default/fallback price ($0, $1, or otherwise) substitutes for a genuine market price, and make sure any policy driven by that value (confirmation depth, profitability gating, collateralization) fails safe (over-protective) rather than fails open (under-protective) when pricing information is unavailable.

### Proof of Concept
1. Configure a Simplex filler with an FX pair strategy that can technically `canFill` an order (e.g. matches token addresses) but where, for a specific order, `resolveOrderLegs`/`sizeOrder`/anchor-factor lookup in `getOrderUsdValue` returns `null` (see the `return null` branches in `sdk/packages/simplex/src/strategies/fx.ts:1752-1774`).
2. Place a large-value cross-chain order using a non-USDC/USDT input token.
3. In `IntentFiller`'s per-order handling (`sdk/packages/simplex/src/core/filler.ts:695-754`), observe that `baseInputUsd` from `ContractInteractionService.getInputUsdValue` is `0` for this token, and since the strategy's `getOrderUsdValue` returned `null`, `inputUsdValue` remains `0`.
4. `requiredConfirmations` is computed from `inputUsdValue = 0`, yielding only the curve's minimum confirmation depth (e.g., 2 blocks on Ethereum) regardless of the order's real economic size.
5. If the source chain transaction is reorged out within that shallow window, the filler still executes the destination-chain fill against a since-invalidated source order, resulting in a loss of filler funds.

### Citations

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

**File:** sdk/packages/simplex/src/core/filler.ts (L695-725)
```typescript
				const sourceQuorumClient = this.chainClientManager.getQuorumClient(order.source)
				// Base layer: stable-only USD value from ContractInteractionService
				const baseInputUsd = await this.contractService.getInputUsdValue(order)

				const canFillCache = new Map<FillerStrategy, boolean>()
				for (const strategy of this.strategies) {
					try {
						canFillCache.set(strategy, await strategy.canFill(order))
					} catch (err) {
						this.logger.error({ orderId: order.id, strategy: strategy.name, err }, "Error checking canFill")
						canFillCache.set(strategy, false)
					}
				}

				let inputUsdValue = baseInputUsd
				for (const [strategy, canFill] of canFillCache) {
					if (!canFill || typeof strategy.getOrderUsdValue !== "function") continue
					try {
						const stratValue = await strategy.getOrderUsdValue(order)

						if (stratValue != null) {
							inputUsdValue = Decimal.max(baseInputUsd, stratValue.inputUsd)
							break
						}
					} catch (err) {
						this.logger.error(
							{ orderId: order.id, strategy: strategy.name, err },
							"Error getting strategy-specific inputUsdValue",
						)
					}
				}
```

**File:** sdk/packages/simplex/src/core/filler.ts (L745-754)
```typescript
					for (const [strategy, canFill] of canFillCache) {
						if (!canFill || !strategy.confirmationPolicy) continue
						requiredConfirmations = Math.max(
							requiredConfirmations,
							strategy.confirmationPolicy.getConfirmationBlocks(
								getChainId(order.source)!,
								inputUsdValue.toNumber(),
							),
						)
					}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1752-1774)
```typescript
	async getOrderUsdValue(order: Order): Promise<{ inputUsd: Decimal } | null> {
		const legs = this.resolveOrderLegs(order)
		if (!legs) return null

		const sized = await this.sizeOrder(order, legs, this.venuePriceMemo())
		if (!sized) return null

		// Leg notionals are in each pair's own token0. Convert to USD through
		// the curve graph before summing — the confirmation curve's amount axis
		// is USD, and a raw token quantity would over-wait for sub-dollar
		// assets and, worse, under-wait for anything above a dollar.
		const factors = this.usdFactors()
		let inputUsd = new Decimal(0)
		for (let i = 0; i < legs.length; i++) {
			const factor = factors.get(normalizeSymbol(legs[i].pair.token0))
			// Unreachable after the constructor's anchor check; refuse to size
			// rather than mislabel a token quantity as dollars.
			if (!factor) return null
			inputUsd = inputUsd.plus(sized.legNotionals[i].mul(factor))
		}
		if (inputUsd.lte(0)) return null
		return { inputUsd }
	}
```

**File:** sdk/packages/simplex/src/config/interpolated-curve.ts (L191-203)
```typescript
	getValue(inputAmount: Decimal | number): number {
		const amount = inputAmount instanceof Decimal ? inputAmount.toNumber() : inputAmount

		if (amount <= this.points[0].amount) {
			return this.points[0].value
		}
		if (amount >= this.points[this.points.length - 1].amount) {
			return this.points[this.points.length - 1].value
		}

		const result = this.linearInterpolate(amount)
		return Math.round(result)
	}
```
