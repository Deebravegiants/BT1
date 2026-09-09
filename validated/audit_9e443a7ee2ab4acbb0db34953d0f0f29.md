### Title
Duplicate intent entries with equal content but different object identity are not deduplicated before signing - ([File: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts])

### Summary
`IntentExecuter.signAndSendIntent` merges intents produced by a caller-supplied `intentPayloadFactory` with the SDK's base intents and attempts to remove duplicates before signing and submitting the payload. The deduplication is implemented with a plain JavaScript `Set`, which only removes duplicates by reference identity, not by value. Any intent that is logically identical but constructed as a new object (the normal way factories build intents) is not deduplicated, so it can be included twice in the signed intent list and executed twice on-chain.

### Finding Description
`mergeIntentPayloads` combines the intents returned by a custom `intentPayloadFactory` with the SDK's default intents: [1](#0-0) 

The intended invariant is: *each logically distinct intent appears exactly once in the signed `intents` array*. `Array.from(new Set([...customPayloadIntents, ...basePayload.intents]))` breaks this invariant because `Set` compares object entries by reference (`===`), not by deep/structural equality. Two intent objects with identical fields (e.g. two `{ intent: "ft_withdraw", token, receiver_id, amount }` objects built independently) are treated as distinct elements and both survive into the final `intents` array that gets signed via `intentSigner.signIntent(intentPayload)` and published via `intentRelayer.publishIntent`/`publishIntents`.

The existing unit test only exercises the case where the factory spreads the *same array reference* (`...intentPayload.intents`) back into its result, which happens to work because the object references are literally identical: [2](#0-1) 

But this is not the general case: any `intentPayloadFactory` that constructs a fresh intent object with content equal to one already in `basePayload.intents` (which is the typical pattern for factories that add withdrawal/transfer intents based on payload contents) bypasses the dedup entirely. The resulting `intentPayload.intents` array can contain the same transfer/withdraw intent twice, and the entire array is signed as one `MultiPayload` and submitted to the `intents.near`-style verifying contract, which executes every intent in the array.

### Impact Explanation
If a duplicate value-equal intent (e.g., an `ft_withdraw`/transfer intent) ends up twice in the signed payload, the on-chain contract will execute it twice, debiting the user's balance twice for what should be a single authorized action. This is a fund-moving equality break — the amount actually debited is not "amount once" as intended by the caller, but "amount x2" — matching the Critical impact category (funds moved beyond what the user authorized).

### Likelihood Explanation
This requires an integrator-supplied `intentPayloadFactory` (a documented, supported extension point of the SDK, e.g. for hooks such as `onBeforePublishIntent` and batch/composed withdrawal flows) to produce an intent object that duplicates by value but not by reference one of the base intents. This is a very plausible real-world pattern since factories generally construct new intent objects (via helper builders, `JSON.parse`, mapping) rather than reusing the exact same object references — the passing test only avoids the bug by accident. No malicious actor is required; a normal caller-supplied factory can trigger it, and the SDK gives no observable error/warning when this happens.

### Recommendation
Replace the reference-based `Set` deduplication with structural/value-based deduplication (e.g., serialize each intent deterministically — sorted keys JSON, or a canonical hash — and dedupe on that serialized key) before constructing the final `intents` array in `mergeIntentPayloads`. Additionally, consider throwing/logging when a value-duplicate intent is detected instead of silently keeping duplicates, similar to how sorted-troves-style systems require an explicit duplicate check rather than relying on incidental identity checks.

### Proof of Concept
```ts
// intentPayloadFactory returns a NEW object with identical content to a base intent
const exec = new IntentExecuter({
  envConfig,
  intentRelayer,
  intentSigner,
  intentPayloadFactory(defaultPayload) {
    // Build a fresh object (different reference) with the same fields as an intent
    // that will also be included via basePayload.intents
    const dup = JSON.parse(JSON.stringify(defaultPayload.intents[0]));
    return { intents: [dup] };
  },
});

await exec.signAndSendIntent({
  intents: [{ intent: "ft_withdraw", token: "usdc.near", receiver_id: "user.near", amount: "1000000" }],
  salt,
});

// Result: intentPayload.intents contains TWO structurally-identical
// ft_withdraw entries (different object references), because
// `new Set([...])` cannot detect the duplication.
// Both entries get signed and submitted, causing the withdrawal
// to execute twice on-chain.
``` [3](#0-2)

### Citations

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

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.test.ts (L71-128)
```typescript
	it("removes duplicated intents", async () => {
		const { intentSigner } = setupMocks();

		vi.mocked(intentSigner.signIntent).mockImplementation(
			() => new Promise(() => {}),
		);

		const exec = new IntentExecuter({
			envConfig: configsByEnvironment.production,
			intentRelayer: new IntentRelayerPublic({
				envConfig: configsByEnvironment.production,
			}),
			intentSigner,
			intentPayloadFactory(intentPayload) {
				return {
					intents: [
						...intentPayload.intents,
						{
							intent: "add_public_key",
							public_key: "my_pk",
						},
					],
				};
			},
		});

		void exec.signAndSendIntent({
			intents: [
				{
					intent: "transfer",
					receiver_id: "foo.near",
					tokens: {},
				},
			],
			salt: Uint8Array.from([1, 2, 3, 4]),
		});

		await vi.waitFor(() =>
			expect(intentSigner.signIntent).toHaveBeenCalledOnce(),
		);
		expect(intentSigner.signIntent).toHaveBeenCalledWith({
			deadline: expect.any(String),
			intents: [
				{
					intent: "transfer",
					receiver_id: "foo.near",
					tokens: {},
				},
				{
					intent: "add_public_key",
					public_key: "my_pk",
				},
			],
			nonce: expect.any(String),
			signer_id: undefined,
			verifying_contract: "intents.near",
		});
	});
```
