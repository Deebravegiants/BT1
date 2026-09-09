Confirmed: the code path traces exactly as described, and the checksum omission in `validateBchAddress`'s legacy branch is real and exploitable through `PoaBridge.validateWithdrawal`.

### Title
`validateBchAddress` legacy branch accepts checksum-invalid BCH addresses, allowing withdrawal to unspendable addresses - (File: packages/intents-sdk/src/lib/validateAddress.ts)

### Summary
`validateBchAddress` at [1](#0-0)  validates legacy BCH addresses (`1...`/`3...` prefixes) using only a base58-alphabet regex, with no base58Check/sha256d checksum verification, unlike the sibling `validateBtcBase58Address` at [2](#0-1)  which explicitly decodes and verifies the double-SHA256 checksum. This lets an attacker submit a syntactically well-formed but checksum-corrupted legacy address that passes `validateAddress(address, Chains.BitcoinCash)`, flows unchanged through `PoaBridge.validateWithdrawal` at [3](#0-2)  and into the on-chain withdrawal memo via `createWithdrawIntentPrimitive`/`createWithdrawMemo` at [4](#0-3) .

### Finding Description
The broken equality: `validateAddress(address, Chains.BitcoinCash) === true` should imply "`address` is a real, checksum-valid BCH destination that can receive funds," but for the legacy branch it only means "`address` matches `/^1[base58chars]{25,34}$/` or `/^3[base58chars]{25,34}$/`" — no base58Check decode, no length-25-byte check, no version-byte check, no sha256d checksum comparison is performed, in contrast to the Bitcoin legacy validator (`validateBtcBase58Address`) which performs all of these.

Exploit flow: an attacker (any unprivileged NEAR Intents user withdrawing their own funds, or a counterparty whose `destinationAddress` an integrator forwards) calls the withdrawal path with `assetId: "nep141:bch.omft.near"` and a `destinationAddress` that matches the legacy regex but has a single corrupted checksum byte (any random base58 string of the right length/prefix will do — the probability of accidentally matching a valid checksum is ~1/2^32, so essentially any such string is "invalid" already, but the point stands more sharply for a deliberately corrupted single byte of a known valid address). `PoaBridge.validateWithdrawal` calls `validateAddress` at [5](#0-4)  which returns `true` for the corrupted string, so no `InvalidDestinationAddressForWithdrawalError` is thrown. The withdrawal intent is then constructed with `memo: "WITHDRAW_TO:<address>"` via `createWithdrawMemo` at [6](#0-5) , and the off-chain PoA bridge relayer will attempt to relay funds to that string on the BCH network, where it does not correspond to any real, checksum-valid address.

None of the existing guards catch this: `compareAddresses` in `validateWithdrawal` only compares the destination against the token's own origin-chain address to prevent self-sends, not general validity; `supports()` ordering and `FeeExceedsAmountError`/`getUnderlyingFee` are unrelated to address format; the intents contract's own signature/nonce verification only authenticates the signer's intent to withdraw to whatever string is in the memo — it has no BCH-specific validation and trusts the SDK's `validateAddress` to have done format validation correctly.

### Impact Explanation
Funds are debited from the user's NEAR Intents balance via a signed `ft_withdraw` intent and routed by the PoA bridge relayer to a destination string that was never checksum-verified. If checksum-invalid, this is not a valid address on the BCH network and the withdrawal cannot land — the funds become unrecoverable/stuck, matching "funds delivered to a wrong address/chain/contract with no recovery" (Critical). This is repeatable on every withdrawal call using a legacy-format BCH address; each call can strand a fresh amount.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: PoA route, `assetId: "nep141:bch.omft.near"`, and a `destinationAddress` string matching the legacy regex (25–34 chars after the `1`/`3` prefix, base58 alphabet). No special privileges, RPC manipulation, or contract-admin access needed — any unprivileged SDK caller supplying this address directly triggers the gap. Whether the off-chain PoA bridge relayer itself performs any additional checksum check downstream is outside this repo's control and out of scope per the audit rules; the SDK's own documented format-validation contract is broken regardless.

### Recommendation
Update `validateBchAddress`'s legacy branch in `packages/intents-sdk/src/lib/validateAddress.ts` to perform full base58Check decoding and sha256d checksum verification (identical to `validateBtcBase58Address`), rather than a bare regex match, before returning `true`.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { validateAddress, validateBchAddress } from "../lib/validateAddress";
import { Chains } from "../lib/caip2";

describe("validateBchAddress legacy branch checksum bypass", () => {
  it("incorrectly accepts a checksum-corrupted legacy BCH address", () => {
    // Known-valid P2PKH legacy address (base58Check, real checksum)
    const valid = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"; // example legacy address
    // Corrupt a single trailing checksum-affecting character
    const corrupted = valid.slice(0, -1) + (valid.at(-1) === "2" ? "3" : "2");

    // Sanity: still matches the naive legacy regex used by validateBchAddress
    expect(/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(corrupted)).toBe(true);

    // Equality under test: validateAddress(address, BitcoinCash) should be false
    // for a checksum-invalid address, matching validateBtcAddress's behavior
    // for the equivalent BTC case.
    const bchResult = validateAddress(corrupted, Chains.BitcoinCash);
    const btcEquivalentResult = validateAddress(corrupted, Chains.Bitcoin); // BTC path DOES verify checksum

    expect(btcEquivalentResult).toBe(false); // BTC correctly rejects
    expect(bchResult).toBe(true); // BUG: BCH incorrectly accepts — demonstrates the divergence
  });
});
```
This test mocks nothing (pure function test) and directly demonstrates that `validateBchAddress`/`validateAddress(..., Chains.BitcoinCash)` returns `true` for a checksum-invalid legacy address where the equivalent BTC validator (`validateBtcAddress`) correctly returns `false`, confirming the broken equality between "format-matches" and "is a real destination."

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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L214-221)
```typescript
export function validateBchAddress(address: string): boolean {
	// Legacy address format (same as Bitcoin)
	if (
		/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(address) ||
		/^3[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(address)
	) {
		return true;
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
