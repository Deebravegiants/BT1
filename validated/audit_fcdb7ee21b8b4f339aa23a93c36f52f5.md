### Title
Phantom-order price snapshot can be manipulated by a self-delegated attacker inflating output-token balance to set the weighted-median rate used to size real cross-chain orders - (File: `sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts`)

### Summary
`aggregatePhantomBids` weights each phantom bid's quoted price by the bidding solver's **live, spot-read ERC-20/vault balance** of the leg's output token on the destination chain. Any EOA can become a "verified solver" for this purpose by self-delegating via EIP-7702 to the chain's `SolverAccount` — a permissionless, self-serve action — and can therefore submit a phantom bid whose weight it fully controls by temporarily holding a large balance of the output token at read time. Because a bidder holding over half the total weight "sets the published price verbatim" (`weightedMedian`), this lets an attacker publish an arbitrary rate for a pair, which then feeds `LiquidityPool.buyRate`/`sellRate` (via `updateLiquidityPools`) and is consumed by `IntentGateway.quoteIntent()`'s default `indexed_rates` strategy to size real users' order inputs/outputs. This is the same bug class as the Napier report: an attacker inflates a price input right before it is read/priced, then exploits the resulting quote against real counterparties.

### Finding Description
1. `runAggregation` (`sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts`, around lines 1479-1497) computes each bid's weight from the solver's current on-chain balance:
```
const weights = await Promise.all(
    quotedLegs.map(async ([, leg]) => {
        const outputToken = toAddress(leg.outputToken)
        const balance = await getBalance(destUrl, chain, outputToken, solver)
        ...
```
2. `weightedMedian` (lines 709-724) picks the price whose cumulative weight crosses half the total — "so a solver holding over half the leg's weight sets the published price verbatim" (as the code comment itself states at `phantom-probe-curve-value-published-price.md` line 41-42 and in the aggregation docstring, lines 1244-1246).
3. `isVerifiedSolverBid` (lines 913-979) only checks that the bidder (a) signed the bid correctly and (b) is EIP-7702-delegated to the chain's `SolverAccount`. Delegation itself is **not gated by any allowlist or stake requirement** — any EOA can self-delegate (see `DelegationService.setupDelegation`, `sdk/packages/simplex/src/services/DelegationService.ts` lines 404-485, which is exactly the self-serve delegation flow every solver — including an attacker — performs).
4. The resulting per-leg median is persisted as `PhantomOrderPriceSnapshotV2` and folded into `LiquidityPool.buyRate`/`sellRate` by `updateLiquidityPools`/`weightedRate`.
5. `IntentGateway.quoteIntent()` defaults to the `indexed_rates` strategy (`sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts`), which reads exactly this pool rate and uses it, unadjusted by the caller, to compute `amountIn`/`amountOut` for a **real** cross-chain intent order that a user then places and escrows funds against.

Put together: an attacker (1) self-delegates an EOA to `SolverAccount` on the destination chain, (2) briefly acquires/borrows a large balance of the leg's output token on that chain, (3) submits a phantom bid at an inflated (or deflated) price during the bid window so that its balance-weighted quote dominates `weightedMedian`, (4) the indexer publishes that price into the pool's `buyRate`/`sellRate`, and (5) a victim's subsequent real order — quoted via `quoteIntent`'s default indexed-rate path — is sized off the manipulated rate. The attacker (as the eventual filler/solver of that real order) can then extract the mispriced difference from the user's escrowed input.

### Impact Explanation
A successfully manipulated published rate directly changes the `amountIn`/`amountOut` used to construct a real, fund-escrowing `IntentGatewayV2` order. A user relying on the default quote could be induced to escrow substantially more input than the fair market rate justifies, or to accept far less output than fair, with the attacker (or a colluding solver aware of the manipulated window) filling that order at the skewed rate. This is a direct value-extraction path against real user funds passing through the IntentGateway/HyperBridge intents system, matching the "concrete theft" bar in the validation criteria.

### Likelihood Explanation
The barrier to becoming a "counted" bidder is only EIP-7702 self-delegation to `SolverAccount`, which is explicitly designed to be permissionless and automatic (Simplex performs it for any operator at startup with no admin approval). Acquiring a large output-token balance at read time is feasible with a flash loan, a large but temporary transfer, or simply parking capital during the bid window since the balance read is a simple spot `eth_call`, not a locked/staked amount. The weighting logic itself documents the exact primitive being exploited ("a solver holding over half the leg's weight sets the published price verbatim"), indicating the design is aware of, but does not fully mitigate, this class of manipulation for any token pair whose real liquidity/weight is thin relative to what an attacker can transiently acquire.

### Recommendation
Do not weight phantom-bid prices purely by a spot balance read at aggregation time. Consider: requiring collateral/stake that cannot be flash-acquired, using a time-weighted or multi-block balance measurement, capping the influence any single bidder's weight can have on the median regardless of balance, or cross-checking the phantom snapshot against an independent, harder-to-manipulate price source before it is allowed to move `LiquidityPool.buyRate`/`sellRate` used for real order quoting.

### Proof of Concept
1. Attacker EOA `A` self-delegates via EIP-7702 to the target chain's `SolverAccount` (permissionless, same flow any Simplex operator uses — `DelegationService.setupDelegation`).
2. Immediately before/during a phantom order's bid window, `A` acquires (via flash loan or temporary transfer) a large balance of the leg's output token `T` on the destination chain — large enough to exceed the combined weight of all other genuine bidders for that leg.
3. `A` submits a phantom bid quoting an inflated (or deflated) amount for `T`, correctly signed per `isVerifiedSolverBid`'s checks (signature over `userOpHash`, nonce bound to `commitment`/session key).
4. When the window closes, `runAggregation`/`weightedMedian` selects `A`'s quote as the leg's `medianPrice` because its balance-derived weight exceeds 50% of total weight (`sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts` lines 709-724, 1479-1502, 1551).
5. `updateLiquidityPools` folds this into `LiquidityPool.buyRate`/`sellRate` for the pair.
6. A victim calls `IntentGateway.quoteIntent()` with no explicit strategy, which reads the manipulated `indexed_rates` (`sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts` lines 44-77) and returns a skewed `amountIn`/`amountOut`.
7. The victim places the resulting order and escrows funds at the skewed rate; `A` (or a colluding solver) fills it, extracting the mispriced value. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L697-724)
```typescript
// Liquidity-weighted median of solver quotes. Each quote's influence is proportional to `weight` —
// the solver's total balance for the output token across native + vault venues — so a solver that
// can actually deliver size moves the price more than one quoting on thin liquidity. Returns the
// lower weighted median: the smallest price whose cumulative weight reaches half of the total.
// Zero-weight quotes contribute nothing.
//
// Callers must not hand this an entry set whose weights are all zero: with nothing to weight by it
// can only pick a quote by position, and for an even-sized set that position is the upper of the
// two middles — so "the median" becomes "whoever quoted higher", settable by a solver holding no
// inventory at all. aggregatePhantomBids drops such legs instead of pricing them. The fallback
// below stays only so an unguarded caller gets a number rather than a crash; treat reaching it as
// a caller bug.
export function weightedMedian(entries: { price: bigint; weight: bigint }[]): bigint {
	const sorted = [...entries].sort((a, b) => (a.price < b.price ? -1 : a.price > b.price ? 1 : 0))
	const totalWeight = sorted.reduce((acc, e) => (e.weight > 0n ? acc + e.weight : acc), 0n)

	if (totalWeight === 0n) {
		return sorted[Math.floor(sorted.length / 2)].price
	}

	let cumulative = 0n
	for (const entry of sorted) {
		if (entry.weight <= 0n) continue
		cumulative += entry.weight
		if (cumulative * 2n >= totalWeight) return entry.price
	}
	return sorted[sorted.length - 1].price
}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L904-979)
```typescript
/**
 * Whether a bid genuinely came from one of our solvers, and so may influence the snapshot.
 *
 * Anyone can submit a bid to the coprocessor, and every accepted quote moves the weighted median the
 * rest of the protocol prices intents against, so a bid is only counted if it clears both of the
 * checks SolverAccount would apply on-chain: the userOp carries a solver signature over this order's
 * userOpHash that recovers to the sender, and the sender is EIP-7702-delegated to the chain's
 * SolverAccount. Fails closed — a bid that cannot be read or verified is not counted.
 */
async function isVerifiedSolverBid(params: {
	userOp: PackedUserOperation
	commitment: string
	sessionKey: HexString
	chainId: bigint
	solverAccounts: readonly string[]
	evmRpcUrl: string
	recoverSigner: RecoverBidSigner
	bidNonceKey: BidNonceKeyFn
	/** Cached per aggregation, so duplicate fillers and retries do not re-read the same answer. */
	isDelegated: DelegationReader
	logger?: AggregationLogger
}): Promise<boolean> {
	const {
		userOp,
		commitment,
		sessionKey,
		chainId,
		solverAccounts,
		evmRpcUrl,
		recoverSigner,
		bidNonceKey,
		isDelegated,
		logger,
	} = params
	const solver = userOp.sender

	const parsed = splitBidSignature(userOp.signature)
	if (!parsed) {
		logger?.warn({ solver, commitment }, "Rejecting phantom bid: malformed userOp signature")
		return false
	}

	// Cheap early-out ONLY. The prefix sits inside userOp.signature, which userOpHash excludes, so it
	// is attacker-mutable and must never be what binds a bid to an order — the nonce key below is.
	if (parsed.commitment.toLowerCase() !== commitment.toLowerCase()) {
		logger?.warn(
			{ solver, commitment, signedFor: parsed.commitment },
			"Rejecting phantom bid: signed for another order",
		)
		return false
	}

	// The authoritative binding, mirroring SolverAccount.validateUserOp on-chain. The nonce IS
	// covered by userOpHash, so a solver signature stays valid only for the (order, sessionKey) pair
	// its nonce key was derived from. `sessionKey` is read from the bid's own calldata, which is also
	// covered by userOpHash — so every operand here is signed, leaving nothing for a replay to swap.
	if (BigInt(userOp.nonce) >> 64n !== bidNonceKey(commitment as HexString, sessionKey)) {
		logger?.warn({ solver, commitment }, "Rejecting phantom bid: nonce does not bind order and session key")
		return false
	}

	// SolverAccount._rawSignatureValidation recovers over the bare userOpHash and requires the signer
	// to be the account itself, which under EIP-7702 is the sender EOA.
	const signer = await recoverSigner(userOp, ENTRY_POINT_V08_ADDRESS, chainId, parsed.solverSignature)
	if (!signer || signer.toLowerCase() !== solver.toLowerCase()) {
		logger?.warn({ solver, commitment, signer }, "Rejecting phantom bid: signature does not recover to the sender")
		return false
	}

	if (!(await isDelegated(evmRpcUrl, solver, solverAccounts))) {
		logger?.warn({ solver, commitment, solverAccounts }, "Rejecting phantom bid: sender is not a delegated solver")
		return false
	}

	return true
}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1479-1502)
```typescript
			const weights = await Promise.all(
				// Price influence: the solver's liquidity in THIS leg's output token on the destination
				// chain, so a leg is weighted by the inventory that actually backs it.
				quotedLegs.map(async ([, leg]) => {
					const outputToken = toAddress(leg.outputToken)
					const balance = await getBalance(destUrl, chain, outputToken, solver)
					return positions.reduce(
						(total, state) =>
							total +
							positionAmountOfToken({
								info: state.info,
								liquidity: state.liquidity,
								sqrtPriceX96: state.sqrtPriceX96,
								outputToken,
							}),
						balance,
					)
				}),
			)
			for (const [position, [legIndex, leg]] of quotedLegs.entries()) {
				const weight = weights[position]
				const entry = quotesByLeg.get(legIndex) ?? { outputToken: leg.outputToken, quotes: [], bidders: [] }
				entry.quotes.push({ price: leg.solverAmount, weight })
				entry.bidders.push({ solver: normalizedSolver as HexString, weight, acceptedSources })
```

**File:** sdk/packages/simplex/src/services/DelegationService.ts (L404-421)
```typescript
	async setupDelegation(chain: string): Promise<boolean> {
		const solverAccountContract = this.configService.getSolverAccountContractAddress(chain)

		if (!solverAccountContract) {
			this.logger.error("solverAccountContractAddress not configured")
			return false
		}

		if (await this.isDelegated(chain)) {
			this.logger.info({ chain }, "EOA already delegated to SolverAccount")
			// Delegated does NOT imply bootstrapped. An account delegated by a release that
			// charged EIP-2612 permits has no Permit2 allowance at all, and the delegation op
			// that would have installed one never runs again. Without this, the first sponsored
			// op falls into a native-funded approve — the exact trap the 2026-09-02 `skipPermit`
			// entry in docs/ai/Decisions.md records hitting on Base and Arbitrum.
			await this.ensurePermit2Allowance(chain)
			return true
		}
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L44-77)
```typescript
	async quote(
		params: QuoteIntentParams,
		source: IntentQuoteChainContext,
		destination: IntentQuoteChainContext,
	): Promise<IndexedRateQuoteIntentResult> {
		validateQuoteParams(params)
		const sourceConfig = getConfigByStateMachineId(source.stateMachineId)
		const destinationConfig = getConfigByStateMachineId(destination.stateMachineId)
		if (!sourceConfig) throw new UnsupportedLiquidityChainError(source.stateMachineId)
		if (!destinationConfig) throw new UnsupportedLiquidityChainError(destination.stateMachineId)

		const tokenIn = this.resolveAsset(sourceConfig.stateMachineId, params.tokenIn)
		const tokenOut = this.resolveAsset(destinationConfig.stateMachineId, params.tokenOut)
		const [protocolFeeBps, rates] = await Promise.all([
			readProtocolFeeBps(this.chainConfigService, source),
			new LiquidityEngine(this.getQueryClient()).getBuyAndSellRates({
				sourceChain: sourceConfig.stateMachineId,
				destinationChain: destinationConfig.stateMachineId,
				tokenInSymbol: tokenIn.symbol,
				tokenOutSymbol: tokenOut.symbol,
			}),
		])
		if (!rates) {
			throw new IndexedRateUnavailableError({
				source: sourceConfig.stateMachineId,
				destination: destinationConfig.stateMachineId,
				tokenIn: tokenIn.symbol,
				tokenOut: tokenOut.symbol,
			})
		}

		const selectedRate = selectIndexedRate(rates, tokenIn.symbol, tokenOut.symbol)
		return quoteWithIndexedRate(params, tokenIn, tokenOut, selectedRate, rates, protocolFeeBps)
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L146-173)
```typescript
function quoteWithIndexedRate(
	params: QuoteIntentParams,
	tokenIn: ResolvedQuoteAsset,
	tokenOut: ResolvedQuoteAsset,
	selectedRate: SelectedIndexedRate,
	rates: BuyAndSellRates,
	protocolFeeBps: bigint,
): IndexedRateQuoteIntentResult {
	const inputUnit = 10n ** BigInt(tokenIn.decimals)
	const outputUnit = 10n ** BigInt(tokenOut.decimals)
	if (params.amountIn !== undefined) {
		const netAmountIn = deductProtocolFee(params.amountIn, protocolFeeBps)
		const amountOut =
			selectedRate.side === "buy"
				? (netAmountIn * selectedRate.scaledRate * outputUnit) / (inputUnit * INDEXED_RATE_SCALE)
				: (netAmountIn * outputUnit * INDEXED_RATE_SCALE) / (inputUnit * selectedRate.scaledRate)
		if (amountOut <= 0n) throw new InvalidIndexedRateError("quote rounds down to zero output")
		return buildResult("EXACT_INPUT", params.amountIn, amountOut, selectedRate, rates, protocolFeeBps)
	}

	if (params.amountOut === undefined) throw new Error("Quote amount is missing after validation")
	const netAmountIn =
		selectedRate.side === "buy"
			? divCeil(params.amountOut * inputUnit * INDEXED_RATE_SCALE, selectedRate.scaledRate * outputUnit)
			: divCeil(params.amountOut * inputUnit * selectedRate.scaledRate, outputUnit * INDEXED_RATE_SCALE)
	const amountIn = grossUpForProtocolFee(netAmountIn, protocolFeeBps)
	return buildResult("EXACT_OUTPUT", amountIn, params.amountOut, selectedRate, rates, protocolFeeBps)
}
```
