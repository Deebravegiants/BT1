This confirms the exploit path: `IntentExecuter.signAndSendIntent` computes `intentHash` via `computeIntentHash(multiPayload)` and hands it to `onBeforePublishIntent` [1](#0-0) , exactly as the question describes for local dedupe/persistence before publishing.

### Title
Wrong length prefix for non-ASCII `domain` in `computeTonConnectHash` causes hash divergence from relayer `intent_hash` - (File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts)

### Summary
`computeTonConnectHash` encodes the TON Connect `AppDomain` field's length prefix using the JavaScript string's UTF-16 code-unit count (`domain.length`) instead of the UTF-8 byte length of the domain, while it appends the actual UTF-8-encoded bytes (`TextEncoder().encode(domain)`). For any `domain` containing non-ASCII characters (e.g. `пример.рф`), these two lengths diverge, producing a length-prefixed field that doesn't match what the TON Connect spec / on-chain `intents.near` verifier (and presumably the Rust reference in `near/intents`) computes, so the locally computed hash never matches the real `intent_hash`.

### Finding Description
The broken equality: `computeIntentHash(mp) == relayer_intent_hash(mp)` for `mp.standard === "ton_connect"` with a non-ASCII `domain`.

In `computeTonConnectHash` [2](#0-1) , the domain segment is built as:
```
numberToBigEndian(domain.length, 4),
new TextEncoder().encode(domain),
```
`domain.length` returns the number of UTF-16 code units in the JS string, which equals the character count for BMP characters — not the number of bytes the following `TextEncoder().encode(domain)` actually produces. Per the TON Connect sign-data spec (referenced in the function's own docstring), `domain_len` must be the byte length of the UTF-8-encoded domain, exactly mirroring how `payload_len` is correctly computed a few lines below via `payloadData.length` (the byte length of the encoded payload) rather than `payloadSchema.text.length`.

For an attacker-controlled `domain` such as `пример.рф` (9 UTF-16 code units, but 17 UTF-8 bytes since each Cyrillic character encodes to 2 bytes), the SDK embeds `9` as the 4-byte big-endian length prefix while still concatenating the full 17-byte UTF-8 domain string. This byte sequence differs from the correctly-formed message (`17` as prefix), so `sha256(message)` — and therefore the resulting `intent_hash` returned by `computeIntentHash` — diverges from whatever value the intents.near contract/relayer derives from the same signed payload using a byte-length-correct implementation.

None of the existing guards catch this: `parseTonAddress`/`tryParseTonAddress` only validate the `address` field [3](#0-2) ; nothing validates or normalizes `domain`. The existing test suite for `computeTonConnectHash` only exercises ASCII domains (`near.com`, `tonconnect-demo-dapp-with-wallet.vercel.app`, `ton-connect.github.io`) [4](#0-3)  and the parity test in `intent-hash.test.ts` likewise only uses an ASCII TON Connect domain [5](#0-4) , so this divergence is untested and unguarded.

### Impact Explanation
`computeIntentHash` is used directly in `IntentExecuter.signAndSendIntent`'s `onBeforePublishIntent` hook to hand the caller the "intent hash" for persistence/dedup purposes before the intent is actually published [1](#0-0) . An integrator that persists this locally-computed hash and later checks intent/settlement status by intent hash (e.g., via `get_status` against the real relayer-derived hash) will never find a match for a TON-Connect-signed intent whose `domain` contains non-ASCII characters, because the locally computed hash is wrong. This can lead the integrator to conclude a withdrawal is "missing" even though it settled, and re-issue/re-sign and re-publish the same withdrawal, resulting in the user being paid twice — a status/hash misreport with double-credit impact, matching the "High" impact category in scope (status or hash misreport causing double credit/refund).

### Likelihood Explanation
The only precondition is that the wallet's TON Connect integration uses (or the dApp is served from) a non-ASCII domain — which is realistic for internationalized/IDN domains (Cyrillic, CJK, etc.) that TON wallets legitimately pass as the `domain` field in `ton_connect` sign-data payloads. No special privileges are needed: any ordinary user signing through a TON wallet with such a domain triggers this on every `ton_connect`-standard intent they sign. It is fully repeatable (deterministic per malformed encoding) and costs the attacker/integrator nothing beyond using an existing non-ASCII domain.

### Recommendation
Compute the domain length prefix from the UTF-8-encoded byte array's length, not the JS string's `.length`, mirroring the fix already used for the payload:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
Add a regression test with a non-ASCII `domain` (e.g., `пример.рф`) comparing against the relayer-derived `intent_hash`, similar to the existing ERC-191 non-ASCII (`café`) parity test.

### Proof of Concept
Vitest test plan (extends `packages/intents-sdk/src/intents/intent-hash.test.ts`):
```ts
it("computes hash for ton_connect with non-ASCII domain (пример.рф)", async () => {
  const multiPayload: MultiPayload = {
    standard: "ton_connect",
    address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
    domain: "пример.рф",
    timestamp: 1762354640,
    payload: {
      type: "text",
      text: '{"signer_id":"...","verifying_contract":"intents.near","deadline":"...","nonce":"...","intents":[]}',
    },
    public_key: "ed25519:...",
    signature: "ed25519:...",
  };

  const localHash = await computeIntentHash(multiPayload);
  const relayerHash = await sim(multiPayload); // via intents.near simulate_intents, as in existing test

  expect(localHash).toEqual(relayerHash); // FAILS with current implementation
});
```
Additionally, a pure unit assertion isolating the root cause without network calls:
```ts
it("domain_len prefix must equal UTF-8 byte length, not UTF-16 length", () => {
  const domain = "пример.рф";
  expect(domain.length).toBe(9);                                   // UTF-16 code units
  expect(new TextEncoder().encode(domain).length).toBe(17);         // actual UTF-8 bytes
  // computeTonConnectHash currently embeds 9 as the length prefix, not 17
});
```

### Citations

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L88-97)
```typescript
		// Call the hook before publishing if provided
		if (this.onBeforePublishIntent) {
			const intentHash = await computeIntentHash(multiPayload);
			await this.onBeforePublishIntent({
				intentHash,
				intentPayload,
				multiPayload,
				relayParams,
			});
		}
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

**File:** packages/intents-sdk/src/lib/ton-address.ts (L107-110)
```typescript
export function tryParseTonAddress(s: string): ParsedTonAddress | null {
	if (s.includes(":")) return parseTonRawAddress(s);
	return parseTonUserFriendlyAddress(s);
}
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts (L1-29)
```typescript
import { describe, expect, it } from "vitest";
import type { MultiPayload } from "@defuse-protocol/contract-types";
import { computeTonConnectHash } from "./ton-connect";

describe("computeTonConnectHash", () => {
	it("produces identical hash whether the address is raw or user-friendly", () => {
		const USER_FRIENDLY = "UQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_YiM";
		const RAW =
			"0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd";
		const payloadWithUserFriendlyAddress = {
			standard: "ton_connect",
			address: USER_FRIENDLY,
			domain: "near.com",
			timestamp: 1778685374,
			payload: { type: "text", text: "hello world" },
			public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
			signature: "ed25519:not-checked-by-hash-fn",
		} satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

		const payloadWithRawAddress = {
			...payloadWithUserFriendlyAddress,
			address: RAW,
		} satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

		expect(computeTonConnectHash(payloadWithUserFriendlyAddress)).toEqual(
			computeTonConnectHash(payloadWithRawAddress),
		);
	});
});
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
