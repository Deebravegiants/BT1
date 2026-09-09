No vulnerability found for this question.

**Reasoning:**

`sendSignedIntents` and `IntentExecuter.sendSignedIntents` only forward already-fully-signed `MultiPayload` objects to `intentRelayer.publishIntents` without any transformation of their contents. [1](#0-0) [2](#0-1) 

For the `sep53` standard, the signed bytes are `sha256("Stellar Signed Message:\n" + payload)`, where `payload` is the JSON-serialized `IntentPayload` string that already embeds `verifying_contract`, `signer_id`, `nonce`, `deadline`, and `intents` at signing time. [3](#0-2) [4](#0-3) 

Because the signature is computed over the entire `payload` string byte-for-byte (including `verifying_contract`), any caller-side mutation of `verifying_contract` after signing changes the message bytes and invalidates the signature. Since `sendSignedIntents`/`publishIntents` never re-derive or mutate `payload`, `signature`, or `standard` — they pass the `MultiPayload` array through unchanged — there is no code path in this SDK by which a caller can alter `verifying_contract` in a payload "signed elsewhere" while keeping the original signature valid. `intents.near`'s own signature verification (outside this repo, but the described mechanism relies on it) would reject any payload where the parsed `verifying_contract` doesn't match the bytes that were actually signed.

The premise "the signature still verifies over the altered payload" is self-contradictory for sep53/NEP413/ERC191-style full-message signing schemes used here: altering any field of the JSON payload changes the hash input, so the same signature cannot verify against the altered content. The claimed equality break (`signed.verifying_contract == the value the caller constructed`) cannot actually diverge through `sendSignedIntents`, because the caller who owns the private key controls what they sign in the first place (via `IntentPayloadBuilder.setVerifyingContract`/`buildAndSign` or their own external signing flow) — that is intended, documented behavior for composing pre-signed intents [5](#0-4) , not an unauthorized alteration of a third party's signed data.

### Citations

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L148-161)
```typescript
	async sendSignedIntents(params: {
		multiPayloads: MultiPayload[];
		quoteHashes?: string[];
	}): Promise<{ tickets: Ticket[] }> {
		const tickets = await this.intentRelayer.publishIntents(
			{
				multiPayloads: params.multiPayloads,
				quoteHashes: params.quoteHashes ?? [],
			},
			{ logger: this.logger },
		);

		return { tickets };
	}
```

**File:** packages/intents-sdk/src/sdk.ts (L622-636)
```typescript
	public async sendSignedIntents(args: {
		multiPayloads: MultiPayload[];
		quoteHashes?: string[];
		logger?: ILogger;
	}): Promise<{ tickets: IntentHash[] }> {
		const tickets = await this.intentRelayer.publishIntents(
			{
				multiPayloads: args.multiPayloads,
				quoteHashes: args.quoteHashes ?? [],
			},
			{ logger: args.logger },
		);

		return { tickets };
	}
```

**File:** packages/intents-sdk/src/intents/intent-hashes/sep53.ts (L9-26)
```typescript
export function computeSep53Prehash(payload: string): Uint8Array {
	const prefix = new TextEncoder().encode("Stellar Signed Message:\n");
	const data = new TextEncoder().encode(payload);

	return utils.concatUint8Arrays([prefix, data]);
}

/**
 * Compute the SHA-256 hash of a SEP-53 payload
 * This is the hash that should be signed
 *
 * @param payload - The message string to hash
 * @returns 32-byte hash as Uint8Array
 */
export function computeSep53Hash(payload: string): Uint8Array {
	const prehash = computeSep53Prehash(payload);
	return sha256(prehash);
}
```

**File:** packages/internal-utils/src/utils/prepareBroadcastRequest.ts (L69-83)
```typescript
		case "STELLAR_SEP53": {
			assert(
				userInfo.userChainType === "stellar",
				"User chain and signature chain must match",
			);
			return {
				standard: "sep53",
				payload: signature.signedData.message,
				// We should encode the Stellar address to base58
				public_key: `ed25519:${base58.encode(
					stellarAddressToBytes(userInfo.userAddress),
				)}`,
				signature: transformED25519Signature(signature.signatureData),
			};
		}
```

**File:** packages/intents-sdk/src/intents/intent-payload-builder.ts (L118-128)
```typescript
	/**
	 * Override the verifying contract address.
	 * Use with caution - normally this is automatically set based on environment.
	 *
	 * @param contractAddress - The contract address to use
	 * @returns The builder instance for chaining
	 */
	setVerifyingContract(contractAddress: string): this {
		this.verifyingContract = contractAddress;
		return this;
	}
```
