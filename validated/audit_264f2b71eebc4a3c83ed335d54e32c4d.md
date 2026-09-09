### No vulnerability found for this question.

**Analysis supporting this conclusion:**

The claimed equality is: for every string `s` where `validateAddress(s, 'solana:...')` returns true, the payout address the Omni Bridge connector uses on the destination chain must equal `s`. Tracing the code path shows this equality holds and is never broken by this repo's code.

`validateSolAddress` only checks that the string decodes as base58 to exactly 32 bytes (and isn't the system program address), which is the correct format check for any Solana account, PDA or otherwise [1](#0-0) .

In `deriveOmniWithdrawIntentParams`, the `destinationAddress` string is forwarded unchanged (aside from a Bitcoin-only lowercase normalization that does not apply to Solana) into `omniAddress(params.omniChainKind, destinationAddress)` [2](#0-1) . `omniAddress` simply prefixes the chain kind onto the exact same address string — it performs no hashing, truncation, or reinterpretation of the bytes. This is confirmed by the test suite, which asserts the emitted `recipient` in the `ft_withdraw` msg equals `omniAddress(ChainKind.Sol, destinationAddress)` built from the *same* user-supplied string [3](#0-2) , and `createWithdrawalIntents` in `OmniBridge` calls this same derivation without further transformation [4](#0-3) .

So the byte-for-byte 32-byte account encoded in the `recipient` field is identical to what the user supplied as `destinationAddress`. Whether the Solana-side Omni Bridge connector program can successfully create/credit an SPL associated token account (ATA) for an off-curve PDA owner is a property of the on-chain connector program, not of this SDK — and off-curve addresses (PDAs) are a normal, supported class of Solana account for owning ATAs; deriving an ATA does not require the owner to be on-curve. There is no divergence introduced inside `packages/intents-sdk` between the address the user controls and the address encoded in the intent, and any question of whether the destination-chain connector can pay out to that specific PDA is explicitly out of scope ("defects inside intents.near, bridge contracts or third-party SDKs with no path through this repo").

No broken equality exists in the SDK code covered by this question.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L312-327)
```typescript
function validateSolAddress(address: string) {
	try {
		if (address === "11111111111111111111111111111111") {
			return false;
		}
		const decoded = base58.decode(address);
		// Solana addresses are raw 32-byte ed25519 public keys, no checksum bytes included
		if (decoded.length !== 32) {
			return false;
		}

		return true;
	} catch {
		return false;
	}
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

**File:** packages/intents-sdk/src/sdk.test.ts (L1476-1490)
```typescript
		const destinationAddress = "39hqXivfCPUSqmXAaX3eo4JcA5bGFXhhs26dmg585DGb";
		const withdrawalParams = {
			assetId: "nep141:sol-c58e6539c2f2e097c251f8edf11f9c03e581f8d4.omft.near",
			amount: 6500n,
			destinationAddress,
			feeInclusive: false,
		};

		const intents = sdk.createWithdrawalIntents({
			withdrawalParams,
			feeEstimation,
		});

		const actualAmount = withdrawalParams.amount;
		const recipient = omniAddress(ChainKind.Sol, destinationAddress);
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L316-327)
```typescript
		intents.push(
			...createWithdrawIntentsPrimitive(
				deriveOmniWithdrawIntentParams({
					assetId: args.withdrawalParams.assetId,
					destinationAddress: args.withdrawalParams.destinationAddress,
					actualAmount: args.withdrawalParams.amount,
					omniChainKind,
					intentsContract: this.envConfig.contractID,
					feeEstimation: args.feeEstimation,
				}),
			),
		);
```
