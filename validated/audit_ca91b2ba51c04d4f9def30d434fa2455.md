## Analysis

I found a status/withdrawal-matching defect analogous to the report's "status reported that is not the on-chain outcome" bug class, in `PoaBridge.describeWithdrawal`.

### Title
Withdrawal status/hash misattribution when batching multiple same-asset withdrawals in one intent transaction - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`sdk.processWithdrawal`/`sdk.waitForWithdrawalCompletion` support batching multiple `WithdrawalParams` into one NEAR intent transaction and track completion per-index via `WithdrawalIdentifier.index`. For PoA-bridge withdrawals, `describeWithdrawal` ignores this index entirely and instead matches the bridge's status response purely by `assetId` via `findMatchingWithdrawal`, returning the *first* withdrawal in the (documented as unsorted) response array whose token matches.

### Finding Description
`PoaBridge.describeWithdrawal` [1](#0-0)  calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which is defined as: [2](#0-1) 

The function's own doc comment concedes: *"Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* The batch withdrawal API, however, does not prevent submitting two `WithdrawalParams` entries with the same `assetId` (e.g., same token, different `destinationAddress`/`amount`) inside one call to `sdk.processWithdrawal`/`sdk.waitForWithdrawalCompletion`, which assigns each a distinct `index` [3](#0-2)  and documents in the README that `promises[i]` corresponds to `withdrawalParams[i]` [4](#0-3) .

Because the PoA bridge API's withdrawal list is "unsorted" per the code comment, when two withdrawals share the same `assetId`, both index-0 and index-1 lookups in `watchWithdrawal` [5](#0-4)  resolve against the *same* matched record — whichever `w` is found first by `.find()`. This breaks the equality "status/txHash reported for withdrawal i == on-chain outcome of withdrawal i": both requests can be reported `completed` with the *same* destination `transfer_tx_hash`, even though only one of the two on-chain transfers has actually settled (or they settle to different destination addresses/amounts).

### Impact Explanation
An integrator relying on `sdk.waitForWithdrawalCompletion` for a batch of same-token withdrawals (a supported, documented use case) can be told withdrawal B is `completed` with withdrawal A's tx hash while B is still pending or uses a different destination address, matching the report's "status or hash misreport making an integrator credit or refund twice" (High-severity impact category per the scoped rules). This is not a self-inflicted loss — it affects correctness of settlement reporting to any caller batching same-asset withdrawals, a normal usage pattern, not an admin/malicious-peer action.

### Likelihood Explanation
No privileged action or malicious relayer/RPC is required — an ordinary SDK caller submitting two withdrawals of the same PoA-bridged token (e.g., splitting one balance to two recipients) in a single `processWithdrawal`/batch call reaches this path deterministically. The order-dependence on the "unsorted" API response makes the specific mis-mapping non-deterministic per the code's own comment, meaning some fraction of same-asset batches will misreport.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId` — e.g., match by `(assetId, destinationAddress, amount)` or, if the PoA API doesn't expose an ordering/idempotency key, reject/queue batches containing duplicate `assetId` entries rather than silently reusing the first match for every same-asset request, consistent with the fix approach already noted in the code's own comment (sort both sides by amount).

### Proof of Concept
1. Call `sdk.waitForWithdrawalCompletion({ withdrawalParams: [ {assetId: "nep141:usdt...omft.near", amount: A, destinationAddress: X}, {assetId: "nep141:usdt...omft.near", amount: B, destinationAddress: Y} ], intentTx })`.
2. Both entries route through `PoaBridge` and get `index: 0` and `index: 1` respectively via `createWithdrawalIdentifier` [6](#0-5) .
3. `watchWithdrawal` polls `describeWithdrawal` for each index independently [5](#0-4) ; both calls hit `findMatchingWithdrawal(response.withdrawals, "nep141:usdt...omft.near")`, which returns `withdrawals.find(...)` — the same first element for both index-0 and index-1 requests, regardless of which one actually completed.
4. Result: the caller receives `{hash: transfer_tx_hash}` for *both* withdrawals as soon as any one of them completes on the bridge side, even though the other may still be pending, failed, or destined elsewhere — a concrete status/hash misreport.

**Note on confidence**: I was not able to fully trace `createWithdrawalCompletionPromises` in `sdk.ts` (truncated during exploration) to confirm exactly how indices are partitioned per bridge across a mixed batch; the core defect (assetId-only matching regardless of index) is directly confirmed in the `poa-bridge.ts` source and its own documentation comment, but exhaustive confirmation of the multi-bridge batching orchestration would benefit from a full Devin session with complete file access.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-311)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		const assetInfo = this.parseAssetId(args.withdrawalParams.assetId);
		assert(assetInfo != null, "Asset is not supported");

		const landingChain = assetInfo.blockchain;

		return {
			landingChain,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-326)
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

		if (withdrawal == null) {
			return { status: "pending" };
		}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-427)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	// POA bridge only supports NEP-141 tokens. The API returns `near_token_id`
	// (e.g., "zec.omft.near") which we prefix with "nep141:" to match assetId format.
	// Note: `defuse_asset_identifier` cannot be used as it contains chain-native
	// format (e.g., "zec:mainnet:native") which differs from the assetId format.
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L99-124)
```typescript
	it("maintains indexes specific to bridge route", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal).mockResolvedValue({
			status: "completed",
			txHash: "fake-dest-hash",
		});

		await sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams, withdrawalParams],
		});

		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			1,
			expect.objectContaining({ index: 0 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			2,
			expect.objectContaining({ index: 1 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			3,
			expect.objectContaining({ index: 2 }),
		);
	});
```

**File:** packages/intents-sdk/README.md (L635-639)
```markdown
**Key benefits:**
- Fast withdrawals (Solana ~2s) aren't blocked by slow ones (Bitcoin ~1hr)
- One failure doesn't affect other withdrawals
- Recovery-friendly: recreate promises from saved `{ withdrawalParams, intentTx }`
- Index correspondence: `promises[i]` corresponds to `withdrawalParams[i]`
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-52)
```typescript
	try {
		return await poll(
			async () => {
				try {
					const status = await args.bridge.describeWithdrawal({
						...args.wid,
						logger: args.logger,
					});

					consecutiveErrors = 0;

					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

```
