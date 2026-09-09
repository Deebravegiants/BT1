### Title
Withdrawal status/tx-hash misreport when multiple withdrawals of the same asset share one NEAR transaction - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` reports the completion status and destination transaction hash of a withdrawal by matching only on `assetId` against the POA bridge API response, ignoring the `index` field that is supposed to disambiguate multiple withdrawals batched in a single NEAR transaction.

### Finding Description
`describeWithdrawal` receives a `WithdrawalIdentifier` that includes both `withdrawalParams.assetId` and `index` (the position of this withdrawal among possibly several created in the same NEAR transaction, see `createWithdrawalIdentifier` at [1](#0-0) ). However, when resolving the actual on-chain outcome, it calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which only compares `nep141:${w.data.near_token_id}` against the requested `assetId` and returns the first match, never consulting `args.index`: [2](#0-1) [3](#0-2) 

The function's own docstring acknowledges the limitation: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." [4](#0-3) 

The equality that should hold is: *the reported `{status, txHash}` for withdrawal at `index=N`, `assetId=A` must correspond to the on-chain outcome of that specific withdrawal N*, not just "some withdrawal of asset A." When a caller submits a single NEAR transaction containing two or more withdrawal intents of the same `assetId` (e.g., different amounts/destination addresses), `Array.prototype.find` returns the first entry in the (explicitly documented as "unsorted") API response list that matches the assetId, regardless of which of the N withdrawals it actually corresponds to.

### Impact Explanation
If an integrator polls `describeWithdrawal` for withdrawal index 1 (e.g., a large amount to address B) while withdrawal index 0 (a smaller amount to address A) of the same asset already completed, the SDK will report index 1 as `completed` with the `transfer_tx_hash` that actually belongs to index 0's on-chain payout to address A. This is a status/hash misreport: the integrator can be led to believe a specific withdrawal (to a specific destination) settled on-chain using a transaction hash that never paid that destination, potentially causing the integrator to credit/release downstream funds or close accounting for a withdrawal that has not actually landed at its correct destination — matching the "status or hash misreport making an integrator credit or refund twice" impact class.

### Likelihood Explanation
This requires the caller (via `createWithdrawalIntents`/SDK usage) to batch more than one withdrawal of the same `assetId` in a single NEAR transaction — a normal, unprivileged usage pattern (no admin or relayer collusion needed) rather than an edge case requiring malicious intervention. The code comment itself confirms this exact scenario is known to be unhandled, and the POA API is stated to return withdrawals in an "unsorted" list, so the first-match behavior is non-deterministic with respect to which real withdrawal it lands on.

### Recommendation
Extend `findMatchingWithdrawal` (both the `poa-bridge.ts` and `internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` variants) to disambiguate using additional withdrawal-specific fields available in the API response (e.g., destination `address`, `amount`, and consuming the `index` positionally after deterministic sorting) rather than matching on `assetId` alone, so that the reported status/txHash is guaranteed to correspond to the specific withdrawal being queried.

### Proof of Concept
1. Caller creates a NEAR transaction with two withdrawal intents for the same `assetId` (e.g., `nep141:eth.omft.near`): withdrawal index 0 → address A, amount 100; withdrawal index 1 → address B, amount 900.
2. POA bridge completes withdrawal 0 (to A) first; withdrawal 1 (to B) is still pending.
3. Integrator calls `bridge.describeWithdrawal({ index: 1, withdrawalParams: { assetId: "nep141:eth.omft.near", ... }, tx })`.
4. `findMatchingWithdrawal` returns the API entry for withdrawal 0 (first match by `assetId`), and `describeWithdrawal` returns `{ status: "completed", txHash: <A's tx hash> }` for what is actually still-pending withdrawal 1 destined for B. [5](#0-4)

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
