No vulnerability found for this question.

**Reasoning:**

The premise requires two *different* unprivileged users to end up sharing the same `IntentsUserId`, and then whichever "signs first" can move the other's funds. Tracing the actual verification path shows this can't happen with distinct users. [1](#0-0) and [2](#0-1)  do produce identical `IntentsUserId` hex strings when `base58.decode(solanaIdentifier)` equals `stellarAddressToBytes(stellarIdentifier)` — both a Solana address and a Stellar `StrKey` account ID are just different textual encodings of the same raw 32-byte ed25519 public key (Solana: base58 of raw key; Stellar: base32 of `version_byte + raw_key + checksum`, stripped by [3](#0-2) ). This equality is expected and by design, not a flaw.

Critically, `prepareSwapSignedData` in [4](#0-3)  and [5](#0-4)  construct the `public_key` field submitted to the intents contract for the "SOLANA" and "STELLAR_SEP53" signature standards using that exact same raw ed25519 key (`ed25519:${userInfo.userAddress}` for Solana, `ed25519:${base58.encode(stellarAddressToBytes(userInfo.userAddress))}` for Stellar). The contract's own signature verification (not part of this repo, out of scope per the rules) validates the ed25519 signature against that literal public key.

Consequently, whoever can produce a valid signature that the contract accepts for that `signer_id` must possess the private key corresponding to those exact 32 raw bytes — and that is definitionally a single entity, not "two different users." A second party who merely knows the public address (which is public information) and re-encodes it into a Stellar `StrKey` string cannot produce a valid ed25519 signature without the private key. So there is no scenario where an unprivileged user without the key can hijack funds belonging to the actual key holder: the "collision" only ever refers to one cryptographic identity expressed under two chain-label conventions, and authorization is still gated by possession of the single underlying private key, which the intents contract's signature check enforces.

### Citations

**File:** packages/internal-utils/src/utils/authIdentity.ts (L67-68)
```typescript
		case "solana":
			return hex.encode(base58.decode(authHandle.identifier)) as IntentsUserId;
```

**File:** packages/internal-utils/src/utils/authIdentity.ts (L82-85)
```typescript
		case "stellar": {
			const decoded = stellarAddressToBytes(authHandle.identifier);
			return hex.encode(decoded) as IntentsUserId;
		}
```

**File:** packages/internal-utils/src/utils/stellarAddressToBytes.ts (L8-11)
```typescript
	const decoded = base32.decode(encoded);
	const payload = decoded.slice(0, -2);
	const data = payload.slice(1);
	const checksum = decoded.slice(-2);
```

**File:** packages/internal-utils/src/utils/prepareBroadcastRequest.ts (L40-51)
```typescript
		case "SOLANA":
			assert(
				userInfo.userChainType === "solana",
				"User chain and signature chain must match",
			);
			return {
				standard: "raw_ed25519",
				payload: new TextDecoder().decode(signature.signedData.message),
				// Solana address is its public key encoded in base58
				public_key: `ed25519:${userInfo.userAddress}`,
				signature: transformED25519Signature(signature.signatureData),
			};
```

**File:** packages/internal-utils/src/utils/prepareBroadcastRequest.ts (L69-83)
```typescript
		case "STELLAR_SEP53": {
			assert(
				userInfo.userChainType === "stellar",
				"User chain and signature chain must match",
			);
			return {
				standard: "sep53",
				payload: signature.signedData.message,
				// We should encode the Stellar address to base58
				public_key: `ed25519:${base58.encode(
					stellarAddressToBytes(userInfo.userAddress),
				)}`,
				signature: transformED25519Signature(signature.signatureData),
			};
		}
```
