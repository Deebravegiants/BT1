### Title
Unbounded `amount_in` on exact-out fee quotes lets a solver charge an arbitrarily inflated fee - (File: `packages/internal-utils/src/solverRelay/getQuote.ts`)

### Summary
`matchesRequest` in `getQuote.ts` only verifies the side of the quote fixed by the caller's request. For `exact_amount_out` requests (used by `getFeeQuote`'s primary path), it validates `quote.amount_out === quoteParams.exact_amount_out` but places no constraint on `quote.amount_in`, which becomes `feeEstimation.amount` charged to the user. Unlike the `exact_amount_in` fallback path in `getFeeQuote` (which caps the ratio at 1.5x), the primary exact-out path has no sanity bound on `amount_in`.

### Finding Description
The broken equality: `feeEstimation.amount` (what the user is actually charged) should approximate the real/fair cost of swapping `feeAmount` of `feeAssetId`, but nothing enforces this — only `quote.amount_out === quoteParams.exact_amount_out` is checked [1](#0-0) .

Path:
1. Every bridge's `estimateWithdrawalFee` (e.g. `omni-bridge.ts`, `direct-bridge.ts`, `hot-bridge.ts`, `aurora-engine-bridge.ts`) calls `getFeeQuote({ feeAmount, feeAssetId, tokenAssetId, ... })` [2](#0-1) .
2. `getFeeQuote`'s primary attempt sends `exact_amount_out: feeAmount.toString()` to `solverRelay.getQuote` with no post-hoc check on the returned `amount_in` [3](#0-2) . Only if this call throws a `QuoteError` does the code fall back to an `exact_amount_in` request with a computed 1.2x buffer and an explicit ≤1.5x ratio sanity check on `quote.amount_out` [4](#0-3) .
3. Inside `getQuote`, `handleQuoteResult` drops quotes that fail `matchesRequest`, but for `exact_amount_out` it only checks `amount_out` equality — `amount_in` is unconstrained [5](#0-4) .
4. `sortQuotes` picks the minimum `amount_in` among valid quotes for exact_out [6](#0-5) , but this only helps if an honest competing quote exists in the same response. If the malicious/only solver's quote is the sole valid one returned, it wins unconditionally.
5. The winning quote's `amount_in` becomes `feeEstimation.amount` directly: `amount: feeQuote ? BigInt(feeQuote.amount_in) : feeAmount` [7](#0-6)  (same pattern in `direct-bridge.ts` and `hot-bridge.ts`).
6. The only downstream guard is `FeeExceedsAmountError`, which fires solely when `feeInclusive` is true and `fee.amount >= withdrawal amount` [8](#0-7) . This bounds the fee only by the withdrawal amount itself — it is not a market-rate sanity check, and when `feeInclusive` is false, there is no check at all.

Attacker input: a permissionless solver responding to the relay's `quote` RPC for a fee-quote request with `amount_out` exactly equal to the requested `feeAmount` and an arbitrarily large `amount_in` (e.g., 1000x fair value).

### Impact Explanation
The inflated `amount_in` becomes `feeEstimation.amount`, which is directly debited from the user via the `token_diff` intent (`-feeEstimation.quote.amount_in` on the input asset) when `createWithdrawalIntents` builds the withdrawal [9](#0-8) . This is a fee overcharge draining a material share (or, if `feeInclusive` is false, potentially more than the entire withdrawal amount, up to the user's whole balance) of the user's funds — matching the "Critical: a fee error draining a material share of the amount" / "High: a fee overcharge" categories. It is repeatable on every withdrawal that requires a fee quote and is answered by (or exclusively answered by) the malicious solver.

### Likelihood Explanation
Preconditions: the malicious actor must operate a solver registered with the solver relay and be selected/be the fastest or only responder for the specific fee-quote pair (`tokenAssetId` -> `feeAssetId`) at the time of the request. This is plausible for lower-liquidity token pairs with fewer competing solvers, or via network-level race conditions where the attacker's response wins the relay's aggregation window. No special privileges beyond being a permissionless solver are required, matching the threat model. The `1.5x` cap exists only on the fallback exact-in path, confirming this was a known control the exact-out path lacks.

### Recommendation
In `getFeeQuote` (`packages/intents-sdk/src/lib/estimate-fee.ts`), after receiving a quote from the primary `exact_amount_out` call, validate `quote.amount_in` against an independent price reference (the same `tokens()` USD price lookup used in the fallback) with a bounded ratio (e.g., the same 1.5x cap), rejecting/retrying if exceeded — mirroring the check already applied to the fallback exact-in path. Alternatively, enforce this bound centrally in `matchesRequest`/`handleQuoteResult` for `exact_amount_out` quotes whenever a reference price is available to the caller.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/estimate-fee.exploit.test.ts
import { vi, describe, it, expect } from "vitest";
import * as quoteWithLogModule from "@defuse-protocol/internal-utils/solverRelay/utils/quoteWithLog";
import { getFeeQuote } from "./estimate-fee";

describe("getFeeQuote exact_out inflation", () => {
  it("accepts a quote with amount_out == feeAmount but amount_in 1000x fair value", async () => {
    const feeAmount = 1000n; // requested exact_amount_out
    const fairAmountIn = 1000n; // honest ~1:1 rate
    const maliciousAmountIn = fairAmountIn * 1000n; // 1000x inflation

    vi.spyOn(quoteWithLogModule, "quoteWithLog").mockResolvedValue([
      {
        amount_in: maliciousAmountIn.toString(),
        amount_out: feeAmount.toString(), // matches exact_amount_out exactly
        defuse_asset_identifier_in: "nep141:token.near",
        defuse_asset_identifier_out: "nep141:wrap.near",
        expiration_time: "2099-01-01T00:00:00.000Z",
        quote_hash: "malicious",
      },
    ]);

    const quote = await getFeeQuote({
      feeAmount,
      feeAssetId: "nep141:wrap.near",
      tokenAssetId: "nep141:token.near",
      envConfig: {} as any,
    });

    // Broken equality: amount_out matches request exactly...
    expect(BigInt(quote.amount_out)).toBe(feeAmount);
    // ...but amount_in (charged to user as feeEstimation.amount) is unbounded/1000x fair value,
    // with no ratio cap applied on this path (unlike the exact-in fallback's 1.5x cap).
    expect(BigInt(quote.amount_in)).toBe(maliciousAmountIn);
    expect(BigInt(quote.amount_in) > fairAmountIn * 10n).toBe(true); // no cap enforced
  });
});
```
This demonstrates `getFeeQuote`/`getQuote` accept the malicious quote unmodified, with `feeEstimation.amount` set to `maliciousAmountIn`, absent any ratio check comparable to the fallback path's 1.5x cap at `packages/intents-sdk/src/lib/estimate-fee.ts:139-159`.

### Citations

**File:** packages/internal-utils/src/solverRelay/getQuote.ts (L108-112)
```typescript
		// For exact_out, sort by `amount_in` in ascending order
		if (BigInt(a.amount_in) < BigInt(b.amount_in)) return -1;
		if (BigInt(a.amount_in) > BigInt(b.amount_in)) return 1;
		return 0;
	});
```

**File:** packages/internal-utils/src/solverRelay/getQuote.ts (L119-138)
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L612-631)
```typescript
		let amount = 0n;
		let quote = null;
		// Skip quoting when native fee = 0 and no storage deposit is needed
		// or for prefunded tokens.
		if (
			totalAmountToQuote > 0n &&
			!this.bridgeConfig.prefundedNativeFeeTokens.includes(
				args.withdrawalParams.assetId,
			)
		) {
			quote = await getFeeQuote({
				feeAmount: totalAmountToQuote,
				feeAssetId: NEAR_NATIVE_ASSET_ID,
				tokenAssetId: args.withdrawalParams.assetId,
				logger: args.logger,
				envConfig: this.envConfig,
				quoteOptions: args.quoteOptions,
				solverRelayApiKey: this.solverRelayApiKey,
			});
			amount += BigInt(quote.amount_in);
```

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L62-80)
```typescript
}): Promise<solverRelay.Quote> {
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

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L139-159)
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
```

**File:** packages/intents-sdk/src/sdk.ts (L421-425)
```typescript
				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
				}
```

**File:** packages/intents-sdk/src/sdk.test.ts (L1918-1926)
```typescript
		await expect(intents).resolves.toEqual([
			{
				intent: "token_diff",
				diff: {
					[feeEstimation.quote.defuse_asset_identifier_in]:
						`-${feeEstimation.quote.amount_in}`,
					[feeEstimation.quote.defuse_asset_identifier_out]:
						feeEstimation.quote.amount_out,
				},
```
