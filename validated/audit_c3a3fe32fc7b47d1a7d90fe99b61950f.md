### Title
Unvalidated `feeEstimation.quote` asset lets a mismatched quote sell an unrelated token in the `token_diff` intent - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.createWithdrawalIntents` builds the `token_diff` intent directly from `args.feeEstimation.quote.defuse_asset_identifier_in/out` without ever checking that this asset matches `args.withdrawalParams.assetId`. `OmniBridge.validateWithdrawal`, which `IntentsSDK.createWithdrawalIntents` calls beforehand, also never cross-checks the quote's asset identifiers against `args.assetId`, so a caller-supplied `feeEstimation` for a different asset/amount passes through unvalidated into the signed payload.

### Finding Description
The broken equality: the `token_diff` amounts and asset the SDK is about to ask the user to sign should equal the `token_diff` amounts and asset that were derived from `estimateWithdrawalFee` for the *same* `withdrawalParams.assetId`/`amount` that is being withdrawn. Instead, `createWithdrawalIntents` uses `args.feeEstimation.quote` verbatim: [1](#0-0) 

while the `ft_withdraw`/`mt_withdraw` leg is built from `args.withdrawalParams.assetId` via `deriveOmniWithdrawIntentParams`: [2](#0-1) 

`IntentsSDK.createWithdrawalIntents` is the only caller that invokes `bridge.validateWithdrawal` before `bridge.createWithdrawalIntents`, but `feeEstimation` is passed through unmodified — the same object the caller supplied: [3](#0-2) 

`OmniBridge.validateWithdrawal` only asserts `feeEstimation.amount > 0n` (or `relayerFee > 0n`), checks the destination address and decimals for `args.assetId`, and validates minimum-amount thresholds — it never inspects `feeEstimation.quote.defuse_asset_identifier_in/out` at all: [4](#0-3) [5](#0-4) 

Because there is no assertion tying `quote.defuse_asset_identifier_in` to `args.withdrawalParams.assetId`, a caller who obtained a `feeEstimation` from an earlier `estimateWithdrawalFee` call for asset A (e.g. `nep141:eth.bridge.near`) and passes it into `createWithdrawalIntents` with `withdrawalParams.assetId` = B (e.g. `nep141:sol.omft.near`) will get a `token_diff` intent that sells `amount_in` of asset A alongside an `ft_withdraw` of asset B — two unrelated legs stitched into one payload the SDK then hands to the caller to sign.

Existing guards do not catch this: `validateAddress`, `compareAddresses`, and `getUnderlyingFee` only operate on `RouteEnum.OmniBridge` underlying-fee fields (`relayerFee`, `storageDepositFee`, `utxoMaxGasFee`, `utxoProtocolFee`), never on `quote`. The `assert(assetInfo !== null, ...)` checks only validate that `withdrawalParams.assetId`/`assetId` is a supported Omni asset, not that it matches the quote. No test in `omni-bridge.test.ts` or `sdk.test.ts` exercises a mismatched-asset quote; all existing tests construct `feeEstimation.quote` with `defuse_asset_identifier_in` set to the same asset as `withdrawalParams.assetId`, which is why this gap is unnoticed by the current suite.

### Impact Explanation
The signed `MultiPayload` would contain a `token_diff` intent that debits `amount_in` of an asset the user never intended to sell (asset A) in exchange for `amount_out` of `wrap.near`/native, on top of a genuine withdrawal of a different asset (asset B). Since the solver network settles `token_diff` intents against the signed message, the signer's balance of asset A is drained for an amount unrelated to their actual withdrawal request. This is intent manipulation moving funds the user did not authorize — matching the Critical severity category. The attacker/integrator can repeat this for every withdrawal call by supplying a stale or foreign `feeEstimation`.

### Likelihood Explanation
Preconditions are low-cost and fully within an ordinary user's/integrator's control: call `estimateWithdrawalFee` once for asset A to obtain a `feeEstimation` object containing a `quote`, then call `createWithdrawalIntents` with `withdrawalParams.assetId` set to asset B while passing that same `feeEstimation`. Both methods are public SDK entry points documented for normal use (`IntentsSDK.createWithdrawalIntents`), and nothing in `validateWithdrawal` or `createWithdrawalIntents` rejects the mismatch. This is feasible with only two SDK calls and no privileged access, and is repeatable per-call.

### Recommendation
In `OmniBridge.createWithdrawalIntents` (and ideally in `validateWithdrawal`), assert that `args.feeEstimation.quote.defuse_asset_identifier_in === args.withdrawalParams.assetId` (accounting for the wrap.near/native special case) before emitting the `token_diff` intent, throwing a descriptive error if they don't match. The same check should be added to `HotBridge.createWithdrawalIntents`, which has the identical unguarded pattern.

### Proof of Concept
Vitest plan (mocks only HTTP, e.g. `BridgeAPI.prototype.getFee` / `solverRelay.getQuote`):
1. Call `sdk.estimateWithdrawalFee` for `withdrawalParams.assetId = "nep141:eth.bridge.near"`, capturing the resulting `feeEstimation` (with `quote.defuse_asset_identifier_in === "nep141:eth.bridge.near"`).
2. Call `sdk.createWithdrawalIntents` with `withdrawalParams.assetId = "nep141:sol.omft.near"` (a different, unrelated Omni asset) but pass the `feeEstimation` from step 1 unchanged.
3. Assert LHS = "the emitted `token_diff.diff` key equals `withdrawalParams.assetId`" vs RHS = "the emitted `token_diff.diff` key equals `feeEstimation.quote.defuse_asset_identifier_in` (`nep141:eth.bridge.near`)" — currently RHS is what happens, diverging from the safe LHS.
4. After the fix, assert `sdk.createWithdrawalIntents(...)` rejects/throws instead of resolving to an intents array containing a `token_diff` for `nep141:eth.bridge.near` alongside an `ft_withdraw` for `nep141:sol.omft.near`.

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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L316-327)
```typescript
		intents.push(
			...createWithdrawIntentsPrimitive(
				deriveOmniWithdrawIntentParams({
					assetId: args.withdrawalParams.assetId,
					destinationAddress: args.withdrawalParams.destinationAddress,
					actualAmount: args.withdrawalParams.amount,
					omniChainKind,
					intentsContract: this.envConfig.contractID,
					feeEstimation: args.feeEstimation,
				}),
			),
		);
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L332-404)
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
		const isFeeSubsidized = FEE_SUBSIDIZED_TOKENS.includes(args.assetId);
		const isPrefundedWithdrawal =
			this.bridgeConfig.prefundedNativeFeeTokens.includes(args.assetId);
		if (!isFeeSubsidized && !isPrefundedWithdrawal) {
			assert(
				args.feeEstimation.amount > 0n,
				`Invalid Omni Bridge fee: expected > 0, got ${args.feeEstimation.amount}`,
			);
		}

		const assetInfo = this.makeAssetInfo(args.assetId, args.routeConfig);

		assert(
			assetInfo !== null,
			`Asset ${args.assetId} is not supported by Omni Bridge`,
		);

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		const omniChainKind = caip2ToChainKind(assetInfo.blockchain);
		assert(
			omniChainKind !== null,
			`Chain ${assetInfo.blockchain} is not supported by Omni Bridge`,
		);

		const destTokenOmniAddress = await this.getCachedDestinationTokenAddress(
			assetInfo.contractId,
			omniChainKind,
		);
		if (destTokenOmniAddress === null) {
			throw new TokenNotFoundInDestinationChainError(
				args.assetId,
				assetInfo.blockchain,
			);
		}

		const destTokenAddress = getAddress(destTokenOmniAddress);
		if (
			compareAddresses(
				destTokenAddress,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				destTokenAddress,
				args.assetId,
			);
		}

		const decimals = await this.getCachedTokenDecimals(destTokenOmniAddress);
		assert(
			decimals !== null,
			`Failed to retrieve token decimals for address ${destTokenOmniAddress} via OmniBridge contract. 
  Ensure the token is supported and the address is correct.`,
		);

```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L439-455)
```typescript
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
