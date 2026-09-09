### Title
Withdrawal status matched only by `assetId`/`near_token_id` causes wrong-withdrawal status/hash misreport for batched same-asset withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` and the underlying `findMatchingWithdrawal` helper (also duplicated in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) resolve the status/`transfer_tx_hash` of a specific withdrawal by matching on `assetId` (i.e. `near_token_id`) only, not by a unique per-withdrawal identifier (index/amount/nonce). When a single intent transaction contains multiple withdrawals of the same asset (a supported batch flow — `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` explicitly accept `WithdrawalParams[]` and poll each one independently by `index`), every one of those parallel `describeWithdrawal` calls queries the POA bridge with the same `tx.hash` and the same `assetId`, and `.find()` returns the *first* withdrawal in the (explicitly documented as "unsorted") response list that matches that asset — regardless of which of the several same-asset withdrawals it actually is.

### Finding Description
`describeWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (lines 313-343) does:
```
const withdrawal = findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId);
```
and `findMatchingWithdrawal` (comment at lines 318-322) explicitly states: *"Response list is unsorted, so we match by assetId instead of index."* This is only correct as long as there is at most one withdrawal per asset per transaction.

`sdk.ts`'s `createWithdrawalCompletionPromises` (lines 557-609) and `waitForWithdrawalCompletion` (lines 481-521) are explicitly designed to support **arrays** of `WithdrawalParams`, each tracked by its own `index`, and poll them independently/in parallel via `watchWithdrawal`. Nothing in this path prevents the caller from submitting two (or more) withdrawals of the *same* `assetId` to different destination addresses/amounts within one batch — the code assigns each its own `index` (see `poa-bridge.test.ts` "maintains indexes specific to bridge route"), but the actual matching in `describeWithdrawal` discards that index entirely and re-derives the match from `assetId` alone. The equivalent `internal-utils` function (`waitForWithdrawalCompletion.ts` lines 135-153) carries the same explicit caveat: *"Currently only matches by assetId... This means multiple withdrawals of the same token in a single transaction are not supported."*

Because both same-asset withdrawal promises query the same `tx.hash`/`assetId` pair, both `.find()` calls converge on the same array entry (the first same-asset withdrawal returned by the API), so:
- One withdrawal correctly reports its own `transfer_tx_hash`.
- The other, unrelated withdrawal (different destination address/amount) incorrectly resolves to the *same* `transfer_tx_hash`/completion status belonging to the first withdrawal.

This breaks the equality "the status/hash reported for withdrawal N corresponds to the on-chain outcome of withdrawal N" — the caller ends up crediting/confirming completion of the wrong withdrawal using the wrong destination's tx hash.

### Impact Explanation
If an integrator relies on `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` to confirm settlement for each of several same-asset withdrawals in a batch (e.g. paying out two different users the same token in one signed intent), the second (or duplicate) withdrawal will be reported as "completed" with the destination tx hash belonging to the *other* withdrawal. This is a status/hash misreport that can cause an integrator to mark a withdrawal as fulfilled when it was not, or to associate the wrong destination transaction with a payout record — potentially leading to double-crediting or crediting against the wrong on-chain transaction. This matches the "status or hash misreport making an integrator credit or refund twice" category (High).

### Likelihood Explanation
Requires the caller to include ≥2 withdrawals of the *same* `assetId` (same POA-bridge-routed token) in a single batched `withdrawalParams` array/transaction — a supported, documented use case of `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` per the SDK's own multi-withdrawal API and tests. No malicious actor or privileged party is needed; it is triggered by ordinary legitimate batch usage of the SDK, and the code comments themselves flag that this scenario is unhandled. However it is contingent on the integrator's own batching pattern (single-asset batches), not the default single-withdrawal happy path, so likelihood is moderate rather than certain.

### Recommendation
Match POA bridge withdrawal status/`transfer_tx_hash` results to the specific `WithdrawalIdentifier` using a combination of `assetId` and a distinguishing field such as amount/destination address, or (preferably) require/consume a unique per-withdrawal correlation id from the POA API. Until the API supports disambiguation, `findMatchingWithdrawal` should refuse to resolve (or should throw/flag ambiguity) when more than one withdrawal candidate matches the same `assetId` within a single `tx.hash`, rather than silently returning the first match, and callers of `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` should be prevented (or explicitly warned) from batching multiple same-asset POA-bridge withdrawals in one transaction.

### Proof of Concept
1. Caller builds an intent transaction with two `ft_withdraw` POA-bridge withdrawals of the same `assetId` (e.g. `nep141:btc.omft.near`) but different destination addresses/amounts, and calls `sdk.createWithdrawalCompletionPromises({ withdrawalParams: [w1, w2], intentTx })`.
2. Both entries get bridge-assigned `index: 0` and `index: 1` respectively (per `poa-bridge.test.ts`'s "maintains indexes specific to bridge route" test), but `describeWithdrawal` for each calls `getWithdrawalStatusWithRetry` with the same `tx.hash`, then `findMatchingWithdrawal(response.withdrawals, assetId)`.
3. The POA API returns both withdrawals (unsorted) with the same `near_token_id`/`assetId`; `.find()` in both invocations returns the same (first) entry.
4. Promise for `w2` resolves with `w1`'s `transfer_tx_hash`, misreporting `w2` as completed on a transaction that actually paid `w1`'s destination. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** packages/intents-sdk/src/sdk.ts (L557-609)
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
