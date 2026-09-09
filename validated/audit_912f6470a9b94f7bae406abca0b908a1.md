No vulnerability found for this question.

The `SynthVault` weight-gaming bug class requires a staking/reward vault that computes a user's reward-weight from a manipulable on-chain spot price at deposit time. This repository (`packages/intents-sdk/src/**`, `packages/internal-utils/src/**`, `packages/crosschain-assetid/src/**`, `contract-types/src/standard-schema.ts`) contains no such vault, weight, or reward-share mechanism — it is a cross-chain intents SDK dealing with bridges, withdrawal fee estimation, and asset-id/token utilities [1](#0-0) [2](#0-1) .

The only place where a "spot price" concept surfaces is `getFeeQuote`'s USD-price-based fallback used to estimate a fee quote when an exact quote request fails, but that price comes from an external price feed (`tokensUsdPricesHttpClient`) and is explicitly out of scope per the rules ("trust assumptions about external RPCs, the relayer, bridge APIs or price feeds; ... price assumptions") [3](#0-2) . There is also no equality being broken here comparable to an inflated reward weight — the fallback quote is bounded and validated against the solver's actual quote (`amount_out` must be within a ratio band and at least `feeAmount`) before use [4](#0-3) .

No unprivileged debit, misdelivery, replay, wrong-contract binding, stuck-funds, double-credit, or overcharge equality violation analogous to the `SynthVault._deposit` weight-inflation bug exists in the in-scope code.

### Citations

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L43-62)
```typescript
/**
 * ExactIn fallback with 1.2x multiplier
 */
export async function getFeeQuote({
	feeAmount,
	feeAssetId,
	tokenAssetId,
	quoteOptions,
	envConfig,
	logger,
	solverRelayApiKey,
}: {
	feeAmount: bigint;
	feeAssetId: string;
	tokenAssetId: string;
	quoteOptions?: QuoteOptions;
	envConfig: EnvConfig;
	logger?: ILogger;
	solverRelayApiKey?: string;
}): Promise<solverRelay.Quote> {
```

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L90-119)
```typescript
		const prices = await tokens({ envConfig });
		const feeAssetPrice = prices.items.find(
			(t) => t.defuse_asset_id === feeAssetId,
		);
		const tokenAssetPrice = prices.items.find(
			(t) => t.defuse_asset_id === tokenAssetId,
		);

		if (feeAssetPrice == null || tokenAssetPrice == null) {
			throw err;
		}

		// Precision-safe computation using fixed-point BigInt
		// Scale USD prices to 1e6 (micro-dollars) for stable integer math
		const USD_SCALE = 1_000_000; // 1e6
		const feePriceScaled = BigInt(Math.round(feeAssetPrice.price * USD_SCALE));
		const tokenPriceScaled = BigInt(
			Math.round(tokenAssetPrice.price * USD_SCALE),
		);
		const feeDecimals = BigInt(feeAssetPrice.decimals);
		const tokenDecimals = BigInt(tokenAssetPrice.decimals);

		// ceil( feeAmount * feePrice / 10^feeDecimals / tokenPrice * 10^tokenDecimals * 1.2 )
		const num = feeAmount * feePriceScaled * 12n * 10n ** tokenDecimals;
		const den = tokenPriceScaled * 10n ** feeDecimals * 10n;
		let exactAmountIn = num / den;
		if (num % den !== 0n) exactAmountIn += 1n; // ceil

		// Avoid sending 0 to the solver
		if (exactAmountIn === 0n) exactAmountIn = 1n;
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

**File:** packages/internal-utils/src/utils/tokenUtils.ts (L1-42)
```typescript
import type {
	BaseTokenInfo,
	TokenValue,
	UnifiedTokenInfo,
} from "../types/base";
import { assert, type AssertErrorType } from "./assert";
import { validateNearAddress } from "./near";
import { isBaseToken } from "./token";

type BalanceMapping = Record<string, bigint>;

export function computeTotalBalance(
	token: BaseTokenInfo["defuseAssetId"][] | BaseTokenInfo | UnifiedTokenInfo,
	balances: BalanceMapping,
): bigint | undefined {
	// Case 1: Array of token IDs
	if (Array.isArray(token)) {
		const uniqueTokens = new Set(token);
		let total = 0n;

		for (const tokenId of uniqueTokens) {
			const balance = balances[tokenId];
			if (balance == null) {
				return undefined;
			}
			total += balance;
		}

		return total;
	}

	// Case 2: Base token
	if (isBaseToken(token)) {
		return balances[token.defuseAssetId];
	}

	// Case 3: Unified token
	return computeTotalBalance(
		token.groupedTokens.map((t) => t.defuseAssetId),
		balances,
	);
}
```
