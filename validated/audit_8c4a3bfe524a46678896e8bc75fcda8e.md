### Title
Live Uniswap V2 spot-price reads for fee conversion make relayer-fee sizing manipulable, mirroring the `slot0` oracle-manipulation bug class - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.quote()`/`quoteNative()` price native-to-fee-token (or fee-token-to-native) conversions off a live Uniswap V2 pool via `getAmountsIn`/`getAmountsOut`, exactly the same class of "read the AMM's current instantaneous price and treat it as ground truth" pattern flagged in the USSD report for `slot0`. The Hyperbridge documentation itself flags this as dangerous when consumed on-chain.

### Finding Description
`EvmHost.quote(DispatchPost)`/`quoteNative()` compute the native-token cost of a dispatch by calling the configured `uniswapV2Router`'s `getAmountsIn`/`getAmountsOut` [1](#0-0) , which read the pool's current reserves — the AMM equivalent of Uniswap V3's `slot0`: a single, most-recent price point with no time-weighting or manipulation resistance. The project's own documentation explicitly warns about this:

> "Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation" [2](#0-1) 

This is a direct restatement of the reported bug class: an instantaneous DEX price read is trusted for a security/economic decision (fee sizing) rather than a manipulation-resistant TWAP. `EvmHost.sol` itself contains 18 call-sites referencing `uniswapV2Router`/`getAmountsIn`/`getAmountsOut` [3](#0-2) , meaning this pricing path is reachable from the core dispatch path that any unprivileged caller invokes when paying protocol fees in native token.

### Impact Explanation
Because relayer fee sizing and native-fee protocol accounting are derived from this manipulable spot price, an attacker able to move the Uniswap V2 pool's reserves within the same transaction (e.g. via a flash loan/flash-swap sandwiching their own dispatch call) can under-price the native-fee-to-fee-token (or fee-token-to-native) conversion. This lets the attacker dispatch a cross-chain message while paying an artificially low relayer fee, which can leave the message under-incentivized for pickup — a route that becomes unable to reliably deliver messages — or let the attacker extract value from the fee/relayer-fee accounting path, both of which are explicitly in-scope impacts (fee/reward accounting, delivery reliability).

### Likelihood Explanation
The precondition (temporarily distorting a Uniswap V2 pool's reserves within a single atomic transaction) is a well-understood, commonly executed technique (flash loans, large same-block swaps) and requires no privileged access — any unprivileged sender who calls the fee-quoting/dispatch path in native-fee mode can attempt it. The documentation's own explicit warning about "vulnerable to sandwich attacks" indicates the maintainers are aware the read is exploitable if consumed inside a transaction rather than purely off-chain, and the extensive on-chain reference count in `EvmHost.sol` indicates the router-based pricing is wired into the live contract, not merely SDK tooling.

### Recommendation
Replace instantaneous `getAmountsIn`/`getAmountsOut` spot reads with a time-weighted price source (e.g., a Uniswap V3/V4 TWAP oracle or an off-chain-pushed, bounded reference price with deviation guards, similar to the `checkPriceGuard`/`referencePrice`/`maxDeviationBps` mechanism already used elsewhere in the codebase for Uniswap V4 venue pricing [4](#0-3) ) wherever a fee or economic amount is computed and enforced within the same on-chain transaction. If `quote()`/`quoteNative()` are intended to be off-chain-only helpers, enforce that intent on-chain (e.g., disallow their use as the sole input to any state-changing fee calculation, or require the caller to supply/attest to a bounded reference price that is checked against the live quote).

### Proof of Concept
1. Attacker takes a flash loan and performs a large swap against the configured `uniswapV2Router` pool to skew reserves in the direction that minimizes the native-fee/fee-token conversion computed by `getAmountsIn`/`getAmountsOut`.
2. In the same transaction, attacker calls the EvmHost dispatch path that relies on `quote()`/`quoteNative()` (`evm/src/core/EvmHost.sol`) to size the required fee amount; the computed fee is now artificially low due to the skewed reserves.
3. Attacker dispatches the message paying the deflated fee, then reverses the initial swap (repaying the flash loan) within the same transaction, restoring the pool and paying only the flash-loan fee as cost.
4. The dispatched message is now under-funded relative to its true delivery cost, leaving relayers under-incentivized to deliver it — degrading or breaking that route's message delivery, or letting the attacker siphon value from the fee-token accounting depending on which conversion direction was targeted.

### Citations

**File:** sdk/packages/sdk/src/chains/evm.ts (L746-777)
```typescript
	async quoteNative(request: IPostRequest | IGetRequest, fee: bigint): Promise<bigint> {
		const totalFee = (await this.quote(request)) + fee
		const feeToken = await this.getFeeTokenWithDecimals()
		// Quote against the router the host actually swaps through on dispatch,
		// which may price differently than the canonical Uniswap V2 router.
		const hostRouter = await this.publicClient.readContract({
			address: this.params.host,
			abi: EvmHost.ABI,
			functionName: "uniswapV2Router",
		})
		return this.getAmountsIn(totalFee, feeToken.address, request.source, hostRouter)
	}

	/**
	 * Given a desired output amount of a token, returns how much native is needed as input.
	 * Uses the chain's Uniswap V2 router (or `router` when provided): WETH → tokenOut path.
	 */
	async getAmountsIn(amountOut: bigint, tokenOutForQuote: HexString, chain?: string, router?: HexString): Promise<bigint> {
		const chainId = chain ?? `EVM-${this.params.chainId}`
		const v2Router = router ?? this.configService.getUniswapRouterV2Address(chainId)
		const WETH = this.configService.getWrappedNativeAssetWithDecimals(chainId).asset
		const v2AmountIn = await this.publicClient.simulateContract({
			address: v2Router,
			abi: UniswapRouterV2.ABI,
			// @ts-ignore
			functionName: "getAmountsIn",
			// @ts-ignore
			args: [amountOut, [WETH, tokenOutForQuote]],
		})

		return v2AmountIn.result[0]
	}
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** evm/src/core/EvmHost.sol (L1-1)
```text
// Copyright (C) Polytope Labs Ltd.
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
