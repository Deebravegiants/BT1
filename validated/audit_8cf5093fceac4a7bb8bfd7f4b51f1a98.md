### Title
Case-insensitive Bitcoin/Litecoin/BCH/Zcash bech32 addresses bypass the destination-matches-token-address safety check - ([File: packages/intents-sdk/src/lib/compareAddresses.ts])

### Summary
`OmniBridge.validateWithdrawal()` uses `compareAddresses()` to block withdrawals whose destination address is identical to the token's own bridged contract address on the destination chain. For Bitcoin-family chains (Bitcoin, Bitcoin Cash, Litecoin, Zcash, Dogecoin) `compareAddresses()` falls back to a raw string equality (`a === b`) that is case-sensitive, while `validateAddress()`/`validateBtcAddress()`/`validateLitecoinBech32Address()`/`validateBchCashAddr()` accept bech32/bech32m/CashAddr addresses in either upper- or lower-case as the *same* address (per BIP-173/CashAddr spec, they are normalized/lower-cased internally before decoding). A user can therefore submit the exact bridged-token address in a different letter case than the one the SDK computed, pass format validation, but slip past the "destination == token address" equality check that was specifically designed to stop this.

### Finding Description
`validateAddress()` in `packages/intents-sdk/src/lib/validateAddress.ts` treats bech32-style addresses as case-insensitive:
- `validateBtcAddress()` lower-cases the prefix check before decoding (`address.toLowerCase().startsWith("bc1")`) at line 131, and `bech32/bech32m.decode()` itself accepts either all-upper or all-lower case input.
- `validateLitecoinBech32Address()` does the same normalization (line 590/529-534).
- `validateBchCashAddr()` explicitly does `address.toLowerCase()` before validating the CashAddr checksum (lines 232-233), so an all-uppercase CashAddr is accepted as valid. [1](#0-0) [2](#0-1) 

However, `compareAddresses()` in `packages/intents-sdk/src/lib/compareAddresses.ts`, used to detect that a withdrawal is being sent to the bridge's own token contract, routes Bitcoin, BitcoinCash, Zcash, Dogecoin, and Litecoin (along with Near, Solana, Fogo, XRPL, Cardano, Aleo, Dash) through a plain `a === b` string comparison with **no case normalization**: [3](#0-2) 

This comparison is invoked from `OmniBridge.validateWithdrawal()`: [4](#0-3) 

The equality this code is supposed to enforce is: *"the destination address the user supplied is not equal to the token's own contract address on the destination chain."* Because `validateAddress()` (the format check the caller/UI relies on) and `compareAddresses()` (the actual safety comparison) disagree about what counts as "the same address" for bech32/CashAddr chains, a user can pass the token's real bridged address written with different letter-casing than what `getAddress(destTokenOmniAddress)` returns. `validateAddress()` will accept it as properly formatted, and `compareAddresses()` will report "not equal" (false negative) even though it decodes to the exact same on-chain address, so `DestinationAddressMatchesTokenAddressError` is never thrown and the withdrawal intent is built and submitted to the actual token/bridge connector address.

### Impact Explanation
This breaks the "address paid == address that was validated as safe" invariant: the recipient the on-chain intent actually pays is the bridge's own token contract address, not a genuine user-controlled address, despite the SDK's explicit guard intended to prevent exactly this. Since token/connector contracts generally cannot forward arbitrary incoming native-asset transfers without operator intervention, this results in a withdrawal "stuck until manual intervention" — one of the explicitly listed High-impact outcomes. It does not require any admin, relayer, or bridge-operator misbehavior; only the withdrawing user's own (possibly automated/attacker-crafted) input.

### Likelihood Explanation
Reaching this requires only calling the public SDK withdrawal flow (`sdk.processWithdrawal` / `estimateWithdrawalFee` → `OmniBridge.validateWithdrawal`) with a `destinationAddress` equal to the bridged token's address but in a different case — for `bc1.../ltc1.../bitcoincash:...` style addresses this is a trivial, well-formed input that legitimately decodes to the same 20/32-byte payload. No cryptographic guessing or race condition is needed; it is a deterministic string-casing choice.

### Recommendation
Normalize addresses before the raw-equality branch in `compareAddresses()` for every chain whose textual encoding is case-insensitive (Bitcoin/Litecoin bech32/bech32m, Bitcoin Cash CashAddr, Zcash `tex1`/`u1` bech32m). Concretely, decode both `a` and `b` through the same chain-specific decoder used by `validateAddress()` (extracting the underlying witness program / hash bytes) and compare the decoded bytes, exactly as is already done for TON, Tron, Aptos/Movement/Sui/Starknet, and EVM chains in the same file. Do not rely on literal string equality for any address format that has more than one valid textual representation.

### Proof of Concept
1. Suppose `destTokenAddress` (computed via `getAddress(destTokenOmniAddress)` in `omni-bridge.ts`) for a BTC-bridged token is `bc1qxyz...` (lower-case, as typically returned by address-encoding libraries).
2. Call the withdrawal flow with `withdrawalParams.destinationAddress = "BC1QXYZ..."` (the identical address, upper-cased).
3. `validateAddress(destinationAddress, Chains.Bitcoin)` → `validateBtcAddress()` lower-cases the prefix, decodes successfully via `bech32.decode()`, and returns `true` (valid format).
4. `compareAddresses(destTokenAddress, args.destinationAddress, Chains.Bitcoin)` executes the `a === b` branch: `"bc1qxyz..." === "BC1QXYZ..."` → `false`.
5. `DestinationAddressMatchesTokenAddressError` is not thrown; `validateWithdrawal()` proceeds and `createWithdrawalIntents()`/`deriveOmniWithdrawIntentParams()` build a real withdrawal intent paying the case-altered (but functionally identical) token/bridge address.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L129-138)
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
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L231-245)
```typescript
function validateBchCashAddr(address: string): boolean {
	// Normalize the address
	let normalized = address.toLowerCase();

	// Add prefix if missing
	if (!normalized.includes(":")) {
		normalized = `bitcoincash:${normalized}`;
	}

	// Must start with bitcoincash:
	if (!normalized.startsWith("bitcoincash:")) {
		return false;
	}

	const payload = normalized.slice("bitcoincash:".length);
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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L384-396)
```typescript
		const destTokenAddress = getAddress(destTokenOmniAddress);
		if (
			compareAddresses(
				destTokenAddress,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				destTokenAddress,
				args.assetId,
			);
		}
```
