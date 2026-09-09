### No vulnerability found for this question.

**Reasoning:**

The question's premise does not match the code. Looking at `packages/intents-sdk/src/sdk.ts` `createWithdrawalIntents`:

```
const actualAmount = args.withdrawalParams.feeInclusive
    ? args.withdrawalParams.amount - args.feeEstimation.amount
    : args.withdrawalParams.amount;
``` [1](#0-0) 

When `feeInclusive: false`, `actualAmount` is set to the raw `withdrawalParams.amount` and is never reduced by `feeEstimation.amount`. So the claim "with `feeInclusive: false` and `amount == feeEstimation.amount` (actualAmount becomes 0n)" is factually inconsistent with this code — `actualAmount` only becomes `amount - fee` (and could hit 0/negative) when `feeInclusive` is `true`, which is a different scenario, not the one under audit here.

Tracing the actual `feeInclusive: false` path end-to-end:
1. `actualAmount = withdrawalParams.amount` (unchanged).
2. `PoaBridge.createWithdrawalIntents` builds a single `ft_withdraw` intent for `actualAmount + relayerFee`, where `relayerFee = getUnderlyingFee(feeEstimation, PoaBridge, "relayerFee")` [2](#0-1) .
3. For a PoA-bridge fee estimate produced honestly by `estimateWithdrawalFee`, `feeEstimation.amount === underlyingFees[PoaBridge].relayerFee` [3](#0-2) , so the single produced debit equals `amount + fee.amount`, matching the claimed invariant `sum(debits) == amount + (feeInclusive ? 0 : fee)` exactly, and the PoA bridge itself forwards `amount` to the destination after deducting its own relayer cut off-chain, matching `destination == amount - 0`.
4. There is no separate `token_diff`/storage-deposit intent produced by `PoaBridge.createWithdrawalIntents` (unlike Hot/Omni bridges) — it's a single `ft_withdraw` intent — so there is no additional divergent debit to account for.
5. A zero/degenerate `actualAmount` (e.g., user deliberately sets `amount: 0n`) is independently blocked by the `MinWithdrawalAmountError` check inside `PoaBridge.validateWithdrawal`, which is invoked (without `skipMinAmountValidation`) from `createWithdrawalIntents` before any intent is signed [4](#0-3) [5](#0-4) .

Since the equality holds under the described `feeInclusive: false` branch and the zero-amount edge case is guarded, no vulnerability was found for this specific question.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L342-344)
```typescript
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - args.feeEstimation.amount
					: args.withdrawalParams.amount;
```

**File:** packages/intents-sdk/src/sdk.ts (L346-354)
```typescript
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L142-161)
```typescript
	createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
	}): Promise<IntentPrimitive[]> {
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L279-292)
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
```
