### Title
Omni Bridge `describeWithdrawal` matches transfer by array index instead of a stable identifier, allowing status/txHash misreport for batched withdrawals - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
`OmniBridge.describeWithdrawal` indexes into the array returned by `this.omniBridgeAPI.getTransfer({ transactionHash })` using `args.index`, the position the withdrawal had when the SDK originally submitted the NEAR intent. This assumes the indexer's transfer array always preserves that same order/count, which is the same class of "assumed fixed cardinality/position" defect as the reported Solana zetaclient bug (assuming exactly one signer account instead of validating which one is relevant).

### Finding Description
`describeWithdrawal` does:
```ts
const transfer = (
    await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash })
)[args.index];
``` [1](#0-0) 

`args.index` is assigned purely from the position of the withdrawal within the caller-supplied array in `createWithdrawalIdentifiers`, using a per-route counter, not any on-chain identifier of the transfer: [2](#0-1) 

The sibling `PoaBridge.describeWithdrawal` explicitly documents and fixes this exact problem: "Response list is unsorted, so we match by assetId instead of index": [3](#0-2) 

and has a dedicated test "matches withdrawal by assetId, not by index" verifying the indexer response order can differ from submission order: [4](#0-3) 

The Omni Bridge implementation was never updated with the same safeguard: it still does `[args.index]` without any check that the array element it grabbed actually corresponds to the withdrawal being polled (no comparison against `destinationAddress`, `assetId`, or `recipient` matching the requested withdrawal). If a single NEAR transaction contains multiple Omni Bridge withdrawals (e.g., a batch of `ft_withdraw`/`mt_withdraw` intents to different chains/recipients within one intent execution — a supported and tested scenario per `sdk.createWithdrawalCompletionPromises.test.ts` and `createWithdrawalIdentifiers`), and the Omni Bridge indexer returns the transfers for that NEAR tx hash in an order that does not match submission order (exactly the scenario POA's own comment/test anticipates for its own API), `describeWithdrawal` will attach the wrong transfer's `recipient`/`finalised.transaction_hash`/`utxo_meta` to the wrong `WithdrawalIdentifier`.

### Impact Explanation
This breaks the equality "status/hash reported for withdrawal N corresponds to the on-chain outcome of withdrawal N." Concretely:
- `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` (which consume `describeWithdrawal` results) could report withdrawal A as `completed` with a `txHash` that actually belongs to withdrawal B's destination chain and recipient, and vice versa.
- An integrator/caller relying on this SDK to determine when a specific withdrawal has landed (e.g., to release custody, mark an off-chain ledger entry as settled, or notify a user) could mark the wrong withdrawal as completed/failed, or attach the wrong transaction hash to a withdrawal — a status misreport that could cause an integrator to credit/refund the wrong withdrawal, matching the "status or hash misreport" High-impact category in scope.

### Likelihood Explanation
Requires: (1) multiple Omni Bridge withdrawals batched in one NEAR transaction (a supported code path per `createWithdrawalIdentifiers`/`createWithdrawalCompletionPromises`), and (2) the Omni Bridge indexer returning transfers for that tx hash in an order that doesn't match submission order. The likelihood of (2) is unconfirmed for the Omni Bridge indexer specifically — I could not find or fetch the `omniBridgeAPI.getTransfer` implementation/backend ordering guarantees in this index, so I cannot definitively prove the indexer is unordered (unlike POA Bridge's API, which the codebase explicitly documents as unordered). This is a real and material uncertainty, and it's the crux of whether the analog is exploitable as opposed to theoretical.

### Recommendation
Match the returned transfer by a stable identifier (e.g., `recipient` address plus `assetId`/token contract, similar to POA's `findMatchingWithdrawal` by `assetId`) rather than raw array index, or otherwise validate that the selected transfer's `recipient`/token matches the requested `withdrawalParams.destinationAddress`/`assetId` before trusting its `txHash`/status.

### Proof of Concept
Not independently reproducible from the index alone: the exploit depends on the actual ordering behavior of the Omni Bridge indexer API (`omniBridgeAPI.getTransfer`), whose backend implementation is out of scope/not present in the indexed files. Existing unit tests (`omni-bridge.test.ts` "returns correct transfer by index") only assert correct behavior when order happens to match submission order; they do not test the out-of-order case that POA Bridge explicitly tests for its own API. [5](#0-4)

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-698)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
}): Promise<{ bridge: Bridge; wid: WithdrawalIdentifier }[]> {
	const indexes = new Map<string, number>();
	const results: { bridge: Bridge; wid: WithdrawalIdentifier }[] = [];

	for (const w of args.withdrawalParams) {
		const bridge = await findBridgeForWithdrawal(args.bridges, w);
		if (bridge == null) {
			throw new BridgeNotFoundError();
		}

		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});

		results.push({ bridge, wid });
	}

	return results;
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const response = await this.getWithdrawalStatusWithRetry(args);

		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1055)
```typescript
		it("matches withdrawal by assetId, not by index", async () => {
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L515-546)
```typescript
		it("returns correct transfer by index", async () => {
			vi.spyOn(BridgeAPI.prototype, "getTransfer").mockResolvedValue([
				createTransferMock({
					recipient: "eth:0x1111111111111111111111111111111111111111",
					finalised: {
						transaction_hash: "0xfirst-tx",
						chain: "Eth",
						timestamp_seconds: 1700000000,
						details: {
							type: "evm",
							block_number: 1,
							transaction_index: null,
							log_index: null,
						},
					},
				}),
				createTransferMock({
					recipient: "eth:0x2222222222222222222222222222222222222222",
					finalised: {
						transaction_hash: "0xsecond-tx",
						chain: "Eth",
						timestamp_seconds: 1700000001,
						details: {
							type: "evm",
							block_number: 2,
							transaction_index: null,
							log_index: null,
						},
					},
				}),
			]);

```
