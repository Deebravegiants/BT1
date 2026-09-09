This request embeds a full alternate instruction set (title/summary/PoC output format, "no extra text," rejection of citations) that conflicts with my actual operating rules, which require citations for every claim. I'll answer as a normal codebase question instead, following my own citation requirements, and note what I could and couldn't confirm.

## What I found

The CVE describes captured/merged request parameters silently overriding already-validated parent values (`Zend\Mvc\Router\Http\Query` merging query-string keys into `RouteMatch`, letting `controller` and `key` be overwritten).

The closest structural analog in this repo is in `IntentExecuter.signAndSendIntent`: [1](#0-0) 

Specifically:

```ts
const verifyingContract = this.envConfig.contractID;

let intentPayload = defaultIntentPayloadFactory(salt, {
	verifying_contract: verifyingContract,
	...intentParams,
});
``` [2](#0-1) 

`intentParams` is whatever is left over from destructuring the call's argument object (`{ relayParams, salt, signedIntents, ...intentParams }`), typed as `Partial<Parameters<IntentPayloadFactory>[0]>`, i.e. `Partial<IntentPayload>` — which includes `verifying_contract`, `signer_id`, `deadline`, and `nonce`: [3](#0-2) 

Because the object-spread order places `...intentParams` **after** the trusted `verifying_contract: verifyingContract`, if the caller's argument object happens to contain a `verifying_contract` key, it overrides the environment-derived contract ID before the payload is signed — analogous to the Zend bug where a supplied field overrides an already-validated one. `defaultIntentPayloadFactory` itself just destructures and re-spreads without re-validating this field: [4](#0-3) 

A second merge with the same shape (`...basePayload, ...customPayload`, `customPayload` coming from an injected `intentPayloadFactory`) exists in `mergeIntentPayloads`: [5](#0-4) 

## What I could not confirm

I ran out of tool-call budget before verifying whether the **public** `IntentsSDK.signAndSendIntent` entry point in `packages/intents-sdk/src/sdk.ts` actually forwards an unfiltered object into `IntentExecuter.signAndSendIntent`, or whether it constructs a narrow object literal (only `intents`, `relayParams`, `signedIntents`, `salt`, etc.) before calling it. The public-facing `SignAndSendArgs` type in `shared-types.ts` does **not** expose `verifying_contract` or `signer_id`: [6](#0-5) 

so at the TypeScript level this looks type-safe for normal SDK consumers. Whether an untrusted/attacker-controlled value could actually reach `intentParams.verifying_contract` through the real public call path (versus only via direct, type-unsafe use of `IntentExecuter`, which is an internal class) is something I was unable to trace to a concrete call site before running out of iterations — this would need a look at the actual `sdk.ts signAndSendIntent` method body and its callers (`signAndSendWithdrawalIntent`, `processWithdrawal`, etc.) to determine whether any user/integrator-supplied `withdrawalParams` or `intent.payload` factory return value could inject a `verifying_contract` or `signer_id` field into that merge.

If you want a definitive answer on reachability (and thus whether this rises to a real "signature bound to the wrong contract" issue), that requires reading the full body of `packages/intents-sdk/src/sdk.ts` around its `signAndSendIntent`/`processWithdrawal` methods, which I did not get to view in full.

### Citations

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L58-83)
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
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L164-181)
```typescript
async function mergeIntentPayloads(
	defaultPayload: IntentPayload,
	intentPayloadFactory: IntentPayloadFactory,
	salt: Salt,
): Promise<IntentPayload> {
	const customPayload = await intentPayloadFactory(defaultPayload);
	const customPayloadIntents = customPayload.intents ?? [];

	const { nonce: _nonce, ...basePayload } = defaultPayload;

	return defaultIntentPayloadFactory(salt, {
		...basePayload,
		...customPayload,
		intents: Array.from(
			new Set([...customPayloadIntents, ...basePayload.intents]),
		),
	});
}
```

**File:** packages/intents-sdk/src/intents/shared-types.ts (L5-15)
```typescript
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

**File:** packages/intents-sdk/src/intents/intent-payload-factory.ts (L10-38)
```typescript
export function defaultIntentPayloadFactory(
	salt: Salt,
	{
		intents,
		verifying_contract,
		...params
	}: Partial<IntentPayload> & Pick<IntentPayload, "verifying_contract">,
): IntentPayload {
	// remove `undefined` properties
	params = Object.fromEntries(
		Object.entries(params).filter(([, value]) => value !== undefined),
	);

	const deadline =
		params.deadline != null
			? new Date(params.deadline)
			: new Date(Date.now() + DEFAULT_DEADLINE_MS);
	const nonceDeadline = new Date(
		deadline.getTime() + DEFAULT_NONCE_DEADLINE_OFFSET_MS,
	);

	return {
		verifying_contract,
		deadline: deadline.toISOString(),
		nonce: VersionedNonceBuilder.encodeNonce(salt, nonceDeadline),
		intents: intents == null ? [] : intents,
		signer_id: undefined, // or you can specify intent user id
		...params,
	};
```

**File:** packages/intents-sdk/src/shared-types.ts (L77-100)
```typescript
export interface SignAndSendArgs {
	intents: IntentPrimitive[];
	/**
	 * Factory function to modify the intent payload draft before signing.
	 * Use this to add or modify intent primitives in the payload.
	 *
	 * @example
	 * ```typescript
	 * payload: (draft) => ({
	 *   intents: [...draft.intents, { intent: "transfer", ... }]
	 * })
	 * ```
	 */
	payload?: IntentPayloadFactory;
	relayParams?: IntentRelayParamsFactory;
	signer?: IIntentSigner;
	onBeforePublishIntent?: OnBeforePublishIntentHook;
	/**
	 * Pre-signed intents for atomic execution.
	 * The newly created intent will be published together with these pre-signed intents.
	 */
	signedIntents?: SignedIntentsComposition;
	logger?: ILogger;
}
```
