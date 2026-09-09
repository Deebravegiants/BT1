[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/sep53.ts (L1-38)
```typescript
import { sha256 } from "@noble/hashes/sha2";
import type { MultiPayload } from "@defuse-protocol/contract-types";
import { utils } from "@defuse-protocol/internal-utils";

/**
 * Compute the prehash for SEP-53 payload
 * Format: "Stellar Signed Message:\n" + message
 */
export function computeSep53Prehash(payload: string): Uint8Array {
	const prefix = new TextEncoder().encode("Stellar Signed Message:\n");
	const data = new TextEncoder().encode(payload);

	return utils.concatUint8Arrays([prefix, data]);
}

/**
 * Compute the SHA-256 hash of a SEP-53 payload
 * This is the hash that should be signed
 *
 * @param payload - The message string to hash
 * @returns 32-byte hash as Uint8Array
 */
export function computeSep53Hash(payload: string): Uint8Array {
	const prehash = computeSep53Prehash(payload);
	return sha256(prehash);
}

/**
 * Compute hash from a signed SEP-53 payload
 *
 * @param signedPayload - The signed SEP-53 payload
 * @returns 32-byte hash as Uint8Array
 */
export function computeSignedSep53Hash(
	signedPayload: Extract<MultiPayload, { standard: "sep53" }>,
): Uint8Array {
	return computeSep53Hash(signedPayload.payload);
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

**File:** packages/internal-utils/src/types/walletMessage.ts (L11-15)
```typescript
export type ERC191SignatureData = {
	type: "ERC191";
	signatureData: string;
	signedData: ERC191Message;
};
```

**File:** packages/internal-utils/src/types/walletMessage.ts (L107-111)
```typescript
export type TronSignatureData = {
	type: "TRON";
	signatureData: string;
	signedData: TronMessage;
};
```

**File:** packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-viem.ts (L27-39)
```typescript
	async signRaw(input: Erc191RawPayload): Promise<MultiPayloadErc191> {
		const signature = await this.config.signer.signMessage?.({
			message: input.payload,
		});
		if (signature == null) {
			throw new Error("No signature is returned");
		}

		return {
			standard: "erc191",
			payload: input.payload,
			signature: utils.transformERC191Signature(signature),
		};
```
