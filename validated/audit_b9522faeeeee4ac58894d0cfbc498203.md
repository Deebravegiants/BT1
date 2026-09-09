[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L340-364)
```typescript
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

**File:** packages/intents-sdk/src/sdk.ts (L421-428)
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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L221-232)
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
