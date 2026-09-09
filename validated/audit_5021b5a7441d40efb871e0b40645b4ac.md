### Title
POA Bridge status misreport for batched same-token withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` matches an on-chain withdrawal record to a `WithdrawalIdentifier` using only `assetId`, ignoring the identifier's `index`. When a batch withdrawal contains two or more legs that withdraw the *same* NEP-141 asset to different destinations (a legitimate use case supported by the public `processWithdrawal`/`createWithdrawalCompletionPromises` API), every leg with that `assetId` resolves to the same matched record — the first one returned by the POA API — regardless of which specific leg's completion is actually being queried.

### Finding Description
`findMatchingWithdrawal` selects a withdrawal purely by `nep141:${w.data.near_token_id} === assetId`: [1](#0-0) 

`describeWithdrawal` uses this match to report status/txHash for a given `WithdrawalIdentifier`, even though the identifier also carries an `index` meant to disambiguate multiple withdrawals in the same NEAR transaction: [2](#0-1) 

The SDK's `createWithdrawalIdentifiers` assigns a per-bridge `index` to each withdrawal leg, confirming multiple same-route legs are expected to be distinguishable by index: [3](#0-2) 

`createWithdrawalCompletionPromises` and `waitForWithdrawalCompletion` then call `bridge.describeWithdrawal` independently per leg (per index) and treat each resolved status as authoritative for that specific leg: [4](#0-3) 

Because `findMatchingWithdrawal` never consults `index`/destination/amount, two legs of the same `assetId` (e.g., withdraw 100 USDC to address A and 50 USDC to address B in the same batch) both resolve to whichever single API record matches that `assetId` first. This breaks the equality "status/txHash reported for withdrawal N == the on-chain outcome of withdrawal N": one leg can be reported `completed` with the other leg's `transfer_tx_hash`, or a `failed`/`pending` leg can be masked by a `completed` sibling.

### Impact Explanation
This matches the allowed High-impact class: "a status or hash misreport making an integrator credit or refund twice." An integrator using `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` to drive per-leg bookkeeping (e.g., mark leg 0 as paid when its promise resolves) could mark the wrong leg complete, potentially crediting/refunding based on a txHash that belongs to a different destination/amount, or missing a genuine failure because a sibling leg's "completed" status is reported instead.

### Likelihood Explanation
This is reachable with no privileged behavior — any caller batching multiple `WithdrawalParams` for the same `assetId` (different destinations/amounts) through the POA bridge route triggers it. The code comment in `poa-bridge.ts` acknowledges the matching is index-agnostic ("matching by assetId... multiple withdrawals of the same token... not supported"), but nothing in the public SDK API (`processWithdrawal`, `createWithdrawalCompletionPromises`) prevents or warns callers against constructing such a batch.

### Recommendation
Either (a) reject/validate at the SDK layer that a single batch cannot contain multiple POA-routed legs with the same `assetId`, surfacing a clear error, or (b) disambiguate matches in `findMatchingWithdrawal` using destination address/amount/order once the POA API exposes enough data to do so, so each `WithdrawalIdentifier.index` maps deterministically to its own on-chain record.

### Proof of Concept
1. Call `sdk.processWithdrawal` (or `createWithdrawalCompletionPromises`) with `withdrawalParams = [{assetId: "nep141:btc.omft.near", destinationAddress: A, amount: 100000n}, {assetId: "nep141:btc.omft.near", destinationAddress: B, amount: 50000n}]`, both routed through `PoaBridge`.
2. POA API returns one `COMPLETED` record for the withdrawal to `A` (`transfer_tx_hash: "tx-A"`) and, separately, a `PENDING`/absent record for `B`.
3. `describeWithdrawal` is called twice, once per identifier (`index: 0` and `index: 1`), both with `assetId = "nep141:btc.omft.near"`.
4. `findMatchingWithdrawal` returns the same `COMPLETED`/`tx-A` record for both calls (see the existing test `matches withdrawal by assetId, not by index` at [5](#0-4)  which demonstrates assetId-based matching working correctly when assetIds differ — but there is no equivalent test/guard when two legs share the same `assetId`).
5. Result: the promise for leg index 1 (destination `B`) resolves as `completed` with `tx-A`'s hash, even though `B`'s withdrawal may still be pending or have failed.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-343)
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

		if (withdrawal.status === "PENDING") {
			return { status: "pending" };
		}

		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
		}

		return {
			status: "failed",
			reason: withdrawal.status,
		};
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1111)
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
				status: "completed",
				txHash: "btc-tx-hash",
			});
		});
```
