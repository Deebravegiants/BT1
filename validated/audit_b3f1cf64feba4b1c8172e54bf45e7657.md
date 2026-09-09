[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L332-340)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		feeEstimation: FeeEstimation;
		routeConfig?: RouteConfig;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
	}): Promise<void> {
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L440-519)
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

		if (utxoChainWithdrawal) {
			// UTXO availability and minimum withdrawal thresholds for UTXO chains are sourced
			// from the Omni Bridge indexer.
			const fee = await withTimeout(
				() =>
					this.omniBridgeAPI.getFee(
						omniAddress(ChainKind.Near, this.envConfig.contractID),
						omniAddress(omniChainKind, args.destinationAddress),
						omniAddress(ChainKind.Near, assetInfo.contractId),
						args.amount,
					),
				{
					timeout: typeof window !== "undefined" ? 10_000 : 3000,
					errorInstance: new OmniWithdrawalApiFeeRequestTimeoutError(),
				},
			);
			// This adds a safeguard against insufficient UTXOs on the connector contract.
			// It cannot guarantee full protection, there is always a potential race condition—
			// but it helps reduce the chance of withdrawals getting stuck due to missing UTXOs.
			if (fee.insufficient_utxo) {
				throw new InsufficientUtxoForOmniBridgeWithdrawalError(
					assetInfo.blockchain,
				);
			}

			assert(
				fee.min_amount !== null &&
					fee.min_amount !== undefined &&
					BigInt(fee.min_amount) > 0n,
				`Invalid min amount value for a UTXO chain withdrawal: expected > 0, got ${fee.min_amount}`,
			);
			const minAmount = BigInt(fee.min_amount);
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

**File:** packages/intents-sdk/src/sdk.ts (L438-442)
```typescript
					// When estimating fees before the exact amount is known, skip minimum amount validation while keeping all other validation intact.
					skipMinAmountValidation:
						args.withdrawalParams.amount === 0n &&
						args.withdrawalParams.feeInclusive === false,
				});
```
