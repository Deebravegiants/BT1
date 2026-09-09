### Title
Legacy BCH address regex path in `validateBchAddress` skips base58 checksum verification, allowing corrupted legacy addresses to be embedded verbatim in `WITHDRAW_TO` memos - (File: packages/intents-sdk/src/lib/validateAddress.ts)

### Summary
`validateBchAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` (lines 214-225) treats any string matching `/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/` or `/^3[1-9A-HJ-NP-Za-km-z]{25,34}$/` as valid without decoding it and verifying the base58Check checksum, while the sibling CashAddr path (`validateBchCashAddr`) and the Bitcoin legacy path (`validateBtcBase58Address`) both perform full checksum verification. A destinationAddress with a corrupted checksum but the right charset/length passes `validateAddress` and is embedded unchanged into the `WITHDRAW_TO:<address>` memo by `createWithdrawIntentPrimitive` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts` (lines 20-23, 28-49).

### Finding Description
The claimed broken equality is: `validateBchAddress(address) === true` should imply the address is a checksum-valid, deliverable BCH address (matching what `createWithdrawIntentPrimitive` signs into the intent memo as the destination truth). In the legacy branch this equality does not hold:

```
// packages/intents-sdk/src/lib/validateAddress.ts:214-225
export function validateBchAddress(address: string): boolean {
	if (
		/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(address) ||
		/^3[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(address)
	) {
		return true;
	}
	return validateBchCashAddr(address);
}
```

The regex only constrains character set and length; it never calls `base58.decode`, never checks the version byte, and never recomputes/compares the double-SHA256 checksum, unlike `validateBtcBase58Address` (lines 140-158) which does exactly that for Bitcoin, and unlike `validateBchCashAddr` which performs full polymod checksum verification for the CashAddr branch. So an attacker can construct a 26-35 character base58-alphabet string starting with `1` or `3` with an arbitrary/corrupted last 4 checksum bytes, and `validateBchAddress` will still return `true`.

Downstream, `createWithdrawIntentPrimitive` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts:6-26) takes `destinationAddress` and passes it straight into `createWithdrawMemo` (lines 28-49), which only strips a `bitcoincash:` prefix and otherwise joins it verbatim into `WITHDRAW_TO:<address>`. There is no re-validation or checksum check at this stage - it trusts the caller already validated the address via `validateAddress`.

### Impact Explanation
The `ft_withdraw` intent's `memo` field (`WITHDRAW_TO:<corrupted-legacy-address>`) is what gets signed by the user and submitted on-chain, then interpreted by the PoA bridge/relayer to route the withdrawal. If the checksum is corrupted, the resulting address is not a valid BCH address at all - the bridge would either reject it (funds stuck, requiring manual intervention) or, in the worst case, decode to bytes that collide with a different/valid-looking destination that the user did not intend, though the more consistently reachable outcome is an invalid/unspendable destination causing the withdrawal to fail post-signature. This is a real divergence: the user's client-side validation (`validateAddress`) reports "valid" for an address that is not actually well-formed, so the SDK does not stop the user from signing a withdrawal to a broken destination. This matches the "withdrawal stuck until manual intervention" category for a legacy-format BCH destination that fails checksum, since the funds are locked into a signed intent instead of being caught before signing.

### Likelihood Explanation
Trivial to trigger: any user (or a counterparty whose address string is forwarded by an integrator, per the threat model) supplies a destinationAddress for `nep141:bch.omft.near` that is legacy-format (`1...`/`3...`), correct length/charset, but with a mangled checksum (e.g., a typo, or a deliberately crafted string). No special privilege or contract knowledge is needed - just calling the public `validateAddress`/withdraw APIs with a malformed string. This is fully repeatable per call and costs nothing beyond constructing the string.

### Recommendation
In `validateBchAddress`, replace the bare regex checks for the legacy branch with a proper base58Check decode + checksum verification (mirroring `validateBtcBase58Address`), confirming the decoded length is 25 bytes, the version byte is 0x00 (P2PKH) or 0x05 (P2SH), and the trailing 4-byte checksum matches `sha256(sha256(payload)).subarray(0,4)`, only then returning `true`.

### Proof of Concept
```ts
// vitest, no HTTP needed - pure unit test on validateAddress.ts
import { validateBchAddress } from "../lib/validateAddress";
import { createWithdrawIntentPrimitive } from "../bridges/poa-bridge/poa-bridge-utils";

test("legacy BCH regex path accepts corrupted checksum", () => {
  // Take a real valid legacy address and mutate the last checksum char
  const valid = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2";
  const corrupted = valid.slice(0, -1) + (valid.at(-1) === "2" ? "3" : "2");

  // Matches the legacy regex - format-only check
  expect(/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/.test(corrupted)).toBe(true);

  // BUG: returns true despite invalid checksum
  expect(validateBchAddress(corrupted)).toBe(true);

  // Embedded verbatim into the signed withdrawal memo
  const primitive = createWithdrawIntentPrimitive({
    assetId: "nep141:bch.omft.near",
    destinationAddress: corrupted,
    destinationMemo: undefined,
    amount: 100n,
  });
  expect(primitive.memo).toBe(`WITHDRAW_TO:${corrupted}`);
});
``` [1](#0-0) [2](#0-1) [3](#0-2)

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
