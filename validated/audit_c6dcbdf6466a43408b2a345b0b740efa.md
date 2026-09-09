### Title
BTC destination address guard bypass via uppercase bech32 case variant of the token's own custodial address - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Finding Description
The equality claimed to hold is: `compareAddresses(destTokenAddress, args.destinationAddress, Chains.Bitcoin)` returns `true` whenever the two addresses decode to the same witness program. That equality is broken.

In `OmniBridge.validateWithdrawal` [1](#0-0) , the destination-matches-token guard calls `compareAddresses(destTokenAddress, args.destinationAddress, assetInfo.blockchain)`. For `Chains.Bitcoin` (and every other UTXO/base58/hex-agnostic chain sharing that branch), `compareAddresses` does a raw bytewise string comparison with no bech32 case-folding: [2](#0-1) . Meanwhile `validateAddress`'s BTC bech32 validator (`validateBtcBech32Address`) is case-insensitive by design, per BIP-173, and the test suite explicitly confirms uppercase bech32 (`BC1Q...`) passes validation: [3](#0-2) [4](#0-3) .

So an attacker can submit `args.destinationAddress` as an uppercase (or mixed-case) variant of `destTokenAddress` (the token's own custodial BTC address returned by `getCachedDestinationTokenAddress`/`getAddress`). `validateAddress` accepts it (case-insensitive), `compareAddresses` rejects the equality (case-sensitive), so `DestinationAddressMatchesTokenAddressError` is never thrown and `validateWithdrawal` resolves normally.

The finding is compounded — not merely theoretical — by `deriveOmniWithdrawIntentParams`, which is invoked later in `createWithdrawalIntents` to actually build the withdrawal intent. That function explicitly lowercases any `bc1`-prefixed destination address before constructing the `recipient`: [5](#0-4) . This means the uppercase input that slipped past the guard is normalized back to lowercase at intent-build time — becoming byte-identical to `destTokenAddress`, the bridge's own custodial address. The guard's entire purpose (blocking a withdrawal whose destination equals the token's own address) is defeated by the very case-insensitivity the downstream code already accounts for.

### Impact Explanation
A BTC withdrawal is built and signed with `recipient` equal to the Omni Bridge's own custodial UTXO address for that token, because `deriveOmniWithdrawIntentParams` normalizes the attacker-supplied uppercase destination to the same lowercase canonical form as the bridge's address. Funds sent to the bridge's own deposit/custodial address for a withdrawal (rather than being redeemed correctly) are not recoverable through normal means — this matches the Critical category: "funds delivered to a wrong address ... with no recovery." Every call with a case-varied destination address reproduces the issue; it is fully repeatable and requires no special privilege beyond being the withdrawing user (attacker directs their own funds, but the bug is that the safety guard meant to catch this exact self-inflicted mistake silently fails to fire, and there's no other backstop before the intent is signed).

### Likelihood Explanation
Preconditions: the withdrawal must target Bitcoin (or another UTXO chain reachable via `Chains.Bitcoin`'s comparison branch), and the attacker only needs to know or query the token's on-chain custodial bech32 address (retrievable via the same `getCachedDestinationTokenAddress`/public bridge info used internally) and re-case it. Cost is negligible — one string transformation. `validateAddress` does not block it, and `compareAddresses` was clearly written under the assumption that BTC addresses are always compared in canonical case, an assumption unverified/unnormalized before comparison. This is easily reproducible in a unit test and does not depend on any external party misbehaving.

### Recommendation
In `compareAddresses.ts`, add a Bitcoin/Zcash-specific (bech32-aware) comparison branch that normalizes both addresses to lowercase (and ideally re-decodes/re-encodes via `bech32`/`bech32m` to canonical form) before comparing, mirroring the case-insensitivity already implemented in `validateBtcBech32Address` and in `deriveOmniWithdrawIntentParams`'s lowercasing logic. At minimum, lowercase both sides of the `Chains.Bitcoin` (and any other bech32-based chain) comparison before the bytewise check.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/compareAddresses.repro.spec.ts
import { describe, it, expect } from "vitest";
import { compareAddresses } from "./compareAddresses";
import { validateAddress } from "./validateAddress";
import { Chains } from "./caip2";

describe("BTC bech32 case bypass", () => {
  const lower = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq";
  const upper = lower.toUpperCase(); // e.g. "BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ"

  it("both decode to the same witness program (valid per BIP-173)", () => {
    expect(validateAddress(lower, Chains.Bitcoin)).toBe(true);
    expect(validateAddress(upper, Chains.Bitcoin)).toBe(true);
  });

  it("compareAddresses incorrectly reports inequality for the same address", () => {
    // destTokenAddress = lower (bridge's canonical custodial address)
    // args.destinationAddress = upper (attacker-supplied case variant)
    expect(compareAddresses(lower, upper, Chains.Bitcoin)).toBe(false); // BUG: should be true
  });
});
```
Follow-up integration test (mocking only HTTP/`getBridgedToken`/`omniBridgeAPI`): call `OmniBridge.validateWithdrawal({ assetId, amount, destinationAddress: upper, feeEstimation, ... })` where the mocked `destTokenOmniAddress` resolves to `lower`; assert the call resolves instead of throwing `DestinationAddressMatchesTokenAddressError`, and then call `deriveOmniWithdrawIntentParams` with the same `destinationAddress: upper` to show the resulting `recipient` equals the token's own address (`lower`), confirming the funds route to the bridge's custodial address.

### Citations

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

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L160-175)
```typescript
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
```

**File:** packages/intents-sdk/src/lib/validateAddress.spec.ts (L80-86)
```typescript
			// Bech32 SegWit v0 (bc1q...)
			"bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
			"bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c",
			"bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
			"bc1q973xrrgje6etkkn9q9azzsgpxeddats8ckvp5s",
			"BC1Q973XRRGJE6ETKKN9Q9AZZSGPXEDDATS8CKVP5S",
			"BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4",
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
