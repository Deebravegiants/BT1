### Title
POA bridge `describeWithdrawal` misreports the wrong withdrawal's status/txHash for multi-withdrawal transactions with duplicate assets - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the status/transaction hash of a specific withdrawal leg (identified by `index` within a NEAR transaction) by matching the POA bridge API response only on `assetId`, ignoring the `index` field entirely. When a single NEAR transaction contains two or more withdrawal legs for the same asset, the function will always report the status/hash of whichever matching entry happens to appear first in the (explicitly documented as unsorted) API response, regardless of which withdrawal `index` was actually requested.

### Finding Description
`createWithdrawalIdentifier` builds a `WithdrawalIdentifier` that carries an `index` distinguishing multiple withdrawals batched into the same NEAR transaction: [1](#0-0) .

`describeWithdrawal` then calls `findMatchingWithdrawal`, but that helper only matches on `assetId` and never consults `index`: [2](#0-1) [3](#0-2) .

The code comments explicitly acknowledge the response list is unsorted and that "multiple withdrawals of the same token in a single transaction are not supported" by this matching logic: [4](#0-3) . Because `Array.prototype.find` returns only the first element satisfying the predicate, if a NEAR transaction contains two withdrawals of the same `assetId` (e.g. two separate withdrawal intents for the same token batched together), calling `describeWithdrawal({ index: 0, ... })` and `describeWithdrawal({ index: 1, ... })` for that transaction will both return the exact same result — the first matching withdrawal record from the API, whose `status` and `transfer_tx_hash` correspond to only one of the two on-chain withdrawal outcomes.

This breaks the equality "status/hash reported for withdrawal N == the actual on-chain outcome of withdrawal N." The status and `txHash` field returned by `describeWithdrawal` are used by integrators to determine whether a specific withdrawal has completed and to obtain its destination-chain transaction hash for reconciliation.

### Impact Explanation
If an integrator relies on `describeWithdrawal` per-index results to mark specific withdrawal legs as completed/failed (e.g., to release custody, mark an order filled, or refund a specific leg), a second same-asset withdrawal in the same transaction will be reported as "completed" with the transaction hash belonging to the *first* leg, even if the second leg is still pending or actually failed. This can cause an integrator to prematurely credit or reconcile a withdrawal that has not actually completed, or to be unable to distinguish between the outcomes of the two legs, matching the "status or hash misreport making an integrator credit or refund twice" category.

### Likelihood Explanation
This requires no privileged access — any caller of the SDK that constructs a withdrawal transaction bundling more than one withdrawal for the same `assetId` within a single NEAR transaction (a valid, unprivileged usage pattern) will trigger the misreport deterministically once both withdrawals reach the POA bridge indexer. The bug is unconditional in that scenario, not merely theoretical, and is already acknowledged in the code's own comment as an unhandled case.

### Recommendation
Extend `findMatchingWithdrawal` (or the underlying POA bridge API) to disambiguate between multiple same-asset withdrawals in one transaction — e.g., by sorting both the API response and locally tracked withdrawal legs by amount (as the existing comment suggests) or by requesting/using a stable per-leg identifier from the POA API — and use that alongside `assetId` when selecting the matching withdrawal for a given `index`.

### Proof of Concept
1. Construct and submit a single NEAR transaction containing two withdrawal intents for the same `assetId` (e.g., two `nep141:btc.omft.near` withdrawals to different destination addresses/amounts), yielding `index: 0` and `index: 1` for the same `tx.hash`.
2. The POA bridge indexer eventually reports both withdrawals: leg 0 as `COMPLETED` with `transfer_tx_hash: "txA"`, leg 1 still `PENDING`.
3. Call `describeWithdrawal({ tx, index: 0, withdrawalParams: { assetId } })` → returns `{ status: "completed", txHash: "txA" }` (correct).
4. Call `describeWithdrawal({ tx, index: 1, withdrawalParams: { assetId } })` → `findMatchingWithdrawal` again returns the same first matching entry (`txA`, `COMPLETED`), so the SDK incorrectly reports leg 1 as completed with `txA`, even though leg 1 is still pending on-chain. [2](#0-1)

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
