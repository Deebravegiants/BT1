### Title
`invalidateNonces` invalidates the nonce in the caller's own signer-namespace, not the original signer's, leaving another signer's payload fully executable - (File: packages/intents-sdk/src/sdk.ts)

### Summary
`invalidateNonces` never calls `.setSigner()` on the builder, so the empty invalidation intent's `signer_id` is left `undefined` and is filled in by the NEP-413 signer implementation with `this.accountId` (the signer actually invoking `invalidateNonces`), not the `signer_id` embedded in the original payload the caller is trying to cancel. On-chain nonce state is namespaced per `signer_id`, so invalidating "nonce X" while signed as account B does nothing to the nonce namespace of account A. If the payload the user is worried about was originally signed by A, it remains fully valid and executable after `invalidateNonces` resolves successfully.

### Finding Description
The broken equality: the caller believes
`nonce_invalidated_for(signer_id_of_original_payload) == true`
after `invalidateNonces` resolves, but what actually happens is
`nonce_invalidated_for(signer_id_of_invalidation_caller) == true`, and these two `signer_id`s can differ.

Trace:
- `invalidateNonces` builds the empty intent via `this.intentBuilder().setNonce(nonce)` only — `setSigner` is never called: [1](#0-0) 
- `IntentPayloadBuilder.buildWithSalt` therefore emits `signer_id: this.signerId` which is `undefined` when `setSigner` was never invoked: [2](#0-1) 
- The NEP-413 signer fills the gap with its own `accountId` when building the message to sign: `signer_id: intent.signer_id ?? this.accountId` [3](#0-2) 
- The contract schema/ABI documents that an empty-intents payload "invalidates the `nonce` for the signer" — i.e., nonce state is keyed by `(signer_id, nonce)`, not by `nonce` alone: [4](#0-3) 
- Publishing then only sends this empty intent (signed by the invoking account) to the relayer: [5](#0-4) 

Root cause: `invalidateNonces` has no mechanism to bind the invalidation intent's `signer_id` to the signer_id of the original payload being cancelled; it silently defaults to whichever account signs the invalidation call. If a caller (e.g., an integrator or a solver acting on a user's behalf) attempts to cancel a nonce that was embedded in a payload signed by a different `signer_id` than the one now invoking `invalidateNonces`, the call reports success (`Promise` resolves, `publishIntents` succeeds) but the on-chain/relayer nonce state for the *original* signer is untouched. Existing guards do not catch this: there is no validation in `invalidateNonces`, `setNonce`, or `buildAndSign` that the nonce's namespace matches the signer being used; `decodeNonce`/`saltedNonceSchema` only recover the embedded *deadline*, not the `signer_id`, since the nonce format has no signer_id field (confirmed by the borsh schema: `salt`, `inner.deadline`, `inner.nonce` only, no signer_id) [6](#0-5) .

Additionally, the code's own comment acknowledges invalidation is relayer-memory-only and not tracked on-chain as of 15 Nov 2025 [5](#0-4) , meaning even a *correctly-namespaced* invalidation offers no on-chain guarantee — this part, however, is an explicitly documented trust assumption about the relayer's behavior, which is out of scope per the audit rules ("trust assumptions about ... the relayer").

The in-scope, non-relayer-trust portion of the bug is the signer_id mismatch: the SDK builds an invalidation payload under the wrong account namespace without any error, warning, or validation, silently no-op'ing the intended invalidation for a payload signed by someone else.

### Impact Explanation
If a caller relies on `invalidateNonces` to cancel a specific nonce that was embedded in a payload signed under a different NEAR account (`signer_id`) than the account used to call `invalidateNonces`, the SDK reports success while the original payload remains fully valid and executable under its own `signer_id` namespace on the `intents.near` contract. Anyone holding that original signed payload (a solver, a relayer, or the original owner) can still submit it and have it executed, replaying/executing a withdrawal or swap the caller believed was cancelled. This matches the "signature replayed or executed twice" / intent executed without authorization pattern (Critical impact category), because the fund-moving intent the caller thought was voided is still live.

This is repeatable on every call where the signer used to invalidate differs from the signer that originally signed the target payload.

### Likelihood Explanation
This requires that whoever calls `invalidateNonces` supplies a `signer`/uses a default signer whose `accountId` differs from the `signer_id` of the payload they intend to void — e.g., an integrator invalidating a counterparty-provided nonce with their own service account, or any workflow where the "current" signer isn't provably the same as the original payload's signer. The SDK provides no runtime check to prevent or warn about this mismatch, and the public API (`args.nonces: string[]`, optional `signer`) explicitly allows arbitrary nonce strings from any source (e.g., forwarded by an integrator) to be invalidated under an arbitrary signer. No special access is needed — this is directly reachable through the documented public method.

### Recommendation
`invalidateNonces` should require (or derive and enforce) that the `signer_id` used for the empty invalidation intent matches the `signer_id` embedded in/derived from the original payload the nonce belongs to. Concretely: accept the original payload's `signer_id` as a required parameter alongside each nonce (or the whole original `signedIntent`), call `.setSigner(signerId)` on the builder, and verify at signing time that the signer actually used (`intentSigner`'s own account) matches that `signer_id` before publishing — throwing/rejecting on mismatch rather than silently succeeding.

### Proof of Concept
```ts
// packages/intents-sdk/src/sdk.invalidateNonces.signerMismatch.test.ts
it("invalidateNonces silently no-ops when signer differs from original payload's signer_id", async () => {
  const { sdk, intentRelayer, defaultIntentSigner } = setupMocks(); // defaultIntentSigner.accountId = "attacker.near"
  noPublish(intentRelayer);

  const nonce = "VigoxLwmUGf35MGLVBG9Fh5cCtJw3D68pSKFcqGCkHU=";
  // Assume this nonce was embedded in a payload originally signed by "victim.near"

  await sdk.invalidateNonces({ nonces: [nonce] }); // resolves without error -> caller believes success

  const call = vi.mocked(defaultIntentSigner.signIntent).mock.calls[0]![0];
  // Left side: signer_id caller intended to invalidate under
  const intendedSignerId = "victim.near";
  // Right side: signer_id actually used in the built/signed empty intent
  const actualSignerId = call.signer_id ?? defaultIntentSigner.accountId;

  expect(actualSignerId).not.toBe(intendedSignerId); // equality is broken
  // => on-chain nonce state for "victim.near" namespace was never touched,
  //    so a payload signed by victim.near with this nonce remains executable.
});
```

### Citations

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

**File:** packages/intents-sdk/src/sdk.ts (L325-331)
```typescript
		// Publish all invalidation intents atomically
		// As for 15 Nov 2025, it's impossible to track onchain invalidation,
		// because Relayer doesn't publish such intents onchain. It invalidates in-memory only.
		await this.intentRelayer.publishIntents(
			{ multiPayloads: signedIntents, quoteHashes: [] },
			{ logger: args.logger },
		);
```

**File:** packages/intents-sdk/src/intents/intent-payload-builder.ts (L197-211)
```typescript
	buildWithSalt(salt: Salt): IntentPayloadWithSigner<HasSigner> {
		const deadline =
			this.deadline ?? new Date(Date.now() + DEFAULT_DEADLINE_MS);
		const nonce =
			this.customNonce ??
			VersionedNonceBuilder.encodeNonce(salt, deadline, this.customRandomBytes);

		return {
			verifying_contract: this.verifyingContract,
			signer_id: this.signerId,
			deadline: deadline.toISOString(),
			nonce,
			intents: [...this.intents],
		} as IntentPayloadWithSigner<HasSigner>;
	}
```

**File:** packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts (L65-77)
```typescript
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

**File:** packages/contract-types/src/index.ts (L344-350)
```typescript
export interface DefusePayloadFor_DefuseIntents {
	deadline: Deadline;
	/**
	 * Sequence of intents to execute in given order. Empty list is also a valid sequence, i.e. it doesn't do anything, but still invalidates the `nonce` for the signer WARNING: Promises created by different intents are executed concurrently and does not rely on the order of the intents in this structure
	 */
	intents?: Intent[];
	nonce: string;
```

**File:** packages/intents-sdk/src/intents/expirable-nonce.ts (L16-22)
```typescript
export const saltedNonceSchema = v.object({
	salt: v.array(v.number()),
	inner: v.object({
		deadline: v.bigint(),
		nonce: v.array(v.number()),
	}),
});
```
