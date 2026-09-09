### Title
Incorrect UTF-16 length used for TON Connect `domain` field breaks `computeIntentHash` for non-ASCII domains - (File: `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`)

### Summary
`computeTonConnectHash` encodes the `domain_len` field using JavaScript's `domain.length` (UTF-16 code-unit count) instead of the actual UTF-8 byte length (`new TextEncoder().encode(domain).length`), while the domain bytes themselves are encoded with `TextEncoder`. For any `domain` string containing characters outside the ASCII range whose UTF-16 code-unit count differs from its UTF-8 byte count (e.g., CJK characters, emoji/surrogate pairs), the length prefix written into the hashed message is wrong, producing a hash that diverges from the byte-correct hash the wallet actually signed and that the intents.near contract/relay computes.

### Finding Description
The broken equality is:
`computeIntentHash(multiPayload)` (local, TS SDK) `==` `intent_hash` returned by `publishIntents`/`simulate_intents` (relay/contract-computed, per the real TON Connect spec).

In `computeTonConnectHash`, the domain length prefix is built as: [1](#0-0) 

Specifically `numberToBigEndian(domain.length, 4)` at line 70 uses the JS string `.length` property (UTF-16 code units), while the actual bytes appended right after are `new TextEncoder().encode(domain)` (UTF-8 bytes) at line 71. For pure ASCII domains these two counts coincide, which is why the existing repo test suite never catches the bug — every fixture domain (`near.com`, `tonconnect-demo-dapp-with-wallet.vercel.app`, `ton-connect.github.io`) is ASCII-only, as seen in `ton-connect.test.ts` and `intent-hash.test.ts`. [2](#0-1) [3](#0-2) 

The real TON Connect sign-data protocol (and the on-chain `intents.near` verifier, cross-checked in the same test file via `simulate_intents`) uses the byte length of the UTF-8-encoded domain, not the UTF-16 code-unit count of the JS string, because that byte length is what the wallet actually hashes/signs at signing time. [4](#0-3) 

**Exploit flow**: An ordinary user (or an integrator building the TON Connect payload themselves rather than trusting a fixed dApp domain) constructs/receives a `MultiPayload` with `standard: "ton_connect"` and a `domain` containing a surrogate pair (e.g., an emoji) or multi-byte character (e.g., a CJK character):
1. The wallet signs the TON Connect payload using the byte-correct algorithm (as per TON Connect spec), so the signature is valid for the byte-correct hash.
2. The caller invokes `computeIntentHash(multiPayload)` locally — this returns a hash computed with the wrong `domain_len` (UTF-16 units), differing from the byte-correct hash.
3. `sdk.publishIntents()` submits the same `multiPayload` to the relay/contract, which verifies the signature and computes the intent hash using the byte-correct algorithm, returning the correct `intent_hash`.
4. The two hashes diverge: `computeIntentHash(multiPayload) != intent_hash`.

No existing guard (`validateAddress`, `assert` checks, schema validation) checks or normalizes the `domain` field's byte length; `domain` is typed as a free-form `string` in the contract-types schema. [5](#0-4) 

### Impact Explanation
An integrator or the SDK caller that persists the locally computed `intent_hash` (e.g., for `waitForIntentSettlement` polling, deduplication, or status tracking) will watch/store the wrong hash whenever the TON Connect `domain` contains non-ASCII multi-byte characters. This causes a status/hash misreport that can make an integrator apply incorrect retry or double-send logic for the user's own ton_connect intent — matching the "status or hash misreport" High severity category. The affected party is the ordinary user/integrator issuing the ton_connect intent themselves; no third party can trigger this against another user's intent.

### Likelihood Explanation
Preconditions are simple and fully attacker/controller-controlled: `standard: "ton_connect"`, a `payload.type: "text"`, and a `domain` value containing any character whose UTF-16 code-unit count differs from its UTF-8 byte count (very common — any CJK character, accented character beyond Latin-1 in some cases, or emoji). No special route/token state or cost is required; this reproduces deterministically on every call with such a domain, since the discrepancy exists in the length prefix construction, not in transient state.

### Recommendation
Replace the domain length calculation with the UTF-8 byte length, matching the actual encoded bytes:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
instead of computing `domain.length` and re-encoding separately. Add a regression test with a domain containing a CJK character and/or an emoji (surrogate pair) to `ton-connect.test.ts`.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "./ton-connect";

describe("computeTonConnectHash - non-ASCII domain divergence", () => {
  it("byte length differs from JS string length for non-ASCII domain", () => {
    const domain = "例え.com"; // CJK characters: UTF-16 length != UTF-8 byte length
    expect(domain.length).not.toEqual(new TextEncoder().encode(domain).length);

    const payload = {
      standard: "ton_connect",
      address: "0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd",
      domain,
      timestamp: 1778685374,
      payload: { type: "text", text: "hello world" },
      public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
      signature: "ed25519:not-checked-by-hash-fn",
    } as const;

    // Compute the hash as the buggy implementation does today (UTF-16 length prefix)
    const buggyHash = computeTonConnectHash(payload as any);

    // Compute the "correct" (byte-length-prefixed) hash manually, simulating
    // what the relay/contract (and the real TON Connect wallet signature) would produce.
    const correctHash = computeTonConnectHashCorrectByteLength(payload as any); // helper using domainBytes.length

    expect(buggyHash).not.toEqual(correctHash);
    // This demonstrates computeIntentHash(multiPayload) !== relay-returned intent_hash
    // whenever domain contains multi-byte UTF-8 characters.
  });
});
```
This mocks only the local hash computation (no HTTP needed to demonstrate the divergence at the unit level), and a full integration test would additionally mock `publishIntents`'s HTTP response to return a hash computed with correct UTF-8 byte length, asserting `computeIntentHash(payload) !== mockedIntentHash`.

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L68-76)
```typescript
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

**File:** packages/intents-sdk/src/intents/intent-hash.test.ts (L101-126)
```typescript
async function sim(signedIntent: MultiPayload) {
	const rpc = new providers.JsonRpcProvider({
		url: "https://near-rpc.defuse.org",
	});

	const result = await utils.queryContract({
		nearClient: rpc,
		contractId: "intents.near",
		methodName: "simulate_intents",
		args: { signed: [signedIntent] },
		finality: "optimistic",
		schema: v.object({
			intents_executed: v.array(
				v.object({
					account_id: v.string(),
					intent_hash: v.string(),
					nonce: v.string(),
				}),
			),
			logs: v.array(v.string()),
		}),
	});

	// biome-ignore lint/style/noNonNullAssertion: test expects exactly one result
	return result.intents_executed[0]!.intent_hash;
}
```

**File:** packages/contract-types/src/index.ts (L1130-1133)
```typescript
	/**
	 * dApp domain
	 */
	domain: string;
```
