### Title
`validateCardanoAddress` accepts pointer-address subtypes (`addrType` 4/5) despite only claiming to support Base + Enterprise addresses - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateCardanoAddress` decodes any bech32 `addr1...` string and accepts it as valid whenever the header nibble `addrType` is in `0..7`, but its own docstring says it only supports Base and Enterprise address types. [1](#0-0)  Types 4 and 5 are pointer addresses, a distinct Cardano address kind not mentioned as supported, so the format-level acceptance is broader than the function's documented/intended scope.

### Finding Description
The equality that should hold is: *address format accepted by `validateAddress(dest, Chains.Cardano)`* == *address format the PoA Cardano route can actually credit (Base + Enterprise, per the function's own doc comment)*. The implementation instead checks only `addrType >= 0 && addrType <= 7`, which is the full range of all defined Shelley-era header types (0-3 base, 4-5 pointer, 6-7 enterprise), not just base/enterprise (0-3, 6-7). [2](#0-1) 

Tracing the call path: `PoaBridge.validateWithdrawal` calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and throws only if it returns `false`; there is no further narrowing of Cardano address subtype anywhere else in `poa-bridge.ts` — the only other checks are `getCachedSupportedTokens` (asset/min-amount checks), `compareAddresses` (token-address collision), and an XRPL-specific branch. [3](#0-2)  None of these guards inspect the Cardano `addrType` byte or reject pointer addresses.

However, whether pointer addresses are actually *unsupported by the real PoA bridge indexer* is an external fact about the bridge service, not something determinable from this repository's code — the repo has no server-side check to compare against, and the question's premise about the bridge's actual crediting capability cannot be verified with the available tools/index. That claim falls under "trust assumptions about ... bridge APIs" behavior, which the rules explicitly place out of scope, and the code path shows no evidence that the bridge's `getSupportedTokens`/withdrawal-estimate APIs reject or accept specific Cardano address subtypes — this repo simply forwards whatever passes `validateCardanoAddress` to the bridge HTTP API and lets it decide.

### Impact Explanation
Within this repository, the demonstrable defect is limited to a documentation/implementation mismatch in `validateCardanoAddress` (it validates a wider address-type range than its docstring claims). No code path in `poa-bridge.ts` performs additional Cardano-subtype-specific validation, so if the external PoA indexer indeed cannot credit pointer addresses, funds could get stuck pending manual intervention — but confirming that outcome requires knowledge of the external bridge service's actual behavior, which is outside this codebase and outside the stated scope (defects/behavior of the bridge API/indexer are explicitly excluded).

### Likelihood Explanation
Reaching `validateCardanoAddress` with a pointer-type address requires only constructing a syntactically valid bech32 `addr1` string with header nibble 4 or 5 — trivial for any unprivileged caller. But whether this constitutes real impact depends entirely on an unverifiable, out-of-repo fact about the PoA bridge's crediting capability for pointer addresses.

### Recommendation
If pointer addresses are indeed not creditable by the destination custodian, narrow `validateCardanoAddress`'s accepted range to only the types it documents (0-3 for base addresses, 6-7 for enterprise addresses), explicitly rejecting 4 and 5:
```ts
return (addrType >= 0 && addrType <= 3) || addrType === 6 || addrType === 7;
```
This aligns the SDK-side format validation with its own documented scope regardless of the bridge's actual behavior.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/validateAddress.spec.ts (illustrative)
import { validateCardanoAddress } from "./validateAddress";
import { bech32 } from "@scure/base";

it("accepts pointer-type Cardano address (addrType 4) despite doc scope of Base+Enterprise only", () => {
  const header = 0b0100_0000; // addrType=4 (pointer), network id bits arbitrary
  const payload = new Uint8Array(29).fill(1);
  payload[0] = header;
  const words = bech32.toWords(payload);
  const address = bech32.encode("addr", words, 120);

  expect(validateCardanoAddress(address)).toBe(true); // asserts left side of equality
});
```
This confirms `validateCardanoAddress` returns `true` for a pointer-type address; grep of `poa-bridge.ts`'s `validateWithdrawal` [3](#0-2)  confirms no subsequent narrowing check exists in this repo. Whether this actually breaks bridge crediting cannot be proven without access to the external PoA bridge indexer's source/behavior, which is unavailable and out of scope.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L471-495)
```typescript
/**
 * Validates Cardano mainnet addresses (Base + Enterprise)
 * Returns true if valid, false if invalid
 */
export function validateCardanoAddress(address: string) {
	try {
		// max length big enough for any Cardano Bech32 addr
		const { prefix, words } = bech32.decode(
			address as `${string}1${string}`,
			120,
		);

		// only mainnet
		if (prefix !== "addr") return false;

		// convert 5-bit words back to bytes
		const data = bech32.fromWords(words);
		//@ts-expect-error
		const addrType = data[0] >> 4;

		return addrType >= 0 && addrType <= 7;
	} catch {
		return false;
	}
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L178-230)
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

		// Use cached getSupportedTokens to avoid frequent API calls
		const { tokens } = await this.getCachedSupportedTokens(
			[toPoaNetwork(assetInfo.blockchain)],
			args.logger,
		);

		const tokenInfo = tokens.find(
			(token) => token.intents_token_id === args.assetId,
		);

		if (tokenInfo == null) {
			throw new UnsupportedAssetIdError(
				args.assetId,
				"`assetId` is not supported in PoA bridge.",
			);
		}

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

		if (!args.skipMinAmountValidation) {
			const minWithdrawalAmount = BigInt(tokenInfo.min_withdrawal_amount);
			if (args.amount < minWithdrawalAmount) {
				throw new MinWithdrawalAmountError(
					minWithdrawalAmount,
					args.amount,
					args.assetId,
				);
			}
		}
```
