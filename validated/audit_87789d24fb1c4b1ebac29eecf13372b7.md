### Title
`computeTonConnectHash` writes UTF-16 code-unit length instead of UTF-8 byte length for `domain`, corrupting the locally recomputed TON Connect intent hash for non-ASCII domains - ([File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts])

### Summary
`computeTonConnectHash` builds the SHA-256 preimage by writing `numberToBigEndian(domain.length, 4)` (JS `string.length`, i.e. UTF-16 code units) immediately followed by `new TextEncoder().encode(domain)` (UTF-8 bytes). For any `domain` containing non-ASCII characters these two counts diverge, so the SDK-side reconstructed hash bytes differ from the bytes that were actually signed/verified using the domain's true UTF-8 byte length, breaking `computeIntentHash(multiPayload) === intent_hash` for TON Connect payloads whose `domain` is not pure ASCII.

### Finding Description
The broken equality is:
`computeIntentHash(multiPayload)` (client-recomputed hash, via `computeSignedTonConnectHash` → `computeTonConnectHash`) should equal `intent_hash` (the hash the relayer/contract derives from the same signed TonConnect message and returns from `publishIntent`).

In [1](#0-0) , for the `"text"` payload type, the function concatenates `numberToBigEndian(domain.length, 4)` and then `new TextEncoder().encode(domain)`. `domain.length` counts UTF-16 code units of the JS string, while `TextEncoder().encode(domain)` produces UTF-8 bytes. For a domain such as `"münchén.example"`, each non-ASCII codepoint (`ü`, `é`) occupies 1 UTF-16 code unit but 2 UTF-8 bytes, so `domain.length` (16) does not equal the UTF-8 byte length (18). The length field written into the hash preimage is therefore wrong, and it does not match the byte length of the data that immediately follows it in the same buffer.

This function is reached from `computeIntentHash` → `computeIntentHashHashBytes` → `computeSignedTonConnectHash` for `standard === "ton_connect"` [2](#0-1) . The `domain` value itself is populated from the wallet's own `signatureData.domain` when constructing the TON Connect `MultiPayload` in `prepareSwapSignedData` [3](#0-2) ; the "domain" used in the real TON Connect sign-data protocol is a UTF-8-length-prefixed field per the TonConnect spec referenced in the file's own docstring [4](#0-3) , so the canonical/contract-side hash uses the correct UTF-8 byte length, while this SDK reimplementation uses the wrong one whenever `domain` is non-ASCII.

Existing repo tests only cover ASCII domains (`"near.com"`, `"tonconnect-demo-dapp-with-wallet.vercel.app"`) [5](#0-4) [6](#0-5) , so this divergence is not caught by the current test suite. No guard in the codebase (`assert`, schema validation, etc.) restricts `domain` to ASCII — the schema only requires `type: "string"` [7](#0-6) .

### Impact Explanation
`computeIntentHash` is the mechanism integrators use to obtain a hash locally (e.g., to persist before publishing, per the question's `onBeforePublishIntent`) and compare it against the `intent_hash` returned by the relay/contract via `publishIntent`/`waitForIntentSettlement`. If the two never match for non-ASCII domains, an integrator relying on this equality for tracking cannot correlate the locally computed hash with the on-chain/relay-confirmed hash. This does not corrupt the actual signed message sent to the wallet or the contract's own verification (those are computed by the TON wallet/contract using the correct UTF-8 length, independent of this SDK's local reconstruction) — the SDK's local hash is simply wrong. The consequence is a hash mismatch used purely for local bookkeeping/idempotency tracking, which can cause an integrator to lose track of a signed intent (mis-associate/duplicate-handle a settlement) if their logic keys off the SDK-derived hash rather than the hash returned by `publishIntent`.

### Likelihood Explanation
Preconditions: `standard === "ton_connect"`, `payload.type === "text"`, and a `domain` string containing any non-ASCII character (any multi-byte UTF-8 codepoint, e.g., accented Latin letters, non-Latin scripts, emoji). The `domain` is supplied by the TON wallet during the TonConnect sign-data flow and reflects the dApp's actual hostname; internationalized domain names (IDNs) rendered in Unicode rather than Punycode are a realistic real-world occurrence. Any user connecting through such a dApp domain, with an ordinary standard SDK call flow, triggers the bug — no privileged access needed, and it is deterministic and repeatable on every call for that domain.

### Recommendation
Compute the domain length from its UTF-8 encoding rather than the JS string length: encode the domain first, then use the resulting `Uint8Array.length` for the 4-byte big-endian prefix, e.g.:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```

### Proof of Concept
Vitest test in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts`:
1. Construct a `MultiPayload` with `standard: "ton_connect"`, `domain: "münchén.example"`, `payload: { type: "text", text: "..." }`.
2. Independently compute the "correct" hash by manually building the preimage using `new TextEncoder().encode(domain).length` for the length prefix (simulating what the contract/relayer would derive), and hash it with `sha256`.
3. Call `computeTonConnectHash(payload)` and assert:
   ```ts
   expect(computeTonConnectHash(payload)).not.toEqual(correctlyComputedHash);
   ```
   demonstrating `numberToBigEndian(domain.length, 4)` (16 for `"münchén.example"`) diverges from `numberToBigEndian(new TextEncoder().encode(domain).length, 4)` (18), causing `computeIntentHash(multiPayload)` to diverge from the mocked relay-returned `intent_hash` in a `publishIntent` HTTP mock.

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L30-49)
```typescript
/**
 * Compute the SHA-256 hash of a TON Connect payload
 *
 * For text and binary payloads:
 * Hash = SHA256(
 *   0xffff +
 *   "ton-connect/sign-data/" +
 *   workchain_id (4 bytes BE) +
 *   address (32 bytes) +
 *   domain_len (4 bytes BE) +
 *   domain +
 *   timestamp (8 bytes BE) +
 *   payload_type ("txt" or "bin") +
 *   payload_len (4 bytes BE) +
 *   payload
 * )
 *
 * @param payload - The TON Connect payload to hash
 * @returns 32-byte hash as Uint8Array
 */
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L60-76)
```typescript
		case "text": {
			const payloadPrefix = "txt";
			const payloadData = new TextEncoder().encode(payloadSchema.text);

			// Build the message to hash
			const parts: Uint8Array[] = [
				new Uint8Array([0xff, 0xff]),
				new TextEncoder().encode("ton-connect/sign-data/"),
				numberToBigEndian(parsedAddress.workchainId, 4),
				parsedAddress.address,
				numberToBigEndian(domain.length, 4),
				new TextEncoder().encode(domain),
				numberToBigEndian(Number(timestamp), 8),
				new TextEncoder().encode(payloadPrefix),
				numberToBigEndian(payloadData.length, 4),
				payloadData,
			];
```

**File:** packages/intents-sdk/src/intents/intent-hash.ts (L54-57)
```typescript
		case "ton_connect":
			return computeSignedTonConnectHash(
				signed as Extract<MultiPayload, { standard: "ton_connect" }>,
			);
```

**File:** packages/internal-utils/src/utils/prepareBroadcastRequest.ts (L57-67)
```typescript
		case "TON_CONNECT": {
			return {
				standard: "ton_connect",
				address: signature.signatureData.address,
				domain: signature.signatureData.domain,
				timestamp: signature.signatureData.timestamp,
				payload: signature.signatureData.payload,
				public_key: `ed25519:${base58.encode(hex.decode(userInfo.userAddress))}`,
				signature: `ed25519:${base58.encode(base64.decode(signature.signatureData.signature))}`,
			};
		}
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts (L10-18)
```typescript
		const payloadWithUserFriendlyAddress = {
			standard: "ton_connect",
			address: USER_FRIENDLY,
			domain: "near.com",
			timestamp: 1778685374,
			payload: { type: "text", text: "hello world" },
			public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
			signature: "ed25519:not-checked-by-hash-fn",
		} satisfies Extract<MultiPayload, { standard: "ton_connect" }>;
```

**File:** packages/intents-sdk/src/intents/intent-hash.test.ts (L70-82)
```typescript
			standard: "ton_connect",
			address:
				"0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
			domain: "tonconnect-demo-dapp-with-wallet.vercel.app",
			timestamp: 1762354640,
			payload: {
				type: "text",
				text: '{\n  "signer_id": "d1e7c122f8a43c7d7433548c4604edd4dffcfe5bb1d036499684980c115500bf",\n  "verifying_contract": "intents.near",\n  "deadline": "2035-11-03T14:57:16.445Z",\n  "nonce": "s7ne425+Pw+eVR7j02peS/wIxHKu64znkTJYeCTAfPk=",\n  "intents": []\n}',
			},
			public_key: "ed25519:F8PB56zdMYNDL7Mq43DV4cV17uRqQkpn6ZygNdqavXCr",
			signature:
				"ed25519:i5REHik6CRvvfnKsUtSDvxPeeLiPQsNMGpg9yARs9vtnZxSV9mht9K1tW2LZp8pGd4C83YZRXNG3Y5dBFdLMENd",
		},
```

**File:** packages/contract-types/src/type-check-schemas.ts (L4488-4488)
```typescript
				domain: { description: "dApp domain", type: "string" },
```
