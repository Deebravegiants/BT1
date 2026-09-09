Based on the available evidence, there's a plausible analog worth reporting, though I was unable to view the exact body of `findMatchingWithdrawal` (only its type signature and call sites) before running out of tool budget.

### Title
Withdrawal status/hash matched by `assetId` alone, not by index/destination/amount, causing misattribution in multi-withdrawal batches - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`describeWithdrawal` in the POA bridge resolves the on-chain status/hash of a specific withdrawal by matching entries in an *unsorted* list returned by the bridge API using **only `assetId`** as the equality key, instead of a per-withdrawal identifier (index, destination, amount). This is the same bug class as the "golden entropy" report: a check is performed at the wrong granularity — validating a coarse/aggregate attribute (`assetId`) as if it uniquely identified a single item in a set, when the set can legitimately contain multiple items sharing that attribute.

### Finding Description
`describeWithdrawal` explicitly comments on this design choice: [1](#0-0) 

and the shared helper used by `waitForWithdrawalCompletion` defines the matching criteria as `assetId` only: [2](#0-1) 

The SDK explicitly supports batches of withdrawals executed atomically in a single NEAR transaction, tracked by array index, as documented: [3](#0-2) [4](#0-3) 

If a user (or integrator) submits two or more withdrawals with the **same `assetId`** in one batch — e.g., withdrawing the same token to two different destination addresses, or splitting one token into two amounts — the POA bridge's status response for that NEAR tx hash will contain multiple withdrawal entries sharing that `assetId`. Because the match key is `assetId` alone (not index, destination, or amount), `findMatchingWithdrawal` will bind whichever entry happens to satisfy `assetId` equality to *every* query for that same `assetId` in the batch, regardless of which logical withdrawal (index 0 vs. index 1) is being polled.

### Impact Explanation
This breaks the equality "the status/txHash reported for withdrawal *i* corresponds to withdrawal *i*'s actual on-chain outcome." An integrator that persists completion state per index (as the RFC's "Index correspondence" model recommends) could:
- Report withdrawal A as `completed` using withdrawal B's `transfer_tx_hash`, causing the wrong destination hash to be recorded/credited against a different withdrawal.
- Cause a double credit/refund decision if both withdrawals resolve to the same status object, or a permanently stuck ("pending") status for one withdrawal in the pair.

This falls under the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
Requires no privileged access — an ordinary user or integrator constructing a batch withdrawal with two identical-`assetId` legs (a scenario the SDK's own batch/granular-control API is designed to support) is sufficient to trigger ambiguous matching. Likelihood depends on how often batches contain duplicate-`assetId` legs and how the unsorted bridge-API response happens to order/return entries; I could not confirm from the indexed code whether `findMatchingWithdrawal`'s internal implementation has any additional disambiguation (e.g., first-pending-first-match, exact index tracking) since its function body was not available in the index.

### Recommendation
Extend the matching criteria (and the `WithdrawalCriteria` type) to include a value that uniquely identifies the specific withdrawal within a batch — e.g., destination address, amount, and/or a memo/nonce echoed by the bridge API — rather than `assetId` alone, mirroring the C4 report's mitigation of validating each discrete unit instead of the aggregate.

### Proof of Concept
1. Call `signAndSendWithdrawalIntent` with a batch `withdrawalParams` array containing two entries with identical `assetId` but different `destinationAddress`/`amount` (supported per `packages/intents-sdk/src/sdk.ts:557-609`).
2. After the batch NEAR tx lands, call `describeWithdrawal` (or `waitForWithdrawalCompletion`) for each index/withdrawal.
3. Because `findMatchingWithdrawal` keys only on `assetId`, both calls resolve against the same bridge-API list entry with that `assetId`, so at least one of the two logical withdrawals gets the other's `status`/`transfer_tx_hash`.

**Note:** I could not retrieve the exact implementation body of `findMatchingWithdrawal` within the tool budget — only its call sites and the `WithdrawalCriteria` type (`{ assetId: string }`) — so I cannot rule out an internal disambiguation step I didn't see. If such logic exists, this finding does not hold; a Devin session with full file access would be needed to confirm the function body definitively.

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L31-68)
```typescript
export type WithdrawalCriteria = {
	assetId: string;
};

export async function waitForWithdrawalCompletion({
	txHash,
	withdrawalCriteria,
	signal,
	baseURL,
	retryOptions = RETRY_CONFIGS.TWO_MINS_GRADUAL,
	logger,
}: {
	txHash: string;
	withdrawalCriteria: WithdrawalCriteria;
	signal: AbortSignal;
	baseURL?: string;
	retryOptions?: RetryOptions;
	logger?: ILogger;
}): Promise<WaitForWithdrawalCompletionOkType> {
	return retry(
		async () => {
			const result = await getWithdrawalStatus(
				{ withdrawal_hash: txHash },
				{ baseURL, fetchOptions: { signal }, logger },
			);

			const withdrawal = findMatchingWithdrawal(
				result.withdrawals,
				withdrawalCriteria,
			);
			if (withdrawal == null) {
				throw new PoaWithdrawalInvariantError(
					"POA Bridge didn't return withdrawal matching criteria",
					result,
					txHash,
					withdrawalCriteria,
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

**File:** docs/design/rfc-batch-withdrawal-granular-control.md (L279-281)
```markdown
### Index correspondence

Array index of returned promise matches array index of input `withdrawalParams`. SDK handles internal per-route indexing transparently.
```
