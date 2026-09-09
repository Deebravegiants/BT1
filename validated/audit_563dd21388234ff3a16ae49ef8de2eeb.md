### Title
`estimateWithdrawalFee` reports `amount: 0` for prefunded Omni tokens while the produced intents still debit the user's wrap.near via a `storage_deposit` intent for the full relayer fee - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`, `omni-withdraw-params.ts`, `omni-bridge-utils.ts`)

### Summary
For assets listed in `bridgeConfigs[OmniBridge].prefundedNativeFeeTokens`, `estimateWithdrawalFee` deliberately skips the fee-quote swap and returns `feeEstimation.amount = 0`, but keeps `underlyingFees.relayerFee = fee.native_token_fee > 0`. When the intents are subsequently built, `deriveOmniWithdrawIntentParams` reads `nativeFee` from `underlyingFees.relayerFee` (not from `feeEstimation.amount`), so `nativeFee > 0` still triggers a `storage_deposit` intent that moves `nativeFee` wrap.near out of the user's balance, even though the fee shown to the caller was zero.

### Finding Description
The broken equality is `feeEstimation.amount == total value leaving the user's balance beyond amount` (as stated in the question's invariant).

In `estimateWithdrawalFee` (`packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts:612-632`), when the asset is in `prefundedNativeFeeTokens`, the `getFeeQuote` call (which normally converts part of the withdrawn asset into the wrap.near needed to pay the relayer) is skipped entirely, so `amount` stays `0n` and `quote` stays `null`. However `underlyingFees.relayerFee` is set earlier from `fee.native_token_fee` and is **not** zeroed for prefunded tokens (only `FEE_SUBSIDIZED_TOKENS` get that treatment, at line 581-583). This is confirmed by the test at `omni-bridge.test.ts:1562-1603`: `getFeeQuoteSpy` is asserted not called, `result.amount` is `0n`, yet `result.underlyingFees[RouteEnum.OmniBridge]?.relayerFee` is asserted to be `50_000_000_000n`.

`validateWithdrawal` (`omni-bridge.ts:341-349`) explicitly exempts prefunded tokens from the `feeEstimation.amount > 0n` assertion, confirmed by the test `"validateWithdrawal accepts a zero fee amount for a prefunded token"` (`omni-bridge.test.ts:1657-1703`), which passes `feeEstimation.amount: 0n` alongside `relayerFee: 50_000_000_000n` and expects success.

When intents are then constructed, `deriveOmniWithdrawIntentParams` (`omni-withdraw-params.ts:66-70, 137-153`) computes `nativeFee` via `getUnderlyingFee(feeEstimation, OmniBridge, "relayerFee")` — i.e., from `underlyingFees.relayerFee`, not from `feeEstimation.amount`. Since `nativeFee = 50_000_000_000n > 0`, `storageDepositAccountId` is computed (non-null). `createWithdrawIntentsPrimitive` (`omni-bridge-utils.ts:56-63`) then unconditionally pushes:
```
{ intent: "storage_deposit", deposit_for_account_id: storageDepositAccountId, amount: nativeFee.toString(), contract_id: OMNI_BRIDGE_CONTRACT }
```
This intent moves `nativeFee` of wrap.near out of the signer's (user's) intents balance, in addition to the `ft_withdraw` intent for the withdrawn token. In the normal (non-prefunded) path, this wrap.near comes from a solver swap whose cost is exactly `feeEstimation.amount` of the withdrawn asset — so the displayed fee tracks the real cost. In the prefunded path, the swap is skipped, so the wrap.near for the `storage_deposit` intent is drawn directly from the user's pre-existing wrap.near balance in the intents contract, with zero accounting in `feeEstimation.amount`.

No existing guard catches this: `assert(feeEstimation.amount > 0n)` is explicitly bypassed for prefunded tokens; `FeeExceedsAmountError` only checks the withdrawal amount vs. quoted fee, not cross-asset wrap.near consumption; nothing in `validateWithdrawal` or `deriveOmniWithdrawIntentParams` verifies that `nativeFee == 0` when `feeEstimation.amount == 0`.

### Impact Explanation
A user withdrawing a token flagged as prefunded is shown (and, with `feeInclusive: true`, budgets for) a fee of exactly `0`. The signed intent batch nevertheless includes a `storage_deposit` intent that debits `nativeFee` (in the test, `50_000_000_000` yoctoNEAR-equivalent wrap.near) from the user's own wrap.near balance in the intents contract — money the fee estimate never disclosed. This is a fee overcharge/misreport matching the "fee overcharge" High-impact category: the caller signs and has debited a value they were told was zero, and it recurs on every withdrawal of a "prefunded" asset for as long as the integrator's config lists it.

### Likelihood Explanation
Preconditions: the route must be OmniBridge, the withdrawn `assetId` must appear in the integrator-supplied `bridgeConfigs[OmniBridge].prefundedNativeFeeTokens`, and `fee.native_token_fee` returned by the Omni fee API must be non-zero (typical for non-NEAR-native assets/chains). This is the documented, intended usage of the `prefundedNativeFeeTokens` feature (added per `CHANGELOG.md`: "Support prefunded tokens for Omni Bridge via Bridge Config") — not a misuse of an escape hatch, but a genuine mismatch between the displayed and actual fee whenever that (intended) config is used. Any ordinary user withdrawing such a token, with no special attacker action needed, will be silently charged wrap.near beyond the displayed `feeEstimation.amount`. It reproduces on every call.

### Recommendation
Either (a) zero out `underlyingFees.relayerFee` (and thus `nativeFee`) for prefunded tokens, so no `storage_deposit`/native fee is charged at all, matching the "prefunded" semantics and the displayed `amount = 0`; or (b) if the relayer fee genuinely still needs to be paid from the user's wrap.near, include that cost in `feeEstimation.amount`/`underlyingFees` so `feeEstimation.amount` reflects the true wrap.near debit, and drop the exemption in `validateWithdrawal` that allows `amount === 0` while `relayerFee > 0`.

### Proof of Concept
```ts
// vitest, packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts

it("prefunded token: feeEstimation.amount is 0 but produced intents still move nativeFee wrap.near", async () => {
  vi.spyOn(BridgeAPI.prototype, "getFee").mockResolvedValue({
    native_token_fee: 50_000_000_000n,
    usd_fee: 0.5,
    insufficient_utxo: false,
  });

  const bridge = new OmniBridge({
    envConfig: configsByEnvironment.production,
    nearProvider: nearFailoverRpcProvider({ urls: PUBLIC_NEAR_RPC_URLS }),
    bridgeConfig: { prefundedNativeFeeTokens: [prefundedAssetId] },
  });
  bridge["storageDepositCache"].set(prefundedTokenId, [0n, 0n]);

  const feeEstimation = await bridge.estimateWithdrawalFee({
    withdrawalParams: {
      assetId: prefundedAssetId,
      destinationAddress: zeroAddress,
      routeConfig: createOmniBridgeRoute(Chains.Ethereum),
      amount: 1_000_000n,
    },
  });

  // Side A of the invariant: displayed fee
  expect(feeEstimation.amount).toBe(0n);

  const params = deriveOmniWithdrawIntentParams({
    assetId: prefundedAssetId,
    destinationAddress: zeroAddress,
    actualAmount: 1_000_000n,
    omniChainKind: ChainKind.Eth,
    intentsContract: "intents.near",
    feeEstimation,
  });
  const intents = createWithdrawIntentsPrimitive(params);

  // Side B of the invariant: actual value moved out of the user (wrap.near via storage_deposit)
  const storageDepositIntent = intents.find(i => i.intent === "storage_deposit");
  expect(storageDepositIntent).toBeDefined();
  expect(storageDepositIntent!.amount).toBe("50000000000"); // nativeFee, non-zero

  // Assert the broken equality: feeEstimation.amount (0) != actual wrap.near debited (50_000_000_000)
  expect(feeEstimation.amount).not.toBe(BigInt(storageDepositIntent!.amount));
});
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L580-632)
```typescript
		// Omni API returns non-zero fee for subsidized tokens, so we enforce 0 fee for specific tokens.
		if (FEE_SUBSIDIZED_TOKENS.includes(args.withdrawalParams.assetId)) {
			fee.native_token_fee = 0n;
		}

		const underlyingFees: RouteFeeStructures[RouteEnum["OmniBridge"]] = {
			relayerFee: fee.native_token_fee,
			storageDepositFee: 0n,
		};

		let totalAmountToQuote = fee.native_token_fee;

		const [minStorageBalance, currentStorageBalance] =
			await this.getCachedStorageDepositValue(assetInfo.contractId);

		const storageDepositFee = minStorageBalance - currentStorageBalance;
		if (storageDepositFee > 0n) {
			totalAmountToQuote += storageDepositFee;
			underlyingFees.storageDepositFee = storageDepositFee;
		}

		// withdraw of nep141:wrap.near
		if (args.withdrawalParams.assetId === NEAR_NATIVE_ASSET_ID) {
			return {
				amount: totalAmountToQuote,
				quote: null,
				underlyingFees: {
					[RouteEnum.OmniBridge]: underlyingFees,
				},
			};
		}

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
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L66-153)
```typescript
	const nativeFee = getUnderlyingFee(
		params.feeEstimation,
		RouteEnum.OmniBridge,
		"relayerFee",
	);
	assert(
		nativeFee >= 0n,
		`Invalid Omni bridge relayer fee: expected >= 0, got ${nativeFee}`,
	);
	const storageDepositAmount = getUnderlyingFee(
		params.feeEstimation,
		RouteEnum.OmniBridge,
		"storageDepositFee",
	);

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

	// Omni contract only accepts lowercase bech32 addresses; uppercase/mixed-case
	// bech32 is spec-valid but rejected on-chain. Base58 (legacy/P2SH) is left as-is.
	const destinationAddress =
		params.omniChainKind === ChainKind.Btc &&
		/^bc1/i.test(params.destinationAddress)
			? params.destinationAddress.toLowerCase()
			: params.destinationAddress;

	const recipient = omniAddress(params.omniChainKind, destinationAddress);
	const externalId = params.externalId ?? crypto.randomUUID();

	return {
		tokenAccountId,
		recipient,
		msg,
		externalId,
		amount,
		nativeFee,
		storageDepositAmount,
		storageDepositAccountId:
			nativeFee > 0n
				? calculateStorageAccountId(
						{
							token: `near:${tokenAccountId}`,
							amount,
							recipient,
							fee: {
								fee: 0n,
								native_fee: nativeFee,
							},
							sender: `near:${params.intentsContract}`,
							msg,
						},
						externalId,
					)
				: null,
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge-utils.ts (L29-76)
```typescript
export function createWithdrawIntentsPrimitive({
	tokenAccountId,
	recipient,
	msg,
	externalId,
	storageDepositAccountId,
	amount,
	nativeFee,
	storageDepositAmount,
}: OmniWithdrawIntentParams): (IntentStorageDeposit | IntentFtWithdraw)[] {
	const ftWithdrawPayload: {
		recipient: OmniAddress;
		fee: string;
		native_token_fee: string;
		external_id: string;
		msg?: string;
	} = {
		recipient,
		fee: "0",
		native_token_fee: nativeFee.toString(),
		external_id: externalId,
	};
	if (msg !== "") {
		ftWithdrawPayload.msg = msg;
	}

	const intents: (IntentStorageDeposit | IntentFtWithdraw)[] = [];
	if (storageDepositAccountId !== null) {
		intents.push({
			deposit_for_account_id: storageDepositAccountId,
			amount: nativeFee.toString(),
			contract_id: OMNI_BRIDGE_CONTRACT,
			intent: "storage_deposit",
		});
	}
	intents.push({
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: OMNI_BRIDGE_CONTRACT,
		amount: amount.toString(),
		storage_deposit:
			storageDepositAmount > 0n ? storageDepositAmount.toString() : undefined,
		msg: JSON.stringify(ftWithdrawPayload),
		min_gas: MIN_GAS_AMOUNT,
	});

	return intents;
}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L1562-1703)
```typescript
		it("estimateWithdrawalFee skips the fee quote for a prefunded token while keeping the relayer fee", async () => {
			vi.spyOn(BridgeAPI.prototype, "getFee").mockResolvedValue({
				native_token_fee: 50_000_000_000n,
				usd_fee: 0.5,
				insufficient_utxo: false,
			});
			const getFeeQuoteSpy = vi
				.spyOn(estimateFee, "getFeeQuote")
				.mockRejectedValue(
					new Error("getFeeQuote must not be called for prefunded tokens"),
				);

			const nearProvider = nearFailoverRpcProvider({
				urls: PUBLIC_NEAR_RPC_URLS,
			});

			const bridge = new OmniBridge({
				envConfig: configsByEnvironment.production,
				nearProvider,
				bridgeConfig: { prefundedNativeFeeTokens: [prefundedAssetId] },
			});

			// Pre-seed storage deposit cache so estimation does not hit the network.
			// biome-ignore lint/complexity/useLiteralKeys: accessing private property for testing
			bridge["storageDepositCache"].set(prefundedTokenId, [0n, 0n]);

			const result = await bridge.estimateWithdrawalFee({
				withdrawalParams: {
					assetId: prefundedAssetId,
					destinationAddress: zeroAddress,
					routeConfig: createOmniBridgeRoute(Chains.Ethereum),
					amount: 1_000_000n,
				},
			});

			expect(getFeeQuoteSpy).not.toHaveBeenCalled();
			expect(result.amount).toBe(0n);
			expect(result.quote).toBeNull();
			expect(result.underlyingFees[RouteEnum.OmniBridge]?.relayerFee).toBe(
				50_000_000_000n,
			);
		});

		it("estimateWithdrawalFee skips the fee quote for a prefunded token while keeping the relayer fee and storage deposit fee", async () => {
			vi.spyOn(BridgeAPI.prototype, "getFee").mockResolvedValue({
				native_token_fee: 50_000_000_000n,
				usd_fee: 0.5,
				insufficient_utxo: false,
			});
			const getFeeQuoteSpy = vi
				.spyOn(estimateFee, "getFeeQuote")
				.mockRejectedValue(
					new Error("getFeeQuote must not be called for prefunded tokens"),
				);

			const nearProvider = nearFailoverRpcProvider({
				urls: PUBLIC_NEAR_RPC_URLS,
			});

			const bridge = new OmniBridge({
				envConfig: configsByEnvironment.production,
				nearProvider,
				bridgeConfig: { prefundedNativeFeeTokens: [prefundedAssetId] },
			});

			const minStoragedDeposit = 1n;
			const currentStorageBalance = 0n;
			const storageBalanceToPay = minStoragedDeposit - currentStorageBalance;
			// Pre-seed storage deposit cache so estimation does not hit the network.
			// biome-ignore lint/complexity/useLiteralKeys: accessing private property for testing
			bridge["storageDepositCache"].set(prefundedTokenId, [
				minStoragedDeposit,
				currentStorageBalance,
			]);

			const result = await bridge.estimateWithdrawalFee({
				withdrawalParams: {
					assetId: prefundedAssetId,
					destinationAddress: zeroAddress,
					routeConfig: createOmniBridgeRoute(Chains.Ethereum),
					amount: 1_000_000n,
				},
			});

			expect(getFeeQuoteSpy).not.toHaveBeenCalled();
			expect(result.amount).toBe(0n);
			expect(result.quote).toBeNull();
			expect(result.underlyingFees[RouteEnum.OmniBridge]?.relayerFee).toBe(
				50_000_000_000n,
			);
			expect(
				result.underlyingFees[RouteEnum.OmniBridge]?.storageDepositFee,
			).toBe(storageBalanceToPay);
		});

		it("validateWithdrawal accepts a zero fee amount for a prefunded token", async () => {
			const highBalance = (
				MIN_STORAGE_BALANCE_FOR_INTENTS_NEAR + 1n
			).toString();

			vi.spyOn(
				omniBridgeUtils,
				"getAccountOmniStorageBalance",
			).mockResolvedValue({ total: highBalance, available: highBalance });
			vi.spyOn(omniBridgeUtils, "getBridgedToken").mockResolvedValue(
				prefundedOriginChainOmniAddress,
			);
			vi.spyOn(omniBridgeUtils, "getTokenDecimals").mockResolvedValue({
				decimals: 6,
				origin_decimals: 6,
			});

			const nearProvider = nearFailoverRpcProvider({
				urls: PUBLIC_NEAR_RPC_URLS,
			});

			const bridge = new OmniBridge({
				envConfig: configsByEnvironment.production,
				nearProvider,
				bridgeConfig: { prefundedNativeFeeTokens: [prefundedAssetId] },
			});

			await expect(
				bridge.validateWithdrawal({
					assetId: prefundedAssetId,
					amount: 1_000_000n,
					destinationAddress: EVM_TEST_ADDRESS,
					feeEstimation: {
						// Prefunded: estimation returns a zero amount but a non-zero relayer fee.
						amount: 0n,
						quote: null,
						underlyingFees: {
							[RouteEnum.OmniBridge]: {
								relayerFee: 50_000_000_000n,
								storageDepositFee: 0n,
							},
						},
					},
					routeConfig: createOmniBridgeRoute(Chains.Ethereum),
				}),
			).resolves.toBeUndefined();
		});
```

**File:** packages/intents-sdk/src/shared-types.ts (L343-348)
```typescript
export interface BridgeConfigs {
	[RouteEnum.OmniBridge]?: {
		/** Asset IDs of subsidized tokens whose withdrawal relayer fee is prefunded. */
		prefundedNativeFeeTokens?: string[];
	};
}
```
