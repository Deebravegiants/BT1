### Title
POA Bridge withdrawal status matched only by `assetId`, causing wrong destination tx hash / status to be reported for co-located withdrawals - (File: packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts, packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
When a single NEAR intents transaction contains more than one POA-bridge withdrawal of the *same* token (`assetId`), both the internal `waitForWithdrawalCompletion` helper and `PoaBridge.describeWithdrawal` pick the *first* withdrawal record returned by the POA Bridge API that matches the `assetId`, ignoring the destination address, amount, or per-withdrawal index. This breaks the equality "status/txHash reported for withdrawal N == on-chain outcome of withdrawal N," letting the status reported for one user's/one output's withdrawal actually belong to a different withdrawal.

### Finding Description
`findMatchingWithdrawal` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts:144-153` matches purely on token identity:
```
return withdrawals.find(
    (w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
);
```
The preceding comment (lines 138-142) explicitly acknowledges: *"Currently only matches by assetId... multiple withdrawals of the same token in a single transaction are not supported."*

The same pattern is used in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343` (`describeWithdrawal`), where the comment states *"Response list is unsorted, so we match by assetId instead of index"* and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`.

Because the POA relayer's `getWithdrawalStatus` API returns all withdrawals attached to a NEAR tx hash without a stable identifier that ties back to `index`, `destinationAddress`, or `amount`, whenever a single NEAR intents transaction contains two or more withdrawals of the same underlying token (e.g. a batched intents transaction produced by a solver/relayer serving multiple users, or a single user withdrawing the same asset to two different destinations), `describeWithdrawal`/`waitForWithdrawalCompletion` will deterministically return the **same** matched record (the first one in the array) for every caller querying that `assetId`/tx hash, regardless of which specific withdrawal (index) is being polled.

This breaks the equality: "status/txHash returned for withdrawal at index i" must equal "the actual on-chain outcome of withdrawal i's specific (destination, amount)". Instead, an unrelated withdrawal's `completed`/`txHash` (or `failed`/`reason`) can be reported for a different withdrawal in the same batch.

### Impact Explanation
`watchWithdrawal` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:33-77`) uses `describeWithdrawal` as source of truth to resolve `waitForWithdrawalCompletion`/`sdk.waitForWithdrawalCompletion`, returning `{ hash: txHash }` to the caller once `status === "completed"`. An integrator relying on the SDK to determine when a specific withdrawal (by index) landed on the destination chain can therefore be told withdrawal B is `completed` with hash `H` while withdrawal A (a different destination/amount, same asset) is actually the one associated with `H`, or the withdrawal that is actually pending/failed gets reported `completed`. This can cause an integrator to credit/release goods or off-ramp funds for the wrong withdrawal, or double-credit two different withdrawals against a single completed transfer — matching the "status or hash misreport making an integrator credit or refund twice" High-severity criterion.

### Likelihood Explanation
This requires more than one POA-bridge withdrawal of the same `nep141` asset within one NEAR intents transaction (multiple `mt_withdraw`/withdrawal intents batched into one signed intent, or multiple users' withdrawals settled in the same relayer transaction). This is a normal, unprivileged usage pattern of the SDK (`sdk.createWithdrawalIntents`/batch withdrawals) rather than requiring any privileged/malicious relayer action — a legitimate but "unlucky" (or intentionally crafted by any caller) batch of same-asset withdrawals triggers the mismatch deterministically, since the code always returns the first array match.

### Recommendation
Track the POA Bridge withdrawal by a criterion that uniquely identifies each output—e.g., include `destinationAddress` and `amount` (and reject/serialize by relative amount ordering as the code comment suggests) in `WithdrawalCriteria`, or require the POA Bridge API to expose a per-output identifier (index or nep141 transfer index) that `findMatchingWithdrawal` can match against instead of `assetId` alone. Until the API supports this, the SDK should either explicitly disallow/assert against batching multiple same-asset POA withdrawals in one call, or surface a clear error instead of silently returning a possibly-incorrect status.

### Proof of Concept
1. Build an intents transaction containing two POA-bridge withdrawal intents for the same asset, e.g. `nep141:btc.omft.near`, with different `destinationAddress`/`amount` (index 0 and index 1), and submit/execute it.
2. Call `sdk.waitForWithdrawalCompletion` (or `bridge.describeWithdrawal`) separately for `wid` at `index: 0` and `index: 1`.
3. Observe both calls invoke `poaBridge.httpClient.getWithdrawalStatus({ withdrawal_hash: tx.hash })`, and `findMatchingWithdrawal` in both `poa-bridge.ts` and `waitForWithdrawalCompletion.ts` filters `response.withdrawals` solely by `nep141:${near_token_id} === assetId`, returning the same (first) entry for both index 0 and index 1 queries.
4. If withdrawal index 1 completes before index 0 (e.g., different destination chain latency), a caller polling index 0's status will incorrectly receive index 1's `transfer_tx_hash`/`completed` status, and vice versa. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-78)
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
				} catch (err: unknown) {
					if (err instanceof WithdrawalFailedError) {
						throw err;
					}

					consecutiveErrors++;
					if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
						throw new WithdrawalWatchError(err);
					}

					args.logger?.warn(
						`Transient error (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}): ${err}`,
					);
					return POLL_PENDING;
				}
			},
			{ stats, signal: args.signal },
		);
	} catch (err: unknown) {
		if (err instanceof PollTimeoutError) {
			throw new WithdrawalWatchError(err);
		}
		throw err;
	}
}
```
