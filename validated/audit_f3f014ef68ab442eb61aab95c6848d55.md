### Title
Case-sensitive raw-string comparison for Litecoin lets `compareAddresses` miss token-address matches, bypassing `DestinationAddressMatchesTokenAddressError` - (File: `packages/intents-sdk/src/lib/compareAddresses.ts`)

### Summary
`compareAddresses` compares Litecoin (and Bitcoin, Dogecoin, Zcash, Solana, XRPL, Cardano, Aleo, Dash) addresses with plain `a === b`, while `validateLitecoinAddress` accepts Bech32/Bech32m `ltc1…` addresses whose HRP is checked case-insensitively (`decoded.prefix.toLowerCase() !== "ltc"`). Per BIP-173, an all-uppercase Bech32 string decodes to the exact same witness program as its all-lowercase form, so a same-address-different-case string can pass `validateAddress` but fail the `a === b` equality check in `compareAddresses`, letting `validateWithdrawal` in `poa-bridge.ts` skip the `DestinationAddressMatchesTokenAddressError` guard.

### Finding Description
`compareAddresses` (packages/intents-sdk/src/lib/compareAddresses.ts, lines 48-60) canonicalizes addresses for EVM, hex-field, TON, Tron, and Stellar chains before comparing, but for `Chains.Litecoin` (and the other chains grouped in the same `case`) it falls back to raw string equality: [1](#0-0) 

`validateLitecoinAddress` (packages/intents-sdk/src/lib/validateAddress.ts, lines 506-618) accepts Bech32/Bech32m SegWit addresses (`ltc1…`) and normalizes the HRP case before validating: [2](#0-1) 

`validateWithdrawal` in `poa-bridge.ts` calls `validateAddress` to accept the destination, then relies on `compareAddresses(tokenInfo.origin_chain_address, args.destinationAddress, assetInfo.blockchain)` to block sending to the token's own address: [3](#0-2) 

If `tokenInfo.origin_chain_address` were a Bech32 Litecoin address, an attacker submitting the same address with different casing (e.g. all uppercase) would pass `validateAddress` (case-insensitive HRP check) but fail `compareAddresses`'s raw `a === b` string check, since the strings differ in case even though they decode to the identical witness program. This would bypass `DestinationAddressMatchesTokenAddressError` and let the withdrawal proceed to the token's own address.

However, this specific scenario requires a Litecoin token whose `origin_chain_address` is a non-`"native"` on-chain contract-style address. Litecoin has no smart-contract/token layer; PoA-bridged Litecoin assets are native LTC, and the code explicitly special-cases `tokenInfo.origin_chain_address !== "native"` to skip the check entirely for native assets. I could not confirm from the available API/test data that any Litecoin-route `origin_chain_address` is ever a non-native Bech32 value — the `poa-bridge.test.ts` file (which exercises `origin_chain_address`) does not contain a Litecoin/Bech32 case in what I was able to inspect, and this is fetched dynamically from `poaBridge.httpClient.getSupportedTokens`, outside repo control.

### Impact Explanation
If reachable, the impact would match the stated Critical class (funds delivered to a wrong/unrecoverable address) — a withdrawal intended to be blocked from targeting the token's own address would go through, with the tokens routed to the token's own account on the destination chain and lost. Repeatable per-call for any Litecoin asset whose token/origin address is exposed as a case-flippable Bech32 string.

### Likelihood Explanation
The precondition — a Litecoin-route token with `origin_chain_address` being a genuine on-chain address (not `"native"`) encoded as Bech32 — does not appear to exist in this codebase given Litecoin's lack of a token/contract standard; the native-LTC path is explicitly excluded via the `!== "native"` guard. Without concrete evidence of a non-native Litecoin `origin_chain_address` from the bridge API, this narrows to a defense-in-depth gap in `compareAddresses`'s raw-string fallback rather than a demonstrated exploitable path for Litecoin specifically.

### Recommendation
Regardless of current reachability for Litecoin, harden `compareAddresses` for chains using the raw `a === b` branch (`Chains.Bitcoin`, `Chains.Litecoin`, `Chains.Dogecoin`, `Chains.Zcash`, etc.) by normalizing Bech32/Bech32m addresses (lowercase HRP + data part, or re-encode from decoded witness program) before comparison, mirroring the canonicalization already done for TON/Tron/Stellar/hex chains.

### Proof of Concept
Not constructed as a full reproducible test because the precondition (a non-native Litecoin `origin_chain_address` returned by the PoA bridge API) could not be confirmed to exist in this repo's data or tests; the vitest plan would be:
1. Mock `poaBridge.httpClient.getSupportedTokens` to return a Litecoin token with `origin_chain_address = "ltc1q..."` (lowercase Bech32) and `intents_token_id` matching a test `assetId`.
2. Call `PoaBridge.validateWithdrawal` with `destinationAddress` equal to the same address but uppercased (`"LTC1Q..."`).
3. Assert `validateAddress(destinationAddress, Chains.Litecoin)` returns `true`.
4. Assert `compareAddresses(origin_chain_address, destinationAddress, Chains.Litecoin)` returns `false` (case mismatch).
5. Assert `validateWithdrawal` resolves without throwing `DestinationAddressMatchesTokenAddressError`, confirming the bypass — contingent on the API actually surfacing such a token, which is unverified here.

### Citations

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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L588-590)
```typescript

	// HRP must be "ltc" (case-insensitive)
	if (decoded.prefix.toLowerCase() !== "ltc") return false;
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L207-219)
```typescript
		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}
```
