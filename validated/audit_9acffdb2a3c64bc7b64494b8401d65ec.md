Confirmed: `createWithdrawMemo` places the raw `destinationAddress` verbatim into the `WITHDRAW_TO:<address>` memo string, with zero re-validation beyond what `validateDogeAddress` already did.### Title
`validateDogeAddress` accepts base58check-invalid Dogecoin addresses (no checksum verification), letting corrupted/mistyped destinations reach `ft_withdraw` memo unmodified - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateDogeAddress` only checks a regex over the base58 alphabet and does not decode/verify the base58check checksum, unlike `validateBtcAddress`, which performs a full double-SHA256 checksum comparison. Any string starting with `D`/`A` of 26-34 base58 characters passes, including strings with corrupted/mistyped payloads such as `DH5yaieqoZN36fDVciNyRueRGvGLR3mr7M`, which then flows verbatim into the `ft_withdraw` intent's `WITHDRAW_TO:<address>` memo.

### Finding Description
The claimed invariant is: for every `s` where `validateAddress(s, Chains.Dogecoin)` returns `true`, the payout Dogecoin account derived by the PoA relayer must equal `s` (i.e., a validated address is a real, checksum-correct account).

`validateDogeAddress` is defined as: [1](#0-0) 
This is a pure regex match against the base58 charset with no checksum decode. Contrast with `validateBtcBase58Address`, which decodes base58, extracts the payload/checksum, and compares against `sha256(sha256(payload))`: [2](#0-1) 

`DH5yaieqoZN36fDVciNyRueRGvGLR3mr7M` is a 34-character string composed entirely of base58-alphabet characters (no `0`, `O`, `I`, `l`), so it matches `/^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/` and `validateDogeAddress` returns `true`, even though its base58check checksum is not verified/known-valid.

The withdrawal flow reaches `PoaBridge.validateWithdrawal`, which calls `validateAddress` and, on success, proceeds without any further byte-level validation: [3](#0-2) 
`PoaBridge.createWithdrawalIntents` then calls `createWithdrawIntentPrimitive`, which builds the `ft_withdraw` intent to `omft.near` and encodes the raw destination address into the memo via `createWithdrawMemo`: [4](#0-3) 
The `destinationAddress` string is passed through byte-for-byte with no additional check — there is no code in this repo that re-validates or normalizes the Dogecoin checksum before it is embedded in `memo: "WITHDRAW_TO:<address>"`.

No existing guard catches this: `validateWithdrawal`'s only address check is `validateAddress` (regex-only for Doge); `compareAddresses` only checks whether the destination equals the token's own origin address (self-send guard), not general validity; `supports()` only checks assetId/route matching; the intents contract's own signature/nonce checks operate on `receiver_id`/`amount`/`nonce`, not on the semantic validity of the memo-embedded off-chain address, since Dogecoin address interpretation happens entirely off-chain by the PoA relayer.

### Impact Explanation
If the destination string has been corrupted (e.g., a single-character transcription error common with unchecksummed strings), the SDK will still report the address as valid, sign and publish the `ft_withdraw` intent, and forward it to the PoA relayer with the bad address baked into the memo. What happens next (relayer rejects it, refunds it, or attempts to send to whatever it decodes) is delegated entirely to the PoA relayer's own logic — a system explicitly noted in the audit rules as an external, out-of-scope trust boundary ("trust assumptions about ... the relayer, bridge APIs ... are OUT OF SCOPE"). The SDK itself does not derive or claim a destination account for this corrupted string; it merely fails to reject invalid input before it reaches an external system. This differs from the excluded case "funds sent by mistake to a correctly validated address" only in that the string that slips through would not be considered a fully "correct" Dogecoin address by strict base58check rules, but the ultimate fund-misdirection outcome depends entirely on the relayer's undocumented handling of unchecksummed strings, which this repository does not control or predict.

### Likelihood Explanation
Preconditions: an attacker/integrator must supply a Dogecoin destination string that (a) matches the base58-alphabet/length regex but (b) has an incorrect checksum — essentially a single/few-character typo of a real address. This is plausible for manually entered addresses. However, whether this results in actual fund loss versus a rejected/bounced relayer-side transaction cannot be determined from this repository; it depends on `bridge.chaindefuser.com`'s undisclosed handling of unchecksummed strings, which is out of scope per the audit rules.

### Recommendation
Implement full base58check decoding and double-SHA256 checksum verification in `validateDogeAddress`, mirroring `validateBtcBase58Address`, checking the version byte (`0x1e` for `D...` P2PKH, and the correct byte for any other supported prefix) and the 4-byte checksum before accepting the address.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/validateAddress.spec.ts
import { validateAddress } from "./validateAddress";
import { Chains } from "./caip2";

it("rejects Dogecoin address with invalid checksum (regex-only bug)", () => {
  // DH5yaieqoZN36fDVciNyRueRGvGLR3mr7M matches the base58 charset/length regex
  // but does not decode to a valid base58check payload/checksum.
  expect(
    validateAddress("DH5yaieqoZN36fDVciNyRueRGvGLR3mr7M", Chains.Dogecoin),
  ).toBe(false); // currently returns true — demonstrates missing checksum check
});
```
This test alone demonstrates the gap in `validateDogeAddress`; it does not by itself prove funds are misrouted, since that final step depends on the external PoA relayer's behavior, which is outside this repository and cannot be asserted here with only HTTP mocks against the relayer's actual address-decoding logic.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L140-157)
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
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L329-331)
```typescript
function validateDogeAddress(address: string) {
	return /^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/.test(address);
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L6-49)
```typescript
export function createWithdrawIntentPrimitive(params: {
	assetId: string;
	destinationAddress: string;
	destinationMemo: string | undefined;
	amount: bigint;
}): Extract<IntentPrimitive, { intent: "ft_withdraw" }> {
	const { contractId: tokenAccountId } = utils.parseDefuseAssetId(
		params.assetId,
	);
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: tokenAccountId,
		amount: params.amount.toString(),
		memo: createWithdrawMemo({
			receiverAddress: params.destinationAddress,
			xrpMemo: params.destinationMemo,
		}),
		min_gas: MIN_GAS_AMOUNT,
	};
}

function createWithdrawMemo({
	receiverAddress,
	xrpMemo,
}: {
	receiverAddress: string;
	xrpMemo: string | undefined;
}) {
	// Strip "bitcoincash:" prefix from BCH CashAddr addresses
	const normalizedAddress = receiverAddress
		.toLowerCase()
		.startsWith("bitcoincash:")
		? receiverAddress.slice("bitcoincash:".length)
		: receiverAddress;

	const memo = ["WITHDRAW_TO", normalizedAddress];

	if (xrpMemo != null && xrpMemo !== "") {
		memo.push(xrpMemo);
	}

	return memo.join(":");
}
```
