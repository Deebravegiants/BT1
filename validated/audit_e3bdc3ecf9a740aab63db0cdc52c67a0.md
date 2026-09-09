Based on the code analysis, both call paths (`_estimateWithdrawalFee` and `createWithdrawalIntents`) apply the minimum-withdrawal check against `actualAmount` (the fee-subtracted amount), consistently.### Verdict



**No vulnerability found for this question.**

Trace and reasoning:

1. `IntentsSDK.createWithdrawalIntents` computes `actualAmount = feeInclusive ? amount - feeEstimation.amount : amount` and calls `bridge.validateWithdrawal({ amount: actualAmount, ... })` **before** calling `bridge.createWithdrawalIntents`. [1](#0-0) 

2. `PoaBridge.validateWithdrawal` enforces `MinWithdrawalAmountError` on exactly this `actualAmount`: [2](#0-1) 

So for the scenario described (`amount` above `min_withdrawal_amount` but `amount - fee` below it), `validateWithdrawal` throws before `bridge.createWithdrawalIntents` is ever invoked — the under-min `actualAmount` never reaches signing unchecked.

3. `_estimateWithdrawalFee` performs the identical `actualAmount` computation and the identical `validateWithdrawal({ amount: actualAmount })` call, plus an additional `FeeExceedsAmountError` guard for the `amount <= fee.amount` case: [3](#0-2) 

Both entrypoints check the *same* fee-adjusted value, contradicting the premise that one path checks `actualAmount` while "elsewhere" checks the fee-less amount.

4. `PoaBridge.createWithdrawalIntents` adds the fee back: `amount: withdrawalParams.amount + relayerFee` where `withdrawalParams.amount` is already `actualAmount`. [4](#0-3) 

Since `PoaBridge.estimateWithdrawalFee` populates `fee.amount` and `underlyingFees[PoaBridge].relayerFee` with the same `relayerFee` value at construction time, `actualAmount + relayerFee = amount` — the signed intent's `amount` field reconstructs exactly the original `amount` the caller specified, and the destination effectively receives `amount - fee`. The debited/signed amount and displayed amount reconcile. [5](#0-4) 

5. The missing explicit `FeeExceedsAmountError` in the top-level `createWithdrawalIntents` is not exploitable: if `feeEstimation.amount > amount`, `actualAmount` becomes negative, and `MinWithdrawalAmountError` in `validateWithdrawal` (`actualAmount < minWithdrawalAmount`, where the minimum is always a positive value) fires regardless, blocking the intent before it's built or signed.

The only way to produce the divergence hypothesized in the question is for the caller to construct an internally-inconsistent `FeeEstimation` object where `.amount` disagrees with `.underlyingFees[PoaBridge].relayerFee` — but that requires the caller/integrator to fabricate a malformed fee object rather than use the SDK's own `estimateWithdrawalFee` output, which is a self-inflicted misuse of the API surface, not an attack reachable by an unprivileged counterparty against a victim's own signed withdrawal, and is out of scope per the stated rules.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L342-354)
```typescript
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
```

**File:** packages/intents-sdk/src/sdk.ts (L421-442)
```typescript
				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
				}
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - fee.amount
					: args.withdrawalParams.amount;

				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					feeEstimation: fee,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
					destinationMemo: args.withdrawalParams.destinationMemo,
					// When estimating fees before the exact amount is known, skip minimum amount validation while keeping all other validation intact.
					skipMinAmountValidation:
						args.withdrawalParams.amount === 0n &&
						args.withdrawalParams.feeInclusive === false,
				});
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L146-161)
```typescript
		const relayerFee = getUnderlyingFee(
			args.feeEstimation,
			RouteEnum.PoaBridge,
			"relayerFee",
		);
		assert(
			relayerFee >= 0n,
			`Invalid POA bridge relayer fee: expected >= 0, got ${relayerFee}`,
		);

		const intent = createWithdrawIntentPrimitive({
			...args.withdrawalParams,
			amount: args.withdrawalParams.amount + relayerFee,
			destinationMemo: args.withdrawalParams.destinationMemo,
		});
		return Promise.resolve([intent]);
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L221-230)
```typescript
		if (!args.skipMinAmountValidation) {
			const minWithdrawalAmount = BigInt(tokenInfo.min_withdrawal_amount);
			if (args.amount < minWithdrawalAmount) {
				throw new MinWithdrawalAmountError(
					minWithdrawalAmount,
					args.amount,
					args.assetId,
				);
			}
		}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L279-293)
```typescript
		const relayerFee = BigInt(estimation.withdrawalFee);
		assert(
			relayerFee >= 0n,
			`Invalid POA bridge relayer fee: expected >= 0, got ${relayerFee}`,
		);
		return {
			amount: relayerFee,
			quote: null,
			underlyingFees: {
				[RouteEnum.PoaBridge]: {
					relayerFee,
				},
			},
		};
	}
```
