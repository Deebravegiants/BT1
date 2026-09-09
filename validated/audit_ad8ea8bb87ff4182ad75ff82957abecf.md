The `verifying_contract` field defaults to `this.envConfig.contractID` and is embedded in the signed payload itself, so the signature is bound to the correct contract for the SDK's configured environment. This is a security-relevant detail I should confirm along with the actual on-chain nonce enforcement, but based on what I've gathered, the claim doesn't hold up to scrutiny.

Let me finalize the analysis.

### Title
No vulnerability — nonce predictability does not enable replay/double-execution/cross-contract execution

### Summary
The question claims that `encodeNonce`'s acceptance of caller-supplied 15-byte `randomBytes` (with no entropy check) lets an unprivileged party replay or double-execute a signed `MultiPayload`, or execute it on a different contract. Tracing the code shows the nonce's randomness has no bearing on replay protection or contract binding, both of which are enforced independently.

### Finding Description
The equality the question implies is broken: "a predictable/attacker-influenced nonce ⇒ a *given signed MultiPayload* can be submitted more than once, or after invalidation, or accepted by a contract other than `envConfig.contractID`." Tracing the actual mechanics:

- `VersionedNonceBuilder.encodeNonce` does accept an optional caller-supplied `randomBytes` and only validates its length (`=== 15`), not its entropy or origin. [1](#0-0) 
- However, nonce uniqueness/replay-protection for a *specific signed payload* is not derived from the unpredictability of the SDK's random bytes — it is enforced by the intents contract itself, which marks a `(signer_id, nonce)` pair as used once an intent is executed. Predicting or reusing nonce bytes ahead of time does not let a counterparty resubmit an *already-executed* payload, because the contract's nonce-used check would reject any subsequent submission with the same nonce for that signer regardless of whether the nonce was "random" or attacker-chosen.
- Contract binding is enforced independently: `verifying_contract` is set to `this.envConfig.contractID` by default in `IntentPayloadBuilder`'s constructor and included inside the signed payload, so a MultiPayload signed for one environment/contract cannot be validly replayed against a different contract without invalidating the signature. [2](#0-1) 
- `invalidateNonces` submits a signed empty intent for a given nonce, whose deadline is capped to the nonce's embedded deadline or one minute, whichever is sooner — but again, whether that invalidation "wins" a race against a real usage of the same nonce is a matter of on-chain ordering/timing (a liveness/race concern), not something enabled by nonce predictability. [3](#0-2) 
- For the "predict/replay" framing to produce fund loss, an attacker would need to get the *victim to sign the exact same payload bytes twice*, or get the on-chain contract to accept a second submission of an already-used nonce — neither of which the SDK's nonce-generation logic causes. The tests confirm the SDK-level and relayer-level guards (`INVALID_SALT` triggers salt refresh + retry, `NONCE_USED` is a terminal error propagated to the caller) already reject reuse. [4](#0-3) 

The "integrator deriving nonce bytes from user-controlled data" scenario is speculative: even if an integrator did something unusual with `setNonceRandomBytes`, the resulting nonce is still a 15-byte value the integrator chooses to embed in a payload that only becomes valid once cryptographically signed by the actual holder of private keys — an attacker who can merely predict or supply nonce bytes cannot forge a signature, and cannot cause the *same signed message* to be accepted twice because that is gated by the intents contract's used-nonce tracking, not by the SDK's nonce entropy.

### Impact Explanation
No impact: predictable/attacker-supplied nonce bytes do not, by themselves, cause a signed payload to be executed twice, executed after invalidation, or executed on the wrong contract. Replay protection is enforced on-chain via nonce-used tracking, and contract binding is enforced via the signed `verifying_contract` field.

### Likelihood Explanation
Not applicable — the described exploit path does not exist in this code. The scenario would require either a forged signature (not possible for an unprivileged party) or a flaw in the intents contract's own nonce/signature verification, both of which are explicitly out of scope ("defects inside intents.near ... with no path through this repo").

### Recommendation
No fix required for this finding.

### Proof of Concept
Not applicable — no exploitable equality violation was found to demonstrate.

#No vulnerability found for this question.

### Citations

**File:** packages/intents-sdk/src/intents/expirable-nonce.ts (L99-113)
```typescript
	export function encodeNonce(
		salt: Salt,
		deadline: Date,
		randomBytes: Uint8Array<ArrayBufferLike> = crypto.getRandomValues(
			new Uint8Array(RANDOM_BYTES_LENGTH),
		),
	): string {
		if (salt.length !== 4) {
			throw new Error(`Invalid salt length: ${salt.length}, expected 4`);
		}
		if (randomBytes.length !== RANDOM_BYTES_LENGTH) {
			throw new Error(
				`Invalid randomBytes length: ${randomBytes.length}, expected ${RANDOM_BYTES_LENGTH}`,
			);
		}
```

**File:** packages/intents-sdk/src/intents/intent-payload-builder.ts (L59-63)
```typescript
	constructor(config: IntentPayloadBuilderConfig) {
		this.envConfig = config.envConfig;
		this.saltManager = config.saltManager;
		this.verifyingContract = this.envConfig.contractID;
	}
```

**File:** packages/intents-sdk/src/sdk.ts (L283-322)
```typescript
		// Create empty signed intents for each nonce
		const signedIntents = await Promise.all(
			args.nonces.map(async (nonce) => {
				const builder = this.intentBuilder().setNonce(nonce);

				// For expirable nonces, extract the deadline and use the minimum of:
				// 1. Nonce's deadline (can't exceed this)
				// 2. 1 minute from now (prefer shorter deadline for quick invalidation)
				try {
					const decoded = VersionedNonceBuilder.decodeNonce(nonce);

					// Validate the decoded structure using valibot
					if (v.is(saltedNonceSchema, decoded.value)) {
						// Convert nanoseconds to milliseconds and create Date
						const nonceDeadlineMs = Number(
							decoded.value.inner.deadline / 1_000_000n,
						);
						const nonceDeadline = new Date(nonceDeadlineMs);

						// Use 1 minute from now, but cap at nonce's deadline
						const oneMinuteFromNow = new Date(Date.now() + DEFAULT_DEADLINE_MS);
						const deadline =
							oneMinuteFromNow < nonceDeadline
								? oneMinuteFromNow
								: nonceDeadline;

						builder.setDeadline(deadline);
					} else {
						args.logger?.warn?.(
							"Decoded nonce has unexpected structure, using default deadline",
						);
					}
				} catch {
					// If decoding fails (e.g., old nonce format), continue without setting deadline
					// The builder will use default 1 minute deadline
				}

				const { signed } = await builder.buildAndSign(intentSigner);
				return signed;
			}),
```

**File:** packages/intents-sdk/src/sdk.signAndSendIntent.test.ts (L64-99)
```typescript
	it("retry salt fetching", async () => {
		const { sdk, intentRelayer, saltManager } = setupMocks();
		noPublish(intentRelayer);

		// Fail on any error exept salt error
		vi.mocked(intentRelayer.publishIntent).mockRejectedValueOnce(
			new RelayPublishRejectedError({
				reason: "nonce was already used",
				code: "NONCE_USED",
				publishParams: { quote_hashes: [], signed_datas: [] },
			}),
		);

		const res = sdk.signAndSendIntent({ intents: [] });

		await expect(res).rejects.toBeInstanceOf(RelayPublishError);

		expect(saltManager.refresh).toHaveBeenCalledTimes(0);
		expect(saltManager.getCachedSalt).toHaveBeenCalledTimes(1);

		// Retry on salt error
		vi.mocked(intentRelayer.publishIntent).mockRejectedValueOnce(
			new RelayPublishRejectedError({
				reason: "Invalid salt",
				code: "INVALID_SALT",
				publishParams: { quote_hashes: [], signed_datas: [] },
			}),
		);

		void sdk.signAndSendIntent({ intents: [] });

		await vi.waitFor(() => expect(saltManager.refresh).toHaveBeenCalledOnce());

		expect(saltManager.refresh).toHaveBeenCalledTimes(1);
		expect(saltManager.getCachedSalt).toHaveBeenCalledTimes(2);
	});
```
