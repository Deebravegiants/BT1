Found this key issue: `createWithdrawalIntents` in `sdk.ts` computes `actualAmount` for a fee-inclusive withdrawal by subtracting `feeEstimation.amount` from `withdrawalParams.amount` **without any check that `feeEstimation.amount < withdrawalParams.amount`**, unlike its sibling `_estimateWithdrawalFee`, which explicitly guards this with `FeeExceedsAmountError`. [1](#0-0) 

Compare to `_estimateWithdrawalFee`, which has the guard: [2](#0-1) 

## Analysis

`createWithdrawalIntents` is a **public, independently callable** method that accepts a caller-supplied `feeEstimation` object directly (it doesn't have to originate from `estimateWithdrawalFee`) [3](#0-2) . If `feeInclusive` is `true` and `feeEstimation.amount >= withdrawalParams.amount`, `actualAmount = amount - feeEstimation.amount` becomes zero or negative (as a `bigint`, this becomes `0n` or negative). This negative/zero `actualAmount` is passed to `bridge.validateWithdrawal` and then to `bridge.createWithdrawalIntents`, which builds the on-chain intent payload directly from it [4](#0-3) .

Because Rust/TS-style negative bigints aren't rejected before being serialized into intent strings, this could produce a malformed or unauthorized-amount `ft_withdraw`/`mt_withdraw` intent (e.g., `hot-bridge.ts`'s `createWithdrawalIntents` uses `amount + feeAmount` and asserts consistency against the HOT SDK's returned intent amounts, but does not itself validate against zero/negative amounts) [5](#0-4) . For `omni-bridge`, a similar direct construction from `actualAmount` happens without re-validating fee vs. amount [6](#0-5) .

This matches the reported bug class: an equality/invariant ("fee ≤ amount so the final debited/withdrawn amount is non-negative") is broken because the check exists in one code path (`_estimateWithdrawalFee`) but is missing in a parallel, independently reachable code path (`createWithdrawalIntents`) that performs the same fee-inclusive subtraction.

### Title
Missing Fee-Exceeds-Amount Check in `createWithdrawalIntents` - (File: `packages/intents-sdk/src/sdk.ts`)

### Summary
`IntentsSDK.createWithdrawalIntents` computes `actualAmount = withdrawalParams.amount - feeEstimation.amount` for fee-inclusive withdrawals without verifying `feeEstimation.amount < withdrawalParams.amount`, unlike the equivalent check present in `_estimateWithdrawalFee` (`FeeExceedsAmountError`). [7](#0-6) [8](#0-7) 

### Finding Description
`createWithdrawalIntents` is documented and typed to accept an arbitrary caller-supplied `feeEstimation` (not necessarily the freshly computed one returned by `estimateWithdrawalFee`) [3](#0-2) . When `feeInclusive` is true, `actualAmount` can become `0n` or negative if `feeEstimation.amount >= withdrawalParams.amount`. This value flows unchecked into `bridge.validateWithdrawal` and `bridge.createWithdrawalIntents`, which build the actual on-chain intent (`ft_withdraw`/`mt_withdraw`) payload from it [9](#0-8) . The sibling method `_estimateWithdrawalFee` explicitly guards this exact scenario by throwing `FeeExceedsAmountError` [10](#0-9) , showing the SDK authors recognize this invariant must hold but failed to enforce it consistently across both entry points.

### Impact Explanation
If a stale, manipulated, or otherwise inflated `feeEstimation` is supplied to `createWithdrawalIntents` (e.g., an integrator caching an old high-fee quote and reusing it with a smaller withdrawal amount, or a race between fee estimation and submission where fees spike), the resulting `actualAmount` could be zero or negative, producing an intent that either withdraws nothing while still being debited fee amounts, or produces malformed/unexpected amounts in the signed intent payload — a fee-related overcharge/misdelivery matching the "fee error draining a material share of the amount" / "fee overcharge" impact category.

### Likelihood Explanation
Requires the caller to pass a `feeEstimation` whose `amount` is close to or exceeds `withdrawalParams.amount` for a fee-inclusive withdrawal without re-deriving it via `estimateWithdrawalFee` immediately prior — plausible in integrations that cache fee quotes or retry with a different `amount` while reusing a prior `feeEstimation`, since the method's public API explicitly allows passing any `feeEstimation` object.

### Recommendation
Add the same `FeeExceedsAmountError` guard used in `_estimateWithdrawalFee` to `createWithdrawalIntents` before computing `actualAmount`, i.e., throw if `withdrawalParams.feeInclusive && withdrawalParams.amount <= feeEstimation.amount`.

### Proof of Concept
1. Call `sdk.estimateWithdrawalFee({ withdrawalParams: { amount: 1000n, feeInclusive: true, ... } })` and obtain `feeEstimation` with `amount: 900n`.
2. Separately (or later) call `sdk.createWithdrawalIntents({ withdrawalParams: { amount: 100n, feeInclusive: true, ... }, feeEstimation })` reusing the stale `feeEstimation` with a smaller `amount`.
3. `actualAmount = 100n - 900n = -800n` is computed with no validation and passed into `bridge.validateWithdrawal`/`bridge.createWithdrawalIntents`, unlike the equivalent path in `estimateWithdrawalFee`, which would have thrown `FeeExceedsAmountError` for the same inputs.

### Citations

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

**File:** packages/intents-sdk/src/sdk.ts (L420-428)
```typescript

				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
				}
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - fee.amount
					: args.withdrawalParams.amount;
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L221-241)
```typescript
		const isNative = "native" in assetInfo;
		const amount = args.withdrawalParams.amount + (isNative ? feeAmount : 0n);

		const intent = await this.hotSdk.buildGaslessWithdrawIntent({
			feeToken: "native",
			feeAmount,
			blockNumber,
			chain: toHotNetworkId(assetInfo.blockchain),
			token: isNative ? "native" : assetInfo.address,
			amount,
			receiver: args.withdrawalParams.destinationAddress,
		});

		// Sanity check, in case HOT SDK changes
		assert(intent.amounts[0] === amount.toString(), "Amount is not correct");
		if (intent.amounts.length === 2) {
			assert(
				intent.amounts[1] === feeAmount.toString(),
				"Amount is not correct",
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L81-116)
```typescript
	let amount = params.actualAmount;
	let msg = "";
	// For withdrawals to Bitcoin and other UTXO chains we need to specify maxGasFee to the relayer
	// that is picking up our TX and sends it to a connector (btc connector for example).
	// Technically we can avoid specifying it in the message and relayer just takes the same value
	// however this introduces a risk that a malicious actor can pick up this tx and submit it to the connector
	// with a higher max gas fee value that can result in recipient getting less BTC.
	// Example with nep141:nbtc.bridge.near (made-up values):
	// utxoFees = 50 + 50 = 100, relayerFee = 2 (excluded; paid in wrap.near)
	//   feeInclusive=false: amount = 4000 -> intent = 4100 -> user receives 4000
	//   feeInclusive=true:  amount = 3898 -> intent = 3998 -> user receives 3898
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
