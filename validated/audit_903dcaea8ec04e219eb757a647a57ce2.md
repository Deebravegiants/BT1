### Title
Unbounded, size-blind Uniswap V4 spot-price oracle lets a flash-loan price manipulation drain Simplex solver liquidity on order fills - (File: `sdk/packages/simplex/src/strategies/fx.ts`, `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
Simplex's pool-based pricing path prices curveless (venue-priced) pairs directly from a Uniswap V4 pool's current `sqrtPriceX96`, with no size/impact term and no execution-cost awareness, and its only defense (`checkPriceGuard`) is an optional, static-reference deviation check rather than a manipulation-resistant TWAP. This mirrors the WOOFi sPMM root cause: a DEX pricing mechanism that trusts an instantaneous, thinly-liquid pool price, exploitable with flash loans to move the price and extract value before it reverts.

### Finding Description
For curveless pairs Simplex derives bid/ask from a live Uniswap V4 pool rather than a static curve: [1](#0-0) 

`UniswapV4FundingPlanner.getExoticTokenPrice` reads the most-liquid qualifying position and computes the price from `computeDirectPoolPriceUsd`, which is described as returning the "raw pool mid derived from `sqrtPriceX96`... never applied [fee tier]... and there is no size or impact term": [2](#0-1) 

The pool's live `slot0` (tick/`sqrtPriceX96`) and `getLiquidity` are read fresh right before pricing/planning a withdrawal, so an attacker can move the tick in the same block/transaction sequence the fill is built from: [3](#0-2) 

The only mitigation, `checkPriceGuard`, rejects a fill only if the pool quote deviates from a **static, operator-configured `referencePrice`** by more than `maxDeviationBps` — it is explicitly optional ("the two go together — one without the other is rejected... omit both to leave the chain unguarded") and checks deviation from a stale reference, not real execution/impact cost: [4](#0-3) [5](#0-4) 

This is exactly the WOOFi sPMM bug class: a pricing formula that trusts instantaneous pool state on a low-liquidity venue, with the guardrail bounding drift against a fixed reference rather than defending against a flash-loan-manipulated spot read, and with the guardrail itself disable-able/misconfigurable per chain.

### Impact Explanation
`computeLegPolicyOutput`/the fill-sizing path extends this manipulated mid "linearly across the whole priced quantity" when sizing `targetOutput` for an order, and the solver funds the deficit by decreasing liquidity from its own Uniswap V4 LP positions (`planWithdrawalForToken`) and paying it to the order's beneficiary via `IntentGateway.fillOrder`: [6](#0-5) 

If an attacker pushes the pool's tick with a flash loan (or a large swap) immediately before/alongside submitting/filling an intent order against a thin V4 position pool, the solver mis-prices the exotic token, over-delivers output from its own escrowed/vaulted liquidity, and the attacker profits from the mispriced fill — a direct theft of solver-held funds reachable from a single submitted intent order, without any privileged role. Because withdrawals are ERC-7821 batched atomically with the fill, the attacker (or a colluding filler-adjacent actor) can also structure the manipulation and the fill within one atomic sequence, closely mirroring WOOFi's flash-loan/repay-in-one-transaction pattern.

### Likelihood Explanation
Likelihood depends on operator configuration: it is High when `referencePrice`/`maxDeviationBps` are unset (explicitly a supported, unguarded configuration) or set with generous deviation, and the exotic-token/stablecoin pool is thin (typical for "exotic" pairs like cNGN, per the docs' own example). Even when the guard is configured, it bounds only deviation from a static reference, not manipulation magnitude relative to real liquidity depth or execution cost, so an attacker operating within the allowed band can still extract value on illiquid pools — as the flow doc itself states, "checkPriceGuard is the only defense on this path, and it checks deviation from a static reference, not execution cost."

### Recommendation
- Replace instantaneous `sqrtPriceX96` spot pricing with a manipulation-resistant TWAP (or require a minimum observation window) for venue-priced pairs.
- Make the price guard (reference price + max deviation) mandatory whenever `[vault.uniswapV4]` pool pricing is used, not optional per chain.
- Incorporate real trade-size price impact (not a linear mid extension) and the pool's fee tier into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput`.
- Add a liquidity-depth floor so pools too thin relative to `maxOrderSize` cannot be used for venue pricing.
- Consider requiring the price to be re-validated at execution time (immediately before the ERC-7821 batch lands) rather than only at evaluation time.

### Proof of Concept
1. Configure/operate a Simplex filler with `[vault.uniswapV4]` pricing a thin exotic-token/USDC pool, with no `referencePrice`/`maxDeviationBps` guard configured (a documented supported state).
2. Attacker takes a flash loan and swaps heavily against the same low-liquidity V4 pool, moving `sqrtPriceX96`/tick sharply in their favor.
3. In the same block (or immediately after), attacker submits/has filled an intent order (`fillOrder`) sized to the exotic token; `UniswapV4FundingPlanner.getExoticTokenPrice`/`computeDirectPoolPriceUsd` reads the manipulated `slot0` and returns a favorable mid price.
4. `evaluateOrder`/`computeLegPolicyOutput` sizes `targetOutput` off this manipulated linear mid; `planWithdrawalForToken` withdraws liquidity from the solver's V4 position to fund the over-priced output, which is paid to the attacker via `fillOrder`.
5. Attacker reverses the initial swap and repays the flash loan, net-profiting the mispriced difference from the solver's LP position — analogous to the WOOFi sequence of flash-loan-driven price manipulation, cheap repayment, and repeated extraction.

### Citations

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L1-22)
```markdown
# Venue pricing (Uniswap V4 funded pairs)

Verified 2026-08-19.

```
resolveLegRates(...)
  curveless pair && token0 is a USD stable
    -> venuePriceMemo() -> getVenueUsdPrice(chain, token1)
         -> UniswapV4FundingPlanner.getExoticTokenPrice
              picks the position with the largest pool liquidity
              -> computeDirectPoolPriceUsd -> sdkPool.token0Price / token1Price
    -> checkPriceGuard(...)   reject if outside maxDeviationBps of the static reference
    -> rate = 1 / venueUsd
  otherwise -> the pair's ask/bid curve at the leg's notional
```

`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-239)
```typescript
	async getExoticTokenPrice(chain: string, exoticToken: string): Promise<Decimal | null> {
		const state = this.stateByChain.get(chain)
		if (!state || !state.isHydrated()) return null

		try {
			await state.refresh()
		} catch (err) {
			this.logger.error({ err, chain }, "Failed to refresh state for price query")
			return null
		}

		const tokenLower = exoticToken.toLowerCase()
		let bestPrice: Decimal | null = null
		let bestLiquidity = 0n

		for (const pos of state.allPositions()) {
			if (pos.currency0.toLowerCase() !== tokenLower && pos.currency1.toLowerCase() !== tokenLower) continue
			const sdkPool = state.getSdkPool(pos.tokenId)
			if (!sdkPool) continue

			const result = this.computeDirectPoolPriceUsd(pos, sdkPool, chain)
			if (result && result.exoticToken.toLowerCase() === tokenLower) {
				const poolLiquidity = state.getPoolLiquidity(pos.tokenId)
				if (poolLiquidity > bestLiquidity) {
					bestPrice = result.priceUsd
					bestLiquidity = poolLiquidity
				}
			}
		}

		if (bestPrice) {
			this.logger.debug({ chain, token: tokenLower, priceUsd: bestPrice.toString() }, "Exotic token price computed")
		}
		return bestPrice
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-170)
```typescript
	async refresh(): Promise<void> {
		const client = this.clientManager.getPublicClient(this.chain)
		const chainId = chainIdFromIdentifier(this.chain)

		// Group positions by poolId to avoid duplicate pool state fetches
		const poolIds = new Set(this.tokenIdToPoolId.values())

		// Fetch slot0 + liquidity for each unique pool via StateView
		const poolStateMap = new Map<string, { sqrtPriceX96: bigint; tick: number; poolLiquidity: bigint }>()

		for (const poolId of poolIds) {
			const [slot0Result, poolLiquidity] = await Promise.all([
				client.readContract({
					address: this.stateView,
					abi: UNISWAP_V4_STATE_VIEW_ABI,
					functionName: "getSlot0",
					args: [poolId as HexString],
				}) as Promise<[bigint, number, number, number]>,
				client.readContract({
					address: this.stateView,
					abi: UNISWAP_V4_STATE_VIEW_ABI,
					functionName: "getLiquidity",
					args: [poolId as HexString],
				}) as Promise<bigint>,
			])

			poolStateMap.set(poolId, {
				sqrtPriceX96: slot0Result[0],
				tick: slot0Result[1],
				poolLiquidity,
			})
		}
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

**File:** sdk/packages/simplex/docs/ai/flows/filling-how-a-fill-amount-is-sized-and-who-else-spends-the-same.md (L1-25)
```markdown
# Filling: how a fill amount is sized, and who else spends the same balance

Verified against the reverted Base fill `0x31de53fe...` (UserOp `0xe090acd1...`), traced end to end.

## Sizing, per leg

`FXFiller.evaluateOrder` walks `order.inputs` and sizes each leg independently (`src/strategies/fx.ts`):

1. `targetOutput` = what the curve will pay (`policyMaxOutput`), in every case. This is the amount the leg intends to hand over, and it may exceed what the user asked for — `IntrinsicIntents.fillOrder` takes `solverAmount > totalRequired` and splits the excess between the beneficiary and the protocol (`surplusShareBps`), and it is the same figure `quotePhantomFill` publishes as the pair's quoted rate. A pair's `maxOrderSize` is optional and does not shorten this: it binds earlier and in the other unit, where `computeLegPolicyOutput` rations `token0ForLeg` against the pair's remaining budget before the rate is applied. `desiredOutput` — the user's ask scaled by the same cap — is no longer a ceiling on payout; it survives as the price gate's comparand and in the short-fill logs.
2. `reserve` = the paymaster reserve for this token (`paymasterReserveForToken`, from `src/services/paymaster`) plus every funding venue's `walletReserveForToken`. Only the vault returns a non-zero venue reserve, its configured `minBalance`; `UniswapV4FundingPlanner` returns `0n`. The paymaster half is seeded outside the venue loop deliberately — the loop is empty when no vault and no V4 positions are configured, and that filler still sizes partial fills.
3. `usableWallet` = balance − reserve. `walletContribution` = `min(targetOutput, usableWallet)`.
4. Any shortfall is requested from each funding venue in turn via `planWithdrawalForToken`, which returns ERC-7821 calls and the amount it expects them to credit. The calls accumulate in `fundingCalls`. For V4 that credit is priced from `liquidityRemoval`, the liquidity the encoded DECREASE_LIQUIDITY actually carries — not the liquidity the planner asked for, which the SDK truncates.
5. `finalOutputAmount` = `min(walletContribution + credited, targetOutput)`.

After the loop, `estimateGasFillPost` prices the fill. A cross-chain order then has to clear one more affordability check: `fillOrder` dispatches the escrow-release message and `HyperApp.dispatchWithFeeToken` pulls `dispatchFee` from the same wallet in the destination host's fee token (USDC on Base — often the token just paid out). The fee is only known here, after the funding calls it depends on exist, and a cross-chain order cannot be partially filled, so the order is skipped when the residue will not cover the fee plus the paymaster reserve.

A capped leg is separately gated as a partial fill when the cap actually shortens it — `capFraction.lt(1) && policyMaxOutput < output.amount`. Both halves matter: with the payout unclamped, a curve running far enough above the order's rate covers the whole ask out of a capped slice, which is a full fill.

Whenever `finalOutputAmount < output.amount` the fill is an under-fill and has to clear `partialEligible()` — same chain, no output calldata, no prior partial — or the order is skipped.

The outputs and the funding calls are cached against the order id (`setFillerOutputs`, `setFundingPrepends`). `ContractInteractionService.prepareBidUserOp` reads them back verbatim and signs them into the bid; nothing re-reads the balance between sizing and execution, and the bid is committed, so an amount that was affordable at evaluation must still be affordable when the UserOp lands.

## The batch, in execution order

`callData` is an ERC-7821 batch: the funding calls first (for V4, `PositionManager.multicall(modifyLiquidities)` encoding DECREASE_LIQUIDITY + TAKE_PAIR), then `approve` for the fill amount, then `IntentGateway.fillOrder`, which does the `transferFrom` that moves the output token to the user.
```
