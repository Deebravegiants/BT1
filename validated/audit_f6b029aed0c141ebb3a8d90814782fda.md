### Title
`validateDogeAddress` skips base58Check checksum verification, allowing checksum-invalid Dogecoin addresses into `WITHDRAW_TO` intents - (File: `packages/intents-sdk/src/lib/validateAddress.ts`)

### Summary
`validateDogeAddress` only checks a regex on character set and length, unlike the sibling Base58Check validators in the same file (BTC, LTC, TRON, DASH) which all decode and verify the SHA-256d checksum. This lets a caller pass a well-formed-looking but checksum-corrupted Dogecoin address through `PoaBridge.validateWithdrawal` and have it embedded verbatim into the on-chain `WITHDRAW_TO:<address>` memo.

### Finding Description
The broken equality is: **address embedded in the withdrawal intent memo == an address capable of receiving funds on Dogecoin**.

`validateDogeAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` is: [1](#0-0) 

This is purely a regex match on `/^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/`, with no base58 decode and no SHA-256d(SHA-256d) checksum comparison — unlike `validateBtcBase58Address`, `validateLitecoinBase58Address`, `validateTronBase58Address`, and `validateDashAddress` in the very same file, all of which decode the base58 payload and compare the last 4 bytes against the expected double-SHA256 checksum.

Reachable path:
1. `PoaBridge.validateWithdrawal` calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and throws `InvalidDestinationAddressForWithdrawalError` only if it returns `false`: [2](#0-1) 
Since `validateDogeAddress` returns `true` for any regex-matching string regardless of checksum validity, a corrupted-checksum address passes this gate.
2. `createWithdrawalIntents` -> `createWithdrawIntentPrimitive` (in `poa-bridge-utils.ts`) embeds `destinationAddress` verbatim into the memo without re-validating checksum: [3](#0-2) 
The resulting `ft_withdraw` intent carries `memo: "WITHDRAW_TO:<corrupted-checksum-address>"`.

None of the existing guards catch this: `compareAddresses` only checks equality against the token's own `origin_chain_address` (a different check), `supports()`/`parseAssetId` only validate the assetId/route mapping, and there is no XRPL-style account-existence RPC check for Dogecoin. The intents contract itself has no knowledge of Dogecoin address semantics — it just relays the opaque memo string to the PoA bridge/relayer, which will attempt (and fail) to construct a real Dogecoin transaction to a checksum-invalid destination.

### Impact Explanation
Funds are debited from the user's intents balance and a `ft_withdraw` intent is signed/broadcast with a memo string encoding a Dogecoin address that fails base58Check — i.e., not a valid, spendable destination. Once relayed, these funds are misrouted to an address that cannot receive/be recovered on the Dogecoin network, with no recovery path through the SDK. This matches the Critical category: "funds delivered to a wrong address/chain/contract with no recovery." It is fully repeatable per call — any caller supplying a crafted Doge address string can trigger the same outcome each time.

### Likelihood Explanation
Preconditions: the `nep141:doge.omft.near` PoA route must be used (a standard, unprivileged withdrawal). Attacker cost is trivial — any 26-34 character base58 string beginning with `D` or `A` with an arbitrary (non-matching) checksum tail satisfies the regex. No special privileges, RPC compromise, or relayer misbehavior needed; this is a pure client-side/library validation gap reachable by any SDK user or integrator forwarding a user-supplied destination address.

### Recommendation
Rewrite `validateDogeAddress` to decode the base58 payload and verify the double-SHA256 checksum and version byte, mirroring `validateBtcBase58Address`/`validateLitecoinBase58Address`/`validateDashAddress`:
- Decode with `base58.decode`.
- Require `decoded.length === 25`.
- Version byte `0x1e` (P2PKH, 'D...') or `0x16` (P2SH, 'A...') for Dogecoin mainnet.
- Compute `sha256(sha256(payload)).subarray(0,4)` and compare against the trailing 4 bytes.
- Return `false` on any exception or mismatch.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { base58 } from "@scure/base";
import { sha256 } from "@noble/hashes/sha2";
import { validateAddress } from "../src/lib/validateAddress";
import { Chains } from "../src/lib/caip2";
import { createWithdrawIntentPrimitive } from "../src/bridges/poa-bridge/poa-bridge-utils";

function craftBadChecksumDogeAddress(): string {
  const version = 0x1e; // Dogecoin P2PKH
  const payload = new Uint8Array(21);
  payload[0] = version;
  // arbitrary hash160 bytes
  crypto.getRandomValues(payload.subarray(1));
  const goodChecksum = sha256(sha256(payload)).subarray(0, 4);
  // Corrupt the checksum
  const badChecksum = Uint8Array.from(goodChecksum);
  badChecksum[0] ^= 0xff;
  const full = new Uint8Array(25);
  full.set(payload, 0);
  full.set(badChecksum, 21);
  return base58.encode(full);
}

describe("validateDogeAddress checksum bypass", () => {
  it("accepts a checksum-invalid Dogecoin address and embeds it in the withdrawal memo", () => {
    const badAddress = craftBadChecksumDogeAddress();

    // LHS: what validateAddress claims
    expect(validateAddress(badAddress, Chains.Dogecoin)).toBe(true);

    // RHS: whether it is actually a valid, spendable Dogecoin address (base58Check must hold)
    // (demonstrate manually that checksum fails)
    const decoded = base58.decode(badAddress);
    const payload = decoded.subarray(0, 21);
    const checksum = decoded.subarray(21, 25);
    const expected = sha256(sha256(payload)).subarray(0, 4);
    const checksumValid = checksum.every((b, i) => b === expected[i]);
    expect(checksumValid).toBe(false); // proves LHS != RHS

    const intent = createWithdrawIntentPrimitive({
      assetId: "nep141:doge.omft.near",
      destinationAddress: badAddress,
      destinationMemo: undefined,
      amount: 1000000n,
    });

    expect(intent.memo).toBe(`WITHDRAW_TO:${badAddress}`);
  });
});
```

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L329-331)
```typescript
function validateDogeAddress(address: string) {
	return /^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/.test(address);
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L178-188)
```typescript
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");

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
