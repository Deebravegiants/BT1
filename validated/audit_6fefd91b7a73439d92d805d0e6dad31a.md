### Title
`validateDogeAddress` accepts checksum-mutated Dogecoin addresses, allowing PoA withdrawal funds to be embedded in a `ft_withdraw` memo pointing to an unspendable address - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateDogeAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` (lines 329-331) is a bare regex `/^[DA][1-9A-HJ-NP-Za-km-z]{25,33}$/` with no base58Check decode or checksum verification, unlike every other base58-family validator in the same file (`validateBtcBase58Address`, `validateLitecoinBase58Address`, `validateTronBase58Address`, `validateDashAddress`), which all decode and verify the double-SHA256 checksum. This means a single flipped character in a valid Dogecoin address — still matching the charset/length regex — passes `validateAddress(addr, Chains.Dogecoin)` even though it decodes to a different, likely unspendable hash160 payload.

### Finding Description
The claimed broken equality: *"address embedded in the `ft_withdraw` memo" == "an address with a valid, checksum-decodable payload."* 

Trace:
- `PoaBridge.validateWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:170-188`) calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and only rejects when it returns `false` [1](#0-0) .
- For Dogecoin, `validateAddress` dispatches to `validateDogeAddress`, a bare regex with no checksum decode [2](#0-1) .
- Compare to the Bitcoin/Litecoin/Tron/Dash validators in the same file, all of which base58-decode and verify the double-SHA256 checksum before returning `true` [3](#0-2) [4](#0-3) .
- `PoaBridge.createWithdrawalIntents` builds the `ft_withdraw` intent via `createWithdrawIntentPrimitive`, which embeds `destinationAddress` verbatim into `memo: "WITHDRAW_TO:<address>"` with no further validation [5](#0-4) [6](#0-5) .

Because a single-character mutation within the same base58 alphabet at the same length still satisfies the regex, `validateDogeAddress` cannot distinguish a genuine address from a corrupted one. The relayer/off-chain bridge that eventually processes the `WITHDRAW_TO` memo has no way within this SDK's control to catch the error either, since the SDK is the only validation point exercised by this code path before the intent is signed.

### Impact Explanation
This is a Critical-severity finding under the stated categories: funds are delivered to an address that has no recoverable owner (no valid private key can correspond to a mutated hash160 with overwhelming probability), matching "funds delivered to a wrong address/chain/contract with no recovery." The signed `ft_withdraw` intent — an on-chain committed action with `receiver_id`, `amount`, and `memo` — carries the corrupted destination, and once broadcast the withdrawal cannot be reversed. This is repeatable for every Dogecoin withdrawal where the destination address string has been corrupted (accidentally, via encoding bugs, or via a malicious counterparty supplying an integrator-forwarded `destinationAddress`), since the flaw is deterministic in the validator, not probabilistic per call.

### Likelihood Explanation
Preconditions are minimal: any caller of `PoaBridge`/`IntentsSDK` withdrawal flow with `assetId: 'nep141:doge.omft.near'` and a `destinationAddress` that is a corrupted (but same-length, same-charset) Dogecoin address will pass validation. No special permissions or contract interaction are required beyond normal SDK usage. This matches the rules' definition of an ordinary attacker/integrator scenario — a counterparty-supplied `destinationAddress` string forwarded by an integrator into `withdrawalParams.destinationAddress`.

### Recommendation
Implement full base58Check verification in `validateDogeAddress`, mirroring `validateBtcBase58Address`/`validateLitecoinBase58Address`/`validateDashAddress`: base58-decode the address, confirm total length is 25 bytes (version + 20-byte hash160 + 4-byte checksum), confirm the version byte matches Dogecoin's mainnet P2PKH (`0x1e`) or P2SH (`0x16`) prefixes, and verify the trailing 4 bytes equal the first 4 bytes of `sha256(sha256(payload))`.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/validateAddress.spec.ts (illustrative, mocks only HTTP-free logic)
import { validateAddress } from "./validateAddress";
import { Chains } from "./caip2";
import { createWithdrawIntentPrimitive } from "../bridges/poa-bridge/poa-bridge-utils";

it("rejects a Dogecoin address with a single mutated character (broken checksum)", () => {
  const validDoge = "D8AQmYBSFoPitwZmEXcbxRTQuLKYPUFqPy"; // valid, well-formed base58Check DOGE address
  // flip one interior character while preserving charset & length
  const mutatedDoge = "D8AQmYBSFoPitwZmEXcbxRTQuLKYPUFqPz";

  // Both currently return true because there is no checksum check:
  expect(validateAddress(validDoge, Chains.Dogecoin)).toBe(true);
  expect(validateAddress(mutatedDoge, Chains.Dogecoin)).toBe(true); // BUG: should be false

  const intent = createWithdrawIntentPrimitive({
    assetId: "nep141:doge.omft.near",
    destinationAddress: mutatedDoge,
    destinationMemo: undefined,
    amount: 1000000n,
  });

  // Memo embeds the unrecoverable, checksum-invalid address with no rejection anywhere in the path
  expect(intent.memo).toBe(`WITHDRAW_TO:${mutatedDoge}`);
});
```
Both sides of the claimed equality diverge: `mutatedDoge` is accepted by `validateAddress`/`validateDogeAddress`, and the same string is what ends up signed inside the `ft_withdraw` memo via `createWithdrawIntentPrimitive`, confirming the destination-truth violation.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L142-162)
```typescript
	createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
	}): Promise<IntentPrimitive[]> {
		const relayerFee = getUnderlyingFee(
			args.feeEstimation,
			RouteEnum.PoaBridge,
			"relayerFee",
		);
		assert(
			relayerFee >= 0n,
			`Invalid POA bridge relayer fee: expected >= 0, got ${relayerFee}`,
		);

		const intent = createWithdrawIntentPrimitive({
			...args.withdrawalParams,
			amount: args.withdrawalParams.amount + relayerFee,
			destinationMemo: args.withdrawalParams.destinationMemo,
		});
		return Promise.resolve([intent]);
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
