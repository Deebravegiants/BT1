### Title
`signAndSendIntent` lets a caller override `verifying_contract`, binding the signature to an attacker-chosen contract instead of the SDK-configured one - (File: `packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts`)

### Summary
`IntentExecuter.signAndSendIntent` is supposed to always sign intents against the SDK's configured `verifying_contract` (`this.envConfig.contractID`), but the object-spread order lets any additional field supplied by the caller silently override that value before the payload is built and signed.

### Finding Description
`signAndSendIntent` destructures `salt`, `relayParams`, and `signedIntents` out of its arguments and treats everything else as `...intentParams`, typed as `Partial<Parameters<IntentPayloadFactory>[0]>`, i.e. `Partial<IntentPayload>` — which includes `verifying_contract` as a settable field [1](#0-0) . It then builds the payload as:
```
const verifyingContract = this.envConfig.contractID;
let intentPayload = defaultIntentPayloadFactory(salt, {
    verifying_contract: verifyingContract,
    ...intentParams,
});
``` [2](#0-1) 
Because `...intentParams` is spread *after* `verifying_contract: verifyingContract`, any `verifying_contract` present in `intentParams` overwrites the environment-derived value. `defaultIntentPayloadFactory` itself also spreads `...params` last over its computed defaults, reinforcing that caller-supplied fields win [3](#0-2) . The resulting `intentPayload.verifying_contract` is what actually gets signed by `this.intentSigner.signIntent(intentPayload)` [4](#0-3) , and it is embedded directly in the signed message for every standard (ERC-191, NEP-413, etc.) — e.g. `verifying_contract: intent.verifying_contract` in the ERC-191 signer [5](#0-4) , and `recipient: intent.verifying_contract` in NEP-413 [6](#0-5) .

The equality that should hold is: *the contract the user's signature is scoped to == the SDK's configured `intents.near` (or equivalent) contract*. That equality can be broken by any caller of `signAndSendIntent` supplying a `verifying_contract` field — the SDK does not strip or validate it against `this.envConfig.contractID`.

### Impact Explanation
This directly matches the High-severity bullet "a signature bound to the wrong contract, signer or nonce." If any code path (e.g., an integrator API that forwards user-controlled request bodies into `sdk.signAndSendIntent(...)`, or a generic "custom intent" feature) passes through extra fields without filtering, an attacker-controlled `verifying_contract` would cause the wallet to produce a valid signature scoped to a different contract than intended, which could be replayed against that other (possibly malicious or looser-validating) contract to authorize unintended actions with the user's key.

### Likelihood Explanation
This is a low-friction, purely internal-SDK API issue — no relayer/RPC/bridge trust assumption or admin cooperation is required. It fires whenever the object passed to `signAndSendIntent` contains a `verifying_contract` key, which TypeScript's structural typing does not prevent since the type is `Partial<IntentPayload>`. However, exploitability in practice depends on whether a specific SDK consumer forwards untrusted/user-controlled fields directly into this call; I could not find, within the in-scope directories, a concrete first-party call site that passes fully attacker-controlled objects into `signAndSendIntent` (the internal call in `sdk.ts`/withdrawal flows constructs fixed field sets). This makes the likelihood moderate rather than confirmed-exploitable end-to-end from this repo alone.

### Recommendation
In `IntentExecuter.signAndSendIntent`, explicitly strip/ignore any `verifying_contract` supplied via `intentParams` (or place the fixed value after the spread instead of before), so the environment-configured contract can never be overridden by caller input:
```ts
const { verifying_contract: _ignored, ...safeIntentParams } = intentParams;
let intentPayload = defaultIntentPayloadFactory(salt, {
    ...safeIntentParams,
    verifying_contract: verifyingContract,
});
```
Apply the same ordering fix in `defaultIntentPayloadFactory` for defense in depth.

### Proof of Concept
```ts
const exec = new IntentExecuter({ envConfig: configsByEnvironment.production, intentRelayer, intentSigner });

// Caller (or any code path forwarding extra fields) passes an extra field:
await exec.signAndSendIntent({
  salt: mySalt,
  intents: [...],
  verifying_contract: "malicious.near", // not part of the documented API surface but accepted due to spread
});

// Result: intentPayload.verifying_contract === "malicious.near" instead of envConfig.contractID,
// and the wallet signature (ERC-191/NEP-413) is scoped to "malicious.near".
```

### Citations

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L58-67)
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
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L70-75)
```typescript
		const verifyingContract = this.envConfig.contractID;

		let intentPayload = defaultIntentPayloadFactory(salt, {
			verifying_contract: verifyingContract,
			...intentParams,
		});
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L85-85)
```typescript
		const multiPayload = await this.intentSigner.signIntent(intentPayload);
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

**File:** packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-viem.ts (L43-59)
```typescript
	async signIntent(intent: IntentPayload): Promise<MultiPayloadErc191> {
		return this.signRaw({
			payload: JSON.stringify({
				signer_id:
					intent.signer_id ??
					this.config.accountId ??
					utils.authHandleToIntentsUserId({
						identifier: this.config.signer.address,
						method: "evm",
					}),
				verifying_contract: intent.verifying_contract,
				deadline: intent.deadline,
				nonce: intent.nonce,
				intents: intent.intents,
			}),
		});
	}
```

**File:** packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts (L64-77)
```typescript
	/** Builds payload from IntentPayload and signs it via signRaw() */
	async signIntent(intent: IntentPayload): Promise<MultiPayloadNep413> {
		return this.signRaw({
			payload: {
				message: JSON.stringify({
					deadline: intent.deadline,
					intents: intent.intents,
					signer_id: intent.signer_id ?? this.accountId,
				}),
				nonce: intent.nonce,
				recipient: intent.verifying_contract,
			},
		});
	}
```
