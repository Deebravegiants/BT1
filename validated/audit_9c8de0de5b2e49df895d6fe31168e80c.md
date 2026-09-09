No vulnerability found for this question.

I reviewed the in-scope signature/checksum verification code (`packages/internal-utils/src/utils/webAuthn.ts`, `packages/internal-utils/src/utils/stellarAddressToBytes.ts`, `packages/intents-sdk/src/lib/compareAddresses.ts`, `packages/intents-sdk/src/lib/validateAddress.ts`, `packages/contract-types/src/standard-schema.ts`) looking for the specific bug class from the report — a MAC/tag/signature check that omits a minimum-length enforcement, allowing a truncated tag/signature to pass verification with non-negligible probability.

None of the equality checks in scope exhibit this pattern:
- `bytesEqual` in `compareAddresses.ts` explicitly checks `a.length !== b.length` before comparing bytes [1](#0-0) .
- `verifyChecksum` in `stellarAddressToBytes.ts` checks `expected.length !== actual.length` before the byte loop [2](#0-1) .
- Public key length is strictly validated (64 bytes for p256, 32 for ed25519) in `parsePublicKey` before any signature verification occurs [3](#0-2) .
- Signature verification itself delegates to `crypto.subtle.verify` (WebCrypto ECDSA) and `tweetnacl.sign.detached.verify`, both of which enforce fixed-length signatures internally rather than accepting arbitrary/truncated tag lengths [4](#0-3) .
- Address checksum validators (`validateDashAddress`, `decodeTronBase58Address`) fix the checksum slice size from a length-checked decoded buffer, so there is no attacker-controlled short-tag path [5](#0-4) .

No reachable code path in the in-scope directories accepts a shortened/variable-length authentication tag or signature in place of the full-length value, so there is no analog to CVE-2018-10903 that breaks an equality relevant to fund custody, signature binding, or delivery in this repo.

### Citations

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L151-156)
```typescript
function bytesEqual(a: Uint8Array, b: Uint8Array): boolean {
	if (a.length !== b.length) return false;
	for (let i = 0; i < a.length; i++) {
		if (a[i] !== b[i]) return false;
	}
	return true;
```

**File:** packages/internal-utils/src/utils/stellarAddressToBytes.ts (L27-37)
```typescript
function verifyChecksum(expected: Uint8Array, actual: Uint8Array): boolean {
	if (expected.length !== actual.length) {
		return false;
	}
	for (let i = 0; i < expected.length; i++) {
		if (expected[i] !== actual[i]) {
			return false;
		}
	}
	return true;
}
```

**File:** packages/internal-utils/src/utils/webAuthn.ts (L8-51)
```typescript
export function parsePublicKey(formattedPublicKey: string): CredentialKey {
	const curveType = getCurveType(formattedPublicKey);

	switch (curveType) {
		case "p256": {
			let publicKey: Uint8Array;

			try {
				publicKey = base58.decode(formattedPublicKey.slice(5));
			} catch (err) {
				throw new Error("Public key is not base58 encoded", { cause: err });
			}

			if (publicKey.length !== 64) {
				throw new Error(
					`Invalid public key size for P-256 curve, it must be 64 bytes, but got ${publicKey.length} bytes`,
				);
			}

			return { curveType, publicKey };
		}

		case "ed25519": {
			let publicKey: Uint8Array;

			try {
				publicKey = base58.decode(formattedPublicKey.slice(8));
			} catch (err) {
				throw new Error("Public key is not base58 encoded", { cause: err });
			}

			if (publicKey.length !== 32) {
				throw new Error(
					`Invalid public key size for Ed25519 curve, it must be 32 bytes, but got ${publicKey.length} bytes`,
				);
			}

			return { curveType, publicKey };
		}

		default:
			throw new Error(`Unsupported curve type ${curveType}`);
	}
}
```

**File:** packages/internal-utils/src/utils/webAuthn.ts (L109-137)
```typescript
	switch (curveType) {
		case "p256": {
			const key = await crypto.subtle.importKey(
				"raw",
				publicKeyWebCryptoAPI,
				{ name: "ECDSA", namedCurve: "P-256" },
				true,
				["verify"],
			);
			return crypto.subtle.verify(
				{ name: "ECDSA", hash: { name: "SHA-256" } },
				key,
				signature,
				signedBytes,
			);
		}

		case "ed25519": {
			return tweetnacl.sign.detached.verify(
				signedBytes,
				signature,
				publicKeyWebCryptoAPI,
			);
		}

		default:
			curveType satisfies never;
			throw new Error(`Unsupported curve type ${curveType}`);
	}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L801-831)
```typescript
export function validateDashAddress(address: string): boolean {
	try {
		const decoded: Uint8Array = base58.decode(address);

		// version (1) + payload (20) + checksum (4)
		if (decoded.length !== 25) return false;

		const version = decoded[0];
		if (
			version !== 0x4c && // P2PKH
			version !== 0x10 // P2SH
		) {
			return false;
		}

		const payload = decoded.subarray(0, 21);
		const checksum = decoded.subarray(21, 25);

		const hash1 = sha256(payload);
		const hash2 = sha256(hash1);
		const expectedChecksum = hash2.subarray(0, 4);

		for (let i = 0; i < 4; i++) {
			if (checksum[i] !== expectedChecksum[i]) return false;
		}

		return true;
	} catch {
		return false;
	}
}
```
