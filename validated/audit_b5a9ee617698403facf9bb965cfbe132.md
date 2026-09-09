### Title
Litecoin address validator accepts Bitcoin P2SH addresses, allowing LTC withdrawals to be silently routed to a Bitcoin-only address - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateLitecoinAddress` treats any base58check string with version byte `0x05` and prefix `3` as a valid Litecoin legacy P2SH address, but that exact encoding (version `0x05`, prefix `3`) is also the standard Bitcoin P2SH format, and nothing in the withdrawal path distinguishes the two chains. `PoaBridge.validateWithdrawal` relies solely on `validateAddress(destinationAddress, assetInfo.blockchain)` for the `nep141:ltc.omft.near` route, so a caller can submit a real Bitcoin address as the Litecoin withdrawal destination and it will be encoded unchanged into the intent memo and sent to the PoA custodian.

### Finding Description
The broken equality is: *the chain the funds are custodied/paid on (Litecoin)* should equal *the chain the destination address actually belongs to/is spendable on*. For the `3...`/`0x05` branch these diverge.

- `validateLitecoinAddress` (`packages/intents-sdk/src/lib/validateAddress.ts:506-535`) special-cases `first === "3"` and calls `validateLitecoinBase58Address(address, 0x05)` (lines 521-525), explicitly commented `"[Inference] This also matches Bitcoin P2SH; cannot distinguish by prefix+version alone."`
- `validateBtcBase58Address` (lines 140-158) accepts the identical base58check encoding: version byte `0x00` or `0x05`, 25-byte length, valid double-SHA256 checksum — i.e. the exact same bytes that satisfy `validateLitecoinBase58Address(address, 0x05)`.
- Therefore any syntactically valid Bitcoin P2SH address (e.g. `3GoitrULXWigQqj4fV6FMVqtz8mru5auYh`) passes both `validateAddress(addr, Chains.Bitcoin)` and `validateAddress(addr, Chains.Litecoin)`.
- `PoaBridge.validateWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:170-188`) performs exactly one format check: `validateAddress(args.destinationAddress, assetInfo.blockchain) === false` → throw. There is no additional network-specific check (no RPC lookup, no checksum-network distinction) for Litecoin the way there is for XRPL (lines 232-257).
- If it passes, `createWithdrawalIntents` (lines 142-162) calls `createWithdrawIntentPrimitive` (`poa-bridge-utils.ts:6-26`), which places `params.destinationAddress` verbatim into the `WITHDRAW_TO:<address>` memo (`createWithdrawMemo`, lines 28-49) with no chain-specific re-encoding.
- Since `Chains.Litecoin` maps to `ltc:mainnet` (`toPoaNetwork`/`caip2Mapping`, `poa-bridge-utils.ts:65`), the PoA custodian processes this as a Litecoin-network payout instruction with a Bitcoin-only address string baked into the memo.

No other guard in the reachable path (`compareAddresses`, `MinWithdrawalAmountError`, `supports()` ordering, `assert` checks, contract-level signature/nonce verification) inspects whether the destination address is genuinely spendable on the target chain; they only compare against the token's own `origin_chain_address` or amount thresholds.

### Impact Explanation
An unprivileged NEAR Intents user (or an integrator relaying a counterparty-supplied `destinationAddress`) can cause `nep141:ltc.omft.near` withdrawal intents to be signed, submitted, and executed by the PoA Litecoin custodian with a destination address that is only valid/spendable on the Bitcoin network. Litecoin's UTXO set and Bitcoin's UTXO set are disjoint networks; a Litecoin-network payout to a base58 `3...`/`0x05` string cannot be swept by whoever controls the corresponding Bitcoin private key on Bitcoin, and is not recoverable through this SDK once broadcast. This matches the **Critical** category: funds delivered to a wrong chain with no recovery path via the SDK, and is repeatable for every LTC withdrawal call.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: PoA route, `nep141:ltc.omft.near` asset, and any valid Bitcoin P2SH address (trivially available/generatable, no special cost). No relayer, RPC, or contract-admin collusion is needed — the caller only needs to invoke `createWithdrawalIntents`/`validateWithdrawal` with `destinationAddress` set to a real BTC P2SH string. This is fully reproducible offline against `validateAddress.ts` and `poa-bridge.ts` without needing live network state (the check is pure format validation).

### Recommendation
Remove or gate the ambiguous `first === "3"` / version `0x05` branch in `validateLitecoinAddress`, since it cannot be distinguished from Bitcoin P2SH by format alone. If legacy `3...` LTC P2SH support is required, require an out-of-band signal (e.g., explicit user/integrator chain confirmation, or reject entirely and require the modern `M...` P2SH / `ltc1...` bech32 formats) rather than silently accepting a string that is simultaneously valid on Bitcoin.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { validateAddress } from "../src/lib/validateAddress";
import { Chains } from "../src/lib/caip2";

describe("Litecoin/Bitcoin P2SH address collision", () => {
  it("accepts the same base58 string as both LTC and BTC destinations", () => {
    const addr = "3GoitrULXWigQqj4fV6FMVqtz8mru5auYh"; // real Bitcoin P2SH, version 0x05

    expect(validateAddress(addr, Chains.Bitcoin)).toBe(true);
    expect(validateAddress(addr, Chains.Litecoin)).toBe(true); // should be false/rejectable
  });
});
```
Follow-up integration test (mocking only the PoA `getSupportedTokens` HTTP call):
```ts
const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });
vi.mocked(poaBridge.httpClient.getSupportedTokens).mockResolvedValueOnce({
  tokens: [{ intents_token_id: "nep141:ltc.omft.near", min_withdrawal_amount: "1", /* ...other fields "" */ }],
});

await expect(bridge.validateWithdrawal({
  assetId: "nep141:ltc.omft.near",
  amount: 1000n,
  destinationAddress: "3GoitrULXWigQqj4fV6FMVqtz8mru5auYh",
})).resolves.toBeUndefined(); // currently passes — should throw

const intents = await bridge.createWithdrawalIntents({
  withdrawalParams: { assetId: "nep141:ltc.omft.near", amount: 1000n, destinationAddress: "3GoitrULXWigQqj4fV6FMVqtz8mru5auYh" },
  feeEstimation: { amount: 0n, underlyingFees: {} },
});
expect(intents[0].memo).toContain("WITHDRAW_TO:3GoitrULXWigQqj4fV6FMVqtz8mru5auYh"); // BTC address encoded unchanged into LTC-route intent
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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L506-525)
```typescript
export function validateLitecoinAddress(address: string): boolean {
	const first = address[0];

	// ---- Base58 (mainnet) ----

	// P2PKH: L... (0x30)
	if (first === "L") {
		return validateLitecoinBase58Address(address, 0x30);
	}

	// P2SH (new): M... (0x32)
	if (first === "M") {
		return validateLitecoinBase58Address(address, 0x32);
	}

	// P2SH (legacy): 3... (0x05)
	// [Inference] This also matches Bitcoin P2SH; cannot distinguish by prefix+version alone.
	if (first === "3") {
		return validateLitecoinBase58Address(address, 0x05);
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L51-76)
```typescript
const caip2Mapping = {
	[Chains.Ethereum]: "eth:1",
	[Chains.Base]: "eth:8453",
	[Chains.Arbitrum]: "eth:42161",
	[Chains.Bitcoin]: "btc:mainnet",
	[Chains.BitcoinCash]: "bch:mainnet",
	[Chains.Dogecoin]: "doge:mainnet",
	[Chains.XRPL]: "xrp:mainnet",
	[Chains.Gnosis]: "eth:100",
	[Chains.Berachain]: "eth:80094",
	[Chains.Tron]: "tron:mainnet",
	[Chains.Sui]: "sui:mainnet",
	[Chains.Movement]: "movement:mainnet",
	[Chains.Cardano]: "cardano:mainnet",
	[Chains.Litecoin]: "ltc:mainnet",
	[Chains.Aleo]: "aleo:mainnet",
	[Chains.Dash]: "dash:mainnet",
	[Chains.Plasma]: "eth:9745",
	[Chains.Adi]: "eth:36900",
} satisfies Record<
	string,
	(typeof poaBridge.PoaBridgeNetworkReference)[Exclude<
		keyof typeof poaBridge.PoaBridgeNetworkReference,
		"NEAR" | "POLYGON" | "BSC" | "MONAD" | "FOGO"
	>]
>;
```
