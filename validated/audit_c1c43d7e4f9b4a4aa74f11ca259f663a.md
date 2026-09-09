### Title
POA Bridge Withdrawal Status Misreported for Duplicate-Asset Batch Withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` matches a withdrawal's on-chain completion status by `assetId` alone rather than by the specific withdrawal being tracked, so batch withdrawals containing two or more entries with the same `assetId` (e.g. paying different destination addresses/amounts in the same intent) can have their statuses cross-reported.

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` [1](#0-0) . This lookup ignores `index`, `destinationAddress`, and `amount`, and the code comment itself documents the limitation: "multiple withdrawals of the same token in a single transaction are not supported" [2](#0-1) .

`sdk.createWithdrawalCompletionPromises` and `sdk.waitForWithdrawalCompletion` accept an array of `WithdrawalParams` and independently poll `bridge.describeWithdrawal` for each item, matching results back to the caller strictly by array index — the SDK's own tests assert "Index correspondence: `promises[i]` corresponds to `withdrawalParams[i]`" and separately verify order-independent resolution [3](#0-2) . Nothing in `WithdrawalParams`, `estimateWithdrawalFee`, or `signAndSendWithdrawalIntent` rejects a batch containing two withdrawals with the same `assetId` but different `destinationAddress`/`amount` — there is no uniqueness check across `withdrawalParams[]` for the POA route. The `Bridge` interface's `describeWithdrawal` contract is a "one-shot status check for a withdrawal" identified by `WithdrawalIdentifier` (which includes `index` and the specific `withdrawalParams`) [4](#0-3) , but the POA implementation silently ignores `index`/amount/address and returns whichever matching-assetId entry the bridge API lists first.

Consequently, if a caller batches two withdrawals of the same token (e.g., paying user A and user B the same asset in one intent), both `describeWithdrawal` calls resolve against the same underlying bridge record. This breaks the equality "status/txHash reported for withdrawal i must reflect the on-chain outcome of withdrawal i" — the caller can receive `{ status: "completed", txHash: X }` for withdrawal index 1 when `X` is actually the destination-chain transaction for withdrawal index 0 (or vice versa), and the still-pending withdrawal is masked as already completed with a hash that belongs to a different recipient/amount.

### Impact Explanation
This matches "a status or hash misreport making an integrator credit or refund twice" (High). An integrator using `processWithdrawal`/`waitForWithdrawalCompletion` on a batch with duplicate `assetId` entries can be told withdrawal B is `completed` with a `txHash` that actually pays out to a different destination/amount (withdrawal A). Depending on integrator logic, this can cause a double-credit/incorrect settlement bookkeeping (marking a still-pending payout as done, or attributing a completed transfer to the wrong recipient in downstream systems) with no way to distinguish the correct hash from the API response.

### Likelihood Explanation
Requires only an ordinary (non-malicious) caller of the public SDK API to submit a batch withdrawal with two entries sharing the same `assetId` on the POA route — a legitimate, unremarkable usage pattern (e.g., paying two users the same token) that is not blocked or documented as disallowed anywhere in `signAndSendWithdrawalIntent`/`estimateWithdrawalFee`/`processWithdrawal`. The only in-code warning is a source comment, not a runtime guard, so there's no assertion or validation function actually preventing this input from reaching `describeWithdrawal`.

### Recommendation
Either (a) reject batches at `estimateWithdrawalFee`/`signAndSendWithdrawalIntent` time when two or more `WithdrawalParams` share both the same bridge route and same `assetId`, surfacing a clear `UnsupportedBatchWithdrawalError`, or (b) disambiguate matches in `findMatchingWithdrawal` by also comparing `destinationAddress` and `amount` (and falling back to stable ordering by amount as the code comment suggests) so each `WithdrawalIdentifier` resolves to its own on-chain record instead of the first assetId match.

### Proof of Concept
1. Caller submits `processWithdrawal({ withdrawalParams: [ {assetId:"nep141:usdt...", amount:100, destinationAddress:"addrA"}, {assetId:"nep141:usdt...", amount:200, destinationAddress:"addrB"} ] })` via the POA route.
2. Both entries produce POA withdrawal intents in the same NEAR tx; the POA bridge indexer eventually returns two `withdrawals[]` records for that `tx.hash`, one for each entry — but `findMatchingWithdrawal` only filters by `near_token_id`/`assetId` [1](#0-0) .
3. `describeWithdrawal` invoked for index 0 (addrA/100) and index 1 (addrB/200) both call `.find()` over the same `withdrawals` array and can return the same array element (e.g., the addrB/200 record) for both indices, depending on array order.
4. `sdk.createWithdrawalCompletionPromises` resolves `promises[0]` with `{ hash: <addrB's tx hash> }` even though `withdrawalParams[0]` was addrA/100 [3](#0-2) , producing a hash/status for the wrong withdrawal.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-417)
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L418-427)
```typescript
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

**File:** packages/intents-sdk/src/sdk.createWithdrawalCompletionPromises.test.ts (L73-97)
```typescript
	it("maintains index correspondence when completions are out of order", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal)
			.mockImplementationOnce(() =>
				wait(50).then(() => ({
					status: "completed" as const,
					txHash: "first-hash",
				})),
			)
			.mockResolvedValueOnce({
				status: "completed",
				txHash: "second-hash",
			});

		const promises = sdk.createWithdrawalCompletionPromises({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams],
		});

		const results = await Promise.all(promises);

		expect(results[0]).toEqual({ hash: "first-hash" });
		expect(results[1]).toEqual({ hash: "second-hash" });
	});
```

**File:** packages/intents-sdk/src/shared-types.ts (L415-431)
```typescript
	/**
	 * Creates a complete withdrawal identifier with all required info.
	 * Derives landingChain from withdrawalParams.routeConfig.chain if available, otherwise from assetId.
	 */
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier;

	/**
	 * One-shot status check for a withdrawal.
	 * Returns the current status without polling.
	 */
	describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus>;
```
