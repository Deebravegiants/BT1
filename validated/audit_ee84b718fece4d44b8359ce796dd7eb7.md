### Title
Fee-token USD-peg assumption in gas-to-fee-token fallback pricing can under-price relayer/settlement fees, stalling order fills - (File: sdk/packages/sdk/src/protocols/intents/utils.ts)

### Summary
`convertGasToFeeToken` and `convertFeeTokenToWei` in the intents SDK hard-code an assumption that the chain's configured fee token is worth exactly $1 whenever their primary Uniswap V2 on-chain quote path fails or returns zero. This mirrors the reported bug class: treating a token as an unconditional 1:1 USD peg instead of deriving its price from a real source, with no fallback to an actual price oracle for the fee token itself.

### Finding Description
`convertGasToFeeToken` first tries to price gas cost in fee-token units via an on-chain Uniswap V2 quote (`ctx.swap.findBestProtocolWithAmountIn`, `wethAddr -> feeToken.address`). If that quote throws or returns `0n`, the function falls back to: [1](#0-0) 

The fallback computes `gasCostUsd` from the native token's real Coingecko price (`fetchPrice`), but then divides by `feeTokenPriceUsd = new Decimal(1)` — an unconditional assumption that the fee token is pegged 1:1 to USD, with no check of what the fee token actually is. The mirror function `convertFeeTokenToWei` makes the same assumption in the opposite direction: [2](#0-1) 

`getFeeToken` resolves the fee token from `chain.getFeeTokenWithDecimals()`, which is a per-chain configured token (not necessarily a canonical audited stablecoin, and not validated against a price feed anywhere in this fallback path): [3](#0-2) 

This is directly analogous to the reported flaw: the external report's `getPriceOfAssetQuotedInUSD()` assumed listed stablecoins are always $1, causing incorrect USD valuations if a peg breaks; here the SDK assumes the *fee token* is always $1 whenever the DEX quote path is unavailable, with the same blind-spot if the fee token depegs or is not actually a USD-pegged asset.

### Impact Explanation
This pricing function feeds directly into `quoteOrderFees` in `IntentGateway.ts`, which computes the solver/relayer fee (`order.fees`) attached to every intent-gateway order placed through the SDK's default `execute`/`executeBest` flow: [4](#0-3) 

If the fallback path is hit (Uniswap V2 route missing/illiquid on a chain, which is common on newer or long-tail EVM chains supported by Hyperbridge) and the fee token is not truly pegged to $1, the computed fee is systematically wrong:
- If the fee token is actually worth less than $1, relayers/solvers are underpaid relative to real gas cost, making orders unprofitable to fill — a route that becomes practically unable to deliver messages (orders time out / go unfilled) until the caller manually overrides fees.
- If the fee token is worth more than $1, users overpay, indicating an unsound fee/value assumption baked into core dispatch pricing.

Because this is on the direct, permissionless path used by any end user placing a cross-chain intent order (single submitted transaction), and it governs whether relayers/solvers are correctly compensated for delivering the order, this falls within the in-scope "relayer fee and reward accounting" / "route unable to deliver messages" categories.

### Likelihood Explanation
The primary Uniswap V2 quote path is expected to succeed on most established chains with deep WETH/fee-token liquidity, so the fallback is a secondary path — but it is explicitly designed to be hit ("If that quote fails or returns zero, falls back...") and is reachable on any less-liquid or newly-added EVM chain, or during periods of pool illiquidity/manipulation causing a zero/failed quote. The SDK code comments themselves acknowledge the fallback "assumes the fee token is worth $1" without any validation that this holds for the configured fee token on that specific chain, so the trigger condition depends on deployment/chain-config choices rather than attacker action, making this a medium-likelihood correctness/config-dependent issue rather than a rare edge case.

### Recommendation
Do not hard-code `feeTokenPriceUsd = new Decimal(1)`. Instead:
1. Fetch the fee token's real USD price via the same `fetchPrice` (Coingecko or other oracle) mechanism already used for the native currency, keyed off the fee token's configured symbol/address, rather than assuming a peg.
2. If no reliable price source exists for the fee token, fail loudly (throw) rather than silently defaulting to $1, so callers don't place orders with a mispriced fee.
3. Only apply the $1 shortcut when the fee token is verified to be one of a small, explicitly-configured set of USD stablecoins for that chain (similar to `USD_STABLE_SYMBOLS` used elsewhere in the codebase, e.g. `sdk/packages/simplex/src/config/asset-registry.ts`), and even then, prefer a live oracle when available.

### Proof of Concept
Not applicable as a runnable PoC — this is a pricing-logic/config-dependent flaw rather than an exploitable state transition. Conceptually: configure an `IntentGateway` for a chain whose fee token is a non-$1-pegged asset (or whose fee token has no deep WETH pool on Uniswap V2), call `quoteOrderFees(order)`, and observe that the derived `fees` is computed from `feeTokenPriceUsd = 1` in `convertGasToFeeToken`'s catch branch (`sdk/packages/sdk/src/protocols/intents/utils.ts:205-214`), producing a fee detached from the token's real market value.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/utils.ts (L33-46)
```typescript
export async function getFeeToken(
	ctx: IntentGatewayContext,
	chainId: string,
	chain: IEvmChain,
): Promise<{ address: HexString; decimals: number }> {
	const cached = ctx.feeTokenCache.get(chainId)
	if (cached && Date.now() - cached.cachedAt < FEE_TOKEN_CACHE_TTL_MS) {
		return cached
	}

	const fresh = await chain.getFeeTokenWithDecimals()
	ctx.feeTokenCache.set(chainId, { ...fresh, cachedAt: Date.now() })
	return fresh
}
```

**File:** sdk/packages/sdk/src/protocols/intents/utils.ts (L205-214)
```typescript
	} catch {
		const nativeCurrency = client.chain?.nativeCurrency
		const chainId = Number.parseInt(evmChainID.split("-")[1])
		const gasCostInToken = new Decimal(formatUnits(gasCostInWei, nativeCurrency?.decimals ?? 18))
		const tokenPriceUsd = await fetchPrice(nativeCurrency?.symbol, chainId)
		const gasCostUsd = gasCostInToken.times(tokenPriceUsd)
		const feeTokenPriceUsd = new Decimal(1)
		const gasCostInFeeToken = gasCostUsd.dividedBy(feeTokenPriceUsd)
		return parseUnits(gasCostInFeeToken.toFixed(feeToken.decimals), feeToken.decimals)
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/utils.ts (L256-265)
```typescript
		return amountOut
	} catch {
		const nativeCurrency = client.chain?.nativeCurrency
		const chainId = Number.parseInt(evmChainID.split("-")[1])
		const feeTokenAmountInToken = new Decimal(formatUnits(feeTokenAmount, feeToken.decimals))
		const nativeTokenPriceUsd = await fetchPrice(nativeCurrency?.symbol, chainId)
		const feeTokenAmountUsd = feeTokenAmountInToken.times(new Decimal(1))
		const nativeAmount = feeTokenAmountUsd.dividedBy(nativeTokenPriceUsd)
		return parseUnits(nativeAmount.toFixed(nativeCurrency?.decimals ?? 18), nativeCurrency?.decimals ?? 18)
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/IntentGateway.ts (L815-854)
```typescript
	async quoteOrderFees(
		order: Order,
		options?: { maxPriorityFeePerGasBumpPercent?: number; maxFeePerGasBumpPercent?: number },
	): Promise<OrderFeesQuote> {
		const isSameChain = this.source.config.stateMachineId === this.dest.config.stateMachineId
		const orderFeeGasPriceBumpPercent = resolveOrderFeeGasPriceBump(this.source.config.stateMachineId, isSameChain)
		const estimate = await this.gasEstimator.estimateFillOrder(
			{
				order,
				maxPriorityFeePerGasBumpPercent: options?.maxPriorityFeePerGasBumpPercent,
				maxFeePerGasBumpPercent: options?.maxFeePerGasBumpPercent,
			},
			{ orderFeeGasPriceBumpPercent },
		)

		if (estimate.totalGasCostWei === 0n || estimate.totalGasInFeeToken === 0n) {
			throw new Error("Gas estimation failed")
		}

		// Same-chain fills need a larger solver fee margin. Cross-chain orders
		// attach (fill gas + the settlement relayer fee, the SAME gas budget a
		// solver's requirement is sized against) with a 5% buffer over the WHOLE
		// sum: the solver's requirement carries no padding of its own, so the
		// buffer must cover the relayer component too — a buffer on fill gas
		// alone is dwarfed whenever the source chain is expensive and the
		// destination cheap (relayer fee >> fill gas), and every SDK-placed
		// order would come up short and be refused.
		const fees = isSameChain
			? estimate.totalGasInFeeToken * 2n
			: ((estimate.totalGasInFeeToken + estimate.relayerFeeInSourceFeeToken) * 105n) / 100n

		const { address: feeToken } = await this.source.getFeeTokenWithDecimals()

		return {
			fees,
			nativeValue: estimate.totalGasCostWei + (estimate.totalGasCostWei * 2n) / 100n,
			feeToken,
			estimate,
		}
	}
```
