### Title
Domain length in `computeTonConnectHash` uses UTF-16 code-unit count instead of UTF-8 byte length, causing hash divergence for non-ASCII TON Connect domains - (File: `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`)

### Summary
`computeTonConnectHash` builds the SHA-256 preimage as `0xffff + "ton-connect/sign-data/" + workchain(4B) + address(32B) + domain_len(4B) + domain_bytes + timestamp(8B) + type + payload_len(4B) + payload_bytes`. The `domain_len` field is computed with `numberToBigEndian(domain.length, 4)`, where `domain.length` is the JavaScript string's UTF-16 code-unit count, not the UTF-8 byte length of the immediately-following `new TextEncoder().encode(domain)` bytes. For any domain containing multi-byte UTF-8 characters (surrogate-pair emoji, non-Latin scripts, etc.), this length field is wrong.

### Finding Description
The equality that must hold is:
`computeIntentHash(multiPayload)` (local, offline computation in this SDK) `==` `intent_hash` returned by the relayer/contract for the identical signed payload (via `publishIntent` / `simulate_intents`).

In `computeTonConnectHash` [1](#0-0) , the domain length is encoded via `numberToBigEndian(domain.length, 4)` while the payload length a few lines later is correctly computed from the encoded byte array (`payloadData.length` where `payloadData = new TextEncoder().encode(payloadSchema.text)`). This inconsistency shows the intended design (per the function's own JSDoc, `domain_len (4 bytes BE) + domain`) is a byte-length-prefixed field, matching the TON Connect signing spec used by TON wallets and, presumably, by the on-chain/relayer verifier that must replicate the exact bytes a TON wallet signed.

For an ASCII-only domain, `domain.length` (UTF-16 units) equals the UTF-8 byte length, so the bug is invisible — which is exactly why the existing test suite (`packages/intents-sdk/src/intents/intent-hash.test.ts`) only exercises an ASCII domain (`"tonconnect-demo-dapp-with-wallet.vercel.app"`) [2](#0-1)  and never a domain with surrogate-pair or multi-byte characters. Once a domain contains a code point outside the BMP (e.g. an emoji, `.length` counts 2 UTF-16 units) or any 2-/3-byte UTF-8 character (e.g. CJK, Cyrillic — 1 UTF-16 unit but 2-3 UTF-8 bytes), `domain.length` diverges from `TextEncoder().encode(domain).length`, corrupting the `domain_len` field and shifting/misinterpreting all subsequent bytes in the hashed message. The resulting SHA-256 digest — and therefore the base58-encoded value returned by `computeIntentHash` — will not equal the digest computed by any spec-correct implementation (the TON wallet that actually signed the data, and presumably the relayer/contract path that must match it to accept the signature).

No existing guard catches this: `computeIntentHash` performs no round-trip validation against the signature or an on-chain digest before being used by callers; the divergence is silent.

### Impact Explanation
Any integrator or SDK consumer relying on `computeIntentHash` to derive the intent hash offline (e.g., to persist it before calling `publishIntent`, as implied by `onBeforePublishIntent`, or to poll `waitForIntentSettlement`) will compute a hash that never matches the hash actually returned by the relay for `ton_connect` intents whose `domain` contains multi-byte UTF-8 characters. This is a hash/status misreport: the integrator's local record of "the intent I submitted" points to a hash that will never settle, while the real intent (with the correct hash) proceeds on-chain. This can cause the integrator to treat the real intent as unconfirmed and retry/resubmit, or fail to credit/refund correctly — matching the High severity category "a status or hash misreport making an integrator credit or refund twice." Repeatable on every `ton_connect` payload with a non-ASCII-multibyte domain.

### Likelihood Explanation
Preconditions: any `ton_connect` MultiPayload whose `domain` field contains at least one character whose UTF-8 encoding length (in bytes) differs from its UTF-16 length (in code units) — this includes ordinary internationalized domain content or any non-ASCII characters, not just emoji. Domain values are attacker/integrator-supplied strings that flow directly into `computeTonConnectHash` with no sanitization. No special privileges are required; the cost is zero (just choosing a domain string with non-ASCII characters), and it triggers on every call, making it fully repeatable.

### Recommendation
Fix `computeTonConnectHash` to compute the domain length from its UTF-8 encoded byte array, consistent with how `payloadData.length` is already computed:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
Add a regression test in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts` using a non-ASCII/multibyte domain (e.g. containing an emoji) and assert the computed hash matches the value derived from `intents.near`'s `simulate_intents` (as already done for other standards in `intent-hash.test.ts`).

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "./ton-connect";

describe("computeTonConnectHash domain length bug", () => {
  it("domain_len byte-count diverges from JS string length for surrogate-pair domain", () => {
    const domain = "👍.example.com"; // 1 surrogate pair (2 UTF-16 units, 4 UTF-8 bytes) + ascii
    const utf16Length = domain.length;                              // JS .length
    const utf8ByteLength = new TextEncoder().encode(domain).length; // actual bytes
    expect(utf16Length).not.toEqual(utf8ByteLength); // proves divergence exists

    const payload = {
      standard: "ton_connect" as const,
      address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
      domain,
      timestamp: 1762354640,
      payload: { type: "text" as const, text: "{}" },
      public_key: "ed25519:F8PB56zdMYNDL7Mq43DV4cV17uRqQkpn6ZygNdqavXCr",
      signature: "ed25519:...",
    };

    // Mock relay publishIntent response with contract-computed intent_hash
    // (obtained via `simulate_intents` on intents.near, using correct UTF-8 byte-length domain_len)
    const mockedIntentHashBytes = /* expected correct SHA-256 bytes using byte length */ new Uint8Array(32);

    const localHashBytes = computeTonConnectHash(payload);

    // Fails: SDK uses domain.length (UTF-16 units) as domain_len instead of UTF-8 byte length
    expect(localHashBytes).not.toEqual(mockedIntentHashBytes);
  });
});
```
This demonstrates that `computeIntentHash` for a `ton_connect` MultiPayload with a multi-byte-UTF-8 domain diverges from the hash a spec-correct verifier (and presumably `publishIntent`'s returned `intent_hash`) would compute.

### Citations

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

**File:** packages/intents-sdk/src/intents/intent-hash.test.ts (L69-82)
```typescript
		{
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
