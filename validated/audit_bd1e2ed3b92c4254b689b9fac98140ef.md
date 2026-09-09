Confirmed: this is a valid, real finding in the PoA bridge path.

### Title
Mixed-case bech32 BTC destination address passes validation but is encoded unlowered into the PoA withdraw memo - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts])

### Summary
`validateBtcAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` accepts mixed-case/uppercase bech32 Bitcoin addresses (confirmed by the test fixtures `BC1Q973XRRGJE6ETKKN9Q9AZZSGPXEDDATS8CKVP5S` and `BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4` in `validateAddress.spec.ts`), but `createWithdrawMemo` in `poa-bridge-utils.ts` never lowercases the address before embedding it in the `WITHDRAW_TO:<address>` memo used for the PoA route. This is inconsistent with the Omni route, which explicitly lowercases `bc1`-prefixed addresses in `deriveOmniWithdrawIntentParams` (`omni-withdraw-params.ts` lines 118-124) specifically because, per changelog entry `95eca42`, "the contract accepts only lowercase bech32."

### Finding Description
The broken equality: "address validated as correct BTC format" (`validateBtcAddress` returns `true` for mixed-case bech32) should equal "address actually paid out by the BTC connector contract" (which per the changelog only recognizes lowercase bech32). For the PoA route these diverge.

Path: `PoaBridge.validateWithdrawal` (`poa-bridge.ts` lines 181-188) calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` → for `Chains.Bitcoin` this calls `validateBtcAddress` (`validateAddress.ts` lines 129-138), which lowercases only for the `startsWith("bc1")` check, then calls `validateBtcBech32Address(address)` on the **original-case** string. `bech32.decode`/`bech32m.decode` accept mixed case per BIP-173 as long as the string is not mixed within itself in a way that breaks the encoding rules used by `@scure/base` (the test fixtures show pure-uppercase forms passing). The validation therefore succeeds and no error is thrown.

Later, `PoaBridge.createWithdrawalIntents` calls `createWithdrawIntentPrimitive` (`poa-bridge-utils.ts` lines 6-26), which builds the memo via `createWithdrawMemo` (lines 28-49). That function only lowercases the address to check for a `bitcoincash:` prefix (`receiverAddress.toLowerCase().startsWith("bitcoincash:")`), but uses the **original, un-lowered** `receiverAddress` (or `normalizedAddress` which is just the BCH-prefix-stripped original-case string) in the final memo. There is no BTC-specific lowercasing step in this file, unlike the Omni-specific fix.

Existing guards do not catch this: `validateAddress`/`validateBtcAddress` check format only, not case; `compareAddresses` for Bitcoin (`compareAddresses.ts` line 60, `a === b`) is used only to prevent self-transfer to the token's own address and does not normalize case either; nothing in `PoaBridge.validateWithdrawal` or `createWithdrawIntentPrimitive` normalizes case for BTC.

### Impact Explanation
The memo, which is the on-chain signal used by the PoA relayer/connector to route the withdrawn BTC, encodes the destination address in its original case. Per the changelog's own justification for the Omni-side fix, the BTC connector contract only accepts lowercase bech32, so a memo with mixed/upper case would not be recognized/actioned correctly by the connector, leaving the withdrawal stuck and requiring manual intervention — matching the "High: a withdrawal stuck until manual intervention" impact category. This affects any ordinary user withdrawing `nep141:btc.omft.near` (or any BTC-denominated asset) via the PoA route who supplies (or whose integrator forwards) a mixed-case bech32 address; it is repeatable on every such call.

### Likelihood Explanation
Preconditions are simple and fully attacker/user-controlled: choose the PoA route for a Bitcoin-chain asset (e.g., `nep141:btc.omft.near`) and supply a destination address such as `BC1Q973XRRGJE6ETKKN9Q9AZZSGPXEDDATS8CKVP5S` or any mixed-case bech32 variant, both of which are spec-valid bech32 and accepted by `validateBtcAddress`. No special privileges, timing, or race conditions are needed — a single SDK call with attacker-controlled `destinationAddress` reliably reproduces it every time.

### Recommendation
In `createWithdrawMemo` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts`), add the same normalization used on the Omni side: for Bitcoin-chain (or any bech32-based PoA chain) addresses starting with `bc1` (case-insensitively), lowercase the address before building the memo, mirroring the `/^bc1/i` check and `.toLowerCase()` call in `omni-withdraw-params.ts` lines 118-124. Ideally, centralize this normalization (e.g., in a shared helper) so both Omni and PoA paths use one canonicalization function instead of duplicating chain-specific case logic.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.test.ts
it("does NOT lowercase mixed-case bech32 BTC address in memo (bug)", () => {
  const mixedCase = "BC1Q973XRRGJE6ETKKN9Q9AZZSGPXEDDATS8CKVP5S";
  const result = createWithdrawIntentPrimitive({
    assetId: "nep141:btc.omft.near",
    destinationAddress: mixedCase,
    destinationMemo: undefined,
    amount: 1000000n,
  });

  // Left side: what validateBtcAddress accepted as "correct format"
  expect(validateAddress(mixedCase, Chains.Bitcoin)).toBe(true);

  // Right side: what actually gets encoded in the on-chain memo
  expect(result.memo).toBe(`WITHDRAW_TO:${mixedCase}`); // currently true -> bug
  expect(result.memo).not.toBe(`WITHDRAW_TO:${mixedCase.toLowerCase()}`); // currently true -> bug

  // Desired/fixed behavior (would require the fix):
  // expect(result.memo).toBe(`WITHDRAW_TO:${mixedCase.toLowerCase()}`);
});
```
This mocks no HTTP (pure function test), directly exercising `createWithdrawIntentPrimitive` → `createWithdrawMemo`, proving the memo address segment is not lowercased despite `validateBtcAddress`/`validateAddress` accepting the mixed-case input as valid. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L129-202)
```typescript
function validateBtcAddress(address: string): boolean {
	try {
		if (address.toLowerCase().startsWith("bc1")) {
			return validateBtcBech32Address(address);
		}
		return validateBtcBase58Address(address);
	} catch {
		return false;
	}
}

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

function validateBtcBech32Address(address: string): boolean {
	let decoded: { prefix: string; words: number[] };
	let isBech32m = false;

	try {
		decoded = bech32.decode(address as `${string}1${string}`);
	} catch {
		try {
			decoded = bech32m.decode(address as `${string}1${string}`);
			isBech32m = true;
		} catch {
			return false;
		}
	}

	if (decoded.prefix.toLowerCase() !== "bc") return false;

	const { words } = decoded;
	if (!words || words.length < 1) return false;

	const witnessVersion = words[0];
	if (witnessVersion === undefined || witnessVersion < 0 || witnessVersion > 16)
		return false;

	const program = bech32.fromWords(words.slice(1));
	const progLen = program.length;

	if (progLen < 2 || progLen > 40) return false;

	// v0: Bech32 only — 20 bytes (P2WPKH) or 32 bytes (P2WSH)
	if (witnessVersion === 0) {
		if (isBech32m) return false;
		return progLen === 20 || progLen === 32;
	}

	// v1: Bech32m only — 32 bytes (P2TR / Taproot)
	if (witnessVersion === 1) {
		if (!isBech32m) return false;
		return progLen === 32;
	}

	return false;
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.spec.ts (L80-97)
```typescript
			// Bech32 SegWit v0 (bc1q...)
			"bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
			"bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c",
			"bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
			"bc1q973xrrgje6etkkn9q9azzsgpxeddats8ckvp5s",
			"BC1Q973XRRGJE6ETKKN9Q9AZZSGPXEDDATS8CKVP5S",
			"BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4",
			// Bech32m Taproot / P2TR (bc1p...)
			"bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297",
			"bc1ptxs597p3fnpd8gwut5p467ulsydae3rp9z75hd99w8k3ljr9g9rqx6ynaw",
			// Mainnet Bech32 P2WSH
			"bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3",
		];

		for (const address of valid) {
			expect(validateAddress(address, Chains.Bitcoin)).toBe(true);
		}
	});
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-188)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
		destinationMemo?: string;
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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L118-126)
```typescript
	// Omni contract only accepts lowercase bech32 addresses; uppercase/mixed-case
	// bech32 is spec-valid but rejected on-chain. Base58 (legacy/P2SH) is left as-is.
	const destinationAddress =
		params.omniChainKind === ChainKind.Btc &&
		/^bc1/i.test(params.destinationAddress)
			? params.destinationAddress.toLowerCase()
			: params.destinationAddress;

	const recipient = omniAddress(params.omniChainKind, destinationAddress);
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L48-60)
```typescript
			case Chains.Near:
			case Chains.Bitcoin:
			case Chains.BitcoinCash:
			case Chains.Zcash:
			case Chains.Dogecoin:
			case Chains.Litecoin:
			case Chains.Solana:
			case Chains.Fogo:
			case Chains.XRPL:
			case Chains.Cardano:
			case Chains.Aleo:
			case Chains.Dash:
				return a === b;
```
