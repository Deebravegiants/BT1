### Title
Aurora Engine withdrawal intent trusts caller-supplied `auroraEngineContractId`/`proxyTokenContractId` with no cross-check against a canonical registry, allowing token misdelivery - (File: `packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts`)

### Summary
`AuroraEngineBridge` builds the `ft_withdraw` intent's `receiver_id` directly from `routeConfig.auroraEngineContractId` / `routeConfig.proxyTokenContractId`, which are caller-supplied fields, without ever validating that they correspond to the legitimate/whitelisted Aurora-Engine contract that actually custodies the asset being withdrawn. This is the same equality-break pattern as the Karak `NativeVault` finding: an address that determines where funds are ultimately routed/custodied is accepted from an untrusted input path instead of being verified against the canonical mapping the protocol maintains for that asset.

### Finding Description
In `createWithdrawalIntents` [1](#0-0) , the receiver of the underlying NEAR `ft_withdraw` intent is taken verbatim from `args.withdrawalParams.routeConfig.auroraEngineContractId` and `args.withdrawalParams.routeConfig.proxyTokenContractId`: [2](#0-1) 

`createWithdrawIntentPrimitive` sets `receiver_id: params.auroraEngineContractId` (or `params.proxyTokenContractId` for non-standard decimals) directly — these become the on-chain destination that will hold/receive the NEP-141 tokens on NEAR before bridging to the virtual chain.

`validateWithdrawal` for this bridge only checks that `destinationAddress` is a well-formed EVM address; it performs **no validation whatsoever** of `auroraEngineContractId` or `proxyTokenContractId` against any canonical/whitelisted set of Aurora Engine deployments for the asset/chain being withdrawn: [3](#0-2) 

Contrast this with the other bridges in the same package, which cross-check the destination/token address against a canonical source before constructing intents — e.g. `OmniBridge.validateWithdrawal` resolves `destTokenOmniAddress` from the bridge's own indexer and asserts consistency [4](#0-3) , and `HotBridge.validateWithdrawal` compares against a resolved token/asset registry [5](#0-4) . `AuroraEngineBridge` has no equivalent check — the equality "receiver_id used == receiver_id verified as the legitimate custodian for this asset" is never enforced.

### Impact Explanation
Because `receiver_id` on a NEP-141 `ft_transfer_call`/`ft_withdraw` is not itself signature-bound to a canonical contract registry inside this SDK, if `routeConfig.auroraEngineContractId`/`proxyTokenContractId` is wrong or attacker-influenced (e.g., supplied by a compromised or malicious upstream integrator/relayer constructing `WithdrawalParams` on behalf of a user, while the user only reviews `assetId`/`amount`/`destinationAddress`), funds are transferred to an arbitrary NEAR account instead of the real Aurora Engine bridge contract. NEP-141 transfers to a contract that doesn't implement the expected deposit logic typically do not revert and the tokens become stuck with no automatic recovery — matching "funds delivered to a wrong address/chain/contract with no recovery."

### Likelihood Explanation
This requires the party constructing `WithdrawalParams.routeConfig` (not necessarily the end signer of the intent) to supply an incorrect/malicious `auroraEngineContractId` or `proxyTokenContractId`. This is plausible in any integration where the route configuration is derived from a mutable/external source rather than hardcoded and verified by the SDK itself, which is exactly the class of trust-boundary bug the Karak analog describes (operator-supplied `extraData` never cross-checked against the canonical mapping).

### Recommendation
In `AuroraEngineBridge.validateWithdrawal` (or in `createWithdrawalIntents`), validate `routeConfig.auroraEngineContractId` and `routeConfig.proxyTokenContractId` against a canonical, SDK-maintained registry/allowlist keyed by `assetId`/virtual chain, analogous to how `OmniBridge`/`HotBridge` resolve and assert the destination token address from their own indexers before building the withdrawal intent.

### Proof of Concept
Not applicable — this is a design/validation gap identified via static code reading; no exploit was executed. The relevant reachable path is:
1. Caller builds `WithdrawalParams` with `routeConfig: { route: RouteEnum.VirtualChain, auroraEngineContractId: "<attacker-account.near>", proxyTokenContractId: null }`.
2. `sdk.createWithdrawalIntents` → `AuroraEngineBridge.supports` returns true (only checks `nep141` standard) [6](#0-5) .
3. `AuroraEngineBridge.validateWithdrawal` passes (only checks EVM destination format).
4. `createWithdrawIntentPrimitive` sets `receiver_id` to the attacker-controlled account, and the resulting signed intent transfers tokens there.

### Citations

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L60-77)
```typescript
	async supports(
		params: Pick<WithdrawalParams, "assetId" | "routeConfig">,
	): Promise<boolean> {
		if (params.routeConfig == null || !this.is(params.routeConfig)) {
			return false;
		}

		const assetInfo = parseDefuseAssetId(params.assetId);
		const isValid = assetInfo.standard === "nep141";

		if (!isValid) {
			throw new UnsupportedAssetIdError(
				params.assetId,
				"`assetId` does not match `routeConfig`.",
			);
		}
		return isValid;
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L83-123)
```typescript
	createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
	}): Promise<IntentPrimitive[]> {
		withdrawalParamsInvariant(args.withdrawalParams);

		const intents: IntentPrimitive[] = [];

		if (args.feeEstimation.quote != null) {
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

		const intent = createWithdrawIntentPrimitive({
			assetId: args.withdrawalParams.assetId,
			auroraEngineContractId:
				args.withdrawalParams.routeConfig.auroraEngineContractId,
			proxyTokenContractId:
				args.withdrawalParams.routeConfig.proxyTokenContractId,
			destinationAddress: args.withdrawalParams.destinationAddress,
			amount: args.withdrawalParams.amount,
			storageDeposit: getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.VirtualChain,
				"storageDepositFee",
			),
		});

		intents.push(intent);

		return Promise.resolve(intents);
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L125-142)
```typescript
	/**
	 * Aurora Engine bridge doesn't have withdrawal restrictions.
	 */
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		if (validateAddress(args.destinationAddress, Chains.Ethereum) === false) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				"virtual-chain",
			);
		}

		return;
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge-utils.ts (L11-51)
```typescript
export function createWithdrawIntentPrimitive(params: {
	assetId: string;
	auroraEngineContractId: string;
	proxyTokenContractId: string | null;
	destinationAddress: string;
	amount: bigint;
	storageDeposit: bigint;
}): IntentFtWithdraw {
	const { contractId: tokenAccountId, standard } = utils.parseDefuseAssetId(
		params.assetId,
	);
	assert(standard === "nep141", "Only NEP-141 is supported");

	// Most cases
	if (params.proxyTokenContractId == null) {
		return {
			intent: "ft_withdraw",
			token: tokenAccountId,
			receiver_id: params.auroraEngineContractId,
			amount: params.amount.toString(),
			msg: makeAuroraEngineDepositMsg(params.destinationAddress),
			storage_deposit:
				params.storageDeposit > 0n
					? params.storageDeposit.toString()
					: undefined,
			min_gas: MIN_GAS_AMOUNT,
		};
	}

	//  Flow for transferring a base token to a virtual chain with a non-standard (non-ETH) base token
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: params.proxyTokenContractId,
		amount: params.amount.toString(),
		msg: `${params.auroraEngineContractId}:${makeAuroraEngineDepositMsg(params.destinationAddress)}`,
		storage_deposit:
			params.storageDeposit > 0n ? params.storageDeposit.toString() : undefined,
		min_gas: MIN_GAS_AMOUNT_NON_STANDARD_DECIMALS,
	};
}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L373-396)
```typescript
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
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L259-284)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");
		hotBlockchainInvariant(assetInfo.blockchain);

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}
		const nativeAsset = "native" in assetInfo;
		const token = nativeAsset ? "native" : assetInfo.address;
		if (
			!nativeAsset &&
			compareAddresses(token, args.destinationAddress, assetInfo.blockchain)
		) {
			throw new DestinationAddressMatchesTokenAddressError(token, args.assetId);
		}
```
