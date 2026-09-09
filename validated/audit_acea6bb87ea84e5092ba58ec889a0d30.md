### Title
Missing destination-equals-token-contract check in `IntentsBridge.validateWithdrawal` — funds can be misdelivered into an unrecoverable ledger balance - ([File: packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts])

### Summary
Every other NEAR-facing withdrawal path in `intents-sdk` (`DirectBridge`, `OmniBridge`, `PoaBridge`, `HotBridge`) validates that the withdrawal `destinationAddress` is not equal to the token's own contract address before building the withdrawal intent, throwing `DestinationAddressMatchesTokenAddressError` if it does. `IntentsBridge.validateWithdrawal` — the sibling bridge that also targets `Chains.Near` — omits this check entirely, breaking the equality "destination address validated ≠ token contract address" that the rest of the codebase enforces.

### Finding Description
`compareAddresses`/`DestinationAddressMatchesTokenAddressError` is consistently used to prevent a withdrawal from being routed to the address of the token contract itself:

- `DirectBridge.validateWithdrawal` (targets `Chains.Near`, same destination chain as `IntentsBridge`) checks `compareAddresses(tokenAccountId, args.destinationAddress, Chains.Near)` and throws if they match. [1](#0-0) 
- `OmniBridge.validateWithdrawal` performs the analogous check against the resolved destination-chain token address. [2](#0-1) 
- `PoaBridge.validateWithdrawal` performs the same check. [3](#0-2) 
- `HotBridge.validateWithdrawal` performs the same check. [4](#0-3) 

`IntentsBridge.validateWithdrawal`, however, only validates that `destinationAddress` is a syntactically valid NEAR address — it never checks it against the token contract id: [5](#0-4) 

`IntentsBridge.createWithdrawalIntents` then builds a `transfer` intent using this unchecked `destinationAddress` verbatim as `receiver_id`: [6](#0-5) 

This "transfer" intent is executed inside the `intents.near` multi-token ledger contract — it moves the caller's intents-ledger balance of `assetId` to the ledger-internal balance keyed by `receiver_id`, it does not perform an actual NEP-141 `ft_transfer` to an external account. If `receiver_id` (the user-supplied `destinationAddress`) equals the underlying token contract's own NEAR account id (`tokenAccountId` for that `assetId`), the balance becomes owned, inside the intents ledger, by an account that is the token contract itself. The token contract has no relationship with, and no signing capability inside, the intents/defuse protocol (it never signs intents), so it can never claim, withdraw, or move that ledger balance out. The tokens are permanently stuck.

### Impact Explanation
This breaks the equality "destination address checked by `validateWithdrawal` ≠ token contract's own address", which the other three/four bridges implement specifically to prevent unrecoverable misdelivery. Because `IntentsBridge` skips it, a withdrawal whose `destinationAddress` happens to equal the `assetId`'s underlying token contract id will pass validation, get executed as a `transfer` intent, and permanently lock the funds inside the `intents.near` ledger under an address that can never sign a reclaiming intent. This matches the report's "High" impact bucket: funds delivered to a wrong/unreachable address with no recovery.

### Likelihood Explanation
Likelihood is Medium: this requires the caller (SDK integrator or a user-controlled `destinationAddress` input) to pass the token's own contract id as the withdrawal destination for an `InternalTransfer`/`IntentsBridge` route. This is exactly the mistake the `DestinationAddressMatchesTokenAddressError` check exists to catch elsewhere in the same codebase (and for the same destination chain, NEAR), which is strong evidence that it's a realistic user/integrator error rather than a purely theoretical one.

### Recommendation
Add the same guard used in `DirectBridge` to `IntentsBridge.validateWithdrawal`:
```ts
const { contractId: tokenAccountId } = utils.parseDefuseAssetId(args.assetId);
if (compareAddresses(tokenAccountId, args.destinationAddress, Chains.Near)) {
  throw new DestinationAddressMatchesTokenAddressError(tokenAccountId, args.assetId);
}
```
placed before `createWithdrawalIntents` is invoked, keeping validation consistent across all bridges targeting `Chains.Near`.

### Proof of Concept
1. Caller invokes SDK withdrawal with `routeConfig: { route: RouteEnum.InternalTransfer }`, `assetId: "nep141:usdc.near"`, `destinationAddress: "usdc.near"` (the token contract's own account id).
2. `IntentsBridge.validateWithdrawal` only runs `validateAddress(args.destinationAddress, Chains.Near)`, which returns `true` because `"usdc.near"` is a syntactically valid NEAR account id; no comparison against the token contract id is performed. [5](#0-4) 
3. `createWithdrawalIntents` builds `{ intent: "transfer", receiver_id: "usdc.near", tokens: { "nep141:usdc.near": amount } }` and it is signed/executed. [7](#0-6) 
4. The intents-ledger balance for `nep141:usdc.near` is now held by account `usdc.near` inside `intents.near`. Since `usdc.near` (the token contract) never signs intents, this balance can never be moved out — the funds are unrecoverable, exactly the scenario `DestinationAddressMatchesTokenAddressError` prevents in `DirectBridge`, `OmniBridge`, `PoaBridge`, and `HotBridge`.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L167-178)
```typescript
		const { contractId: tokenAccountId } = utils.parseDefuseAssetId(
			args.assetId,
		);

		if (
			compareAddresses(tokenAccountId, args.destinationAddress, Chains.Near)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenAccountId,
				args.assetId,
			);
		}
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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L277-284)
```typescript
		const nativeAsset = "native" in assetInfo;
		const token = nativeAsset ? "native" : assetInfo.address;
		if (
			!nativeAsset &&
			compareAddresses(token, args.destinationAddress, assetInfo.blockchain)
		) {
			throw new DestinationAddressMatchesTokenAddressError(token, args.assetId);
		}
```

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
