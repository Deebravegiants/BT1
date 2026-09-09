Confirmed: `validateWithdrawal` in `hot-bridge.ts` calls `validateAddress(args.destinationAddress, assetInfo.blockchain)` and gates the whole withdrawal on it, so whatever `validateAddress` accepts for a given chain becomes the format truth used to actually build and route the withdrawal intent (`createWithdrawalIntents` uses `args.withdrawalParams.destinationAddress` as `receiver` directly).### Title
Missing zero-address exclusion for Sui, Aptos, and Starknet in `validateAddress` — funds can be withdrawn to unspendable zero address - ([File: packages/intents-sdk/src/lib/validateAddress.ts])

### Summary
`validateEthAddress` explicitly rejects the all-zero address and the well-known burn address, but `validateSuiAddress`, `validateAptosAddress`, and `validateStarknetAddress` are pure regex format checks with no equivalent exclusion. An attacker-supplied `destinationAddress` of `0x` + `"0".repeat(64)` (or `0x0` for Starknet) passes `validateAddress` for these three chains and is threaded straight into withdrawal construction, resulting in funds routed to an unspendable, unrecoverable address.

### Finding Description
The claimed equality is: *`validateAddress(address, chain) === true` should imply the address is a real, spendable, non-burn destination on that chain*, exactly as it does for `Chains.Ethereum` and its EVM siblings via the explicit checks in `validateEthAddress`: [1](#0-0) 

For Sui, Aptos, and Starknet, the corresponding validators only check hex-string format/length with no zero-address guard: [2](#0-1) [3](#0-2) 

`0x` + `"0".repeat(64)` matches the Sui regex `/^(?:0x)?[a-fA-F0-9]{64}$/` and the Aptos regex `/^0x[a-fA-F0-9]{64}$/`; `0x0` matches the Starknet regex `/^0x[a-fA-F0-9]{1,64}$/`. None of these functions exclude the chain's canonical zero/burn address the way `validateEthAddress` does, so the equality breaks: format-valid ≠ spendable destination on these three chains.

This directly matters because `validateAddress` gates real withdrawal construction. In `HotBridge.validateWithdrawal`, the address is checked with `validateAddress` and, if it passes, the flow proceeds (trustline check, then downstream `createWithdrawalIntents` builds the actual withdraw intent using `args.withdrawalParams.destinationAddress` as `receiver`): [4](#0-3) [5](#0-4) 

Regarding the first part of the question (checksum-cased zero address bypassing the strict `===` zero-address check for Ethereum): this premise does not hold. The all-zero address `"0x0000000000000000000000000000000000000000"` contains only the digit `0` and no hex letters (`a`–`f`), so there is no possible mixed-case/checksummed variant of it — `toLowerCase()`/`toUpperCase()` transforms are no-ops on an all-digit string. The strict `===` check therefore cannot be bypassed by casing for this specific address; this part of the question is a false premise, not a real bug.

### Impact Explanation
An unprivileged caller (an ordinary user or an integrator forwarding a counterparty-supplied `destinationAddress`) can pass the chain's zero address for Sui, Aptos, or Starknet withdrawals. `validateAddress` returns `true`, `validateWithdrawal` does not throw `InvalidDestinationAddressForWithdrawalError`, and the withdrawal intent is built with the zero address as `receiver`. This results in funds delivered to an address with no known private key — unspendable and unrecoverable, matching the Critical category ("funds delivered to a wrong address/chain/contract with no recovery"). This is repeatable per withdrawal call, on any of the three affected chains.

### Likelihood Explanation
Preconditions: a withdrawal route through a bridge that calls `validateAddress`/`validateWithdrawal` (e.g., `HotBridge`) for an asset on Sui, Aptos, or Starknet. Attacker cost is trivial — no special permissions, keys, or economic cost beyond the withdrawal amount itself; the "attack" input is simply the well-known zero address string. Feasibility is high since the check is purely client-side string validation with no additional server-side chain-specific guard identified in this scope.

### Recommendation
Add explicit zero-address (and, where applicable, known burn-address) exclusions to `validateSuiAddress`, `validateAptosAddress`, and `validateStarknetAddress`, mirroring the pattern used in `validateEthAddress` (reject the all-zero 32-byte/64-hex-char value, using case-insensitive comparison for consistency even though these all-zero values have no letters).

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { validateAddress } from "../lib/validateAddress";
import { Chains } from "../lib/caip2";

describe("zero-address exclusion inconsistency", () => {
  it("Ethereum rejects the zero address", () => {
    expect(validateAddress("0x0000000000000000000000000000000000000000", Chains.Ethereum)).toBe(false);
  });

  it("Sui incorrectly accepts the zero address (BUG)", () => {
    expect(validateAddress(`0x${"0".repeat(64)}`, Chains.Sui)).toBe(true); // should be false
  });

  it("Aptos incorrectly accepts the zero address (BUG)", () => {
    expect(validateAddress(`0x${"0".repeat(64)}`, Chains.Aptos)).toBe(true); // should be false
  });

  it("Starknet incorrectly accepts the zero address (BUG)", () => {
    expect(validateAddress("0x0", Chains.Starknet)).toBe(true); // should be false
  });
});
```
This test only exercises the pure `validateAddress` function (no HTTP mocking required) and demonstrates the inconsistency: `Chains.Ethereum` correctly rejects the zero address while `Chains.Sui`, `Chains.Aptos`, and `Chains.Starknet` do not.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L105-113)
```typescript
function validateEthAddress(address: string) {
	if (
		address === "0x0000000000000000000000000000000000000000" ||
		address.toLowerCase() === "0x000000000000000000000000000000000000dead"
	) {
		return false;
	}
	return isAddress(address, { strict: true });
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L436-446)
```typescript
function validateSuiAddress(address: string) {
	return /^(?:0x)?[a-fA-F0-9]{64}$/.test(address);
}

function validateStellarAddress(address: string) {
	return /^G[A-Z0-9]{55}$/.test(address);
}

function validateAptosAddress(address: string) {
	return /^0x[a-fA-F0-9]{64}$/.test(address);
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L502-504)
```typescript
function validateStarknetAddress(address: string): boolean {
	return /^0x[a-fA-F0-9]{1,64}$/.test(address);
}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L224-232)
```typescript
		const intent = await this.hotSdk.buildGaslessWithdrawIntent({
			feeToken: "native",
			feeAmount,
			blockNumber,
			chain: toHotNetworkId(assetInfo.blockchain),
			token: isNative ? "native" : assetInfo.address,
			amount,
			receiver: args.withdrawalParams.destinationAddress,
		});
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L259-284)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");
		hotBlockchainInvariant(assetInfo.blockchain);

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}
		const nativeAsset = "native" in assetInfo;
		const token = nativeAsset ? "native" : assetInfo.address;
		if (
			!nativeAsset &&
			compareAddresses(token, args.destinationAddress, assetInfo.blockchain)
		) {
			throw new DestinationAddressMatchesTokenAddressError(token, args.assetId);
		}
```
