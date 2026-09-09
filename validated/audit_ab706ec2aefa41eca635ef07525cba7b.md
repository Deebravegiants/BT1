This confirms the analysis. `createWithdrawIntentPrimitive` only builds an `IntentFtWithdraw` primitive (`intent`, `token`, `receiver_id`, `amount`, `msg`, `storage_deposit`, `min_gas`) — it has no `verifying_contract` field at all, since `verifying_contract` is not part of an individual intent primitive; it's a property of the outer signed payload.

## Verdict

**No vulnerability found for this question.**

### Why the claimed invariant break does not hold

The equality to verify is `MultiPayload.payload.verifying_contract == envConfig.contractID`.

Tracing the only reachable path for a single `processWithdrawal` call through `AuroraEngineBridge`:

1. `IntentsSDK.processWithdrawal` → `estimateWithdrawalFee`/`_estimateWithdrawalFee` → `AuroraEngineBridge.estimateWithdrawalFee`/`validateWithdrawal` — none of these touch `verifying_contract`; they only compute `fee`, validate `destinationAddress` via `validateAddress`, and enforce NEP-141 asset standard via `withdrawalParamsInvariant`. [1](#0-0) 
2. `createWithdrawalIntents` (both the SDK-level dispatcher and the bridge's own method) produce only `IntentPrimitive[]` (a `token_diff` and an `ft_withdraw`), with no `verifying_contract` field — that field does not exist on the individual intent primitive at all. [2](#0-1) 
3. The `verifying_contract` value is only ever set once, centrally, in `IntentExecuter.signAndSendIntent`, unconditionally derived from `this.envConfig.contractID` and passed into `defaultIntentPayloadFactory`. The public entrypoints that reach this code (`signAndSendWithdrawalIntent` → `signAndSendIntent`) only forward `intents`, never a caller-supplied `verifying_contract`. [3](#0-2) 
4. None of the attacker-controlled inputs listed in the question (`asset`, `address`, `routeConfig`, `fee object`, `batch order`) can inject a `verifying_contract` value — that field simply isn't part of `WithdrawalParams`, `FeeEstimation`, or `IntentPrimitive`. [4](#0-3) 
5. `AuroraEngineBridge.describeWithdrawal` always returns `{ status: "completed", txHash: null }`, which is a documented bridge design characteristic (no on-chain tx hash to report for this virtual-chain route), not evidence of a bypassed contract-identity check. [5](#0-4) 

The only two places where `verifying_contract` could diverge from `envConfig.contractID` are:
- `args.intent.payload` (a custom `IntentPayloadFactory` merged via `mergeIntentPayloads`), and
- `args.intent.signedIntents` (pre-signed `MultiPayload`s composed via `composeMultiPayloads`),

both of which are explicitly documented, opt-in escape hatches for integrators — not something a permissionless counterparty/solver can inject through `assetId`, `destinationAddress`, `routeConfig`, fee, or batch ordering. Per the rules, exploits requiring "the integrator to deliberately misuse a documented escape hatch" are out of scope. [6](#0-5) 

Since no attacker-controlled input on the stated entrypoint (`processWithdrawal` for the `AuroraEngineBridge` single-withdrawal path) can set or influence `verifying_contract`, the equality `verifying_contract == contractID` holds unconditionally for this path, both before and after the described exploit flow.

### Citations

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

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L220-222)
```typescript
	async describeWithdrawal(): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: null };
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

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L58-100)
```typescript
	async signAndSendIntent({
		relayParams: relayParamsFactory,
		salt,
		signedIntents,
		...intentParams
	}: {
		relayParams?: IntentRelayParamsFactory;
		salt: Salt;
		signedIntents?: SignedIntentsComposition;
	} & Partial<Parameters<IntentPayloadFactory>[0]>): Promise<{
		ticket: Ticket;
	}> {
		const verifyingContract = this.envConfig.contractID;

		let intentPayload = defaultIntentPayloadFactory(salt, {
			verifying_contract: verifyingContract,
			...intentParams,
		});

		if (this.intentPayloadFactory) {
			intentPayload = await mergeIntentPayloads(
				intentPayload,
				this.intentPayloadFactory,
				salt,
			);
		}

		const multiPayload = await this.intentSigner.signIntent(intentPayload);
		const relayParams = relayParamsFactory ? await relayParamsFactory() : {};

		// Call the hook before publishing if provided
		if (this.onBeforePublishIntent) {
			const intentHash = await computeIntentHash(multiPayload);
			await this.onBeforePublishIntent({
				intentHash,
				intentPayload,
				multiPayload,
				relayParams,
			});
		}

		// Compose with pre-signed intents if provided
		const composedPayloads = composeMultiPayloads(multiPayload, signedIntents);
```

**File:** packages/intents-sdk/src/intents/shared-types.ts (L1-16)
```typescript
import type { Intent, MultiPayload } from "@defuse-protocol/contract-types";

export type IntentPrimitive = Intent;

export interface IntentPayload {
	verifying_contract: string;
	deadline: string;
	nonce: string;
	intents: IntentPrimitive[];
	signer_id: string | undefined;
}

export type IntentPayloadFactory = (
	intentParams: IntentPayload,
) => Promise<Partial<IntentPayload>> | Partial<IntentPayload>;

```
