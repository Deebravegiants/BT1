### Title
`IntentsBridge` omits the token-address collision guard, letting internal transfers set `receiver_id` equal to the withdrawn token's own NEAR contract account - ([File: packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts])

### Summary
`IntentsBridge.validateWithdrawal` only checks `validateAddress(destinationAddress, Chains.Near)` and never compares `destinationAddress` against the NEP-141 token contract encoded in `assetId`, unlike `OmniBridge`, `PoaBridge`, `DirectBridge`, and `HotBridge`, which all import `compareAddresses`/`DestinationAddressMatchesTokenAddressError` to block exactly this case. As a result, `createWithdrawalIntents` will happily embed `destinationAddress` verbatim as `receiver_id` in a `transfer` intent even when it equals the token's own custodian account (e.g. `wrap.near` for `nep141:wrap.near`).

### Finding Description
Broken equality: sibling bridges enforce `receiver_id (on destination chain) != token contract address (on destination chain)`; `IntentsBridge` has no equivalent check for `receiver_id (NEAR) != token contract account (NEAR, parsed from assetId)`.

Code path:
- `IntentsBridge.validateWithdrawal` [1](#0-0)  only calls `validateAddress(args.destinationAddress, Chains.Near)`, which accepts any syntactically valid NEAR account id, including the token's own contract account.
- `IntentsBridge.createWithdrawalIntents` [2](#0-1)  then embeds `args.withdrawalParams.destinationAddress` verbatim as `receiver_id` of a `transfer` intent, with `tokens: { [assetId]: amount }`.
- In contrast, `OmniBridge` imports both `DestinationAddressMatchesTokenAddressError` and `compareAddresses` [3](#0-2)  specifically, per the helper's own doc comment, "to block transfers to the token's own address" [4](#0-3) . `PoaBridge`, `DirectBridge`, and `HotBridge` all wire in the same guard (confirmed via grep hits in each file), but `IntentsBridge` never imports either symbol.

Root cause: the `transfer` intent moves an internal multi-token ledger balance inside `intents.near` from the signer to `receiver_id`. If `receiver_id` is set to the token's own NEAR contract account (parsed from `assetId`, e.g. `wrap.near`), the balance is credited to that contract's ledger entry. That contract has no logic or key material to call back into `intents.near` to reclaim or forward the balance, so the funds become permanently stranded — the same failure mode the sibling bridges explicitly guard against for their respective destination chains.

Existing guards do not catch this: `validateAddress` only verifies NEAR address syntax, not collision with the token account; there is no `compareAddresses`/`DestinationAddressMatchesTokenAddressError` call anywhere in `intents-bridge.ts`; and `supports()`/`FeeExceedsAmountError`/`getUnderlyingFee` are unrelated to address validation.

### Impact Explanation
An intent is signed and submitted with `receiver_id` equal to the token contract's own NEAR account, permanently misrouting the internal balance of the withdrawn token to an account with no way to move it back out. This matches "funds delivered to a wrong address/chain/contract with no recovery" (Critical). It is repeatable for any `nep141:*` asset routed through `RouteEnum.InternalTransfer` whenever `destinationAddress` equals that asset's underlying token account.

### Likelihood Explanation
Preconditions: the withdrawal must route through `IntentsBridge` (`routeConfig.route === RouteEnum.InternalTransfer`), and `destinationAddress` must equal the NEAR account embedded in `assetId`. This can happen either through user/integrator error or through a counterparty-supplied `destinationAddress` string that an integrator forwards without independently checking it against the asset's token account (the SDK provides no such check itself). Attacker cost is a single crafted string; no privileged access is needed. The sibling bridges treat this exact scenario as attacker/foot-gun-worthy enough to add a dedicated error type and address-comparison utility, indicating the risk is considered real elsewhere in the same codebase; `IntentsBridge` alone is missing it.

### Recommendation
In `IntentsBridge.validateWithdrawal`, parse the NEAR token account from `args.assetId` (e.g. strip the `nep141:` prefix) and use `compareAddresses(args.destinationAddress, tokenAccountId, Chains.Near)` to throw `DestinationAddressMatchesTokenAddressError` when they match, mirroring `OmniBridge`/`PoaBridge`/`DirectBridge`/`HotBridge`.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.test.ts
it("should reject when destinationAddress equals the token's own contract account", async () => {
  const bridge = new IntentsBridge();
  const assetId = "nep141:wrap.near";
  const tokenAccountId = "wrap.near"; // token contract for assetId

  // Equality under test: receiver_id (paid) should NOT equal token custodian account
  await expect(
    bridge.validateWithdrawal({
      assetId,
      amount: 1000n,
      destinationAddress: tokenAccountId,
    }),
  ).rejects.toThrow(/* expected: DestinationAddressMatchesTokenAddressError */);

  // Current (buggy) behavior demonstrating the bypass:
  const intents = await bridge.createWithdrawalIntents({
    withdrawalParams: {
      assetId,
      amount: 1000n,
      destinationAddress: tokenAccountId,
      feeInclusive: false,
    },
    feeEstimation: { amount: 0n, quote: null, underlyingFees: { [RouteEnum.InternalTransfer]: null } },
  });
  expect(intents[0].receiver_id).toBe(tokenAccountId); // == token's own custodian account
});
```
This test mocks no HTTP (none is required for `IntentsBridge`), directly exercising `validateWithdrawal` and `createWithdrawalIntents` to show `receiver_id` collides with the token account with no thrown error, unlike the equivalent tests already present for `OmniBridge`/`PoaBridge`/`HotBridge`/`DirectBridge`.

### Citations

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L37-54)
```typescript
	createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
	}): Promise<IntentPrimitive[]> {
		const intents: IntentPrimitive[] = [
			{
				intent: "transfer",
				receiver_id: args.withdrawalParams.destinationAddress,
				tokens: {
					[args.withdrawalParams.assetId]:
						args.withdrawalParams.amount.toString(),
				},
				memo: args.withdrawalParams.destinationMemo,
			},
		];

		return Promise.resolve(intents);
	}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L59-72)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		if (validateAddress(args.destinationAddress, Chains.Near) === false) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				"near-intents",
			);
		}
		return;
	}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L76-84)
```typescript
import {
	DestinationAddressMatchesTokenAddressError,
	InvalidDestinationAddressForWithdrawalError,
	MinWithdrawalAmountError,
	UnsupportedAssetIdError,
} from "../../classes/errors";
import { validateAddress } from "../../lib/validateAddress";
import { POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE } from "../../constants/poa-tokens-migrated-to-omni-bridge";
import { compareAddresses } from "../../lib/compareAddresses";
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L7-11)
```typescript
/**
 * Compares two addresses for equality using each chain's canonical form,
 * e.g. to block transfers to the token's own address. Returns false (not
 * throw) on malformed input.
 */
```
