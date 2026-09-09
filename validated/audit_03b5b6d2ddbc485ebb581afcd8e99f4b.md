### Title
POA Bridge withdrawal status/hash misattributed across multiple same-asset batch withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` reports the completion status and destination transaction hash of an on-chain withdrawal, but it resolves which POA bridge withdrawal record belongs to a given `WithdrawalIdentifier` by matching on `assetId` only, ignoring the `index` field that uniquely identifies a specific withdrawal within a batch intent.

### Finding Description
`findMatchingWithdrawal` selects the first entry in the POA bridge's response array whose `near_token_id` matches the requested `assetId` [1](#0-0) . `describeWithdrawal` calls this helper using only `args.withdrawalParams.assetId`, discarding `args.index` even though `WithdrawalIdentifier.index` exists specifically to disambiguate multiple withdrawals from the same batch transaction [2](#0-1) .

The SDK's batch-withdrawal machinery explicitly assigns a distinct `index` per bridge route so that multiple withdrawals of the same asset in one intent transaction can be tracked independently [3](#0-2) , and `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` rely on that index to poll and resolve each withdrawal's own promise independently [4](#0-3) . If a batch contains two or more withdrawals of the same `assetId` (e.g., same token withdrawn to two different destination addresses), the POA bridge's own tests confirm the response list is unordered and `.find()` returns the first same-asset entry for every index requested [5](#0-4) . The same defect exists independently in `internal-utils`' `waitForWithdrawalCompletion` helper, which uses an identical `findMatchingWithdrawal(withdrawals, { assetId })` matcher [6](#0-5) .

Both implementations carry a code comment acknowledging the limitation ("multiple withdrawals of the same token in a single transaction are not supported"), so this is a documented gap rather than a hidden logic error, but it is reachable through the normal, unprivileged batch-withdrawal API (`sdk.processWithdrawal`, `sdk.waitForWithdrawalCompletion`, `sdk.createWithdrawalCompletionPromises`) with no malicious input required — an ordinary integrator batching two same-token withdrawals with different destination addresses triggers it.

### Impact Explanation
When two same-asset POA withdrawals are batched to different destination addresses, `describeWithdrawal`/`waitForWithdrawalCompletion` can report the wrong `transfer_tx_hash` and/or wrong completion status for a given index — e.g., withdrawal #1 (destined for address B) may be reported as "completed" with the destination tx hash that actually belongs to withdrawal #0 (destined for address A). An integrator relying on this per-withdrawal status to release funds, mark an order fulfilled, or issue a refund could credit/refund the wrong user or the same withdrawal twice, matching the "status or hash misreport making an integrator credit or refund twice" category.

### Likelihood Explanation
This requires no attacker action beyond normal usage: any integrator who batches ≥2 withdrawals of the same NEP-141 asset (even to different destinations) via `processWithdrawal`/`waitForWithdrawalCompletion` triggers the ambiguous match. This is a fairly plausible usage pattern for exchanges/wallets batching payouts of the same token to multiple users.

### Recommendation
Extend the POA bridge API/response (or client-side correlation) to disambiguate withdrawals by more than `assetId` — e.g., additionally match by `destinationAddress` and `amount`, or wait for POA bridge API support for per-withdrawal identifiers/index, as already suggested in the existing code comment. Until fixed, the SDK should either throw/reject explicitly when it detects multiple same-asset withdrawals in a single batch rather than silently returning a possibly-incorrect match, so integrators aren't silently given wrong statuses.

### Proof of Concept
1. Submit a batch withdrawal via `sdk.processWithdrawal({ withdrawalParams: [ {assetId: 'nep141:x.omft.near', destinationAddress: A, amount: 100}, {assetId: 'nep141:x.omft.near', destinationAddress: B, amount: 200} ] })`.
2. The POA bridge indexes both withdrawals for the same NEAR tx hash; its status API returns an unordered array containing both entries with the same `near_token_id`.
3. `createWithdrawalIdentifiers` assigns `index: 0` to A's withdrawal and `index: 1` to B's withdrawal (per-route counter) [7](#0-6) .
4. `describeWithdrawal` is invoked once per index, but both calls execute `findMatchingWithdrawal(response.withdrawals, "nep141:x.omft.near")`, which returns the same first matching record for both calls (confirmed by existing test `"matches withdrawal by assetId, not by index"`) [5](#0-4) .
5. The promise/result intended for B's withdrawal instead resolves with A's `transfer_tx_hash` (or vice versa), misreporting completion/destination hash for the wrong withdrawal.

**Note on confidence:** This defect is explicitly documented in code comments as a known limitation rather than a silent bug, and I could not verify from the available index whether any upstream code path in this repo actually prevents batching duplicate `assetId` POA withdrawals (which would make this unreachable). Given the ask-only/index-based investigation constraints, a Devin session with full repo access would be needed to confirm whether `sdk.ts` or bridge `supports()`/validation logic blocks duplicate-asset batches before reaching this code.

### Citations

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1107)
```typescript
		it("matches withdrawal by assetId, not by index", async () => {
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
				withdrawals: [
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "other-tx-hash",
							chain: "eth",
							defuse_asset_identifier: "nep141:eth.omft.near",
							near_token_id: "eth.omft.near",
							decimals: 18,
							amount: 1000000,
							account_id: "test.near",
							address: zeroAddress,
							created: "2024-01-01T00:00:00Z",
						},
					},
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "btc-tx-hash",
							chain: "btc",
							defuse_asset_identifier: "nep141:btc.omft.near",
							near_token_id: "btc.omft.near",
							decimals: 8,
							amount: 100000,
							account_id: "test.near",
							address: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
							created: "2024-01-01T00:00:00Z",
						},
					},
				],
			});

			const bridge = new PoaBridge({
				envConfig: configsByEnvironment.production,
				xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
			});

			const result = await bridge.describeWithdrawal({
				landingChain: Chains.Bitcoin,
				index: 0,
				withdrawalParams: {
					assetId: "nep141:btc.omft.near",
					amount: 100000n,
					destinationAddress: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
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
