### Title
`computeTonConnectHash` diverges from a 64-bit big-endian encoding for `timestamp` values ≥ 2^31 due to JS 32-bit signed bitwise semantics - ([File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts])

### Summary
`numberToBigEndian(Number(timestamp), 8)` in `computeTonConnectHash` builds an 8-byte big-endian buffer using a `for` loop with `num & 0xff` and `num >>= 8`, but JS's `&` and `>>` operators coerce operands via `ToInt32` (32-bit) and `>>` is an arithmetic (sign-propagating) shift. For `timestamp` values whose low-32-bit representation has the sign bit set (i.e. `timestamp mod 2^32 >= 2^31`), the shift sign-extends with `1`s instead of `0`s, and for `timestamp >= 2^32` the leading bits are silently truncated. Either way the resulting 8-byte buffer differs from the correct unsigned 64-bit big-endian encoding, producing a different SHA-256 hash than a spec-compliant TON Connect verifier would compute for the same numeric `timestamp`.

### Finding Description
The broken equality is: `computeIntentHash(multiPayload)` (client-side, via `computeTonConnectHash`, at [1](#0-0) ) must equal the `intent_hash` a spec-compliant TON Connect verifier (and thus the on-chain/relayer settlement) computes for the same payload.

Root cause, traced in `numberToBigEndian`: [2](#0-1) 
Each loop iteration does `result[i] = num & 0xff; num >>= 8;`. Both `&` and `>>` force `num` through `ToInt32`, and `>>` is arithmetic (sign-extending), not logical (`>>>`). Concretely:

- For `timestamp = 3_000_000_000` (which is `> 2^31` but `< 2^32`): `ToInt32(3_000_000_000) = -1_294_967_296` (negative). Tracing the loop byte-by-byte, the low 4 bytes correctly resolve to `B2 D0 5E 00`, but once the shifted value itself becomes negative (`num` reaches `-1` after enough right-shifts), the sign-extension fills the remaining high-order bytes with `0xFF` instead of `0x00`. The function outputs `FF FF FF FF B2 D0 5E 00` instead of the correct unsigned 64-bit BE `00 00 00 00 B2 D0 5E 00` — a 4-byte divergence that completely changes the SHA-256 input and thus the hash.
- For `timestamp = 5_000_000_000` (`> 2^32`): `ToInt32` truncates the value modulo 2^32 before any byte extraction begins, so the byte that should carry the overflow (`0x01` at position 3 in `00 00 00 01 2A 05 F2 00`) is silently dropped, yielding `00 00 00 00 2A 05 F2 00` instead.

Both cases are the same root cause: `numberToBigEndian` is not a correct unsigned 64-bit big-endian encoder — it is limited by JS 32-bit bitwise-operator semantics.

`timestamp` is caller-controlled: the `MultiPayloadTonConnect` type declares `timestamp: PickFirstDateTimeint64` (`string | number`), and `computeTonConnectHash` does `Number(timestamp)` with no range check or clamping [3](#0-2) . Nothing in `prepareBroadcastRequest.ts` clamps it either — it passes `signature.signatureData.timestamp` straight through [4](#0-3) . Since the SDK does not ship its own TON Connect signer (per its README, `ton_connect` signing is "available on the protocol level, but not included to SDK"), an application/integrator composes and hashes `ton_connect` `MultiPayload`s itself (e.g. via `signAndSendIntent`'s `signedIntents`/custom `intentPayloadFactory` path, or by calling `computeIntentHash` directly), so any counterparty-influenced or attacker-influenced timestamp value flows unclamped into `computeTonConnectHash`.

Existing guards do not catch this: there is no `assert`, schema-level numeric-range check, or clamp on `timestamp` visible in `ton-connect.ts`, `prepareBroadcastRequest.ts`, or the `IntentExecuter`/`intent-hash.ts` call chain (`computeIntentHash` → `computeIntentHashHashBytes` → `computeSignedTonConnectHash` → `computeTonConnectHash`) [5](#0-4) .

### Impact Explanation
`computeIntentHash` is used by `IntentExecuter.signAndSendIntent` to compute the hash passed into `onBeforePublishIntent` *before* the intent is actually published to the relayer [6](#0-5) . If an integrator persists this locally-computed hash for tracking/idempotency and the real on-chain settlement hash (computed correctly per the TON Connect spec) differs because of a large `timestamp`, the integrator's stored hash will never match the settled intent. This is a status/hash misreport that can cause the integrator to treat a funded, settled withdrawal as unsettled and duplicate/resend it — matching the High/Critical "status or hash misreport making an integrator credit or refund twice" category. It is repeatable on every call where the `ton_connect` payload's `timestamp` falls in the affected ranges (`>= 2^31`, or the `2^31–2^32` sign-extension sub-case specifically).

### Likelihood Explanation
Preconditions: the payload standard must be `ton_connect` and its `timestamp` field must be attacker/counterparty-influenced and reach a value `>= 2^31` (as raw seconds, this is year ~2038-plus, but nothing in the code prevents an out-of-range or malformed value from being supplied directly since it's simply `Number(timestamp)` with no bound check). Attacker cost is a single out-of-range numeric field in a payload they control or influence (e.g., a counterparty-forwarded string as noted in scope). Feasibility is high given no validation exists in the traced path; however, exploitation requires the integrator to actually rely on the locally computed hash to match on-chain settlement (a realistic but integrator-specific usage pattern that the codebase's own README documents as a use case for `onBeforePublishIntent`).

### Recommendation
Rewrite `numberToBigEndian` to correctly encode 64-bit unsigned big-endian values without relying on JS 32-bit bitwise operators — e.g. use `BigInt` throughout (`BigInt(timestamp)` and `>>` on `BigInt`, or `DataView.setBigUint64`) so the encoding is correct for the full unsigned 64-bit range, matching what a spec-compliant TON Connect verifier computes.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "./ton-connect";

// Reference correct 64-bit BE encoder using BigInt (spec-correct)
function correctBigEndian64(num: bigint): Uint8Array {
  const result = new Uint8Array(8);
  let n = num;
  for (let i = 7; i >= 0; i--) {
    result[i] = Number(n & 0xffn);
    n >>= 8n;
  }
  return result;
}

it("diverges from correct 64-bit BE encoding for timestamp in [2^31, 2^32)", () => {
  const basePayload = {
    standard: "ton_connect" as const,
    address: "0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd",
    domain: "near.com",
    payload: { type: "text" as const, text: "hello world" },
    public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
    signature: "ed25519:not-checked-by-hash-fn",
  };

  const timestamp = 3_000_000_000;
  const brokenHash = computeTonConnectHash({ ...basePayload, timestamp });

  // Manually build the spec-correct message using correctBigEndian64 for the timestamp
  // and compare against computeTonConnectHash's output — they must differ.
  expect(brokenHash).not.toEqual(
    /* hash built with correctBigEndian64(BigInt(timestamp)) substituted for the timestamp bytes */
  );
});
```
(The reference test in the repo, `ton-connect.test.ts`, only checks address-encoding equivalence and does not cover large `timestamp` values, so this divergence is not currently caught by existing tests.)

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

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L50-72)
```typescript
export function computeTonConnectHash(
	payload: Extract<MultiPayload, { standard: "ton_connect" }>,
): Uint8Array {
	const { address, domain, timestamp, payload: payloadSchema } = payload;

	// Parse address if it's a string
	const parsedAddress = parseTonAddress(address);

	const schemaType = payloadSchema.type;
	switch (schemaType) {
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

**File:** packages/intents-sdk/src/intents/intent-hash.ts (L54-57)
```typescript
		case "ton_connect":
			return computeSignedTonConnectHash(
				signed as Extract<MultiPayload, { standard: "ton_connect" }>,
			);
```

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
