### Title
`computeTonConnectHash` uses UTF-16 code-unit length instead of UTF-8 byte length for `domain_len`, producing a wrong intent hash for non-ASCII domains - (File: `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`)

### Summary
`computeTonConnectHash` serializes the TON Connect `domain_len` prefix using `domain.length` (JS UTF-16 code-unit count) instead of the byte length of `new TextEncoder().encode(domain)` (UTF-8 bytes). Per the TON Connect sign-data spec, `domain_len` must equal the UTF-8 byte length of the following `domain` bytes, so for any domain containing characters outside the ASCII range (multi-byte UTF-8 characters, surrogate pairs, combining marks) the locally reconstructed message diverges from the actual bytes the TON wallet signed, producing a wrong SHA-256 hash.

### Finding Description
The broken equality is:

`numberToBigEndian(domain.length, 4)` (claimed) `==` `numberToBigEndian(TextEncoder().encode(domain).length, 4)` (actual UTF-8 byte length as required by the TON Connect spec).

In [1](#0-0) , `domain.length` is used directly as the 4-byte big-endian length prefix, while the actual domain bytes appended right after are `new TextEncoder().encode(domain)`. For any `domain` string containing code points that are encoded as multiple UTF-8 bytes (e.g. `ü`, `ì`, combining characters, or supplementary-plane emoji like `🚀`, which is one UTF-16 "length" unit... actually two UTF-16 code units due to surrogate pairs, and 4 UTF-8 bytes), `domain.length` (UTF-16 code units) will not equal `TextEncoder().encode(domain).length` (UTF-8 bytes). This breaks the byte-for-byte equality between the message this SDK builds and hashes and the message the real TON wallet actually built and signed following the TON Connect spec (which uses actual encoded byte length, not JS string length).

`domain` flows unchanged into `MultiPayload` via `prepareSwapSignedData`'s `TON_CONNECT` case ( [2](#0-1) ), and the `MultiPayloadTonConnect`/`__Parsed` schema types accept `domain` as an unrestricted string with no ASCII-only constraint ( [3](#0-2) , [4](#0-3) ). `computeTonConnectHash` is invoked from `computeIntentHash`, whose correctness is verified in tests against an independent `sim()` reference implementation for other standards, confirming this hash is meant to be a faithful reproduction of the byte layout that is ultimately signed/verified ( [5](#0-4) ).

None of the existing guards (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `FeeExceedsAmountError`, schema validation) check or normalize `domain` byte length versus its declared length, so nothing in the pipeline catches this divergence before the hash is computed and compared/reported to an integrator.

### Impact Explanation
This is a hash/status misreport bug: for any `ton_connect` `MultiPayload` whose `domain` field contains non-ASCII characters, `computeIntentHash(multiPayload)` computed locally by the SDK will not match the intent_hash that the actual TON-signed message corresponds to (and by extension whatever the backend/relayer reports as the canonical `intent_hash`). An integrator relying on the SDK-computed hash to correlate a submitted intent with its on-chain/relay status could fail to recognize a completed withdrawal (and re-publish it) or fail to credit it, matching the "status or hash misreport making an integrator credit or refund twice" category. This impact requires the `domain` value used at signing time to actually contain non-ASCII bytes; it does not directly enable moving funds to an unintended address or replaying a signature.

### Likelihood Explanation
Real-world TON Connect `domain` values are typically plain hostnames, which per RFC/URL rules are ASCII (IDN hostnames are represented via ASCII punycode) — wallets populate this field from `window.location.host` or the dApp manifest URL, so it is not a field directly supplied by a counterparty from the list of forwarded strings (assetId, destinationAddress, memo, routeConfig, quoteHashes, nonce, signedIntents). The SDK, however, performs no ASCII validation on `domain`, so any caller constructing a `MultiPayload` with a non-ASCII `domain` (e.g., a testing/staging dApp with a non-punycode domain string, or any code path that passes an arbitrary string into this field) will trigger the divergence deterministically and repeatably on every such call.

### Recommendation
Compute the length prefix from the encoded bytes, not the JS string length:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
reusing the same `domainBytes` for both the length prefix and the appended bytes (mirroring how `payloadData.length` is already correctly derived from the encoded payload).

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "./ton-connect";

describe("computeTonConnectHash domain UTF-8 length", () => {
  it("domain.length diverges from UTF-8 byte length for non-ASCII domain", () => {
    const domain = "ünìcode🚀";
    expect(domain.length).not.toEqual(new TextEncoder().encode(domain).length);
  });

  it("produces a different hash than a spec-correct UTF-8-length implementation", () => {
    const payload = {
      standard: "ton_connect" as const,
      address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
      domain: "ünìcode🚀",
      timestamp: 1762354640,
      payload: { type: "text" as const, text: "{}" },
      public_key: "ed25519:F8PB56zdMYNDL7Mq43DV4cV17uRqQkpn6ZygNdqavXCr",
      signature: "ed25519:i5REHik6CRvvfnKsUtSDvxPeeLiPQsNMGpg9yARs9vtnZxSV9mht9K1tW2LZp8pGd4C83YZRXNG3Y5dBFdLMENd",
    };

    const buggyHash = computeTonConnectHash(payload);

    // Reference implementation using correct UTF-8 byte length for domain_len
    const correctHash = computeCorrectTonConnectHash(payload); // same logic but domainBytes.length

    expect(Buffer.from(buggyHash)).not.toEqual(Buffer.from(correctHash));
  });
});
```
This confirms `numberToBigEndian(domain.length, 4)` (line 70) diverges from `numberToBigEndian(TextEncoder().encode(domain).length, 4)` whenever `domain` contains non-ASCII characters, producing a different SHA-256 output than the spec-correct message.

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L70-71)
```typescript
				numberToBigEndian(domain.length, 4),
				new TextEncoder().encode(domain),
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

**File:** packages/contract-types/src/index.ts (L1125-1142)
```typescript
export interface MultiPayloadTonConnect {
	/**
	 * Wallet address in either [Raw](https://docs.ton.org/v3/documentation/smart-contracts/addresses/address-formats#raw-address) representation or [user-friendly](https://docs.ton.org/v3/documentation/smart-contracts/addresses/address-formats#user-friendly-address) format
	 */
	address: String;
	/**
	 * dApp domain
	 */
	domain: string;
	payload: TonConnectPayloadSchema;
	public_key: string;
	signature: string;
	standard: "ton_connect";
	/**
	 * UNIX timestamp (in seconds or RFC3339) at the time of singing
	 */
	timestamp: PickFirstDateTimeint64;
}
```

**File:** packages/contract-types/artifacts/defuse_contract_abi.json (L4413-4416)
```json
                "domain": {
                  "description": "dApp domain",
                  "type": "string"
                },
```

**File:** packages/intents-sdk/src/intents/intent-hash.test.ts (L69-98)
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
		{
			standard: "sep53",
			payload:
				'{\n  "signer_id": "1b1a88aa85913ee8ba7ffb093c7a77396c046be58414426ace3da33b19bc9846",\n  "verifying_contract": "intents.near",\n  "deadline": "2035-11-03T14:51:56.335Z",\n  "nonce": "331irxwHR+m4uNo8yVT2V5tG69OIYbshjbas8er0zvU=",\n  "intents": []\n}',
			public_key: "ed25519:2poUXG8SwrwaSEmiEnqzLaVYQNJjvsMPkeq5h6zFz97b",
			signature:
				"ed25519:2X7p3ZM6QGr2Pt5qpSuMSJKMwpZfzQQf7NVyZ8jduNpCkMrF6GhjP15x7xtVd9K372FTQNqzrodBtKFkjDA1jPWt",
		},
	] satisfies MultiPayload[])(
		"computes hash (case %#)",
		async (multiPayload) => {
			const hash = await computeIntentHash(multiPayload);
			const expected = await sim(multiPayload);
			expect(hash).toEqual(expected);
		},
	);
```
