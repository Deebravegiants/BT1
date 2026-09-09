### Title
POA Bridge status matching ignores index, misreporting completion/txHash when a batch withdrawal contains two withdrawals of the same token - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
The SDK officially supports batch withdrawals — multiple withdrawal items settled in a single intent/transaction — via `signAndSendWithdrawalIntent`/`processWithdrawal`/`createWithdrawalCompletionPromises`. For the POA bridge route, `describeWithdrawal` resolves which API-reported withdrawal corresponds to a given `WithdrawalIdentifier` using `findMatchingWithdrawal`, which matches **only by `assetId` (near_token_id)**, deliberately ignoring the `index` field that uniquely distinguishes withdrawals in the batch.

### Finding Description
`PoaBridge.describeWithdrawal` explicitly discards the per-item `index` and matches purely on asset type: [1](#0-0) 

The matching helper's own doc-comment confirms the root cause and that it was a known, unaddressed limitation: [2](#0-1) 

The identical unsafe pattern also exists in the lower-level completion helper used by `internal-utils`: [3](#0-2) 

Meanwhile, batch withdrawals (multiple `withdrawalParams` entries settled by one NEAR intent transaction) are a first-class, documented SDK feature, and nothing in the withdrawal-parameter validation prevents two entries from sharing the same `assetId`: [4](#0-3) [5](#0-4) 

`createWithdrawalCompletionPromises`/`watchWithdrawal` build one `WithdrawalIdentifier` per batch entry (carrying a distinct `index`) and poll each independently: [6](#0-5) [7](#0-6) 

Because `findMatchingWithdrawal` ignores `index`, when a batch contains two (or more) withdrawals of the *same* underlying NEP-141 token — e.g., two different destination addresses or amounts of the same asset — `Array.find` in `findMatchingWithdrawal` returns the **same first matching entry** from the POA API response for both `WithdrawalIdentifier`s. This breaks the equality "status/txHash reported for withdrawal N == the on-chain outcome for withdrawal N": both watchers converge on the first array element's `status`/`transfer_tx_hash`, regardless of which entry actually corresponds to their own amount/destination address.

### Impact Explanation
An integrator using `createWithdrawalCompletionPromises`, `waitForWithdrawalCompletion`, or `processWithdrawal` for a batch that includes two same-asset POA withdrawals will:
- have the second (or later) withdrawal falsely reported `"completed"` with a `txHash` that actually belongs to a *different* withdrawal (different destination address/amount), before its own transfer has actually landed, or
- never obtain independent confirmation for the correct destination, since the same first entry is always matched.

This is a status/hash misreport that can cause an integrator to credit or release funds/refund for a withdrawal whose actual on-chain settlement (destination, amount) differs from what was reported — matching the "High" impact category of a status misreport causing double credit/refund.

### Likelihood Explanation
This requires no malicious actor — it is triggered purely by ordinary API usage: any legitimate caller building a batch (documented and tested feature) that happens to contain two withdrawals of the same token via the POA route (e.g., splitting a large withdrawal across two destination addresses, or a refund + withdrawal of the same asset) will hit this path deterministically. The code comment itself acknowledges the limitation exists and is unhandled, confirming this is a real, currently-reachable gap rather than a theoretical one.

### Recommendation
`findMatchingWithdrawal` in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` should disambiguate by more than `assetId` — e.g., also matching on `amount` and `destinationAddress` (or, if the POA API cannot provide a stable per-item key, track and exclude already-matched entries per call so distinct batch items are never collapsed onto the same underlying withdrawal), and/or reject/flag batches containing duplicate `assetId` entries routed to the POA bridge until the API supports disambiguation, consistent with the function's own caveat.

### Proof of Concept
1. Caller submits a batch withdrawal with two entries: `{ assetId: "nep141:usdt...", amount: 100n, destinationAddress: "A" }` and `{ assetId: "nep141:usdt...", amount: 200n, destinationAddress: "B" }`, both routed via the POA bridge, in a single NEAR intent transaction.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` respectively (see `packages/intents-sdk/src/core/withdrawal-watcher.test.ts:183-221` for index-assignment behavior).
3. POA bridge's `getWithdrawalStatus` returns both withdrawals for `tx_hash` (one `COMPLETED` with `transfer_tx_hash: "tx-A"`, one still `PENDING`).
4. `PoaBridge.describeWithdrawal` for `index:1` calls `findMatchingWithdrawal(withdrawals, "nep141:usdt...")`, which returns the **first** entry (`tx-A`, destined for address "A") regardless of `index`.
5. The watcher for withdrawal `index:1` (destined for "B") resolves as `{ status: "completed", txHash: "tx-A" }`, even though "B" has not received funds — a status/hash misreport for the wrong destination/amount.

### Citations

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-153)
```typescript
/**
 * Finds a withdrawal matching the given criteria.
 *
 * NOTE: Currently only matches by assetId (near_token_id). This means multiple
 * withdrawals of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: types.WithdrawalStatusResponseOk["result"]["withdrawals"],
	criteria: WithdrawalCriteria,
):
	| types.WithdrawalStatusResponseOk["result"]["withdrawals"][number]
	| undefined {
	return withdrawals.find(
		(w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
	);
}
```

**File:** packages/intents-sdk/README.md (L521-548)
```markdown
### Batch Withdrawals

Process multiple withdrawals in a single intent:

```typescript
const withdrawalParams = [
    {
        assetId: 'nep141:usdt.tether-token.near',
        amount: 1000000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    },
    {
        assetId: 'nep245:v2_1.omni.hot.tg:137_qiStmoQJDQPTebaPjgx5VBxZv6L',
        amount: 100000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    }
]

// Method 1: Complete end-to-end batch processing
const batchResult = await sdk.processWithdrawal({
    withdrawalParams,
    // feeEstimation is optional - will be estimated automatically if not provided
});

console.log('Batch intent hash:', batchResult.intentHash);
console.log('Destination transactions:', batchResult.destinationTx); // Array of results
```

**File:** packages/intents-sdk/src/sdk.signAndSendWithdrawalIntent.test.ts (L50-79)
```typescript
	it("supports batch withdrawals", async () => {
		const { sdk, intentRelayer, defaultIntentSigner } = setupMocks();
		noPublish(intentRelayer);

		void sdk.signAndSendWithdrawalIntent({
			withdrawalParams: [
				withdrawalParams,
				withdrawalParams,
				withdrawalParams,
				withdrawalParams,
			],
			feeEstimation: [fee, fee, fee, fee],
		});

		await vi.waitFor(() =>
			expect(defaultIntentSigner.signIntent).toHaveBeenCalledOnce(),
		);

		expect(vi.mocked(defaultIntentSigner.signIntent).mock.lastCall).toEqual([
			{
				...AnyIntent,
				intents: [
					AnyTransferIntentPrimitive,
					AnyTransferIntentPrimitive,
					AnyTransferIntentPrimitive,
					AnyTransferIntentPrimitive,
				],
			},
		]);
	});
```

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-53)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

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

					return POLL_PENDING;
```
