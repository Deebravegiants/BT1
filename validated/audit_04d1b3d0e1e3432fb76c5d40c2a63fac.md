No vulnerability found for this question.

The premise fails at the quote-acquisition layer, before `createWithdrawalIntents` ever sees the quote. `HotBridge.estimateWithdrawalFee` requests the fee quote via `getFeeQuote`, which issues a `solverRelay.getQuote` call with `exact_amount_out: feeAmount.toString()` [1](#0-0) . Inside `getQuote`, every solver-returned quote is validated by `matchesRequest` before being considered usable: for an exact-out request, it requires `BigInt(quote.amount_out) === BigInt(quoteParams.exact_amount_out)` exactly, and any quote failing this (including a solver trying to inflate `amount_out`) is dropped with a warning rather than returned [2](#0-1) [3](#0-2) .

For the fallback exact-in path (used only when the exact-out quote request fails with `QuoteError`), a malicious solver could try to maximize `amount_out`, but `getFeeQuote` explicitly bounds it: it throws away the quote if `actualRatio > 1500n` (i.e., `amount_out` more than 1.5x `feeAmount`) or if `amount_out < feeAmount` [4](#0-3) . So even in the degraded path, the solver-controlled upside is capped at 1.5x the actual relayer fee by design, not "far above" as the question assumes, and this is an existing, intentional guard (see `packages/internal-utils/CHANGELOG.md` entry "Drop quotes whose returned tokens or fixed amount don't match the request") [5](#0-4) .

By the time `HotBridge.createWithdrawalIntents` builds the `token_diff` intent from `args.feeEstimation.quote.amount_out` [6](#0-5) , `quote.amount_out` has already been constrained to equal (or, in the fallback, be within 1.5x of) `feeAmount = getUnderlyingFee(...,"relayerFee")` [7](#0-6) . There is no code path in this repo where a raw, unchecked solver quote reaches `createWithdrawalIntents`; the "trusted verbatim" quote has already passed `matchesRequest`/ratio validation upstream. Constructing a scenario where an inflated, unvalidated quote object is injected directly into `feeEstimation.quote` would require the integrator to bypass `estimateWithdrawalFee` and hand-craft the `FeeEstimation` object themselves — that is deliberate misuse of the API surface, which is explicitly out of scope per the audit rules.

### Citations

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L63-80)
```typescript
	try {
		return await solverRelay.getQuote({
			quoteParams: {
				defuse_asset_identifier_in: tokenAssetId,
				defuse_asset_identifier_out: feeAssetId,
				exact_amount_out: feeAmount.toString(),
				wait_ms: quoteOptions?.waitMs,
				min_wait_ms: quoteOptions?.minWaitMs,
				max_wait_ms: quoteOptions?.maxWaitMs,
				trusted_metadata: quoteOptions?.trustedMetadata,
			},
			config: {
				baseURL: envConfig.solverRelayBaseURL,
				logBalanceSufficient: false,
				logger: logger,
				solverRelayApiKey,
			},
		});
```

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L139-160)
```typescript
		// Check if the quote is reasonable (should be around 1.2x due to our buffer)
		// Use BigInt arithmetic with scaling to get precise ratio
		const RATIO_SCALE = 1000n; // Scale by 1000 for 3 decimal precision
		const actualRatio = (BigInt(quote.amount_out) * RATIO_SCALE) / feeAmount;
		const actualRatioNumber = Number(actualRatio) / Number(RATIO_SCALE);

		if (actualRatio > 1500n) {
			// 1.5x with scaling
			logger?.warn(
				`Quote amount_out ratio is too high: ${actualRatioNumber.toFixed(2)}x`,
			);
			throw err;
		}

		if (BigInt(quote.amount_out) < feeAmount) {
			logger?.warn(
				`Quote amount_out (${quote.amount_out}) is less than feeAmount (${feeAmount}), exact_amount_in: ${exactAmountIn}, ` +
					`fee asset price: ${feeAssetPrice.price} USD, token asset price: ${tokenAssetPrice.price} USD`,
			);
			throw err;
		}
		return quote;
```

**File:** packages/internal-utils/src/solverRelay/getQuote.ts (L60-72)
```typescript
		// The relay aggregates quotes from independent solvers, so a buggy or
		// malicious solver can return a quote that doesn't match what we asked
		// for: wrong tokens, or a different fixed amount than requested. Acting
		// on such a quote would make the user swap the wrong assets/amounts, and
		// a mismatched fixed amount also makes sortQuotes compare unlike quotes.
		// Drop it (it is neither usable nor an INSUFFICIENT_AMOUNT failure).
		if (!matchesRequest(q, quoteParams)) {
			logger?.warn("quote: dropping quote that doesn't match the request", {
				quoteParams,
				quote: q,
			});
			continue;
		}
```

**File:** packages/internal-utils/src/solverRelay/getQuote.ts (L119-139)
```typescript
function matchesRequest(
	quote: Quote,
	quoteParams: GetQuoteParams["quoteParams"],
): boolean {
	if (
		quote.defuse_asset_identifier_in !==
			quoteParams.defuse_asset_identifier_in ||
		quote.defuse_asset_identifier_out !==
			quoteParams.defuse_asset_identifier_out
	) {
		return false;
	}

	// Only the side fixed by the request is verified; the other side is what the
	// solver competes on (max amount_out for exact_in, min amount_in for
	// exact_out). Compare as BigInt so formatting differences don't matter.
	if (quoteParams.exact_amount_in != null) {
		return BigInt(quote.amount_in) === BigInt(quoteParams.exact_amount_in);
	}
	return BigInt(quote.amount_out) === BigInt(quoteParams.exact_amount_out);
}
```

**File:** packages/internal-utils/CHANGELOG.md (L37-41)
```markdown
## 0.34.1

### Patch Changes

- a6f918c: Drop quotes whose returned tokens or fixed amount don't match the request
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L197-201)
```typescript
		const feeAmount = getUnderlyingFee(
			args.feeEstimation,
			RouteEnum.HotBridge,
			"relayerFee",
		);
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L208-219)
```typescript
		if (args.feeEstimation.quote !== null) {
			intents.push({
				intent: "token_diff",
				diff: {
					[args.feeEstimation.quote.defuse_asset_identifier_in]:
						`-${args.feeEstimation.quote.amount_in}`,
					[args.feeEstimation.quote.defuse_asset_identifier_out]:
						args.feeEstimation.quote.amount_out,
				},
				referral: args.referral,
			});
		}
```
