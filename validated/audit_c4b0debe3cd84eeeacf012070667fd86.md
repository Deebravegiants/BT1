### Title
Unvalidated positional ticket extraction in composed intent publishing can misreport the wrong ticket for the caller's intent - (File: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts)

### Summary
`IntentExecuter.signAndSendIntent()` composes the caller's newly-signed `multiPayload` together with optional pre-signed `before`/`after` payloads, sends them atomically via `publishIntents()`, and then picks the ticket belonging to the caller's own intent purely by positional index (`tickets[beforeCount]`), with no check that the returned `tickets` array actually has one ticket per submitted payload, in the same order.

### Finding Description
In `signAndSendIntent`:
```ts
const composedPayloads = composeMultiPayloads(multiPayload, signedIntents);
if (composedPayloads.length > 1) {
  ...
  const tickets = await this.intentRelayer.publishIntents({ multiPayloads: composedPayloads, quoteHashes }, { logger: this.logger });
  const beforeCount = signedIntents?.before?.length ?? 0;
  const newIntentTicket = tickets[beforeCount];
  return { ticket: newIntentTicket as Ticket };
}
``` [1](#0-0) 

The relayer's `publishIntents` result is not validated against `composedPayloads.length` before indexing into it — it simply assumes `tickets[beforeCount]` corresponds to the payload the caller just signed. This assumption is enforced only by test doubles (which always mock a well-formed 1:1 array), not by any runtime check in the production code: [2](#0-1) 

The underlying relayer implementation, `IntentRelayerPublic.publishIntents`, forwards the solver-relay response's `intent_hashes` array directly, and even treats an "already processed" (idempotent) response as `Ok`, returning whatever `intent_hashes` the relay reports for that call: [3](#0-2) [4](#0-3) 

The `PublishIntentsResponse` type itself does not guarantee that `intent_hashes.length` equals the number of `signed_datas` submitted, or that ordering is preserved — it's simply `intent_hashes: string[]` with no positional contract enforced in types or code: [5](#0-4) 

This is analogous to the `poolIdArrayIndexForExcessDeposit` bug class: the code advances/derives a critical index (`beforeCount`) and uses it to select an item from a downstream response without verifying that the response actually has the expected shape for that index to be meaningful. If the relay ever returns fewer hashes than payloads submitted (e.g., a partial "already processed" dedup response, or a differently-ordered/truncated array), `tickets[beforeCount]` silently returns `undefined` or, worse, the ticket belonging to a different payload (e.g. one of the caller-unrelated `before`/`after` pre-signed intents), and this wrong ticket is returned to the caller as if it were their own intent's tracking hash.

### Impact Explanation
If `newIntentTicket` ends up being the ticket for a different composed payload (or `undefined`), the caller of `signAndSendIntent` — typically an integrator using `sdk.signAndSendIntent` — is handed the wrong intent hash. Consumers use this ticket to `waitForSettlement`, to poll for on-chain execution, and to decide whether to credit/refund a user. A wrong-ticket misreport means the integrator could wait on / consider settled a completely different intent than the one it actually cares about, and treat their own intent as unconfirmed or vice-versa — a status/hash misreport that can lead to a double credit or a stuck perceived-pending withdrawal, matching the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
This path is only reachable when a caller supplies `signedIntents.before`/`.after` (composing multiple pre-signed payloads with a new one) — a supported, documented SDK feature (`sendSignedIntents`/`signAndSendIntent` with `SignedIntentsComposition`), not a hypothetical corner case. The only external dependency required is the solver-relay returning an `intent_hashes` array whose length/order doesn't strictly match `composedPayloads`, which the code's own comment ("already processed") suggests is an anticipated real response variant — no malicious relay behavior is required, just a benign edge case in relay response shape that the SDK does not defensively validate.

### Recommendation
Before indexing into `tickets`, assert `tickets.length === composedPayloads.length` and throw a descriptive error otherwise. Prefer keying the returned ticket by hash correlation (e.g., compute the intent hash of `multiPayload` client-side via `computeIntentHash` and match it against relay-reported hashes) rather than trusting positional index equivalence between the request array and the response array.

### Proof of Concept
1. Caller invokes `sdk.signAndSendIntent({ intents, signedIntents: { before: [presignedA] } })`, so `composedPayloads = [presignedA, newPayload]`, `beforeCount = 1`.
2. The solver relay processes this batch, but for some payloads returns `reason: "already processed"` and returns an `intent_hashes` array reflecting only the not-yet-processed subset (e.g., `["hash-for-presignedA"]`) — this is treated as `Ok` per `parsePublishIntentsResponse`'s "already processed" branch: [6](#0-5) 
3. `tickets = ["hash-for-presignedA"]`, and `tickets[beforeCount] = tickets[1] = undefined`.
4. `IntentExecuter.signAndSendIntent` returns `{ ticket: undefined }` to the caller, who then calls `waitForSettlement(undefined, ...)`, silently misreporting the status of an intent that has no meaningful correlation to what the caller actually signed and submitted.

### Citations

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L99-123)
```typescript
		// Compose with pre-signed intents if provided
		const composedPayloads = composeMultiPayloads(multiPayload, signedIntents);

		// If we have multiple payloads (with signed intents), publish them atomically
		if (composedPayloads.length > 1) {
			const quoteHashes =
				(relayParams as { quoteHashes?: string[] }).quoteHashes ?? [];

			// Publish all payloads atomically using the relayer's batch method
			const tickets = await this.intentRelayer.publishIntents(
				{
					multiPayloads: composedPayloads,
					quoteHashes,
				},
				{ logger: this.logger },
			);

			// Calculate the index of the newly created intent
			// Order is: [before...] -> newPayload -> [after...]
			const beforeCount = signedIntents?.before?.length ?? 0;
			const newIntentTicket = tickets[beforeCount];

			// Return the ticket for the newly created intent
			// Note: All composed intents execute atomically, but we return the main one
			return { ticket: newIntentTicket as Ticket };
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.test.ts (L272-324)
```typescript
		it("composes intents with prepend only", async () => {
			const { intentSigner, intentRelayer } = setupMocks();
			const salt = Uint8Array.from([1, 2, 3, 4]);

			const prependIntent1 = await intentSigner.signIntent(
				defaultIntentPayloadFactory(salt, { verifying_contract: "" }),
			);
			const prependIntent2 = await intentSigner.signIntent(
				defaultIntentPayloadFactory(salt, { verifying_contract: "" }),
			);

			vi.mocked(intentRelayer.publishIntents).mockResolvedValue([
				"hash-prepend-1",
				"hash-prepend-2",
				"hash-new-intent",
			]);

			const exec = new IntentExecuter({
				envConfig: configsByEnvironment.production,
				intentRelayer,
				intentSigner,
			});

			const result = await exec.signAndSendIntent({
				intents: [
					{
						intent: "transfer",
						receiver_id: "alice.near",
						tokens: { "wrap.near": "1000" },
					},
				],
				signedIntents: {
					before: [prependIntent1, prependIntent2],
				},
				salt,
			});

			// Should return the hash of the newly created intent (at index 2)
			expect(result.ticket).toBe("hash-new-intent");

			// Should call publishIntents with all 3 payloads with correct order
			expect(intentRelayer.publishIntents).toHaveBeenCalledOnce();
			expect(intentRelayer.publishIntents).toHaveBeenCalledWith(
				expect.objectContaining({
					multiPayloads: [
						prependIntent1,
						prependIntent2,
						expect.objectContaining({ standard: "erc191" }),
					],
				}),
				expect.any(Object),
			);
		});
```

**File:** packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts (L44-71)
```typescript
	// how to pass additional params like quoteHashes or some relay specific params ?
	async publishIntents(
		{
			multiPayloads,
			quoteHashes,
		}: {
			multiPayloads: MultiPayload[];
			quoteHashes: string[];
		},
		ctx: { logger?: ILogger } = {},
	): Promise<IntentHash[]> {
		const result = await solverRelay.publishIntents(
			{
				quote_hashes: quoteHashes,
				signed_datas: multiPayloads,
			},
			{
				baseURL: this.envConfig.solverRelayBaseURL,
				logger: ctx.logger,
				solverRelayApiKey: this.solverRelayApiKey,
			},
		);
		if (result.isOk()) {
			return result.unwrap() as IntentHash[];
		}

		throw result.unwrapErr();
	}
```

**File:** packages/internal-utils/src/solverRelay/publishIntents.ts (L53-65)
```typescript
function parsePublishIntentsResponse(
	publishParams: Parameters<typeof solverRelayClient.publishIntents>[0],
	response: Awaited<ReturnType<typeof solverRelayClient.publishIntents>>,
): Result<PublishIntentsReturnType, PublishIntentsErrorType> {
	if (response.status === "OK") {
		return Ok(response.intent_hashes);
	}

	if (response.reason === "already processed") {
		return Ok(response.intent_hashes);
	}

	return Err(toRelayPublishError(publishParams, response));
```

**File:** packages/internal-utils/src/solverRelay/solverRelayHttpClient/types.ts (L104-116)
```typescript
export type PublishIntentsResponse = JSONRPCResponse<
	PublishIntentsResponseSuccess | PublishIntentsResponseFailure
>;

export type PublishIntentsResponseSuccess = {
	intent_hashes: string[];
	status: "OK";
};
export type PublishIntentsResponseFailure = {
	intent_hashes: string[];
	status: "FAILED";
	reason: string | "expired" | "internal";
};
```
