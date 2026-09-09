### No vulnerability found for this question.

The claimed exploit requires that a NEP-413 message where `signer_id` names an account not actually controlled by the signing key be accepted somewhere downstream. `IntentSignerNEP413.signIntent` at [1](#0-0)  simply serializes `intent.signer_id ?? this.accountId` into the message and calls `signRaw`, which hashes and signs with whatever key `signMessageFn` uses [2](#0-1) . The SDK indeed performs no equality check between `signer_id` and the key behind `signMessageFn` — but that check is not the SDK's responsibility to enforce; it is enforced by the `intents.near` contract when it verifies the NEP-413 signature against the on-chain access keys registered for the claimed `signer_id` account. A signature produced by an attacker-controlled key can never validate against a victim account's registered public key on-chain, so a payload with `signer_id = victim` but signed by the attacker's key will simply be rejected by the contract's own signature/nonce verification — this is standard NEP-413 semantics, not a gap introduced by this repo.

This matches the exclusion in the audit rules: "Check whether ... the intents contract's own signature and nonce verification already prevent the divergence," and "defects inside intents.near, bridge contracts ... with no path through this repo" are out of scope. The attacker here is only crafting a message for their *own* keys/account combination they fully control (they supply both `signMessage` and `accountId` in the constructor); nothing forces any victim or integrator to accept or relay this self-inconsistent payload, and even if a solver/relayer submitted it, on-chain verification rejects it. There is no reachable path in the SDK that lets an attacker forge a payload that a victim's actual key material would be bound to, nor any path that moves the victim's funds using only the attacker's own signature.

### Citations

**File:** packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts (L37-62)
```typescript
	async signRaw(input: Nep413RawPayload): Promise<MultiPayloadNep413> {
		const nep413Payload: NEP413Payload = {
			message: input.payload.message,
			nonce: Array.from(base64.decode(input.payload.nonce)),
			recipient: input.payload.recipient,
			callback_url: input.payload.callbackUrl,
		};

		const nep413Hash = await hashNEP413Message(nep413Payload);

		const { publicKey, signature } = await this.signMessageFn(
			nep413Payload,
			nep413Hash,
		);

		const signatureFormatted = signature.startsWith("ed25519:")
			? signature
			: `ed25519:${base58.encode(base64.decode(signature))}`;

		return {
			standard: "nep413",
			payload: input.payload,
			public_key: publicKey,
			signature: signatureFormatted,
		};
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
