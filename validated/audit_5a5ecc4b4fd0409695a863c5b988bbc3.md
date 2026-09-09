### Title
Litecoin address validation accepts Bitcoin P2SH addresses ('3...', version 0x05), breaking Litecoin destination-address truth - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateLitecoinAddress()` treats any Base58Check string with version byte `0x05` (prefix `3`) as a valid Litecoin P2SH address, but this is byte-for-byte identical to Bitcoin's mainnet P2SH encoding. `IntentsSDK.createWithdrawalIntents` for `nep141:ltc.omft.near` accepts such an address, and `createWithdrawIntentPrimitive()` embeds it verbatim into the `ft_withdraw` memo as `WITHDRAW_TO:<address>` with no cross-chain disambiguation.

### Finding Description
The broken equality is: *the address validated as "spendable on Litecoin" == the address whose keys can actually spend on Litecoin*. `validateLitecoinAddress()` in [1](#0-0)  explicitly accepts prefix `3` decoded with version `0x05`, and the code even carries a comment acknowledging the ambiguity: "[Inference] This also matches Bitcoin P2SH; cannot distinguish by prefix+version alone." [2](#0-1)  shows Bitcoin's own P2SH validator uses the identical version byte `0x05`, confirming the two address spaces are indistinguishable from the string alone.

The withdrawal path is `IntentsSDK.createWithdrawalIntents` → `bridge.validateWithdrawal` (which internally calls `validateAddress(destinationAddress, blockchain)` derived from the asset's chain, as seen in the pattern used across bridges, e.g. `OmniBridge.validateWithdrawal` at [3](#0-2) ) → `bridge.createWithdrawalIntents` → `createWithdrawIntentPrimitive()` in [4](#0-3) , which calls `createWithdrawMemo()` and writes the raw destination address into `memo: "WITHDRAW_TO:<address>"` at [5](#0-4) . Existing tests confirm this exact memo format for other assets, e.g. `memo: "WITHDRAW_TO:bc1q..."` for BTC withdrawals in [6](#0-5) .

None of the other guards catch this: `compareAddresses` only checks for self-transfer to the token contract address, `FeeExceedsAmountError`/`getUnderlyingFee` only concern fee math, and `supports()`/route ordering only pick which bridge handles the asset — none of them attempt to verify that a Base58 P2SH payload is actually a Litecoin script rather than a Bitcoin one, because that distinction is fundamentally not encoded in the string itself (both chains share the same Base58Check version byte for P2SH). The PoA bridge server that ultimately parses the `WITHDRAW_TO:` memo receives an address string it cannot chain-disambiguate either.

### Impact Explanation
The `ft_withdraw` intent is signed by the user themselves (not injected by an attacker against a victim), so this is a self-inflicted funds-misdirection bug triggered by any ordinary caller (or an integrator forwarding an externally supplied `destinationAddress` string). Because a valid Bitcoin P2SH hash is not guaranteed to correspond to any script with spendable keys on the Litecoin chain (different signing/script context, no chain-specific commitment in the version byte), funds sent this way can be delivered to a script hash on the Litecoin ledger that no private key controls, or that corresponds to an unrelated/incorrect Bitcoin-side commitment — i.e., "funds delivered to a wrong address/chain with no recovery," matching the Critical category. This is repeatable on every LTC withdrawal that uses a `3...` legacy P2SH-style address.

### Likelihood Explanation
Preconditions: the user (or integrator on the user's behalf) must supply a `nep141:ltc.omft.near` withdrawal with a `destinationAddress` starting with `3` and valid Base58Check/version-0x05 checksum — trivial and costs nothing, requiring no privileged access, no relayer/RPC compromise, and no social engineering. Any ordinary user calling the public `IntentsSDK.createWithdrawalIntents` API can trigger it, e.g. reusing a Bitcoin P2SH address by mistake, or an integrator passing through a user-provided string without realizing prefix-based validation is insufficient for LTC. This is fully reachable through documented, unprivileged SDK usage.

### Recommendation
Litecoin legacy P2SH addresses starting with `3` cannot be safely distinguished from Bitcoin P2SH addresses by version byte alone; the SDK should either (a) drop acceptance of the `3...` legacy P2SH prefix for Litecoin entirely (Litecoin's modern P2SH prefix is `M...`/`0x32`, which is unambiguous), or (b) require callers to explicitly confirm chain intent for `3...` addresses, and document that reusing legacy `3...` addresses for LTC withdrawals is unsafe. At minimum, remove the silent acceptance in `validateLitecoinAddress()` at [1](#0-0)  and treat `3...` as invalid for LTC.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/validateAddress.spec.ts
import { describe, it, expect } from "vitest";
import { validateLitecoinAddress } from "./validateAddress";
import { createWithdrawIntentPrimitive } from "../bridges/poa-bridge/poa-bridge-utils";

describe("DESTINATION_TRUTH violation for LTC legacy P2SH", () => {
	it("accepts a Bitcoin P2SH address as a valid Litecoin address", () => {
		const btcP2sh = "3GoitrULXWigQqj4fV6FMVqtz8mru5auYh"; // real BTC mainnet P2SH
		// Side 1: address accepted as "spendable on Litecoin"
		expect(validateLitecoinAddress(btcP2sh)).toBe(true);
	});

	it("embeds an unverified BTC-shaped address into the LTC withdraw memo", () => {
		const btcP2sh = "3GoitrULXWigQqj4fV6FMVqtz8mru5auYh";
		const intent = createWithdrawIntentPrimitive({
			assetId: "nep141:ltc.omft.near",
			destinationAddress: btcP2sh,
			destinationMemo: undefined,
			amount: 100_000_000n,
		});
		// Side 2: no chain-specific proof this script is spendable on Litecoin
		expect(intent.memo).toBe(`WITHDRAW_TO:${btcP2sh}`);
		// DESTINATION_TRUTH fails: validateLitecoinAddress()===true does not imply
		// this hash160/script is controlled by keys usable on the Litecoin chain.
	});
});
```

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L140-148)
```typescript
function validateBtcBase58Address(address: string): boolean {
	const decoded: Uint8Array = base58.decode(address);

	// version (1) + hash160 (20) + checksum (4) = 25 bytes
	if (decoded.length !== 25) return false;

	const version = decoded[0];
	// 0x00 = P2PKH mainnet, 0x05 = P2SH mainnet
	if (version !== 0x00 && version !== 0x05) return false;
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L521-525)
```typescript
	// P2SH (legacy): 3... (0x05)
	// [Inference] This also matches Bitcoin P2SH; cannot distinguish by prefix+version alone.
	if (first === "3") {
		return validateLitecoinBase58Address(address, 0x05);
	}
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L6-26)
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L28-49)
```typescript
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

**File:** packages/intents-sdk/src/sdk.test.ts (L117-126)
```typescript
		await expect(intents).resolves.toEqual([
			{
				amount: "100001500",
				intent: "ft_withdraw",
				memo: "WITHDRAW_TO:bc1qsfq3eat543rzzwargvnjeqjzgl4tatse3mr3lu",
				min_gas: "17050000000000",
				receiver_id: "btc.omft.near",
				token: "btc.omft.near",
			},
		]);
```
