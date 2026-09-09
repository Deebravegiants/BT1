### Title
Case-variant Bitcoin/Litecoin/Dogecoin/Zcash bech32 addresses bypass the "destination matches token address" withdrawal guard - (File: `packages/intents-sdk/src/lib/compareAddresses.ts`)

### Summary
`compareAddresses` is used by every bridge's `validateWithdrawal` to block withdrawals whose `destinationAddress` equals the bridge's own token/contract address (which would otherwise strand funds). For EVM, Aptos/Movement/Sui/Starknet, TON, and Tron chains the function explicitly canonicalizes both sides before comparing so that alternate-but-equivalent textual encodings of the same address are still recognized as equal. For Bitcoin, Bitcoin Cash, Zcash, Dogecoin, Litecoin, Solana, XRPL, Cardano, Aleo and Dash it falls back to a raw `a === b` string comparison with no normalization.

### Finding Description
`compareAddresses` is defined at [1](#0-0) . Its doc comment states its purpose is "to block transfers to the token's own address" [2](#0-1) . For most chains it deliberately normalizes non-canonical representations before comparing — e.g. EVM via `getAddress` checksumming, Aptos/Sui/Starknet hex normalization (`compareHexAddress`/`normalizeHexAddress`), TON via `tryParseTonAddress`, and Tron by decoding both base58check and hex forms to raw bytes [3](#0-2) . However, for the UTXO/other chains it takes the branch:
```
case Chains.Near:
case Chains.Bitcoin:
case Chains.BitcoinCash:
case Chains.Zcash:
case Chains.Dogecoin:
case Chains.Litecoin:
case Chains.Solana:
case Chains.Fogo:
case Chains.XRPL:
case Chains.Cardano:
case Chains.Aleo:
case Chains.Dash:
    return a === b;
``` [4](#0-3) 

Bitcoin (and Litecoin/Dogecoin/Zcash, which share the same address formats) support bech32/bech32m native-segwit addresses (`bc1...`) alongside legacy base58check addresses. Per BIP-173, a bech32 string is valid in either all-lowercase or all-uppercase form (mixed case is invalid, but a fully-uppercased variant of a valid lowercase address decodes to the exact same witness program/bytes). `validateAddress` for Bitcoin uses `validateBtcAddress`, which is built on `@scure/base`'s `bech32`/`bech32m` decoders imported at [5](#0-4)  — these decoders accept both cases per spec, so an uppercase variant of the bridge's own bech32 address passes `validateAddress` format validation just like the canonical lowercase form does.

Because `compareAddresses` for Bitcoin only does `a === b` (raw string equality) rather than decoding to bytes as it does for Tron/TON/Aptos, an attacker who supplies the token's own address in the alternate valid case (e.g., uppercased) will pass `validateAddress` (format is valid) but will NOT trigger `DestinationAddressMatchesTokenAddressError`, because the stored `origin_chain_address`/`destTokenAddress` string (canonical case) will not `===` the attacker-supplied differently-cased string, even though both refer to byte-identical on-chain addresses.

This guard is invoked in every bridge implementation's `validateWithdrawal`, e.g. `PoaBridge.validateWithdrawal` [6](#0-5)  and `OmniBridge.validateWithdrawal` [7](#0-6) , and `DirectBridge.validateWithdrawal` [8](#0-7) , all of which rely on `compareAddresses` returning `true` only when the destination is actually the token's own address.

### Impact Explanation
If an unprivileged user requests a withdrawal with a case-transformed (but format-valid) bech32 encoding of the token's own bridge address as `destinationAddress`, the equality check that is supposed to reject "destination == token address" fails to detect the match. The withdrawal would then be permitted and executed on-chain against a destination that is functionally the bridge/token's own address, resulting in funds delivered to a wrong/self-referential address that (per the code's own rationale for the check) has "no recovery" — matching the "funds delivered to a wrong address/chain/contract with no recovery" High/Critical impact category.

### Likelihood Explanation
Exploitability requires only that the attacker control the `destinationAddress` withdrawal parameter (standard, unprivileged flow) and that the bridge's native BTC/LTC/DOGE/ZEC token/contract address is itself a bech32 address (increasingly common for native segwit BTC-family bridges). The bech32/bech32m case-insensitivity is a standard, well-known property (BIP-173), making this a straightforward, deterministic bypass with no cryptographic or timing requirements — the only uncertainty is whether the specific deployed bridge configuration currently uses a bech32-format `origin_chain_address`/token address for these chains (this repo's tests only exercise legacy base58 BTC addresses, so I could not confirm from the indexed code whether a bech32 token address is actually configured in production).

### Recommendation
Normalize UTXO-chain addresses (Bitcoin, Bitcoin Cash, Litecoin, Dogecoin, Zcash) to their decoded byte form (script/witness program) before comparison in `compareAddresses`, mirroring the approach already used for Tron/TON/Aptos/Sui/Starknet, instead of relying on raw string equality (`a === b`).

### Proof of Concept
1. Identify the bridge's canonical BTC-family destination/own address that `compareAddresses` is meant to block, e.g. `bc1qexampleaddress...` (lowercase bech32).
2. Call the bridge's `validateWithdrawal` (or the SDK's withdrawal creation flow) with `destinationAddress` set to the uppercased form, e.g. `BC1QEXAMPLEADDRESS...`.
3. `validateAddress(destinationAddress, Chains.Bitcoin)` returns `true` (bech32 decoder accepts uppercase per BIP-173).
4. `compareAddresses(tokenAccountAddress, destinationAddress, Chains.Bitcoin)` evaluates `a === b` with `a` in canonical lowercase and `b` in uppercase → returns `false`, so `DestinationAddressMatchesTokenAddressError` is never thrown.
5. The withdrawal proceeds and funds are sent to the address that decodes to the identical witness program as the token's own address, defeating the intended protection.

### Citations

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L7-11)
```typescript
/**
 * Compares two addresses for equality using each chain's canonical form,
 * e.g. to block transfers to the token's own address. Returns false (not
 * throw) on malformed input.
 */
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L12-68)
```typescript
export function compareAddresses(
	a: string,
	b: string,
	blockchain: Chain,
): boolean {
	try {
		switch (blockchain) {
			case Chains.Ethereum:
			case Chains.Optimism:
			case Chains.BNB:
			case Chains.Gnosis:
			case Chains.Polygon:
			case Chains.Monad:
			case Chains.LayerX:
			case Chains.Adi:
			case Chains.Base:
			case Chains.Arbitrum:
			case Chains.Avalanche:
			case Chains.Berachain:
			case Chains.Plasma:
			case Chains.Scroll:
			case Chains.Abstract:
			case Chains.HyperCore:
			case Chains.HyperEvm:
				return getAddress(a) === getAddress(b);
			case Chains.Aptos:
			case Chains.Movement:
			case Chains.Sui:
			case Chains.Starknet:
				return compareHexAddress(a, b);
			case Chains.TON:
				return compareTonAddress(a, b);
			case Chains.Tron:
				return compareTronAddress(a, b);
			case Chains.Stellar:
				return a.toUpperCase() === b.toUpperCase();
			case Chains.Near:
			case Chains.Bitcoin:
			case Chains.BitcoinCash:
			case Chains.Zcash:
			case Chains.Dogecoin:
			case Chains.Litecoin:
			case Chains.Solana:
			case Chains.Fogo:
			case Chains.XRPL:
			case Chains.Cardano:
			case Chains.Aleo:
			case Chains.Dash:
				return a === b;
			default:
				blockchain satisfies never;
				return false;
		}
	} catch {
		return false;
	}
}
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L70-150)
```typescript
// Aptos/Movement/Sui/Starknet addresses are hex field elements: case is not
// significant, and both zero-padded (0x000...01) and short (0x1) forms refer
// to the same address.
function compareHexAddress(a: string, b: string): boolean {
	const normalizedA = normalizeHexAddress(a);
	const normalizedB = normalizeHexAddress(b);
	if (normalizedA === null || normalizedB === null) return false;
	return normalizedA === normalizedB;
}

function normalizeHexAddress(address: string): string | null {
	const withoutPrefix = address.toLowerCase().startsWith("0x")
		? address.slice(2)
		: address;
	if (withoutPrefix.length === 0 || !/^[0-9a-fA-F]+$/.test(withoutPrefix)) {
		return null;
	}
	const withoutLeadingZeros = withoutPrefix.replace(/^0+/, "");
	return withoutLeadingZeros.toLowerCase() || "0";
}

// TON accounts have multiple valid textual forms (raw "0:hex", friendly
// base64/base64url, bounceable/non-bounceable) that all refer to the same
// (workchain, address) pair.
function compareTonAddress(a: string, b: string): boolean {
	const parsedA = tryParseTonAddress(a);
	const parsedB = tryParseTonAddress(b);
	if (parsedA === null || parsedB === null) return false;

	return (
		parsedA.workchainId === parsedB.workchainId &&
		bytesEqual(parsedA.address, parsedB.address)
	);
}

// Tron addresses are represented either as base58check (T...) or as hex
// (41...); both encode the same 21-byte version+hash160 payload.
function compareTronAddress(a: string, b: string): boolean {
	const payloadA = decodeTronAddress(a);
	const payloadB = decodeTronAddress(b);
	if (payloadA === null || payloadB === null) return false;

	return bytesEqual(payloadA, payloadB);
}

function decodeTronAddress(address: string): Uint8Array | null {
	const base58Payload = decodeTronBase58Address(address);
	if (base58Payload !== null) return base58Payload;

	return decodeTronHexAddress(address);
}

function decodeTronBase58Address(address: string): Uint8Array | null {
	try {
		const decoded = base58.decode(address);
		if (decoded.length !== 25) return null;

		// version (1) + hash160 (20) + checksum (4)
		const payload = decoded.subarray(0, 21);
		const checksum = decoded.subarray(21, 25);
		const expectedChecksum = sha256(sha256(payload)).subarray(0, 4);
		for (let i = 0; i < 4; i++) {
			if (checksum[i] !== expectedChecksum[i]) return null;
		}

		return payload[0] === 0x41 ? payload : null;
	} catch {
		return null;
	}
}

function decodeTronHexAddress(address: string): Uint8Array | null {
	try {
		const decoded = hex.decode(address);
		if (decoded.length !== 21) return null;
		return decoded[0] === 0x41 ? decoded : null;
	} catch {
		return null;
	}
}

```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L1-2)
```typescript
import { sha256 } from "@noble/hashes/sha2";
import { base58, bech32m, hex, bech32 } from "@scure/base";
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L207-219)
```typescript
		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L384-396)
```typescript
		const destTokenAddress = getAddress(destTokenOmniAddress);
		if (
			compareAddresses(
				destTokenAddress,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				destTokenAddress,
				args.assetId,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L171-178)
```typescript
		if (
			compareAddresses(tokenAccountId, args.destinationAddress, Chains.Near)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenAccountId,
				args.assetId,
			);
		}
```
