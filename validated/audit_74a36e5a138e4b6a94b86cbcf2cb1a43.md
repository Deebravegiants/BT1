## Title
Static $1 stablecoin valuation in Simplex's cross-chain confirmation sizing weakens reorg protection during a stable depeg — (`sdk/packages/simplex/src/services/ContractInteractionService.ts`)

### Summary
Hyperbridge's reference intent-filler ("Simplex") sizes the reorg-protection confirmation depth for a cross-chain order from the order's USD value, but `ContractInteractionService.getInputUsdValue` derives that value by treating every USDC/USDT input as worth exactly $1, with no live price check. Because this hardcoded valuation feeds directly into the confirmation-depth curve that gates when the filler commits (pays out) capital on the destination chain, a depegged/mispriced stable input can cause the filler to under-count the order's real USD exposure and consequently wait fewer blocks than the order's true value warrants before paying out — exactly the "static stable price outdated during a depeg" bug class from the referenced report, but here it degrades the solver's own reorg defense instead of a collateral system.

### Finding Description
`getInputUsdValue` sums only USDC/USDT inputs and always values 1 token unit at $1: [1](#0-0) 

This "base" USD value is computed unconditionally for every incoming order in the core filler's order-intake path, and used (via `Decimal.max` with any strategy-specific value) to size `requiredConfirmations` for cross-chain orders through each fillable strategy's `confirmationPolicy.getConfirmationBlocks(...)`: [2](#0-1) 

The confirmation wait is explicitly the reorg defense the filler relies on before it commits destination-chain capital, as documented: [3](#0-2) 

and the docs describe the exact risk model this static valuation undermines — cross-chain fills are "evaluated from the solver's own reading of source-chain state," with "no on-chain safety net to catch it after the fact" if that reading is wrong: [4](#0-3) 

`getInputUsdValue` never queries a live oracle or the pair's own curve for USDC/USDT; it is a flat $1-per-unit assumption baked into the "base layer" valuation that the filler always computes before any strategy-specific pricing runs. Since `inputUsdValue = Decimal.max(baseInputUsd, stratValue.inputUsd)`, whichever of the base ($1-pegged) or strategy figure is *higher* wins — but the base path is the one that is always computed and is what backstops orders whose fillable strategy either lacks a `getOrderUsdValue` or a `confirmationPolicy`. In any of those cases the entire confirmation-depth decision rests solely on the hardcoded $1 assumption.

### Impact Explanation
If a stablecoin used as an order's input genuinely trades away from its $1 peg (a real, recurring event — USDC's 2023 depeg, various algorithmic/USD-pegged token depegs), the filler's reorg-protection sizing becomes wrong in the direction that matters for solver safety: the order's *true* USD exposure can exceed the $1-per-unit assumption baked into `getInputUsdValue`, so the filler waits fewer confirmation blocks than the order's real value warrants before paying out on the destination chain. An attacker who can place a large-notional order using such a token can induce the filler to release destination funds before the source-chain deposit is irreversibly confirmed, then have the source-chain transaction reorged out — a direct theft of the solver's committed capital, the same "overvalued/undercollateralized position, liquidator/response can't act in time" pattern flagged in the source report, translated to Hyperbridge's solver risk engine instead of a lending protocol's collateral engine.

### Likelihood Explanation
Exploitability requires (a) a genuine, even transient, depeg or mispricing of a stablecoin the filler accepts as input, and (b) an attacker capable of executing (or opportunistically riding) a source-chain reorg within the shortened confirmation window. Stablecoin depegs are documented, recurring market events (cited directly in the source report), and the filler's own architecture treats reorg risk as a first-class, actively-defended threat (quorum RPC checks, per-chain confirmation curves) — indicating the maintainers already consider chain-reorg-driven fund loss a realistic, in-scope risk that this static pricing path silently weakens whenever the peg assumption breaks.

### Recommendation
Do not hardcode USDC/USDT (or any configured stable) at $1 in `getInputUsdValue`. Price stable inputs the same way the FX strategy prices everything else feeding confirmation depth — via a live rate source (the operator's own curves/venue quote, or an external oracle) with a deviation guard analogous to `checkPriceGuard`/`referenceRate`'s price-guard band already used elsewhere in the codebase for venue pricing. At minimum, clamp confirmation sizing to use the *maximum* of the $1 assumption and a live-priced estimate, so a peg break can only ever increase — never decrease — the computed USD exposure and required confirmations.

### Proof of Concept
1. Configure a Simplex filler accepting a stablecoin `S` (USDC/USDT) as an order input, with the default confirmation policy (e.g. Ethereum: $1,000 → 2 blocks, $100,000 → 15 blocks) per `DEFAULT_CONFIRMATION_POLICIES` [5](#0-4) .
2. Have `S` trade briefly above its $1 peg on the relevant chain (e.g., $1.20) due to a depeg event, while the attacker places a cross-chain order whose input is a large quantity of `S` — real USD value ~$120,000, but `getInputUsdValue` reports it as $100,000 (quantity × $1).
3. `handleNewOrder` computes `requiredConfirmations` from the understated $100,000 figure (15 blocks) instead of the true ~$120,000+ exposure that should require deeper confirmation per the curve.
4. The filler pays out on the destination chain once the (shortened) confirmation count is reached.
5. The attacker reorgs the source chain within that shorter window, invalidating the deposit — the filler has already released destination funds against a deposit that no longer exists.

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

**File:** sdk/packages/simplex/src/core/filler.ts (L691-754)
```typescript
				// Confirmations are counted with BFT-quorum semantics across the
				// operator's configured endpoints, so with independent providers a
				// single compromised or reorged provider cannot vouch for inclusion
				// depth on cross-chain orders.
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

				const isCrossChain = order.source !== order.destination
				let requiredConfirmations = 0
				if (isCrossChain) {
					const fillableStrategies = [...canFillCache].filter(([, canFill]) => canFill)
					if (fillableStrategies.length === 0) {
						this.logger.debug(
							{ orderId: order.id, source: order.source, destination: order.destination },
							"Skipping cross-chain order: no strategy can fill it",
						)
						return
					}
					if (!fillableStrategies.some(([strategy]) => strategy.confirmationPolicy)) {
						this.logger.warn(
							{ orderId: order.id, source: order.source, destination: order.destination },
							"Skipping cross-chain order: no fillable strategy has a confirmation policy configured",
						)
						return
					}
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

**File:** docs/content/developers/evm/simplex/confirmations.mdx (L8-27)
```text
A cross-chain fill commits capital on one chain because of something the solver read on another. Two settings decide how much that reading is trusted: how many confirmations an order waits for, and how many independent endpoints have to agree on what they saw.

## Confirmation Policy

Before processing a cross-chain order, Simplex waits for enough block confirmations to guard against chain reorganizations. The number of confirmations scales with order value using a curve — small orders are processed quickly, large orders wait longer. Same-chain orders always proceed without additional confirmation delay.

### Built-in Defaults

Simplex ships with default confirmation policies for common chains. These apply automatically when no user-configured policy exists for a chain. User-configured policies override the default for that chain. Every configured chain must be covered by a built-in default or a custom entry — a chain with neither fails at startup rather than silently dropping that chain's cross-chain orders at fill time.

| Chain | Chain ID | Min ($1,000) | Max ($100,000) | Block Time |
|---|---|---|---|---|
| Ethereum | 1 | 2 blocks (~24s) | 15 blocks (~3m) | ~12s |
| BNB Chain | 56 | 2 blocks (~6s) | 3 blocks (~9s) | ~3s |
| Polygon | 137 | 2 blocks (~4s) | 5 blocks (~10s) | ~2s |
| Base | 8453 | 2 blocks (~4s) | 90 blocks (~3m) | ~2s |
| Arbitrum | 42161 | 8 blocks (~2s) | 720 blocks (~3m) | ~0.25s |
| Unichain | 130 | 2 blocks (~2s) | 180 blocks (~3m) | ~1s |

Values between the min and max order amounts are linearly interpolated.
```

**File:** docs/content/developers/evm/simplex/confirmations.mdx (L76-78)
```text
### Why this matters for cross-chain orders

On a cross-chain fill, Simplex observes an `OrderPlaced` (or `PartialFill` / `OrderFilled`) event on the source chain and then commits capital on the destination chain. Unlike same-chain fills — where the destination `fillOrder` call will revert if the source-chain order does not exist — cross-chain bids submitted through Hyperbridge are evaluated from the solver's own reading of source-chain state. A single RPC is therefore both an availability and an integrity choke point: if it lies about which orders were placed, the solver can be induced to pay out against events that never happened, and there is no on-chain safety net to catch it after the fact.
```

**File:** sdk/packages/simplex/src/config/interpolated-curve.ts (L26-32)
```typescript
export const DEFAULT_CONFIRMATION_POLICIES: Record<string, CurveConfig> = {
	"1": {
		points: [
			{ amount: "1000", value: 2 },
			{ amount: "100000", value: 15 },
		],
	}, // Ethereum (~12s blocks, ~24s–3min)
```
