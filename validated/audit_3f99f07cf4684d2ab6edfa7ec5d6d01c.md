### Title
Stellar destination address accepted with no base32/CRC16 checksum validation, allowing signed withdrawals to non-existent addresses - (File: packages/intents-sdk/src/lib/validateAddress.ts)

### Summary
`validateAddress` for `Chains.Stellar` delegates to `validateStellarAddress`, which only checks a regex `/^G[A-Z0-9]{55}$/` and never decodes the base32 payload or verifies the CRC16 checksum required by the Stellar `StrKey` encoding. This lets `OmniBridge.validateWithdrawal` accept any 56-character string starting with `G` composed of uppercase letters/digits, even if it does not decode to a real Stellar ed25519 public key, and that unchecked string is carried verbatim into the signed withdrawal intent.

### Finding Description
The broken equality: "address accepted by `validateAddress(..., Chains.Stellar)`" should equal "address that decodes to a real Stellar `G...` account id (valid base32 + CRC16 checksum)". In `validateStellarAddress`:
```
function validateStellarAddress(address: string) {
	return /^G[A-Z0-9]{55}$/.test(address);
}
``` [1](#0-0) 
this only checks length/charset, unlike the other chain validators in the same file that perform full checksum verification, e.g. Bitcoin/Tron/Litecoin/Dash base58Check (`sha256(sha256(payload))` compared byte-by-byte) [2](#0-1)  or Bitcoin Cash's BCH polymod checksum [3](#0-2) . Stellar's `StrKey` format encodes a version byte + 32-byte payload + 2-byte CRC16-XModem checksum in base32, so a random uppercase/digit string can match the regex without being valid base32 or without its CRC16 matching.

Code path: `OmniBridge.validateWithdrawal` calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and only throws `InvalidDestinationAddressForWithdrawalError` if it returns `false` [4](#0-3) . Because the regex is satisfiable by garbage input, this check passes for a non-genuine Stellar address. After other checks (fee, token existence, storage balance, min amount), `validateWithdrawal` returns without further address validation. Then `OmniBridge.createWithdrawalIntents` builds the withdrawal intent via `deriveOmniWithdrawIntentParams({ ..., destinationAddress: args.withdrawalParams.destinationAddress, ... })` [5](#0-4) , which stores the unchecked string as the recipient in the resulting withdrawal intent primitive that gets signed by the user via `createWithdrawIntentsPrimitive`. No other guard (`compareAddresses`, `supports()`, the intents contract's signature/nonce checks) re-validates that the destination decodes to a genuine Stellar account — those checks concern token-address collision and contract-level authenticity, not Stellar address well-formedness.

Attacker input: a caller of the public SDK (an integrator forwarding a user-supplied `destinationAddress`, or the user themselves) supplies any string of the form `G` + 55 chars from `[A-Z0-9]` that is not a genuine base32-encoded, CRC16-valid Stellar `StrKey` (e.g. `G` followed by 55 `A`s). This passes `validateStellarAddress`, propagates through `validateWithdrawal` and `createWithdrawalIntents`, and ends up as the recipient in a signed, submitted withdrawal intent.

### Impact Explanation
The user's own signed withdrawal intent will contain a `recipient` field equal to the invalid/garbage Stellar-looking string. Once the bridge relayer/contract processes this withdrawal on the Stellar side, funds are moved out of the user's intents balance but the destination is not a valid Stellar account — there is no path to deliver the funds and no automatic refund mechanism inside this SDK layer, matching the Critical category: "funds delivered to a wrong address/chain/contract with no recovery." Because the SDK is the layer responsible for pre-flight address validation before signing, this is a direct SDK defect, not merely a "funds sent by mistake to a correctly-validated address" (which is explicitly out of scope) — here the address is *not* validated correctly. This is repeatable on every withdrawal call to a Stellar-destined Omni-bridged token; each call with a malformed `G...` string produces a fresh unrecoverable withdrawal.

### Likelihood Explanation
Preconditions are modest: any Omni-bridged token that has a valid destination token on Stellar (`assetInfo.blockchain === Chains.Stellar`), which is a normal, supported route. The attacker (or a careless integrator forwarding third-party input) needs only to supply a 56-character string starting with `G` using uppercase letters and digits — trivial to construct, at zero cost, with no special privileges. It is fully client-controlled input reaching signing logic with no additional gating, so it is highly feasible and repeatable.

### Recommendation
Implement proper Stellar `StrKey` decoding in `validateStellarAddress`: base32-decode the address (RFC 4648 base32 alphabet `A-Z2-7`, note this regex currently wrongly allows `0-9` and disallows lowered/other valid base32 characters like `2-7` exclusively — actually Stellar strkey uses base32 alphabet `A-Z2-7`), verify total decoded length is 35 bytes (1 version byte + 32 payload + 2 checksum), verify the version byte corresponds to `ed25519 public key` (0x30 for `G` prefix), and verify the trailing 2-byte CRC16-XModem checksum matches the checksum computed over the version+payload bytes, mirroring the pattern already used for BTC/Tron/Litecoin/Dash checksum validation in this same file.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/validateAddress.spec.ts (illustrative)
import { validateAddress } from "./validateAddress";
import { Chains } from "./caip2";

it("rejects a well-formed but checksum-invalid Stellar address (currently fails)", () => {
  // 'G' + 55 chars, valid charset, but not a real base32/CRC16-valid StrKey
  const fakeStellarAddress = "G" + "A".repeat(55);

  // EXISTING BROKEN BEHAVIOR: passes despite invalid checksum
  expect(validateAddress(fakeStellarAddress, Chains.Stellar)).toBe(true);
});
```
And, tracing through `OmniBridge`:
```ts
// packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (illustrative, mocks HTTP only)
it("signs a withdrawal intent with an invalid Stellar recipient", async () => {
  const fakeStellarAddress = "G" + "A".repeat(55);
  // mock only omniBridgeAPI.getFee / getBridgedToken / storage balance HTTP calls
  await bridge.validateWithdrawal({
    assetId: STELLAR_OMNI_ASSET_ID,
    amount: 1000n,
    destinationAddress: fakeStellarAddress,
    feeEstimation,
  }); // does NOT throw InvalidDestinationAddressForWithdrawalError

  const intents = await bridge.createWithdrawalIntents({
    withdrawalParams: { assetId: STELLAR_OMNI_ASSET_ID, amount: 1000n, destinationAddress: fakeStellarAddress },
    feeEstimation,
  });

  // assert recipient equals the invalid string verbatim in the produced intent primitive
  expect(JSON.stringify(intents)).toContain(fakeStellarAddress);
});
```
Both assertions demonstrate the broken equality: `validateAddress(...) === true` for an address that is not a valid Stellar account id, and the invalid string reaches the signed intent's recipient field unchanged.

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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L271-310)
```typescript
function verifyBchChecksum(address: string): boolean {
	const CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

	// Split prefix and payload
	const colonIndex = address.indexOf(":");
	const prefix = address.slice(0, colonIndex);
	const payload = address.slice(colonIndex + 1);

	// Expand prefix for checksum (each character's lower 5 bits)
	const prefixData: number[] = [];
	for (const char of prefix) {
		prefixData.push(char.charCodeAt(0) & 0x1f);
	}
	prefixData.push(0); // separator

	// Convert payload to 5-bit values
	const payloadData: number[] = [];
	for (const char of payload) {
		const idx = CHARSET.indexOf(char);
		if (idx === -1) return false;
		payloadData.push(idx);
	}

	const values = [...prefixData, ...payloadData];

	// BCH polymod calculation
	let c = 1n;
	for (const d of values) {
		const c0 = c >> 35n;
		c = ((c & 0x07ffffffffn) << 5n) ^ BigInt(d);
		if (c0 & 0x01n) c ^= 0x98f2bc8e61n;
		if (c0 & 0x02n) c ^= 0x79b76d99e2n;
		if (c0 & 0x04n) c ^= 0xf33e5fb3c4n;
		if (c0 & 0x08n) c ^= 0xae2eabe2a8n;
		if (c0 & 0x10n) c ^= 0x1e4f43e470n;
	}

	// XOR with 1 and check if result is 0
	return (c ^ 1n) === 0n;
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L440-442)
```typescript
function validateStellarAddress(address: string) {
	return /^G[A-Z0-9]{55}$/.test(address);
}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L316-327)
```typescript
		intents.push(
			...createWithdrawIntentsPrimitive(
				deriveOmniWithdrawIntentParams({
					assetId: args.withdrawalParams.assetId,
					destinationAddress: args.withdrawalParams.destinationAddress,
					actualAmount: args.withdrawalParams.amount,
					omniChainKind,
					intentsContract: this.envConfig.contractID,
					feeEstimation: args.feeEstimation,
				}),
			),
		);
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L358-365)
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
