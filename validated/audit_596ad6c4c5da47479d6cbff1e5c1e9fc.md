Confirmed: `validateBchAddress` (packages/intents-sdk/src/lib/validateAddress.ts, lines 214-225) validates legacy BCH addresses with regex only (`/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/` or `/^3.../`), with no base58 decode or sha256d checksum verification, unlike `validateBtcBase58Address` (lines 140-158) and `validateDashAddress`/`validateLitecoinBase58Address`/`validateTronBase58Address` which all decode base58 and verify the double-SHA256 checksum before returning true.

### Title
Legacy BitcoinCash address validation accepts checksum-invalid Base58 strings, allowing withdrawal to unspendable/mistyped addresses - (File: packages/intents-sdk/src/lib/validateAddress.ts)

### Summary
`validateBchAddress`'s legacy branch validates only regex length/charset (`/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/` and the `3...` P2SH equivalent) and never decodes the Base58 payload or verifies the SHA256d checksum, unlike `validateBtcBase58Address` for Bitcoin. This lets a corrupted/mistyped legacy address that matches the regex but fails checksum verification pass `validateAddress` for `Chains.BitcoinCash` and thus `PoaBridge.validateWithdrawal`.

### Finding Description
The broken equality: `(chain=BitcoinCash, destinationAddress validated=true)` is claimed to imply `destinationAddress is a real, checksum-valid, payable BCH legacy address`. In `validateBchAddress` (packages/intents-sdk/src/lib/validateAddress.ts:214-225), the legacy branch only runs a regex test on length and Base58 charset — it never calls `base58.decode` nor computes `sha256(sha256(payload))` to compare against the trailing 4-byte checksum, in contrast to `validateBtcBase58Address` (lines 140-158) which explicitly performs this checksum check. An attacker (an ordinary user withdrawing their own BCH, or a counterparty-supplied `destinationAddress` forwarded by an integrator) can supply any 26-35 character Base58-charset string starting with `1` or `3` — including one with a flipped/corrupted checksum, e.g. a single mistyped character in `1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2` — and `validateBchAddress` returns `true`. This flows into `PoaBridge.validateWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:181-188), which only calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and throws only if it returns `false`. Since the regex-only check returns `true`, the malformed address passes and the withdrawal proceeds to intent creation and execution with no further BCH-specific checksum verification anywhere in `PoaBridge`.

### Impact Explanation
Because `validateWithdrawal` accepts the malformed legacy address as valid, the SDK will sign/submit a withdrawal intent (and the POA relayer will attempt on-chain transfer) to an address that never had a matching valid checksum. On real BCH nodes/wallets, addresses failing the checksum are rejected as invalid and cannot be constructed as a valid destination by any wallet, meaning either (a) the relayer/bridge rejects the transfer downstream (best case, but that behavior is not guaranteed nor validated in this codebase) or (b) if the bridge software does not itself re-validate the checksum, funds are broadcast to an address with no known private key, permanently stranding withdrawn funds with no recovery path. This matches "funds delivered to a wrong address/chain/contract with no recovery" (Critical).

### Likelihood Explanation
This requires no privilege beyond being an ordinary user/integrator performing a normal BitcoinCash withdrawal via `PoaBridge` and supplying a destination address with a corrupted checksum (e.g., a typo, or a copy-paste/OCR error, or deliberate testing of the SDK's validation robustness). The attacker cost is zero — constructing a Base58 string matching the length/charset regex with an invalid checksum is trivial, and the flaw is deterministic and repeatable on every call.

### Recommendation
In `validateBchAddress`, for the legacy branch, decode the Base58 string and verify the SHA256d checksum exactly as `validateBtcBase58Address` does (version byte 0x00 for P2PKH / 0x05 for P2SH, 25 decoded bytes, and checksum comparison), rejecting addresses whose checksum does not match, instead of relying on the regex alone.

### Proof of Concept
```ts
// validateAddress.spec.ts (or new test file)
import { validateBchAddress } from "../src/lib/validateAddress";
import { base58 } from "@scure/base";
import { sha256 } from "@noble/hashes/sha2";

test("validateBchAddress accepts a legacy address with a corrupted checksum", () => {
  // Take a known-valid BTC/BCH legacy P2PKH address and decode it.
  const validAddress = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2";
  const decoded = base58.decode(validAddress);
  const payload = decoded.subarray(0, 21);
  const goodChecksum = decoded.subarray(21, 25);
  const expected = sha256(sha256(payload)).subarray(0, 4);

  // Sanity: this address's checksum is actually correct.
  expect(Array.from(goodChecksum)).toEqual(Array.from(expected));

  // Corrupt one checksum byte, re-encode.
  const corrupted = Uint8Array.from(decoded);
  corrupted[24] = (corrupted[24]! + 1) % 256;
  const corruptedAddress = base58.encode(corrupted);

  // Confirm corrupted address's checksum indeed fails proper verification.
  const corruptedPayload = corrupted.subarray(0, 21);
  const corruptedChecksum = corrupted.subarray(21, 25);
  const expectedForCorrupted = sha256(sha256(corruptedPayload)).subarray(0, 4);
  expect(Array.from(corruptedChecksum)).not.toEqual(Array.from(expectedForCorrupted));

  // validateBchAddress still returns true (regex-only), despite failing checksum.
  expect(validateBchAddress(corruptedAddress)).toBe(true);
});
```
This demonstrates `validateBchAddress` returning `true` for an address whose checksum verification fails, confirming the broken equality between "address validated for BitcoinCash" and "address is a real payable BCH address." [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L140-158)
```typescript
function validateBtcBase58Address(address: string): boolean {
	const decoded: Uint8Array = base58.decode(address);

	// version (1) + hash160 (20) + checksum (4) = 25 bytes
	if (decoded.length !== 25) return false;

	const version = decoded[0];
	// 0x00 = P2PKH mainnet, 0x05 = P2SH mainnet
	if (version !== 0x00 && version !== 0x05) return false;

	const payload = decoded.subarray(0, 21);
	const checksum = decoded.subarray(21, 25);
	const expectedChecksum = sha256(sha256(payload)).subarray(0, 4);

	for (let i = 0; i < 4; i++) {
		if (checksum[i] !== expectedChecksum[i]) return false;
	}
	return true;
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L214-225)
```typescript
export function validateBchAddress(address: string): boolean {
	// Legacy address format (same as Bitcoin)
	if (
		/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(address) ||
		/^3[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(address)
	) {
		return true;
	}

	// CashAddr format
	return validateBchCashAddr(address);
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L181-188)
```typescript
		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}
```
