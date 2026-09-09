### Title
Zcash destination-address self-transfer guard bypassed via alternate encoding (TEX / Unified Address) - (File: `packages/intents-sdk/src/lib/compareAddresses.ts`)

### Finding Description
The invariant this check is supposed to enforce is: for the OmniBridge Zcash route, `compareAddresses(destTokenAddress, destinationAddress, 'bip122:00040fe8ec8471911baa1db1266ea15d')` must be `true` whenever `destinationAddress` and `destTokenAddress` denote the same Zcash account, so that `validateWithdrawal` can throw `DestinationAddressMatchesTokenAddressError` and block the self-send.

In `OmniBridge.validateWithdrawal` (`packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts:384-396`), `destTokenAddress` is derived by calling `getAddress(destTokenOmniAddress)` on the token's own `OmniAddress` on the Zcash chain (e.g. a transparent `t1…`/`t3…` address, since Zcash tokens are represented via a transparent receiving address). This value is compared against the attacker-controlled `args.destinationAddress` using `compareAddresses`.

`compareAddresses` (`packages/intents-sdk/src/lib/compareAddresses.ts:48-60`) handles `Chains.Zcash` with a plain `a === b` raw string comparison — no chain-specific canonicalisation, unlike EVM (`getAddress`), Aptos/Sui/Starknet (`compareHexAddress`), TON (`compareTonAddress`), or Tron (`compareTronAddress`).

But `validateAddress` for Zcash (`packages/intents-sdk/src/lib/validateAddress.ts:344-371`, `validateZcashAddress`) accepts three structurally different, but semantically overlapping, textual forms:
- Transparent `t1`/`t3` (base58check, hash160 payload)
- `tex1…` (ZIP-320 TEX address — bech32m encoding of the *same* 20-byte hash160 as a P2PKH transparent address, defined specifically as an alternate encoding for an already-existing transparent P2PKH address)
- `u1…` Unified Addresses (ZIP-316), which can wrap a P2PKH/P2SH receiver whose payload is again the same hash160/hash used by a `t1`/`t3` address (`validateZcashUnifiedAddress` in `packages/intents-sdk/src/lib/zcash-unified-address.ts`)

Because `validateAddress` accepts all of these forms but `compareAddresses` for Zcash only compares raw strings, an attacker can submit `destinationAddress` as a `tex1…` (or `u1…`) encoding of the exact same hash160 underlying the token contract's `t1…`/`t3…` address. `validateAddress` passes (it is a well-formed TEX/UA address), `compareAddresses(destTokenAddress, destinationAddress, Zcash)` returns `false` because the strings differ even though they resolve to the same transparent receiver, so `DestinationAddressMatchesTokenAddressError` is never thrown. `validateWithdrawal` proceeds, and `deriveOmniWithdrawIntentParams`/`createWithdrawIntentsPrimitive` build a withdrawal that sends the tokens to the token contract's own transparent address, encoded differently, where they are unrecoverable.

None of the other guards in `validateWithdrawal` catch this: `validateAddress` only checks format, not aliasing; the storage-balance, decimals, and fee assertions are unrelated to destination correctness; and there is no on-chain Zcash contract semantics to prevent sending funds to a "dead" transparent address once the SDK signs the intent.

### Impact Explanation
This causes an ordinary user's own withdrawal-intent construction to route the withdrawn tokens to the bridged token's own address on Zcash — funds sent to a contract/account with no way to recover them, matching the Critical category "funds delivered to a wrong address/chain/contract with no recovery." This is triggered purely by the caller choosing an alternate (but valid) textual encoding of the token's known address; no privileged access or malicious external party is needed, and is repeatable for any Zcash-routed OmniBridge withdrawal.

### Likelihood Explanation
Precondition: the target NEP-141 token must have a bridged deployment on Zcash (`destTokenOmniAddress` resolves), and its canonical `OmniAddress` there is a transparent `t1`/`t3` receiver (typical for a chain without smart contracts). The attacker only needs to compute the TEX (ZIP-320) or Unified-Address encoding of that same hash160/payload — trivial, deterministic, off-chain computation from a publicly-known token address. Attacker cost is negligible and the bug is deterministic/repeatable on every call with the crafted destination.

### Recommendation
In `compareAddresses`, add a Zcash-specific canonicalisation branch instead of `a === b`: decode `t1`/`t3` to raw hash160+version, decode `tex1` via bech32m to the same 20-byte hash and treat it as equivalent to the P2PKH transparent form, and decode `u1…` Unified Addresses to extract each receiver (P2PKH/P2SH/Orchard) and compare the underlying receiver bytes against the transparent form. Only return `true`/`false` based on canonical payload equality, mirroring the approach already used for TON and Tron in the same file.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/compareAddresses.spec.ts (illustrative)
import { compareAddresses } from "./compareAddresses";
import { Chains } from "./caip2";

it("BUG: tex1 encoding of the token's own transparent address is not recognised as equal", () => {
  const tokenTransparentAddress = "t1KktQvSFwFcpgU4wZ9Jg9UgN9dJVXfCJ4t"; // destTokenAddress from getAddress(destTokenOmniAddress)
  // tex1... encodes the SAME 20-byte hash160 as the t1 address above (ZIP-320)
  const texEncodingOfSameHash = "tex1<bech32m of same hash160>";

  // Precondition: validateAddress accepts the TEX form (format-only check)
  // expect(validateAddress(texEncodingOfSameHash, Chains.Zcash)).toBe(true);

  // Broken invariant: same account, but compareAddresses says "different"
  expect(
    compareAddresses(tokenTransparentAddress, texEncodingOfSameHash, Chains.Zcash),
  ).toBe(true); // FAILS today — returns false due to raw string comparison
});
```
This demonstrates that `validateWithdrawal` in `omni-bridge.ts` would not throw `DestinationAddressMatchesTokenAddressError` for a `destinationAddress` that is a different textual encoding of the token's own Zcash address. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L48-60)
```typescript
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
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L344-371)
```typescript
function validateZcashAddress(address: string) {
	// Transparent address validation
	if (address.startsWith("t1") || address.startsWith("t3")) {
		// t1 for P2PKH addresses, t3 for P2SH addresses
		return /^t[13][a-km-zA-HJ-NP-Z1-9]{33}$/.test(address);
	}

	// TEX address validation
	const expectedHrp = "tex";
	if (address.startsWith(`${expectedHrp}1`)) {
		try {
			const decoded = bech32m.decodeToBytes(address);
			if (decoded.prefix !== expectedHrp) {
				return false;
			}
			return decoded.bytes.length === 20;
		} catch {
			return false;
		}
	}

	// Unified address validation
	if (address.startsWith("u1")) {
		return validateZcashUnifiedAddress(address);
	}

	return false;
}
```

**File:** packages/intents-sdk/src/lib/zcash-unified-address.ts (L68-151)
```typescript
export function validateZcashUnifiedAddress(address: string): boolean {
	try {
		const decoded = bech32m.decodeToBytes(address);
		if (decoded.prefix !== ZCASH_UA_MAINNET_HRP) return false;

		const payload = decoded.bytes;
		if (payload.length < F4_MIN_LEN || payload.length > F4_MAX_LEN) {
			return false;
		}

		const unjumbled = f4JumbleInverse(payload);

		// Padding is the last 16 bytes: HRP followed by zeros.
		const paddingLen = 16;
		if (unjumbled.length <= paddingLen) return false;
		const paddingStart = unjumbled.length - paddingLen;

		if (unjumbled[paddingStart] !== ZCASH_UA_MAINNET_HRP.charCodeAt(0)) {
			return false;
		}
		for (let i = paddingStart + 1; i < unjumbled.length; i++) {
			if (unjumbled[i] !== 0) return false;
		}

		let offset = 0;
		let lastTypecode = -1;
		let hasOrchardOrTransparent = false;
		let hasP2pkh = false;
		let hasP2sh = false;

		while (offset < paddingStart) {
			const typeRead = readCompactSize(unjumbled, offset, paddingStart);
			if (typeRead === null) return false;
			const typecode = typeRead.value;
			offset = typeRead.next;

			if (typecode > MAX_TYPECODE_OR_LENGTH) return false;

			// ZIP 316: typecodes must be strictly ascending (this also rejects duplicates).
			if (typecode <= lastTypecode) return false;
			lastTypecode = typecode;

			const lenRead = readCompactSize(unjumbled, offset, paddingStart);
			if (lenRead === null) return false;
			const len = lenRead.value;
			offset = lenRead.next;

			if (len === 0 || len > MAX_TYPECODE_OR_LENGTH) return false;
			if (offset + len > paddingStart) return false;

			const expectedLen = KNOWN_RECEIVER_LENGTH[typecode];
			if (expectedLen !== undefined && len !== expectedLen) return false;

			if (
				expectedLen === undefined &&
				typecode >= MUST_UNDERSTAND_METADATA_MIN &&
				typecode <= MUST_UNDERSTAND_METADATA_MAX
			) {
				return false;
			}

			if (typecode === RECEIVER_TYPECODE.P2PKH) hasP2pkh = true;
			if (typecode === RECEIVER_TYPECODE.P2SH) hasP2sh = true;
			if (
				typecode === RECEIVER_TYPECODE.P2PKH ||
				typecode === RECEIVER_TYPECODE.P2SH ||
				typecode === RECEIVER_TYPECODE.ORCHARD
			) {
				hasOrchardOrTransparent = true;
			}

			offset += len;
		}

		if (offset !== paddingStart) return false;

		// ZIP 316: a UA MUST NOT include both P2SH and P2PKH receivers.
		if (hasP2pkh && hasP2sh) return false;

		return hasOrchardOrTransparent;
	} catch {
		return false;
	}
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
