## No vulnerability found for this question.

**Analysis summary:**

The claimed path doesn't hold up. `IntentsSDK.sendSignedIntents` accepts an already-built `MultiPayload[]` array directly — it does not internally call `transformERC191Signature`/`prepareSwapSignedData` at all [1](#0-0) . Those transform functions live in `packages/internal-utils/src/utils/prepareBroadcastRequest.ts` and are invoked by a wallet-integration layer (`prepareSwapSignedData`) before a `MultiPayload` is ever handed to `sendSignedIntents`; they are not on the `IntentsSDK.sendSignedIntents` entrypoint's call graph.

Examining `transformERC191Signature`/`normalizeERC191Signature` themselves for the described TronLink `0x…1b` input: [2](#0-1) 

- `normalizeERC191Signature` reads the last byte as `v`, and `toRecoveryBit` correctly maps `27→0`, `28→1`, and passes through `0`/`1` unchanged, throwing on any other value — so `v=1b` (27) is properly normalized to `0`.
- `transformERC191Signature` strips a leading `0x` (if present) before hex-decoding, so the `0x` prefix is handled correctly and does not leak into the byte array.
- The resulting `r||s||v'` bytes are base58-encoded with a `secp256k1:` prefix; no bytes are dropped, reordered, or substituted — the transform is a pure re-encoding of the same signature bytes the wallet produced.

The `payload` field for the `TRON`/`tip191` case is passed through unchanged (`signature.signedData.message`) [3](#0-2) , so the message that gets hashed/verified is exactly what the user approved. TIP-191/ERC-191 payloads carry no separate `public_key` field — the signer is recovered via `ecrecover` from the signature bytes over the TIP-191-prefixed hash (`computeTip191Hash`, using the Tron-specific `"\x19TRON Signed Message:\n"` prefix) [4](#0-3) , so there is no "wrong public key" field to smuggle in.

Given the transform only re-encodes signature bytes (no reordering/truncation/mis-slicing), the invariant "signature verifies over payload under the caller's key" is preserved, and `sendSignedIntents` doesn't even execute this transform code, there is no divergence supporting a High-severity signature-binding bug here.

### Citations

**File:** packages/intents-sdk/src/sdk.sendSignedIntents.test.ts (L12-18)
```typescript
		const multiPayload: MultiPayload = {
			payload: "test-payload-1",
			signature: "test-signature-1",
			standard: "erc191",
		};

		void sdk.sendSignedIntents({ multiPayloads: [multiPayload] });
```

**File:** packages/internal-utils/src/utils/prepareBroadcastRequest.ts (L85-91)
```typescript
		case "TRON": {
			return {
				standard: "tip191",
				payload: signature.signedData.message,
				signature: transformERC191Signature(signature.signatureData), // TIP-191 is compatible with ERC191
			};
		}
```

**File:** packages/internal-utils/src/utils/prepareBroadcastRequest.ts (L104-134)
```typescript
export function transformERC191Signature(signature: string) {
	const normalizedSignature = normalizeERC191Signature(signature);
	const bytes = hex.decode(
		normalizedSignature.startsWith("0x")
			? normalizedSignature.slice(2)
			: normalizedSignature,
	);
	return `secp256k1:${base58.encode(bytes)}`;
}

export function normalizeERC191Signature(signature: string): string {
	// Get `v` from the last two characters
	let v = Number.parseInt(signature.slice(-2), 16);

	// // Normalize `v` to be either 0 or 1
	v = toRecoveryBit(v);

	// Convert `v` back to hex
	const vHex = v.toString(16).padStart(2, "0");

	// Reconstruct the full signature with the adjusted `v`
	return signature.slice(0, -2) + vHex;
}

// Copy from viem/utils/signature/recoverPublicKey.ts
function toRecoveryBit(yParityOrV: number) {
	if (yParityOrV === 0 || yParityOrV === 1) return yParityOrV;
	if (yParityOrV === 27) return 0;
	if (yParityOrV === 28) return 1;
	throw new Error("Invalid yParityOrV value");
}
```

**File:** packages/intents-sdk/src/intents/intent-hashes/tip191.ts (L1-20)
```typescript
import { keccak_256 } from "@noble/hashes/sha3";
import type { MultiPayload } from "@defuse-protocol/contract-types";

/**
 * Compute the prehash for TIP-191 payload
 * Format: "\x19TRON Signed Message:\n" + length + message
 * Note: Prefix from https://tronweb.network/docu/docs/Sign%20and%20Verify%20Message/
 */
export function computeTip191Prehash(payload: string): Uint8Array {
	const data = new TextEncoder().encode(payload);
	const prefix = new TextEncoder().encode(
		`\x19TRON Signed Message:\n${data.length}`,
	);

	const result = new Uint8Array(prefix.length + data.length);
	result.set(prefix, 0);
	result.set(data, prefix.length);

	return result;
}
```
