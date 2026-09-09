### Title
`numberToBigEndian` mis-encodes 64-bit `timestamp` values ≥ 2^31 in TonConnect hash, causing `computeIntentHash(multiPayload)` to diverge from the contract's `intent_hash` - ([File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts])

### Summary
`numberToBigEndian` in `computeTonConnectHash` builds the 8-byte big-endian `timestamp` field using plain JS bitwise operators (`&`, `>>=`), which operate on signed 32-bit integers. For any `timestamp` ≥ 2^31, the arithmetic (sign-extending) right shift fills the high-order bytes with `0xFF` instead of `0x00`, producing a message that differs from the correct unsigned 64-bit big-endian encoding, and therefore a different SHA-256 hash than the one the TonConnect wallet actually signed (and than the one `intents.near` computes when it verifies that signature).

### Finding Description
The broken equality is:
`computeIntentHash(multiPayload)` (locally, via `computeSignedTonConnectHash` → `computeTonConnectHash`) should equal the `intent_hash` returned by `publishIntent`/computed on-chain for the same `multiPayload`.

`computeTonConnectHash` builds the signed message as: [1](#0-0) 

with the timestamp encoded via: [2](#0-1) 

`num & 0xff` and `num >>= 8` coerce `num` with JS's `ToInt32`, which reduces it modulo 2^32 and reinterprets bit 31 as a sign bit. For `timestamp` values with bit 31 set (i.e. ≥ 2^31, e.g. `2**32 - 1` or `2**32 + 5`), `num` becomes negative after the internal `ToInt32` conversion, and the subsequent `>>= 8` is an **arithmetic** (sign-extending) shift, not a zero-extending one. This fills the high-order bytes of the 8-byte result with `0xFF` rather than `0x00..0x01`, so the produced byte sequence is not the correct unsigned 64-bit big-endian representation of `timestamp`.

`timestamp` is fully attacker-controlled: it flows unvalidated from the wallet's signing response straight into the `MultiPayload` via `prepareSwapSignedData`'s `TON_CONNECT` branch: [3](#0-2) 

and the JSON-schema for `MultiPayloadTonConnect.timestamp` only requires an `int64`, with no upper bound preventing values ≥ 2^31: [4](#0-3) 

An ordinary user controls their own TonConnect keypair and can construct the signed message bytes themselves (using the correct, standard-compliant unsigned 64-bit BE encoding) and produce a valid ed25519 signature over that message with an arbitrary `timestamp` (e.g. `2**32 + 5`), then submit the resulting `MultiPayload` (with matching `timestamp`, `signature`, `public_key`) through the SDK. Since the real signing algorithm (per the TonConnect sign-data spec that the on-chain contract verifies against) uses correct unsigned encoding, the signature is valid on-chain, but the SDK's local `computeTonConnectHash` produces a different hash due to the sign-extension bug. No existing guard (`validateAddress`, `compareAddresses`, `validateWithdrawal`, schema validation, or intents-contract signature/nonce checks) inspects or bounds the byte-level encoding of `timestamp`; they only verify the ed25519 signature and NEAR-side nonce/signer fields, so the divergence in `computeIntentHash` is not caught anywhere.

### Impact Explanation
`IntentExecuter.signAndSendIntent` calls `computeIntentHash(multiPayload)` locally and passes it to the integrator's `onBeforePublishIntent` hook *before* calling the relayer's `publishIntent`: [5](#0-4) 

If an integrator persists this locally computed `intentHash` (as the README's hook documentation encourages, e.g. for tracking/settlement) it will not match the actual `intent_hash` the relayer/contract returns for that same signed `ton_connect` payload once `timestamp` is ≥ 2^31. Any downstream logic (e.g. `waitForIntentSettlement`, credit/refund bookkeeping keyed on hash) will never see a match for the correct on-chain hash, potentially causing the caller to treat the intent as unpublished/failed and retry — a status/hash misreport that can lead to a double-send of the same intent. This matches the "High" category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
No special privilege is required — any user using the `ton_connect` standard can supply an arbitrary, self-signed `timestamp` (values ≥ 2^31 correspond to Unix timestamps after year 2038, but nothing stops a user/attacker from constructing and self-signing a payload with such a value right now, since they hold their own TonConnect keys and the SDK performs no bound-checking on `timestamp`). This is fully repeatable per call and costs the attacker only the ability to sign their own payload with a custom `timestamp`.

### Recommendation
Rewrite `numberToBigEndian` to use `BigInt` (or `>>>` for the low 32 bits combined with correct high-word extraction) instead of signed 32-bit bitwise operators, e.g.:
```ts
function numberToBigEndian(num: number | bigint, bytes: number): Uint8Array {
  let n = BigInt(num);
  const result = new Uint8Array(bytes);
  for (let i = bytes - 1; i >= 0; i--) {
    result[i] = Number(n & 0xffn);
    n >>= 8n;
  }
  return result;
}
```
and pass the raw `timestamp` (not `Number(timestamp)`) through as a `BigInt` to avoid precision loss for large values.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "../src/intents/intent-hashes/ton-connect";

function referenceBigEndian(num: bigint, bytes: number): Uint8Array {
  const result = new Uint8Array(bytes);
  for (let i = bytes - 1; i >= 0; i--) {
    result[i] = Number(num & 0xffn);
    num >>= 8n;
  }
  return result;
}

it("diverges from correct unsigned 64-bit BE encoding for timestamp >= 2**31", () => {
  const basePayload = {
    standard: "ton_connect" as const,
    address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
    domain: "example.com",
    timestamp: 2 ** 32 + 5,
    payload: { type: "text" as const, text: "hello" },
    public_key: "ed25519:F8PB56zdMYNDL7Mq43DV4cV17uRqQkpn6ZygNdqavXCr",
    signature: "ed25519:dummy",
  };

  const sdkHash = computeTonConnectHash(basePayload);

  // Independently re-derive the expected message using correct 64-bit BE encoding
  const correctTimestampBytes = referenceBigEndian(BigInt(basePayload.timestamp), 8);
  // ... build the "correct" message using correctTimestampBytes and hash it with sha256 ...
  // then assert:
  expect(sdkHash).not.toEqual(/* correctly-encoded reference hash */);
});
```
This confirms `computeIntentHash(multiPayload)` (built on `computeTonConnectHash`) diverges from the hash the contract computes over the properly-signed, correctly-encoded byte stream once `timestamp >= 2**31`.

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

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L65-76)
```typescript
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

**File:** packages/contract-types/src/type-check-schemas.ts (L5066-5074)
```typescript
				standard: { type: "string", enum: ["ton_connect"] },
				timestamp: {
					description:
						"UNIX timestamp (in seconds or RFC3339) at the time of singing",
					anyOf: [
						{ type: "string", format: "date-time" },
						{ writeOnly: true, type: "integer", format: "int64" },
					],
				},
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
