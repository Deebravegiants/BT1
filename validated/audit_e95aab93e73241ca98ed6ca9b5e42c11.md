### Title
`findMatchingWithdrawal` matches POA withdrawal status by `assetId` only, misreporting status/txHash for the wrong withdrawal when a batch contains multiple withdrawals of the same token - (File: packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts, packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
Both the low-level `waitForWithdrawalCompletion` helper and `PoaBridge.describeWithdrawal` resolve the status/destination tx hash of a specific withdrawal index by scanning the POA bridge's returned withdrawal list and matching **only on `assetId`/`near_token_id`**, ignoring `index`, `amount`, and `destinationAddress`. This breaks the equality "the status/hash reported for withdrawal N is the on-chain outcome of withdrawal N" whenever a single NEAR transaction contains more than one withdrawal of the same token (e.g. a batch withdrawal splitting the same asset to two different destination addresses/amounts).

### Finding Description
`findMatchingWithdrawal` in `poa-bridge.ts` selects the first withdrawal entry whose `near_token_id` matches the requested `assetId`: [1](#0-0) 

This function is explicitly documented as unsound for the multi-withdrawal-same-token case: [2](#0-1) 

`describeWithdrawal` then blindly trusts whatever entry was returned by this best-effort match and reports its status/`transfer_tx_hash` as the result for the caller's specific `withdrawalParams`/`index`: [3](#0-2) 

The exact same matching-by-`assetId`-only logic (with the identical caveat comment) is duplicated in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`: [4](#0-3) [5](#0-4) 

Concretely, when `sdk.createWithdrawalCompletionPromises`/`watchWithdrawal` polls each withdrawal identifier independently by calling `bridge.describeWithdrawal` per index: [6](#0-5) 

if a caller submits two POA withdrawals of the **same asset** in one NEAR transaction (e.g. same token withdrawn to two different destination addresses/amounts, which is a supported multi-withdrawal intent execution), `describeWithdrawal(index=0)` and `describeWithdrawal(index=1)` will both resolve `findMatchingWithdrawal` against the identical `assetId` and can return the *same* array entry (typically the first match) for both indexes. This means:
- Index 0's `destinationAddress`/`amount` may be completely different from what is actually reported completed.
- The reported `transfer_tx_hash` for index 0 could actually belong to the withdrawal destined for index 1's address/amount.
- If index 1's real withdrawal is still pending or failed, the caller is told (via `describeWithdrawal(index=1)` also matching the *same* first entry) that it is "completed" with the wrong `transfer_tx_hash`, while its actual on-chain withdrawal has not happened yet.

This directly breaks the required equality: "a status/hash reported that is not the true on-chain outcome" for that specific withdrawal index/destination.

### Impact Explanation
An integrator building on `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` relies on the returned `status`/`txHash` per withdrawal index to decide when to consider a withdrawal settled (e.g., to mark an order complete, release custody, or notify a user their funds arrived at a specific destination). Because the match is only on `assetId`, two same-token withdrawals in one batch can be conflated:
- The same `transfer_tx_hash` can be reported as the "completed" outcome of two different withdrawal indices with two different destination addresses, causing the integrator to credit/consider two distinct withdrawals settled based on a single real transfer.
- A withdrawal that actually failed/is still pending can be masked as "completed" because the matcher grabbed a different index's completed entry.

This matches the "status or hash misreport making an integrator credit or refund twice" High-impact criterion, since it can cause an integrator to believe funds arrived at address B (or twice) when in fact only one transfer occurred, potentially to a different address than reported.

### Likelihood Explanation
This requires a batch/multi-withdrawal call where two or more withdrawals in the same underlying request share the same `assetId` (same NEP-141 token) but differ in destination address and/or amount. This is a realistic usage pattern (e.g., splitting a payout of the same token to two users), not an attacker-controlled edge case requiring privileged roles — it's a normal caller-driven withdrawal batching scenario, and the code comments themselves acknowledge this is an unhandled case ("Currently only matches by assetId... multiple withdrawals of the same token in a single transaction are not supported").

### Recommendation
Match withdrawals using more specific criteria than `assetId` alone — at minimum include `destinationAddress` and `amount` (and stable ordering/index correlation as suggested in the existing code comment: sort both API results and withdrawal params by amount, since fees are equal for the same token, to preserve relative ordering). Until such disambiguation is implemented, `describeWithdrawal`/`waitForWithdrawalCompletion` should refuse to resolve (remain "pending" or throw an invariant error) when more than one withdrawal entry matches the same `assetId`, rather than silently picking the first match.

### Proof of Concept
1. Caller submits an intent execution containing two POA withdrawals of the same token, e.g.:
   - index 0: `assetId: "nep141:usdc.omft.near"`, `amount: 100`, `destinationAddress: "addrA"`
   - index 1: `assetId: "nep141:usdc.omft.near"`, `amount: 200`, `destinationAddress: "addrB"`
2. POA bridge status API returns withdrawals list containing one `COMPLETED` entry for the `addrB`/`200` withdrawal (transfer_tx_hash = `0xB`) and one `PENDING` entry for `addrA`/`100`.
3. `findMatchingWithdrawal` for index 0 (`describeWithdrawal({assetId:"nep141:usdc.omft.near", index:0, ...})`) iterates `withdrawals.find(w => nep141:${w.data.near_token_id} === assetId)` and returns the **first** entry regardless of index — if the completed entry happens to be first in the (documented as "unsorted") response array, index 0's `describeWithdrawal` call incorrectly reports `{status:"completed", txHash:"0xB"}`, even though the actual on-chain outcome for `addrA` is still pending.
4. `watchWithdrawal`/`createWithdrawalCompletionPromises` resolves index 0 as completed with `0xB`, an outcome that never happened for `addrA`'s withdrawal — the caller now believes a withdrawal to `addrA` settled, referencing a transaction that actually sent funds to `addrB`. [3](#0-2) [7](#0-6)

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L405-427)
```typescript
type WithdrawalStatusResponse = Awaited<
	ReturnType<typeof poaBridge.httpClient.getWithdrawalStatus>
>;

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L50-84)
```typescript
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

			if (withdrawal.status === "COMPLETED") {
				if (withdrawal.data.transfer_tx_hash == null) {
					throw new PoaWithdrawalInvariantError(
						"POA Bridge didn't return transfer_tx_hash for COMPLETED withdrawal",
						result,
						txHash,
						withdrawalCriteria,
					);
				}

				return {
					destinationTxHash: withdrawal.data.transfer_tx_hash,
					chain: withdrawal.data.chain,
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
