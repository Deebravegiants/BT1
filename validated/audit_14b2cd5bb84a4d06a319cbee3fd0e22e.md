### Title
Unbounded exact-out `amount_in` from a permissionless solver inflates `OmniBridge.estimateWithdrawalFee`'s combined relayer+storage fee - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.estimateWithdrawalFee` combines the relayer fee and storage-deposit fee into `totalAmountToQuote` and requests a single exact-out quote via `getFeeQuote`, which forwards to `solverRelay.getQuote` with `exact_amount_out` set. Neither `getQuote`'s `matchesRequest`/`sortQuotes` logic nor `getFeeQuote` validates the returned `amount_in` against any expected/fair value for the exact-out path, so a permissionless solver can return an arbitrarily large `amount_in` that is adopted verbatim as `feeEstimation.amount` and later debited from the user via the `token_diff` intent.

### Finding Description
Equality that should hold: `feeEstimation.amount == real relayerFee + storageDepositFee` (expressed in the withdrawal token, at a fair market rate). This breaks when the exact-out quote path returns an inflated `amount_in`.

Trace:
- `estimateWithdrawalFee` computes `totalAmountToQuote = fee.native_token_fee + storageDepositFee` [1](#0-0) .
- It calls `getFeeQuote({ feeAmount: totalAmountToQuote, feeAssetId: NEAR_NATIVE_ASSET_ID, tokenAssetId: withdrawalParams.assetId, ... })` and sets `amount += BigInt(quote.amount_in)`, which becomes `feeEstimation.amount` [2](#0-1) .
- `getFeeQuote`'s primary path issues `solverRelay.getQuote` with `exact_amount_out: feeAmount.toString()` and returns whatever quote is selected, with no check that `amount_in` is reasonable [3](#0-2) . The reasonableness check (`actualRatio > 1500n` / 1.5x cap) only exists in the `exact_amount_in` fallback branch that runs after a `QuoteError`, i.e., only when the exact-out quote fails outright [4](#0-3) .
- Inside `solverRelay.getQuote`'s `handleQuoteResult`, `matchesRequest` for an exact-out request only verifies `quote.amount_out === exact_amount_out`; it explicitly does not check `amount_in`, leaving it "what the solver competes on" [5](#0-4) . `sortQuotes` picks the lowest `amount_in` among *valid* quotes for `exact_out` [6](#0-5) , but if a single (or colluding) permissionless solver is the only responder, or all responders inflate `amount_in`, there is no floor/ceiling comparison against feeAmount's fair value.
- The resulting `quote.amount_in` is used directly to build the debit leg of the `token_diff` intent: `[quote.defuse_asset_identifier_in]: -${quote.amount_in}` [7](#0-6) .

Existing guards that do not prevent this:
- `validateWithdrawal` only asserts `feeEstimation.amount > 0n` and that `relayerFee > 0n` for non-UTXO chains — both are satisfied by an inflated fee, so they don't catch overcharge [8](#0-7) [9](#0-8) .
- `FeeExceedsAmountError` only fires if the fee exceeds the total withdrawal amount, not if it is merely inflated but still smaller than the amount [10](#0-9) .
- No price-sanity check exists on the exact-out success path (unlike the exact-in fallback's 1.5x ratio check).

### Impact Explanation
The user's `token_diff` intent debits `quote.amount_in` of the withdrawal token to pay for a relayer/storage fee that a permissionless solver can inflate arbitrarily on the exact-out quote leg. This is a fee overcharge that can drain a material share of the withdrawal amount, matching the "Critical - fee error draining a material share of the amount" / "High - fee overcharge" impact categories. It affects any OmniBridge withdrawal where the token is not in `FEE_SUBSIDIZED_TOKENS`/`prefundedNativeFeeTokens` and where a storage deposit or relayer fee quote is required, and is repeatable per withdrawal call.

### Likelihood Explanation
Preconditions: token not fee-subsidized and not in `prefundedNativeFeeTokens`; `totalAmountToQuote > 0n` (true whenever a relayer fee or storage deposit is owed) [2](#0-1) . Attacker cost is low: any permissionless solver responding to the relay's quote request can submit an inflated `amount_in` for the requested `exact_amount_out`; nothing in `matchesRequest`/`sortQuotes`/`getFeeQuote` bounds it on the success path. This requires no privileged access, RPC compromise, or relayer misbehavior — only a normal solver participating in the intents solver market, which is within the defined attacker model.

### Recommendation
Add a sanity/ratio check on the exact-out success path in `getFeeQuote` (mirroring the 1.5x check already used in the exact-in fallback), comparing `quote.amount_in` against an expected fair value derived from token/fee asset prices, and reject/retry when it exceeds a bounded multiplier. Alternatively, cap `amount_in` using a price-oracle-derived ceiling before using it to build the debit intent in `OmniBridge.createWithdrawalIntents`/`estimateWithdrawalFee`.

### Proof of Concept
Vitest plan (mock only HTTP/solverRelay):
1. Mock `BridgeAPI.getFee` to return `native_token_fee = 100n`, no `insufficient_utxo`.
2. Mock NEAR storage balance helpers so `minStorageBalance - currentStorageBalance = 50n` (storage deposit needed), giving `totalAmountToQuote = 150n`.
3. Mock `solverRelay.getQuote` (or the lower-level `quoteWithLog`) to resolve, for the `exact_amount_out: "150"` request, a quote with `amount_out: "150"`, `amount_in: "1000000"` (grossly inflated vs. a fair ~150-run rate), `defuse_asset_identifier_in/out` matching the request.
4. Call `omniBridge.estimateWithdrawalFee(...)` for a non-subsidized token.
5. Assert `feeEstimation.amount === 1000000n` and `feeEstimation.quote.amount_in === "1000000"`, i.e. `feeEstimation.amount` (LHS) far exceeds the real fee value 150 converted to token units at fair price (RHS), with no throw/cap — demonstrating the broken equality `feeEstimation.amount == real relayerFee + storageDepositFee`.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L304-315)
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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L341-349)
```typescript
		const isFeeSubsidized = FEE_SUBSIDIZED_TOKENS.includes(args.assetId);
		const isPrefundedWithdrawal =
			this.bridgeConfig.prefundedNativeFeeTokens.includes(args.assetId);
		if (!isFeeSubsidized && !isPrefundedWithdrawal) {
			assert(
				args.feeEstimation.amount > 0n,
				`Invalid Omni Bridge fee: expected > 0, got ${args.feeEstimation.amount}`,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L440-455)
```typescript
		if (!utxoChainWithdrawal && !isFeeSubsidized) {
			const relayerFee = getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.OmniBridge,
				"relayerFee",
			);
			// Currently only UTXO chains withdrawals can have 0 relayerFee
			assert(
				getUnderlyingFee(
					args.feeEstimation,
					RouteEnum.OmniBridge,
					"relayerFee",
				) > 0n,
				`Invalid Omni Bridge relayer fee for non UTXO chain withdrawal: expected > 0, got ${relayerFee}`,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L590-599)
```typescript
		let totalAmountToQuote = fee.native_token_fee;

		const [minStorageBalance, currentStorageBalance] =
			await this.getCachedStorageDepositValue(assetInfo.contractId);

		const storageDepositFee = minStorageBalance - currentStorageBalance;
		if (storageDepositFee > 0n) {
			totalAmountToQuote += storageDepositFee;
			underlyingFees.storageDepositFee = storageDepositFee;
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L616-632)
```typescript
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
		}
```

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

**File:** packages/internal-utils/src/solverRelay/getQuote.ts (L96-112)
```typescript
function sortQuotes(
	quotes: Quote[],
	quoteKind: "exact_in" | "exact_out",
): Quote[] {
	return quotes.slice().sort((a, b) => {
		if (quoteKind === "exact_in") {
			// For exact_in, sort by `amount_out` in descending order
			if (BigInt(a.amount_out) > BigInt(b.amount_out)) return -1;
			if (BigInt(a.amount_out) < BigInt(b.amount_out)) return 1;
			return 0;
		}

		// For exact_out, sort by `amount_in` in ascending order
		if (BigInt(a.amount_in) < BigInt(b.amount_in)) return -1;
		if (BigInt(a.amount_in) > BigInt(b.amount_in)) return 1;
		return 0;
	});
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

**File:** packages/intents-sdk/src/classes/errors.ts (L8-21)
```typescript
export class FeeExceedsAmountError extends BaseError {
	constructor(
		public feeEstimation: FeeEstimation,
		public amount: bigint,
	) {
		super("Amount too small to pay fee.", {
			metaMessages: [
				`Required fee: ${feeEstimation.amount}`,
				`Withdrawal amount: ${amount}`,
			],
			name: "FeeExceedsAmountError",
		});
	}
}
```
