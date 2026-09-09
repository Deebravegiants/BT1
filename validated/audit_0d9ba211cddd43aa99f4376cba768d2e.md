Confirmed finding. `validateDogeAddress` performs regex-only validation with no base58Check decode/checksum step, unlike its sibling validators in the same file that all verify the double-SHA256 checksum before accepting an address.

### Title
Dogecoin address validation skips base58Check checksum verification, allowing checksum-corrupted addresses into signed withdrawal intents - (File: packages/intents-sdk/src/lib/validateAddress.ts)

### Summary
`validateDogeAddress` at `packages/intents-sdk/src/lib/validateAddress.ts` lines 329-331 validates only the character-class/length shape of a Dogecoin address via regex, unlike `validateBtcBase58Address`, `validateLitecoinBase58Address`, `validateTronBase58Address`, and `validateDashAddress` in the same file, all of which base58-decode the address and verify the trailing 4-byte double-SHA256 checksum before returning `true`. This lets a regex-valid but checksum-invalid Dogecoin address pass `validateAddress(addr, Chains.Dogecoin)`, after which `createWithdrawIntentPrimitive` embeds it verbatim into the `WITHDRAW_TO:<address>` memo of a signed `ft_withdraw` intent.

### Finding Description
The broken equality is: **"address accepted by `validateAddress` for Dogecoin" == "a well-formed, checksum-valid Dogecoin address that a Dogecoin node/bridge can actually spend to."** For every other base58Check chain implemented in this file (`validateBtcBase58Address` lines 140-158, `validateLitecoinBase58Address` lines 537-567, `validateDashAddress` lines 801-831, `validateTronBase58Address` lines 384-403), this equality is enforced by decoding with `base58.decode`, slicing off the last 4 bytes as `checksum`, recomputing `sha256(sha256(payload)).subarray(0,4)`, and byte-comparing. `validateDogeAddress` (lines 329-331) does none of this — it is a pure regex test `/^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/` with no `base58.decode` call, no checksum computation, and no version-byte check.

Exploit flow:
1. Attacker (an ordinary user requesting their own withdrawal) picks/derives any base58-alphabet string starting with `D` or `A`, of the right length, and flips a trailing character so the double-SHA256 checksum no longer matches the payload — the regex still matches since it only inspects character class and length, not checksum bytes.
2. Calls SDK withdraw flow with `Chains.Dogecoin` and this address as `destinationAddress`. `PoaBridge.validateWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts lines 181-188) calls `validateAddress(args.destinationAddress, assetInfo.blockchain)`, which returns `true`.
3. `createWithdrawalIntents` → `createWithdrawIntentPrimitive` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts lines 6-26) embeds the address unchanged into `memo: "WITHDRAW_TO:<address>"`.
4. The SDK signs and submits this `ft_withdraw` intent; the user's balance is debited on execution.
5. The off-chain PoA relayer that reads the memo must itself detect the bad checksum and refuse to broadcast on the Dogecoin network — but by then the on-chain NEAR intent has already executed and debited the user, so if the relayer's own validation is anything short of perfect (or interprets the bytes differently than expected), no on-chain recovery path exists inside this repo.

No other guard closes this gap: `compareAddresses` only compares two addresses for equality of representation, it doesn't validate checksum validity; `getUnderlyingFee`/`FeeExceedsAmountError` are fee-only checks; the intents contract's own signature/nonce verification confirms authorization, not destination-address correctness.

### Impact Explanation
Once `validateWithdrawal` passes, the SDK proceeds to build and sign a real `ft_withdraw` intent debiting the user's on-chain balance, with the corrupted address baked into the memo consumed by the PoA relayer. If the relayer's off-chain checksum check is bypassed, differs from expectations, or a permissive/alternate consumer of the memo credits a derived address anyway, funds are irrecoverably misrouted — the debit on NEAR has already occurred and cannot be undone by the SDK. This matches the Critical category: "funds delivered to a wrong address/chain/contract with no recovery."

### Likelihood Explanation
The precondition is narrow but trivially attacker-controlled: only a Dogecoin PoA-route withdrawal with an address that is regex-shaped correctly but checksum-corrupted (a one-character typo/flip is enough, cost is zero, fully repeatable per withdrawal call). No special privilege, relayer collusion, or RPC manipulation is required — this is a pure client-side validation gap reachable by any SDK caller supplying their own `destinationAddress`.

### Recommendation
Rewrite `validateDogeAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` to mirror `validateDashAddress`/`validateBtcBase58Address`: base58-decode the address, verify total length is 25 bytes, check the version byte (`0x1e` for Dogecoin P2PKH / `0x16` for P2SH), and verify the trailing 4-byte checksum equals `sha256(sha256(payload)).subarray(0,4)` before returning `true`.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/validateAddress.doge-checksum.spec.ts
import { describe, it, expect } from "vitest";
import { base58 } from "@scure/base";
import { sha256 } from "@noble/hashes/sha2";
import { validateAddress } from "./validateAddress";
import { Chains } from "./caip2";
import { createWithdrawIntentPrimitive } from "../bridges/poa-bridge/poa-bridge-utils";

function buildDogeAddressWithBadChecksum(): string {
  const version = 0x1e; // Dogecoin P2PKH
  const payload = new Uint8Array(21);
  payload[0] = version;
  // fill hash160 bytes with arbitrary data
  for (let i = 1; i < 21; i++) payload[i] = i;

  const goodChecksum = sha256(sha256(payload)).subarray(0, 4);
  const badChecksum = Uint8Array.from(goodChecksum);
  badChecksum[0] ^= 0xff; // corrupt checksum, but keep base58 char class valid

  const full = new Uint8Array(25);
  full.set(payload, 0);
  full.set(badChecksum, 21);

  return base58.encode(full);
}

describe("Dogecoin address checksum gap", () => {
  it("validateAddress accepts a regex-valid but checksum-invalid Doge address", () => {
    const addr = buildDogeAddressWithBadChecksum();

    // LHS: SDK's validation verdict
    const isValid = validateAddress(addr, Chains.Dogecoin);

    // RHS: ground truth base58Check checksum validity
    const decoded = base58.decode(addr);
    const payload = decoded.subarray(0, 21);
    const checksum = decoded.subarray(21, 25);
    const expected = sha256(sha256(payload)).subarray(0, 4);
    const checksumValid = expected.every((b, i) => b === checksum[i]);

    expect(isValid).toBe(true);        // SDK says OK
    expect(checksumValid).toBe(false); // but it is NOT a valid Dogecoin address
  });

  it("createWithdrawIntentPrimitive still embeds the checksum-invalid address in WITHDRAW_TO", () => {
    const addr = buildDogeAddressWithBadChecksum();
    const intent = createWithdrawIntentPrimitive({
      assetId: "nep141:doge.omft.near",
      destinationAddress: addr,
      destinationMemo: undefined,
      amount: 1000n,
    });
    expect(intent.memo).toBe(`WITHDRAW_TO:${addr}`);
  });
});
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L329-331)
```typescript
function validateDogeAddress(address: string) {
	return /^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/.test(address);
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L801-831)
```typescript
export function validateDashAddress(address: string): boolean {
	try {
		const decoded: Uint8Array = base58.decode(address);

		// version (1) + payload (20) + checksum (4)
		if (decoded.length !== 25) return false;

		const version = decoded[0];
		if (
			version !== 0x4c && // P2PKH
			version !== 0x10 // P2SH
		) {
			return false;
		}

		const payload = decoded.subarray(0, 21);
		const checksum = decoded.subarray(21, 25);

		const hash1 = sha256(payload);
		const hash2 = sha256(hash1);
		const expectedChecksum = hash2.subarray(0, 4);

		for (let i = 0; i < 4; i++) {
			if (checksum[i] !== expectedChecksum[i]) return false;
		}

		return true;
	} catch {
		return false;
	}
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
