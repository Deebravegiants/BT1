### Title
Stale `FeeEstimation` from one withdrawal accepted for a different withdrawal amount, causing fee/amount mismatch - (File: packages/intents-sdk/src/lib/estimate-fee.ts, packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts, packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts)

### Summary
`getUnderlyingFee` only checks that a route key exists in `feeEstimation.underlyingFees`, never that the `feeEstimation` object was produced for the specific `assetId`/`amount`/`destinationAddress` being withdrawn now. `OmniBridge.validateWithdrawal` re-fetches live fee data (`omniBridgeAPI.getFee`) for the *current* amount only to run sanity/min-amount checks, but `OmniBridge.createWithdrawalIntents` → `deriveOmniWithdrawIntentParams` still pulls `relayerFee`/`utxoMaxGasFee`/`utxoProtocolFee` straight from the caller-supplied (possibly stale) `feeEstimation`, so the actual `ft_withdraw` amount is built from fee figures that don't correspond to the withdrawal being executed.

### Finding Description
The broken equality: `feeEstimation.underlyingFees[route].{relayerFee,utxoMaxGasFee,utxoProtocolFee}` used to compute `ft_withdraw.amount` for withdrawal B should equal the fee that a fresh `estimateWithdrawalFee` call for B's exact `amount`/`destinationAddress` would return. Instead it is only required to equal whatever was returned for *some prior* withdrawal on the same route.

Code path:
- `getUnderlyingFee` (`packages/intents-sdk/src/lib/estimate-fee.ts:26-41`) indexes `feeEstimation.underlyingFees?.[route]` and throws only if the route key is absent — no binding to `assetId`/`amount`/`destinationAddress`. [1](#0-0) 
- `IntentsSDK.createWithdrawalIntents` (`packages/intents-sdk/src/sdk.ts:334-372`) accepts an arbitrary caller-supplied `feeEstimation` alongside `withdrawalParams`, runs `bridge.validateWithdrawal`, then calls `bridge.createWithdrawalIntents` with that same `feeEstimation`. [2](#0-1) 
- `OmniBridge.validateWithdrawal` for UTXO chains fetches fresh fee data (`insufficient_utxo`, `min_amount`) for the *current* `args.amount`, but only sanity-checks that the stale `utxoMaxGasFee`/`utxoProtocolFee` from `args.feeEstimation` are `> 0n` — it never compares them against the freshly fetched `fee.gas_fee`/`fee.protocol_fee`. [3](#0-2) 
- `OmniBridge.createWithdrawalIntents` passes the same stale `feeEstimation` into `deriveOmniWithdrawIntentParams`, which builds the actual `ft_withdraw` amount and `msg.MaxGasFee` using `getUnderlyingFee(feeEstimation, ...)` — the stale relayer/gas/protocol fee values — added to the *new* `actualAmount`. [4](#0-3) 

Exploit flow: attacker (or integrator forwarding user input) calls `estimateWithdrawalFee` for withdrawal A (small BTC amount, `RouteEnum.OmniBridge`), obtaining a `FeeEstimation` with small `utxoMaxGasFee`/`utxoProtocolFee`. They then call `createWithdrawalIntents`/`signAndSendWithdrawalIntent` for withdrawal B (same route, much larger amount, possibly same or different destination) passing A's `FeeEstimation`. `validateWithdrawal` only checks that B's `min_amount` requirement is satisfied by `B.amount + staleFee(A)`, which is trivially true for a much larger B. `createWithdrawalIntents` then builds `ft_withdraw.amount = B.amount + staleUtxoMaxGasFee(A) + staleUtxoProtocolFee(A)` and `msg.MaxGasFee = staleUtxoMaxGasFee(A)`, i.e., a fee amount that has no relationship to what a fresh estimate for B would have produced.

Existing guards (`validateAddress`, `compareAddresses`, the `> 0n` assertions, `FeeExceedsAmountError`, `min_amount`/`insufficient_utxo` checks) do not address this because none of them re-derive or compare the fee values against a fresh, amount-specific estimate — they only validate that the stale numbers are non-zero and that the resulting total clears the network's current minimum.

### Impact Explanation
The relayer fee/gas fee actually embedded in the signed `ft_withdraw` intent for withdrawal B is not the fee a fresh estimate for B would produce, but a stale figure carried over from an unrelated, differently-sized withdrawal A. This is a fee error directly affecting what is debited from the user's balance and instructed to the relayer (`MaxGasFee`) for a withdrawal the user did not see quoted this way — matching the Critical category ("a fee error draining a material share of the amount") when the mismatch is large (e.g., a fee real-estate quoted for a tiny amount reused on a withdrawal orders of magnitude larger, or vice versa causing relayer underpayment/stuck withdrawal). This is repeatable per call and requires no privileged access — any caller (or integrator forwarding attacker-controlled fee estimation objects across separate withdrawal calls) can trigger it.

### Likelihood Explanation
Preconditions: caller must retain and later reuse a `FeeEstimation` object obtained from a previous `estimateWithdrawalFee` call for a different `amount`/`destinationAddress` on the same route (most concretely demonstrated with UTXO/OmniBridge withdrawals where `utxoMaxGasFee`/`utxoProtocolFee` are amount/network-state dependent). This requires only calling two public SDK methods with attacker-controlled arguments — no special privileges, RPC manipulation, or contract admin access. Feasibility is high since nothing in `createWithdrawalIntents` or `validateWithdrawal` cryptographically or programmatically binds the `feeEstimation` to the specific withdrawal request being processed.

### Recommendation
Bind `FeeEstimation` to the exact withdrawal it was computed for — e.g., include a hash/fingerprint of `assetId`, `amount`, `destinationAddress`, `destinationMemo`, and `routeConfig` in the returned `FeeEstimation`, and have `createWithdrawalIntents`/`validateWithdrawal` assert that this fingerprint matches the current `withdrawalParams` before consuming `underlyingFees`. Alternatively, in `OmniBridge.validateWithdrawal`, replace the `> 0n` sanity checks on `utxoMaxGasFee`/`utxoProtocolFee`/`relayerFee` with an exact equality check against the freshly fetched `fee.gas_fee`/`fee.protocol_fee`/`fee.native_token_fee` for the current `amount`/`destinationAddress`, and reject if they diverge.

### Proof of Concept
```ts
// vitest, mocking only HTTP (omniBridgeAPI.getFee, storage balance RPCs, solver relay quote)
it("accepts a stale FeeEstimation from a small BTC withdrawal for a much larger withdrawal", async () => {
  const sdk = new IntentsSDK({ referral: "x" });

  // Mock omniBridgeAPI.getFee to return fees proportional/appropriate to `amount`
  mockOmniGetFee((toAmount) => ({
    native_token_fee: 0n,
    gas_fee: computeRealisticGasFee(toAmount),   // e.g. scales with amount/network state
    protocol_fee: computeRealisticProtocolFee(toAmount),
    min_amount: MIN_BTC,
    insufficient_utxo: false,
  }));

  const smallParams = { assetId: BTC_ASSET, amount: 1000n, destinationAddress: BTC_ADDR, routeConfig: { route: RouteEnum.OmniBridge } };
  const largeParams = { ...smallParams, amount: 1_000_000n };

  const feeA = await sdk.estimateWithdrawalFee({ withdrawalParams: smallParams });
  const freshFeeB = await sdk.estimateWithdrawalFee({ withdrawalParams: largeParams });

  // feeA.underlyingFees[OmniBridge].utxoMaxGasFee/utxoProtocolFee != freshFeeB's equivalents
  expect(feeA.underlyingFees[RouteEnum.OmniBridge].utxoMaxGasFee)
    .not.toBe(freshFeeB.underlyingFees[RouteEnum.OmniBridge].utxoMaxGasFee);

  // Reuse stale feeA for the large withdrawal B
  const intents = await sdk.createWithdrawalIntents({
    withdrawalParams: largeParams,
    feeEstimation: feeA, // stale, mismatched
  });

  const ftWithdraw = intents.find((i) => i.intent === "ft_withdraw");
  const expectedAmountWithFreshFee =
    largeParams.amount +
    freshFeeB.underlyingFees[RouteEnum.OmniBridge].utxoMaxGasFee +
    freshFeeB.underlyingFees[RouteEnum.OmniBridge].utxoProtocolFee;

  // Demonstrates amount conservation break: intent amount uses stale fee, not fresh fee for B
  expect(BigInt(ftWithdraw.amount)).not.toBe(expectedAmountWithFreshFee);
  expect(BigInt(ftWithdraw.amount)).toBe(
    largeParams.amount +
      feeA.underlyingFees[RouteEnum.OmniBridge].utxoMaxGasFee +
      feeA.underlyingFees[RouteEnum.OmniBridge].utxoProtocolFee,
  );
});
```

### Citations

**File:** packages/intents-sdk/src/lib/estimate-fee.ts (L26-41)
```typescript
export function getUnderlyingFee<
	R extends keyof UnderlyingFees,
	K extends keyof NonNullable<UnderlyingFees[R]>,
>(
	feeEstimation: FeeEstimation,
	route: R,
	feeKey: K,
): NonNullable<UnderlyingFees[R]>[K] {
	const routeFees = feeEstimation.underlyingFees?.[route];
	if (routeFees === undefined) {
		throw new Error(
			`Missing underlying fees for route "${String(route)}". Fee estimation must populate underlyingFees before creating withdrawal intents.`,
		);
	}
	return (routeFees as NonNullable<UnderlyingFees[R]>)[feeKey];
}
```

**File:** packages/intents-sdk/src/sdk.ts (L334-364)
```typescript
	public async createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
		logger?: ILogger;
	}): Promise<IntentPrimitive[]> {
		for (const bridge of this.bridges) {
			if (await bridge.supports(args.withdrawalParams)) {
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - args.feeEstimation.amount
					: args.withdrawalParams.amount;

				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					destinationMemo: args.withdrawalParams.destinationMemo,
					feeEstimation: args.feeEstimation,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
				});

				return bridge.createWithdrawalIntents({
					withdrawalParams: {
						...args.withdrawalParams,
						amount: actualAmount,
					},
					feeEstimation: args.feeEstimation,
					referral: args.referral ?? this.referral,
				});
			}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L489-519)
```typescript
			const utxoMaxGasFee = getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.OmniBridge,
				"utxoMaxGasFee",
			);
			const utxoProtocolFee = getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.OmniBridge,
				"utxoProtocolFee",
			);
			assert(
				utxoMaxGasFee !== undefined && utxoMaxGasFee > 0n,
				`Invalid Omni Bridge utxo max gas fee: expected > 0, got ${utxoMaxGasFee}`,
			);
			assert(
				utxoProtocolFee !== undefined && utxoProtocolFee > 0n,
				`Invalid Omni Bridge utxo protocol fee: expected > 0, got ${utxoProtocolFee}`,
			);

			if (!args.skipMinAmountValidation) {
				// args.amount is without fee, we need to pass an amount with fee
				const actualAmountWithFee =
					args.amount + utxoMaxGasFee + utxoProtocolFee;
				if (actualAmountWithFee < minAmount) {
					throw new MinWithdrawalAmountError(
						minAmount,
						actualAmountWithFee,
						args.assetId,
					);
				}
			}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L92-116)
```typescript
	if (isUtxoChain(params.omniChainKind)) {
		const utxoMaxGasFee = getUnderlyingFee(
			params.feeEstimation,
			RouteEnum.OmniBridge,
			"utxoMaxGasFee",
		);
		const utxoProtocolFee = getUnderlyingFee(
			params.feeEstimation,
			RouteEnum.OmniBridge,
			"utxoProtocolFee",
		);
		assert(
			utxoMaxGasFee !== undefined && utxoMaxGasFee > 0n,
			`Invalid Omni Bridge utxo max gas fee: expected > 0, got ${utxoMaxGasFee}`,
		);
		assert(
			utxoProtocolFee !== undefined && utxoProtocolFee > 0n,
			`Invalid Omni Bridge utxo protocol fee: expected > 0, got ${utxoProtocolFee}`,
		);

		// UTXO withdrawals add protocol + max gas fees to the intent amount since they're paid
		// from the withdrawn asset, not wrap.near.
		amount += utxoMaxGasFee + utxoProtocolFee;
		msg = JSON.stringify({ MaxGasFee: utxoMaxGasFee.toString() });
	}
```
