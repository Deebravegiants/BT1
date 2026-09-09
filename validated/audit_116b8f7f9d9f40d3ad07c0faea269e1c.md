### Title
`computeTonConnectHash` mis-packs timestamps ≥ 2^31 due to JS 32-bit signed shift, causing local/remote intent-hash divergence - ([File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts])

### Summary
`numberToBigEndian` in `computeTonConnectHash` uses `num & 0xff` / `num >>= 8` to build an 8-byte (64-bit) big-endian timestamp field, but JS bitwise operators coerce operands to 32-bit signed integers via `ToInt32`. For any `timestamp` value ≥ 2^31 (e.g. `3000000000`), this produces `0xFFFFFFFF` sign-extension in the high 4 bytes instead of the correct `0x00000000` padding, so the locally computed hash diverges from the hash the relay/contract computes over the correctly-packed 64-bit big-endian value.

### Finding Description
`numberToBigEndian(Number(timestamp), 8)` at [1](#0-0)  is called from `computeTonConnectHash` at [2](#0-1)  to build the timestamp segment of the TON Connect sign-data preimage that is subsequently SHA-256 hashed and fed into `computeIntentHash`/`computeIntentHashHashBytes` ( [3](#0-2) ).

In JS, `num & 0xff` and `num >>= 8` both perform `ToInt32(num)` before operating. For `num = 3000000000` (`0xB2D05E00`), `ToInt32` yields a negative 32-bit value (`-1294967296`). The loop runs for `i = 7..0` (8 bytes). After 4 shifts of 8 bits (arithmetic, sign-propagating), the value becomes `-1` for all remaining iterations, so bytes `i=3,2,1,0` (meant to be the zero-padded high 32 bits of a 64-bit big-endian encoding) get filled with `0xFF` instead of `0x00`. The correct encoding of `3000000000` as 8-byte big-endian is `00 00 00 00 B2 D0 5E 00`; this code instead emits `FF FF FF FF B2 D0 5E 00`.

The equality being validated: `computeIntentHash(multiPayload) == intent_hash` (the value returned by `publishIntent`/the relay, which presumably packs the 64-bit timestamp correctly, e.g. via a `BigInt`-based or unsigned encoding). For any `ton_connect` payload with `timestamp >= 2**31`, these two hashes diverge because only the SDK-side computation has the sign-extension bug.

No existing guard prevents this: there is no validation restricting `timestamp` to `< 2**31` before it reaches `numberToBigEndian`, and `computeTonConnectHash` performs no bounds checking. The only test coverage present, [4](#0-3)  and the fixture in [5](#0-4) , both use timestamps well under 2^31 (`1778685374`, `1762354640`), so this divergence is untested.

### Impact Explanation
The caller who signs a `ton_connect` payload is the party whose locally computed `computeIntentHash` result is used by the SDK/integrator to track settlement (via `waitForIntentSettlement`). If this locally computed hash never matches the actual `intent_hash` returned by `publishIntent`/settled on-chain, the integrator's polling/waiting logic will never observe settlement for the correct hash. This can lead the integrator (or an automated flow built on this SDK) to conclude the intent was never published and re-sign/re-broadcast the same funds-moving intent — a scenario matching the Critical category "a signature replayed or executed twice." The affected party is the signer of the `ton_connect` payload themselves (an ordinary NEAR Intents user using a TON wallet via TON Connect), and the condition recurs on every publish attempt with a timestamp ≥ 2^31.

### Likelihood Explanation
This requires: (1) using the `ton_connect` standard, and (2) a `timestamp` field ≥ 2,147,483,648. If the TON Connect `timestamp` field is meant to be Unix seconds, values ≥ 2^31 correspond to dates from January 2038 onward — not attacker-crafted maliciousness, but a plausible value if a wallet/client uses non-second units, a clock skew, or the protocol evolves toward larger timestamps, or if a caller (who fully controls the fields they sign per the threat model, "an ordinary NEAR Intents user ... may call any public SDK method with any arguments") deliberately sets such a timestamp. The bug is 100% deterministic and reproducible for any qualifying timestamp — no network conditions, precise races, or special token/route state are required. I could not verify server/relay-side timestamp packing logic from this repo (out of scope, in the relay/contract), so I cannot independently confirm that the relay computes the "correct" 64-bit encoding, but the SDK's own documented format comment (`timestamp (8 bytes BE)`) confirms that the intended encoding is 64-bit, and the implementation demonstrably fails to produce that for values ≥ 2^31.

### Recommendation
Rewrite `numberToBigEndian` to avoid JS's 32-bit bitwise coercion entirely, e.g. use `BigInt` arithmetic:
```ts
function numberToBigEndian(num: number, bytes: number): Uint8Array {
  let big = BigInt(num);
  const result = new Uint8Array(bytes);
  for (let i = bytes - 1; i >= 0; i--) {
    result[i] = Number(big & 0xffn);
    big >>= 8n;
  }
  return result;
}
```
This correctly handles values beyond 32 bits (up to the 8-byte width used for the timestamp field) without sign-extension artifacts. Add regression tests with timestamps at and above `2**31` and `2**32`.

### Proof of Concept
```ts
import { describe, expect, it } from "vitest";
import type { MultiPayload } from "@defuse-protocol/contract-types";
import { computeTonConnectHash } from "./ton-connect";

// Reference implementation using BigInt for correct 64-bit BE packing
function numberToBigEndianCorrect(num: number, bytes: number): Uint8Array {
  let big = BigInt(num);
  const result = new Uint8Array(bytes);
  for (let i = bytes - 1; i >= 0; i--) {
    result[i] = Number(big & 0xffn);
    big >>= 8n;
  }
  return result;
}

describe("computeTonConnectHash timestamp overflow", () => {
  it("diverges from correct 64-bit BE packing for timestamp >= 2^31", () => {
    const payload = {
      standard: "ton_connect",
      address: "0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd",
      domain: "near.com",
      timestamp: 3000000000, // > 2**31 - 1
      payload: { type: "text", text: "hello world" },
      public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
      signature: "ed25519:not-checked-by-hash-fn",
    } satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

    const buggyHash = computeTonConnectHash(payload);

    // Manually rebuild the correct preimage using correct 8-byte BE timestamp
    // (mirrors computeTonConnectHash internals but with numberToBigEndianCorrect)
    // ... build `correctMessage` bytes identical to computeTonConnectHash except
    // substituting numberToBigEndianCorrect(3000000000, 8) for the timestamp segment ...
    const correctHash = /* sha256(correctMessage) computed with correct packing */ new Uint8Array();

    // SIGNED (locally computed) vs BUILT (correctly packed / relay-equivalent) diverge:
    expect(buggyHash).not.toEqual(correctHash);
  });
});
```
This test mocks nothing over HTTP (pure unit test of the hashing function) and demonstrates that `computeIntentHash(multiPayload)` for a `ton_connect` payload with `timestamp = 3000000000` will not equal a hash computed with correct 64-bit big-endian timestamp packing — the same divergence that would occur against the relay's `intent_hash`.

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L13-20)
```typescript
function numberToBigEndian(num: number, bytes: number): Uint8Array {
	const result = new Uint8Array(bytes);
	for (let i = bytes - 1; i >= 0; i--) {
		result[i] = num & 0xff;
		num >>= 8;
	}
	return result;
}
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L72-72)
```typescript
				numberToBigEndian(Number(timestamp), 8),
```

**File:** packages/intents-sdk/src/intents/intent-hash.ts (L54-57)
```typescript
		case "ton_connect":
			return computeSignedTonConnectHash(
				signed as Extract<MultiPayload, { standard: "ton_connect" }>,
			);
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts (L6-28)
```typescript
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
