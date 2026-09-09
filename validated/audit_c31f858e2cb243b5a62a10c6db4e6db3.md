### Title
Omni Bridge `prefundedNativeFeeTokens` reports `feeEstimation.amount = 0` while a nonzero relayer fee is silently debited from the user's `wrap.near` balance via a `storage_deposit` intent - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
For assets listed in `bridgeConfigs[OmniBridge].prefundedNativeFeeTokens`, `estimateWithdrawalFee` returns `feeEstimation.amount = 0` even though the Omni fee API can return a nonzero `native_token_fee`. That nonzero fee is preserved as `underlyingFees.relayerFee` and later turned into a `storage_deposit` intent that debits `nativeFee` yoctoNEAR of the user's own `wrap.near` balance, with nothing in the returned `feeEstimation` reflecting this deduction.

### Finding Description
The broken equality is: `feeEstimation.amount` should equal the total value that leaves the user's balance beyond `amount`, across all assets. For prefunded tokens it does not.

In `estimateWithdrawalFee` (`packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts:580-632`), tokens in `FEE_SUBSIDIZED_TOKENS` have `fee.native_token_fee` explicitly zeroed: [1](#0-0) 
but tokens in `prefundedNativeFeeTokens` only skip the fee-quote conversion step; the underlying `relayerFee` (`fee.native_token_fee`) is left untouched and can be nonzero, while `amount` (returned as `feeEstimation.amount`) stays `0`: [2](#0-1) 

`validateWithdrawal` explicitly exempts prefunded tokens from the `feeEstimation.amount > 0` sanity check that otherwise guards non-subsidized tokens: [3](#0-2) 

Then `deriveOmniWithdrawIntentParams` reads `relayerFee` (not `feeEstimation.amount`) as `nativeFee`, and whenever `nativeFee > 0n` it computes a `storageDepositAccountId` and includes it in the output: [4](#0-3) [5](#0-4) 

`createWithdrawIntentsPrimitive` then unconditionally emits a `storage_deposit` intent for `nativeFee` whenever `storageDepositAccountId !== null`: [6](#0-5) 

Per the contract schema's own documentation, this `StorageDeposit` intent "subtract[s] from user's NEP-141 `wNEAR` balance" and "the wNEAR will not be refunded in any case": [7](#0-6) 

This intent is part of the same signed multi-intent payload that the withdrawing user signs, so the debit comes from the withdrawing user's own wrap.near balance, not from any separate reserve. Tests directly confirm this exact combination is produced: `relayerFee: 50_000_000_000n` while `result.amount` (i.e. `feeEstimation.amount`) is `0n`: [8](#0-7) 
and `validateWithdrawal` accepting a zero `feeEstimation.amount` alongside a nonzero `relayerFee` for a prefunded token: [9](#0-8) 

`IntentsSDK.processWithdrawal` → `estimateWithdrawalFee` (via `_estimateWithdrawalFee` in `packages/intents-sdk/src/sdk.ts:408-453`) surfaces this `fee` object as-is to the caller, and with `feeInclusive: true` computes `actualAmount = amount - fee.amount` (i.e. `amount - 0`), so the withdrawn-token amount is not reduced either — the wrap.near debit is entirely uncounted anywhere in the reported numbers: [10](#0-9) 

No existing guard catches this: `FeeExceedsAmountError` only compares `fee.amount` against the withdrawal `amount` of the *same* asset, not against a separate wrap.near debit; `validateWithdrawal`'s `feeEstimation.amount > 0` assertion is explicitly bypassed for `isPrefundedWithdrawal`.

### Impact Explanation
An integrator (or any caller of `estimateWithdrawalFee`/`processWithdrawal`) relying on `feeEstimation.amount` to know "how much value beyond `amount` will leave the balance" is misled: for a prefunded asset with a nonzero API-reported `native_token_fee`, the SDK reports zero fee but still signs and publishes an intent that irreversibly debits `nativeFee` yoctoNEAR of `wrap.near` from the withdrawing user's balance (the docstring states this wNEAR "will not be refunded in any case"). This is a fee overcharge relative to what was disclosed, matching the "fee overcharge" High-severity category. It is repeatable on every withdrawal of a prefunded asset for which the fee API still returns a nonzero `native_token_fee`.

### Likelihood Explanation
Preconditions: an integrator has configured `bridgeConfigs[RouteEnum.OmniBridge].prefundedNativeFeeTokens` to include an asset ID (a documented, integrator-controlled config), and the Omni fee API (`getFee`) returns a nonzero `native_token_fee` for that asset/route (which the code does not force to zero for prefunded tokens, unlike `FEE_SUBSIDIZED_TOKENS`). Any call to `estimateWithdrawalFee`/`processWithdrawal` for that asset then triggers the divergence deterministically — no special attacker action beyond normal SDK usage. There is no cost to trigger and it recurs on every such withdrawal, though it requires the integrator-side config to include a token whose relayer fee is not actually zero.

### Recommendation
For `prefundedNativeFeeTokens`, either (a) force `fee.native_token_fee = 0n` the same way `FEE_SUBSIDIZED_TOKENS` does so no `storage_deposit`/`nativeFee` debit is generated, or (b) if the fee genuinely needs to be paid from the user's wrap.near, include `relayerFee`/`nativeFee` in the returned `feeEstimation.amount` (denominated appropriately, e.g. as a separate wrap.near-denominated field surfaced to callers) so the reported fee matches the real value leaving the user's balance.

### Proof of Concept
Vitest plan (mirrors `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts` "prefundedNativeFeeTokens" describe block):
1. Mock `BridgeAPI.prototype.getFee` to resolve `{ native_token_fee: 50_000_000_000n, usd_fee: 0.5, insufficient_utxo: false }`.
2. Construct `OmniBridge` with `bridgeConfig: { prefundedNativeFeeTokens: [prefundedAssetId] }`.
3. Call `estimateWithdrawalFee` for `prefundedAssetId`; assert `result.amount === 0n` and `result.underlyingFees[RouteEnum.OmniBridge].relayerFee === 50_000_000_000n` — establishing the two sides of the equality diverge (`feeEstimation.amount = 0` vs. `relayerFee = 50_000_000_000n`).
4. Feed that `result` into `deriveOmniWithdrawIntentParams`/`createWithdrawIntentsPrimitive` (or `sdk.createWithdrawalIntents`) and assert the produced intents array contains a `storage_deposit` intent with `amount: "50000000000"` deducted from the withdrawing account, while `feeEstimation.amount` reported to the caller remains `0n`.
5. Assert the invariant `feeEstimation.amount == total value leaving the user's balance beyond amount` fails: `0n !== 50_000_000_000n` (the wrap.near actually debited via the `storage_deposit` intent).

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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L580-588)
```typescript
		// Omni API returns non-zero fee for subsidized tokens, so we enforce 0 fee for specific tokens.
		if (FEE_SUBSIDIZED_TOKENS.includes(args.withdrawalParams.assetId)) {
			fee.native_token_fee = 0n;
		}

		const underlyingFees: RouteFeeStructures[RouteEnum["OmniBridge"]] = {
			relayerFee: fee.native_token_fee,
			storageDepositFee: 0n,
		};
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L612-632)
```typescript
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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L66-79)
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L129-154)
```typescript
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
	};
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge-utils.ts (L55-63)
```typescript
	const intents: (IntentStorageDeposit | IntentFtWithdraw)[] = [];
	if (storageDepositAccountId !== null) {
		intents.push({
			deposit_for_account_id: storageDepositAccountId,
			amount: nativeFee.toString(),
			contract_id: OMNI_BRIDGE_CONTRACT,
			intent: "storage_deposit",
		});
	}
```

**File:** packages/contract-types/src/type-check-schemas.ts (L6430-6432)
```typescript
export const StorageDepositSchema: JSONSchemaType<Types.StorageDeposit> = {
	description:
		"Make [NEP-145](https://nomicon.io/Standards/StorageManagement#nep-145) `storage_deposit` for an `account_id` on `contract_id`. The `amount` will be subtracted from user's NEP-141 `wNEAR` balance. NOTE: the `wNEAR` will not be refunded in any case.\n\nWARNING: use this intent only if paying storage_deposit is not a prerequisite for other intents to succeed. If some intent (e.g. ft_withdraw) requires storage_deposit, then use storage_deposit field of corresponding intent instead of adding a separate `StorageDeposit` intent. This is due to the fact that intents that fire `Promise`s are not guaranteed to be executed sequentially, in the order of the provided intents in `DefuseIntents`.",
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L1562-1603)
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L1657-1703)
```typescript
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

**File:** packages/intents-sdk/src/sdk.ts (L420-444)
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

				return fee;
```
