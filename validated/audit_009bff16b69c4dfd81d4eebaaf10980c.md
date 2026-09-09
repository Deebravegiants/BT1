### Title
`validateDogeAddress` accepts base58 strings with an invalid checksum, allowing signed withdrawals to unspendable Dogecoin addresses - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateDogeAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` validates Dogecoin destination addresses using only a regex on the character set/length, unlike every other base58-based address validator in the same file, which decode the address and verify the double-SHA256 checksum. This lets `PoaBridge.validateWithdrawal` accept a syntactically well-formed but checksum-invalid Doge address and proceed to sign/build a withdrawal intent that embeds that address verbatim in the `ft_withdraw` memo.

### Finding Description
The broken equality is: **the address accepted by `validateAddress(address, Chains.Dogecoin)` == a real, checksum-valid, spendable Dogecoin address**. This equality is not enforced.

`validateDogeAddress` is:
```ts
function validateDogeAddress(address: string) {
	return /^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/.test(address);
}
``` [1](#0-0) 

This is the only base58-family validator in the file that skips checksum verification. Contrast with `validateBtcBase58Address`, `validateLitecoinBase58Address`, `validateTronBase58Address`, and `validateDashAddress`, all of which decode the base58 payload and recompute/verify `sha256(sha256(payload)).subarray(0,4)` against the trailing 4 checksum bytes: [2](#0-1) [3](#0-2) 

The call path is: `PoaBridge.validateWithdrawal` calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and only rejects on `false` (regex mismatch), throwing `InvalidDestinationAddressForWithdrawalError` otherwise it proceeds: [4](#0-3) 

Assuming the address passes the checksum-agnostic regex and other checks (`origin_chain_address` mismatch, min-amount, etc. — none of which perform checksum validation either), `createWithdrawIntentPrimitive` embeds the raw, unverified address string into the `ft_withdraw` memo as `WITHDRAW_TO:<address>`: [5](#0-4) [6](#0-5) 

None of `compareAddresses`, the min-withdrawal check, or the assetId/token lookup logic in `validateWithdrawal` perform any checksum decoding for Doge; they operate on the already-accepted string. Nothing downstream re-derives or re-validates the checksum before the intent is signed. The intents contract itself only verifies signatures/nonces on the NEAR intent structure — it has no knowledge of Dogecoin base58 checksums and cannot catch this.

Attacker input: any string matching `/^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/` (e.g., take a valid Doge address and flip one trailing base58 character to break only the checksum bytes while keeping the regex-visible charset/length valid).

### Impact Explanation
A user (or an integrator forwarding a counterparty-controlled `destinationAddress`) can cause `validateWithdrawal` to resolve successfully for a Dogecoin withdrawal whose destination address is not a real, checksum-valid address. The signed NEAR intent's `ft_withdraw` memo (`WITHDRAW_TO:<corrupted-address>`) is what the relayer/bridge uses off-chain to resolve payout. Once the intent is signed on NEAR and funds are debited, the Dogecoin payout leg will fail to resolve to a real on-chain destination (the relayer cannot construct a valid Dogecoin output script for the address, since the checksum is invalid). This matches "funds delivered to a wrong address/chain/contract with no recovery" (Critical) — the on-chain NEAR debit occurs and executes with a memo that cannot be honored on the Dogecoin side within this repo's own address-format guarantee, and there is no re-validation step to catch it before signing.

Note: the actual on-chain execution correctness of the relayer's payout mechanism is outside this repo's control (out of scope per the rules), but the specific bug in scope is that **this SDK's own validation function**, whose entire purpose is to catch invalid destination addresses before signing, fails to do so for Doge specifically, unlike its BTC/LTC/Dash/Tron siblings.

### Likelihood Explanation
- Preconditions: PoA route, `assetId: 'nep141:doge.omft.near'`, attacker supplies any `destinationAddress` matching the Doge regex with a corrupted checksum.
- Attacker cost: trivial — construct or mutate a base58 string; no special privileges needed, matches the "unprivileged attacker" threat model (ordinary user or counterparty providing `destinationAddress`).
- Feasibility: high, since `validateWithdrawal` is a public, always-reachable SDK entry point in the withdrawal flow, and no other check in the code path performs checksum validation for Doge.
- Repeatable: yes, per call, with no rate limiting relevant to this specific defect.

### Recommendation
Rewrite `validateDogeAddress` to decode the base58 payload and verify the version byte (`0x1E` for `D...` P2PKH mainnet, or the appropriate P2SH version) and the double-SHA256 checksum, mirroring `validateBtcBase58Address` / `validateDashAddress`:
```ts
function validateDogeAddress(address: string): boolean {
	try {
		const decoded = base58.decode(address);
		if (decoded.length !== 25) return false;
		const version = decoded[0];
		if (version !== 0x1e /* P2PKH */ && version !== 0x16 /* P2SH */) return false;
		const payload = decoded.subarray(0, 21);
		const checksum = decoded.subarray(21, 25);
		const expectedChecksum = sha256(sha256(payload)).subarray(0, 4);
		for (let i = 0; i < 4; i++) if (checksum[i] !== expectedChecksum[i]) return false;
		return true;
	} catch {
		return false;
	}
}
```

### Proof of Concept
Vitest test plan (mocks only HTTP, per rules):
```ts
import { describe, it, expect, vi } from "vitest";
import { PoaBridge } from "../../bridges/poa-bridge/poa-bridge";
import { InvalidDestinationAddressForWithdrawalError } from "../../classes/errors";
import { configsByEnvironment } from "@defuse-protocol/internal-utils";
import { configureXrplRpcUrls } from "../../lib/configure-rpc-config";
import { PUBLIC_XRPL_RPC_URLS } from "../../constants/public-rpc-urls";

it("rejects a checksum-invalid but regex-valid Doge address", async () => {
  const bridge = new PoaBridge({
    envConfig: configsByEnvironment.production,
    xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
  });

  // Valid Doge address from existing test suite: "D86DwJpYsyV7nTP2ib5qdwGsb2Tj7LgzPP"
  // Flip last character to corrupt checksum bytes while keeping charset/length valid.
  const corruptedAddress = "D86DwJpYsyV7nTP2ib5qdwGsb2Tj7LgzPQ";

  // LEFT side of equality: what validateAddress/validateWithdrawal currently accepts
  // RIGHT side: whether this is a real checksum-valid Dogecoin address (it is not)
  await expect(
    bridge.validateWithdrawal({
      amount: 50000000000n,
      assetId: "nep141:doge.omft.near",
      destinationAddress: corruptedAddress,
    }),
  ).rejects.toThrow(InvalidDestinationAddressForWithdrawalError);
  // Currently this resolves() instead of rejecting — demonstrating the bug.
});
```
This test asserts the two sides of the broken equality directly: it expects `validateWithdrawal` to reject on checksum-invalid input (right side: real spendable address), whereas current behavior is that it resolves because `validateDogeAddress` only checks the regex (left side: any charset/length-matching string), proving the divergence.

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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L801-830)
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L177-188)
```typescript
	}): Promise<void> {
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
