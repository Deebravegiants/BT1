### Title
Missing fee-exceeds-amount guard in `createWithdrawalIntents()` allows negative/underflowed withdrawal amounts - (File: `packages/intents-sdk/src/sdk.ts`)

### Summary
`IntentsSDK.createWithdrawalIntents()` computes `actualAmount = withdrawalParams.amount - feeEstimation.amount` when `feeInclusive` is true, but unlike its sibling method `_estimateWithdrawalFee()`, it never checks that `amount > feeEstimation.amount` before doing the subtraction. This mirrors the "withdrawal transaction output value can go below the dust limit and even become negative" bug class from the reference report.

### Finding Description
`_estimateWithdrawalFee()` explicitly guards against the fee exceeding the amount before subtracting: [1](#0-0) 

However `createWithdrawalIntents()`, a separately callable public API method that accepts a caller-supplied `feeEstimation` object (not necessarily the one freshly produced by `estimateWithdrawalFee`), performs the identical subtraction with no such check: [2](#0-1) 

Because `feeEstimation` is a plain data object passed in by the caller/integrator (e.g., a stale quote captured earlier, or a fee estimate for a different `withdrawalParams.amount`), any caller can invoke `createWithdrawalIntents` with `feeEstimation.amount >= withdrawalParams.amount` and `feeInclusive: true`. `actualAmount` then becomes zero or negative. This value is passed straight into `bridge.validateWithdrawal()` and `bridge.createWithdrawalIntents()`, and ultimately serialized as a string amount (`actualAmount.toString()`) inside the constructed intent (e.g., `ft_withdraw`), as shown in the test fixtures building such messages: [3](#0-2) 

For most bridge paths (`OmniBridge.validateWithdrawal`), the only amount-floor checks that exist are asset/route specific (`MIN_WITHDRAWAL_AMOUNT` for UTXO chains, `MIN_AMOUNT_SOL_OMNI_WITHDRAWAL` for SOL) — there is no generic `amount > 0` assertion covering the general NEP-141/EVM withdrawal branch: [4](#0-3) 

This breaks the equality that the debited/withdrawn amount must equal `amount - fee` and remain non-negative before being embedded in a signed intent — the same class of error flagged in the external report ("output value can go below the dust limit and even become negative... validate the output value after subtracting the estimated fee").

### Impact Explanation
A withdrawal intent constructed with a negative or zero amount can either (a) be rejected on-chain after the user's nonce/signature has already been consumed by the relayer, leaving the withdrawal stuck and requiring manual intervention, or (b) if the destination bridge/contract coerces the negative bigint into an unsigned representation during serialization, potentially misrepresent the withdrawn amount. This falls under the "withdrawal stuck until manual intervention" / fee-overcharge impact category described in scope rules.

### Likelihood Explanation
Requires a caller of the SDK (integrator) to invoke `createWithdrawalIntents()` directly with a `feeEstimation` that does not match the current `withdrawalParams.amount` (e.g., a cached/stale fee quote, or a fee quote obtained for a larger amount) combined with `feeInclusive: true`. This is a plausible integration pattern since `createWithdrawalIntents` and `estimateWithdrawalFee` are decoupled public methods and nothing in the type system prevents passing a mismatched pair.

### Recommendation
Add the same guard used in `_estimateWithdrawalFee()` to `createWithdrawalIntents()`: throw `FeeExceedsAmountError` (or equivalent) when `withdrawalParams.feeInclusive && withdrawalParams.amount <= feeEstimation.amount`, before computing `actualAmount`.

### Proof of Concept
1. Call `sdk.estimateWithdrawalFee({ withdrawalParams: { amount: 1000n, feeInclusive: true, ... } })` to obtain a `feeEstimation` with `amount: 950n`.
2. Later, call `sdk.createWithdrawalIntents({ withdrawalParams: { amount: 500n, feeInclusive: true, ...}, feeEstimation })` reusing the stale `feeEstimation` (amount 950n) for a smaller withdrawal amount (500n).
3. `actualAmount = 500n - 950n = -450n` is computed with no guard, and is forwarded to `bridge.validateWithdrawal` / `bridge.createWithdrawalIntents`, producing an intent with a negative/invalid amount instead of being rejected up front like `_estimateWithdrawalFee` would do.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L334-354)
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

**File:** packages/intents-sdk/src/sdk.test.ts (L1581-1600)
```typescript
		const actualAmount = withdrawalParams.amount;
		await expect(intents).resolves.toEqual([
			{
				intent: "ft_withdraw",
				min_gas: "37400000000000",
				token: "nbtc.bridge.near",
				receiver_id: OMNI_BRIDGE_CONTRACT,
				amount: actualAmount.toString(),
				storage_deposit: undefined,
				msg: JSON.stringify({
					recipient: omniAddress(ChainKind.Btc, destinationAddress),
					fee: "0",
					native_token_fee: "0",
					external_id: OMNI_WITHDRAWAL_EXTERNAL_ID,
					msg: JSON.stringify({
						MaxGasFee: utxoMaxGasFee.toString(),
					}),
				}),
			},
		]);
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L405-531)
```typescript
		if (!args.skipMinAmountValidation) {
			// verifyTransferAmount ensures (amount - fee) > 0 after normalisation.
			// We pass the actual amount and a zero fee to avoid fee-handling differences
			// between different withdrawal types (UTXO transfers vs regular transfers where the fee is paid in wrap.near).
			const normalisationCheckSucceeded = verifyTransferAmount(
				args.amount, // total amount without fee
				0n, // fee
				decimals.origin_decimals,
				decimals.decimals,
			);
			if (normalisationCheckSucceeded === false) {
				const minAmount = getMinimumTransferableAmount(
					decimals.origin_decimals,
					decimals.decimals,
				);
				throw new MinWithdrawalAmountError(
					minAmount,
					args.amount,
					args.assetId,
				);
			}
		}

		const intentsStorageBalance = await this.getCachedIntentsStorageBalance();

		// Ensure available storage balance is > MIN_STORAGE_BALANCE_FOR_INTENTS_NEAR.
		// If it’s lower, block the transfer—otherwise the funds will be refunded
		// to the intents contract account instead of the original withdrawing account.
		if (intentsStorageBalance <= MIN_STORAGE_BALANCE_FOR_INTENTS_NEAR) {
			throw new IntentsNearOmniAvailableBalanceTooLowError(
				intentsStorageBalance.toString(),
			);
		}

		const utxoChainWithdrawal = isUtxoChain(omniChainKind);
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
		} else if (
			!args.skipMinAmountValidation &&
			omniChainKind === ChainKind.Sol &&
			assetInfo.contractId === SOL_OMNI_CONTRACT_ID &&
			args.amount < MIN_AMOUNT_SOL_OMNI_WITHDRAWAL
		) {
			throw new MinWithdrawalAmountError(
				MIN_AMOUNT_SOL_OMNI_WITHDRAWAL,
				args.amount,
				args.assetId,
			);
		}
```
