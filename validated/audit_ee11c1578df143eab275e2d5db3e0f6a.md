### Title
Route confusion for PoA-bridge tokens via `createVirtualChainRoute` lets caller redirect `ft_withdraw` to an arbitrary NEAR account — (File: `packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts`)

### Summary
`AuroraEngineBridge.supports()`/`validateWithdrawal()` accept **any** NEP-141 `assetId` — including PoA-bridge-only assets like `nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near` (TRC-20 USDT) — as long as `routeConfig.route === RouteEnum.VirtualChain`, with no check that the token is actually bound to the given `auroraEngineContractId`. Because `AuroraEngineBridge` is ordered before `PoaBridge` in `IntentsSDK.bridges`, supplying `createVirtualChainRoute(anyNearAccountId, proxyTokenContractId)` for a PoA token produces a signed `ft_withdraw` intent whose `receiver_id` is the caller-chosen `auroraEngineContractId`/`proxyTokenContractId` rather than the token's real custodian, with no bridge ever throwing.

### Finding Description
The claimed equality is: *the `receiver_id` of the produced `ft_withdraw` intent must equal the real bridge custodian for `assetId` on the chain named by the caller*. For `nep141:tron-...omft.near`, the correct custodian, per `PoaBridge`'s own `createWithdrawIntentPrimitive` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts:6-26`), is the token account itself (`receiver_id: tokenAccountId`), with the destination address carried in a `WITHDRAW_TO:<addr>` memo validated by Tron address rules and cross-checked against the PoA bridge API's known token list (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:170-219`).

Instead, in `IntentsSDK.createWithdrawalIntents` (`packages/intents-sdk/src/sdk.ts:334-372`) the SDK iterates `this.bridges` in the fixed order set in the constructor (`packages/intents-sdk/src/sdk.ts:158-197`), where `AuroraEngineBridge` (index 1) precedes `PoaBridge` (index 2). `AuroraEngineBridge.supports()` (`packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts:60-77`) only checks:
- `routeConfig.route === RouteEnum.VirtualChain`
- `parseDefuseAssetId(assetId).standard === "nep141"`

It does **not** verify that the token actually originates from, or is registered for, any Aurora Engine chain, nor that `auroraEngineContractId` is a legitimate/known contract for that asset. `validateWithdrawal()` (lines 128-142) only checks the destination address is EVM-formatted; it never inspects `auroraEngineContractId` or cross-references it against `assetId`.

The intent is then built by `createWithdrawIntentPrimitive` (`packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge-utils.ts:11-51`), which sets:
```
receiver_id: params.auroraEngineContractId   // (or proxyTokenContractId)
msg: makeAuroraEngineDepositMsg(destinationAddress)  // stripped EVM address
```
Both `auroraEngineContractId` and `proxyTokenContractId` come straight from the caller-supplied `routeConfig` (`createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`, `packages/intents-sdk/src/lib/route-config-factory.ts:32-41`) with no validation against a registry.

Since `AuroraEngineBridge.supports()` returns `true` for the TRC-20 asset whenever `VirtualChain` route is passed, `PoaBridge` (which does have the correct token↔chain↔address checks) is never reached — the loop in `sdk.ts` returns on the first match. No bridge throws; a fully well-formed `ft_withdraw` `IntentPrimitive` is returned with `receiver_id` equal to an attacker-named NEAR account instead of the real PoA token custodian, and a `msg` payload built for an EVM/Aurora deposit that has no meaning for the Tron PoA bridge.

Because `IntentsSDK.createWithdrawalIntents` takes `feeEstimation` as an independent, caller-supplied argument (not internally re-derived from `routeConfig`), the caller can supply an arbitrary `feeEstimation` object matching `RouteEnum.VirtualChain` shape without ever calling `estimateWithdrawalFee`, fully decoupling fee legitimacy from the withdrawal path chosen.

### Impact Explanation
The returned `IntentPrimitive[]` — once signed by the victim integrator/user and submitted — executes `ft_withdraw` on the real Tron-USDT token contract (`tron-...omft.near`) with `receiver_id` set to an arbitrary NEAR account chosen by whoever supplied `routeConfig`. The tokens are transferred on-chain (NEAR) to that account instead of being withdrawn to Tron; there is no bridging to Tron at all and no recovery path, since the token contract has no knowledge of "Aurora Engine" semantics for this asset. This matches the Critical impact category: "funds delivered to a wrong address/chain/contract with no recovery." It is repeatable for every PoA-bridge NEP-141 asset (any `.omft.near` token, not limited to Tron) whenever `routeConfig` is influenced by an untrusted counterparty and forwarded by an integrator without an allow-list check on `auroraEngineContractId`.

### Likelihood Explanation
Preconditions: an integrator must forward attacker/counterparty-supplied `routeConfig` (specifically `auroraEngineContractId`/`proxyTokenContractId`) into `IntentsSDK.createWithdrawalIntents` alongside a PoA-only `assetId`, then sign and submit the resulting intents without independently validating `receiver_id`. This is explicitly listed as an in-scope attacker capability in the rules ("a counterparty whose strings an integrator forwards into the SDK ... routeConfig"). No special privileges, RPC compromise, or malicious relayer are required — the malformed route is produced purely from library logic operating on attacker-controlled function arguments, and requires no on-chain state manipulation.

### Recommendation
In `AuroraEngineBridge.supports()`/`validateWithdrawal()`, verify that `assetId` actually corresponds to a token issued for/known to the specified `auroraEngineContractId` (e.g., via an on-chain registry lookup or an explicit allow-list, similar to how `PoaBridge.parseAssetId` restricts to `poaTokenFactoryContractID`-suffixed contracts and known chain prefixes). Reject NEP-141 assets whose canonical bridge is PoA/Omni when `VirtualChain` route is requested unless `auroraEngineContractId` is verified to be the token's registered Aurora Engine. Additionally, consider re-validating that `feeEstimation.underlyingFees` was produced by the same bridge/route actually selected, to prevent decoupled/forged fee estimations.

### Proof of Concept
```ts
// vitest, mocks only HTTP/RPC where unavoidable
import { IntentsSDK, RouteEnum, createVirtualChainRoute } from "...";

const sdk = new IntentsSDK({ referral: "", intentSigner });

const intents = await sdk.createWithdrawalIntents({
  withdrawalParams: {
    assetId: "nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near", // PoA TRC-20 USDT
    amount: 1000000n,
    destinationAddress: "0x0000000000000000000000000000000000000001", // EVM-shaped, irrelevant to Tron
    feeInclusive: false,
    routeConfig: createVirtualChainRoute("attacker-controlled.near", null),
  },
  feeEstimation: {
    amount: 0n,
    quote: null,
    underlyingFees: { [RouteEnum.VirtualChain]: { storageDepositFee: 0n } },
  },
});

// Assert broken equality:
// Expected (real PoA custodian): receiver_id === "tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near"
// Actual: receiver_id === "attacker-controlled.near"
expect(intents.at(-1)).toMatchObject({
  intent: "ft_withdraw",
  token: "tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near",
  receiver_id: "attacker-controlled.near", // NOT the token's real bridge custodian
});
```
This demonstrates that `bridge.route` resolves to `RouteEnum.VirtualChain` (via `AuroraEngineBridge`) instead of `RouteEnum.PoaBridge`, and no error is thrown, for a token whose only legitimate bridge is PoA. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L154-197)
```typescript
		/**
		 * Order of bridges matters, because the first bridge that supports the `withdrawalParams` will be used.
		 * More specific bridges should be placed before more generic ones.
		 */
		this.bridges = [
			new IntentsBridge(),
			new AuroraEngineBridge({
				envConfig: this.envConfig,
				nearProvider,
				solverRelayApiKey: this.solverRelayApiKey,
			}),
			new PoaBridge({
				envConfig: this.envConfig,
				xrplRpcUrls,
			}),
			new HotBridge({
				envConfig: this.envConfig,
				solverRelayApiKey: this.solverRelayApiKey,
				hotSdk: new hotLabsOmniSdk_HotBridge({
					apiKey: this.hotBridgeApiKey,
					logger: console,
					evmRpc: evmRpcUrls,
					// 1. HotBridge from omni-sdk does not support FailoverProvider.
					// 2. omni-sdk has near-api-js@5.0.1, and it uses `instanceof` which doesn't work when multiple versions of packages are installed
					nearRpc: nearRpcUrls,
					stellarRpc: stellarRpcUrls.soroban,
					stellarHorizonRpc: stellarRpcUrls.horizon,
					async executeNearTransaction() {
						throw new Error("not implemented");
					},
				}),
			}),
			new OmniBridge({
				envConfig: this.envConfig,
				nearProvider,
				solverRelayApiKey: this.solverRelayApiKey,
				bridgeConfig: args.bridgeConfigs?.[RouteEnum.OmniBridge],
			}),
			new DirectBridge({
				envConfig: this.envConfig,
				nearProvider,
				solverRelayApiKey: this.solverRelayApiKey,
			}),
		];
```

**File:** packages/intents-sdk/src/sdk.ts (L334-372)
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
		}

		throw new Error(
			`Cannot determine bridge for withdrawal = ${stringify(
				args.withdrawalParams,
			)}`,
		);
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L60-123)
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

	parseAssetId(): null {
		return null;
	}

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

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L128-142)
```typescript
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L6-26)
```typescript
export function createWithdrawIntentPrimitive(params: {
	assetId: string;
	destinationAddress: string;
	destinationMemo: string | undefined;
	amount: bigint;
}): Extract<IntentPrimitive, { intent: "ft_withdraw" }> {
	const { contractId: tokenAccountId } = utils.parseDefuseAssetId(
		params.assetId,
	);
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: tokenAccountId,
		amount: params.amount.toString(),
		memo: createWithdrawMemo({
			receiverAddress: params.destinationAddress,
			xrpMemo: params.destinationMemo,
		}),
		min_gas: MIN_GAS_AMOUNT,
	};
}
```

**File:** packages/intents-sdk/src/lib/route-config-factory.ts (L32-41)
```typescript
export function createVirtualChainRoute(
	auroraEngineContractId: string,
	proxyTokenContractId: string | null,
): VirtualChainRouteConfig {
	return {
		route: RouteEnum.VirtualChain,
		auroraEngineContractId,
		proxyTokenContractId,
	};
}
```
