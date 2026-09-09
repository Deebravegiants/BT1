### Title
`signAndSendIntent` lets caller-supplied `verifying_contract` silently override the trusted contract ID - (File: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts)

### Summary
`IntentExecuter.signAndSendIntent` is designed to bind every signed intent to the SDK's configured contract (`this.envConfig.contractID`). However, the object spread order used to build the payload lets any field present in the caller-supplied `intentParams` — including `verifying_contract` — clobber that trusted value before the payload is signed.

### Finding Description
`signAndSendIntent` destructures its arguments as `{ relayParams, salt, signedIntents, ...intentParams }`, where `intentParams` has type `Partial<Parameters<IntentPayloadFactory>[0]>`, i.e. `Partial<IntentPayload>`. `IntentPayload` includes the `verifying_contract` field. The method then builds the payload as: [1](#0-0) 

```
const verifyingContract = this.envConfig.contractID;

let intentPayload = defaultIntentPayloadFactory(salt, {
    verifying_contract: verifyingContract,
    ...intentParams,
});
```

Because `...intentParams` is spread *after* `verifying_contract: verifyingContract`, any `verifying_contract` key present in `intentParams` overwrites the value derived from `this.envConfig.contractID`. The intended invariant — "the signed payload's `verifying_contract` equals the SDK's configured/validated contract ID" — is broken: the field that ends up inside the object that gets cryptographically signed by `this.intentSigner.signIntent(intentPayload)` can instead be whatever value was passed into the call, not the one the code explicitly computed and intended to enforce.

The same unguarded-override pattern is repeated in the optional custom-factory merge step, where `customPayload` (spread after `basePayload`) can again override `verifying_contract`: [2](#0-1) 

The nonce is explicitly stripped out (`const { nonce: _nonce, ...basePayload } = defaultPayload;`) to protect it from being clobbered, but no equivalent protection exists for `verifying_contract`, showing the omission is likely unintentional given the explicit `const verifyingContract = this.envConfig.contractID;` line whose purpose is defeated by the later spread.

### Impact Explanation
`verifying_contract` is a security-critical field of the signed intent payload: it determines which on-chain contract the user's signature is valid against. If any code path allows this field to be supplied/overridden away from `this.envConfig.contractID`, the resulting signature can be bound to a different contract than the one that was validated and intended, matching the "High" impact category of a signature bound to the wrong contract.

### Likelihood Explanation
Exploitability depends on whether the concrete caller-facing surface (e.g. `sdk.ts`) forwards an unfiltered `verifying_contract` field from up-stream, less-trusted input into `intentParams`. Within `intent-executer.ts` itself there is no filtering/whitelisting of `intentParams` before it's spread, so any code path that forwards a broader options object into `signAndSendIntent` — including one influenced by external quote/intent data — would allow this override. I was not able to fully trace every call site in the remaining time to confirm whether an unprivileged, non-integrator actor can control this field end-to-end; this should be verified against `sdk.ts` and its callers.

### Recommendation
Compute `verifying_contract` last, after spreading `intentParams`/`customPayload`, so it cannot be overridden:
```ts
let intentPayload = defaultIntentPayloadFactory(salt, {
    ...intentParams,
    verifying_contract: verifyingContract,
});
```
and, in `mergeIntentPayloads`, explicitly strip `verifying_contract` from `customPayload` the same way `nonce` is stripped, re-asserting `verifying_contract: defaultPayload.verifying_contract` in the final merged object.

### Proof of Concept
```ts
// Attacker/integrator calls the public API with an extra field that
// Partial<IntentPayload> happily accepts:
await intentExecuter.signAndSendIntent({
  salt,
  verifying_contract: "attacker-contract.near", // not filtered out
  // ...other normal intent params
});
// Inside signAndSendIntent:
//   verifying_contract: verifyingContract,   // = this.envConfig.contractID
//   ...intentParams,                         // overrides it with "attacker-contract.near"
// => intentSigner.signIntent() signs a payload bound to "attacker-contract.near"
//    instead of the SDK's configured, validated contract.
```

### Citations

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L70-75)
```typescript
		const verifyingContract = this.envConfig.contractID;

		let intentPayload = defaultIntentPayloadFactory(salt, {
			verifying_contract: verifyingContract,
			...intentParams,
		});
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
