### Title
`stellarAddressToBytes` omits version-byte validation, allowing address type collision in `authHandleToIntentsUserId` - (File: packages/internal-utils/src/utils/stellarAddressToBytes.ts)

### Summary
`stellarAddressToBytes` decodes a Stellar base32 string, verifies the round-trip base32 encoding and the CRC16-XModem checksum, but never asserts that `payload[0]` equals the expected StrKey version byte (`0x30` for `G...` account IDs) before stripping it and returning the remaining 32 bytes. Any other StrKey type (e.g. muxed account `M...`, contract `C...`) built from the same 32-byte payload with a different, but still valid, version byte and correctly recomputed CRC will decode to the identical byte array.

### Finding Description
The broken equality is: `hex.encode(stellarAddressToBytes(wrongVersionString))` (used inside `authHandleToIntentsUserId`'s `"stellar"` case) `==` `hex.encode(stellarAddressToBytes(victimGAddress))`, for two StrKey strings sharing the same 32-byte payload but different, non-`0x30` version bytes.

In `authIdentity.ts`, the `"stellar"` branch does: [1](#0-0) 
which calls `stellarAddressToBytes` and directly hex-encodes the decoded payload as the `IntentsUserId`, with no check on which StrKey version was used.

In `stellarAddressToBytes.ts`, the only checks performed are the base32 round-trip and the checksum: [2](#0-1) 
`payload[0]` (the version byte) is read into local scope but is never compared against `0x30` (the account ID version byte used by the counterpart encoder `bytesToStellarAddress`): [3](#0-2) 

Because CRC16-XModem is computed over the full payload (version byte + data), an attacker can construct a valid alternate-version StrKey string (e.g. muxed account `M...`, version `0x60`, or contract id `C...`, version `0x02`) around the exact same 32-byte payload as a victim's real `G...` address, recomputing the correct CRC for that new payload. `stellarAddressToBytes` accepts it, strips the version byte, and returns the same 32 raw bytes — so `authHandleToIntentsUserId` produces the exact same hex `IntentsUserId` for the attacker's differently-typed credential as for the victim's real account.

Existing guards do not catch this: there is no version-byte assertion anywhere in `stellarAddressToBytes`, and `authHandleToIntentsUserId` performs no additional type discrimination for the `"stellar"` method before returning the derived ID.

### Impact Explanation
The `IntentsUserId` derived here is the SDK's mapping from an off-chain credential/address to the on-chain principal (`signer_id`) used across intent construction and signature-identity association. A collision lets an attacker-controlled, differently-typed Stellar credential (not the victim's actual `G...` account) derive to the identical `IntentsUserId` as the victim's real account. This matches "signature bound to the wrong ... signer" / intent manipulation impact category, since downstream code trusting this derived ID as the canonical representation of "this Stellar principal" cannot distinguish the wrongly-typed credential from the legitimate one.

### Likelihood Explanation
The attacker only needs to know/observe the victim's real 32-byte Stellar payload (trivially recoverable from any public `G...` address) and compute a correct CRC16-XModem over an alternate version byte — pure client-side arithmetic, no privileged access, repeatable for any target address at negligible cost.

### Recommendation
In `stellarAddressToBytes`, after checksum verification, assert `payload[0] === 0x30` (or accept an explicit expected-version parameter/set of allowed versions for callers that need muxed/contract support) and throw otherwise, mirroring the version byte used by `bytesToStellarAddress`.

### Proof of Concept
```ts
// stellarAddressToBytes.test.ts (illustrative)
import { base32 } from "@scure/base";
import { stellarAddressToBytes } from "./stellarAddressToBytes";
import { authHandleToIntentsUserId } from "./authIdentity";

function encodeWithVersion(payloadData: Uint8Array, version: number) {
  const payload = new Uint8Array(1 + payloadData.length);
  payload[0] = version;
  payload.set(payloadData, 1);
  const checksum = calculateChecksum(payload); // reuse/reimplement CRC16-XModem
  const combined = new Uint8Array(payload.length + checksum.length);
  combined.set(payload);
  combined.set(checksum, payload.length);
  return base32.encode(combined);
}

const rawPayload = /* victim's 32-byte Stellar account payload */;
const victimG = encodeWithVersion(rawPayload, 0x30);   // real G... address
const attackerM = encodeWithVersion(rawPayload, 0x60); // e.g. muxed-account version byte, valid CRC

test("version byte is not validated -> identical IntentsUserId", () => {
  const victimBytes = stellarAddressToBytes(victimG);
  const attackerBytes = stellarAddressToBytes(attackerM);
  expect(attackerBytes).toEqual(victimBytes); // demonstrates the collision

  const victimId = authHandleToIntentsUserId(victimG, "stellar");
  const attackerId = authHandleToIntentsUserId(attackerM, "stellar");
  expect(attackerId).toBe(victimId); // BROKEN: should not be equal for different credential types
});
```

### Citations

**File:** packages/internal-utils/src/utils/authIdentity.ts (L82-85)
```typescript
		case "stellar": {
			const decoded = stellarAddressToBytes(authHandle.identifier);
			return hex.encode(decoded) as IntentsUserId;
		}
```

**File:** packages/internal-utils/src/utils/stellarAddressToBytes.ts (L3-24)
```typescript
export function stellarAddressToBytes(encoded: string): Uint8Array {
	if (typeof encoded !== "string") {
		throw new TypeError("encoded argument must be of type String");
	}

	const decoded = base32.decode(encoded);
	const payload = decoded.slice(0, -2);
	const data = payload.slice(1);
	const checksum = decoded.slice(-2);

	if (encoded !== base32.encode(decoded)) {
		throw new Error("invalid encoded string");
	}

	const expectedChecksum = calculateChecksum(payload);

	if (!verifyChecksum(expectedChecksum, checksum)) {
		throw new Error("invalid checksum");
	}

	return new Uint8Array(data);
}
```

**File:** packages/internal-utils/src/utils/stellarAddressToBytes.ts (L94-107)
```typescript
export function bytesToStellarAddress(data: Uint8Array): string {
	const payload = new Uint8Array(1 + data.length);
	payload[0] = 0x30; // accountId version byte
	payload.set(data, 1);

	const checksum = calculateChecksum(payload);

	// Combine payload and checksum
	const combined = new Uint8Array(payload.length + checksum.length);
	combined.set(payload);
	combined.set(checksum, payload.length);

	return base32.encode(combined);
}
```
