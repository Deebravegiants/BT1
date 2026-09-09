### Title
POA Bridge withdrawal status matches by `assetId` only, causing cross-withdrawal status/hash misreport for batched same-asset withdrawals - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal()` and `internal-utils`' `waitForWithdrawalCompletion()` both identify which POA withdrawal record belongs to a given `WithdrawalIdentifier`/`index` purely by matching `assetId` (via `near_token_id`), ignoring `index`, `amount`, and `destinationAddress`. When a single NEAR transaction contains more than one withdrawal of the same asset (which the SDK's own batch API — `signAndSendWithdrawalIntent` with an array of `withdrawalParams` — explicitly supports), both withdrawals resolve to the *same* matched record, so the wrong `transfer_tx_hash`/status can be reported for a withdrawal that is actually still pending, failed, or going to a different destination.

### Finding Description
`findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` is used by `describeWithdrawal`: [1](#0-0) 

It returns the **first** withdrawal in the unsorted API response array whose `near_token_id`-derived assetId matches — it does not use `args.index`, `args.withdrawalParams.destinationAddress`, or `args.withdrawalParams.amount` to disambiguate: [2](#0-1) 

The same pattern, with the same documented limitation, exists in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`: [3](#0-2) 

The code comment on both copies of this function explicitly acknowledges the gap: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." [4](#0-3) 

The SDK, however, does support submitting multiple withdrawals atomically in one NEAR transaction, including with the same `assetId`, via `signAndSendWithdrawalIntent`/`processWithdrawal` with an array of `withdrawalParams`, as shown in the tests: [5](#0-4) 

If a caller batches two POA-routed withdrawals of the same token (e.g., two separate BTC withdrawals to two different destination addresses) in one NEAR tx, both produce a `WithdrawalIdentifier` with the same `landingChain`/`assetId` but different `index`. When `describeWithdrawal({..., index: 0})` and `describeWithdrawal({..., index: 1})` are both called, `findMatchingWithdrawal` returns the *same* array element for both, because matching is keyed solely on `assetId`. If that element is `COMPLETED`, both calls report the identical `status: "completed", txHash` — even though the second withdrawal (index 1) may in reality be `PENDING`, have a different destination `transfer_tx_hash`, or have failed.

### Impact Explanation
This breaks the equality "status/hash reported == actual on-chain outcome for *this specific* withdrawal." An integrator or downstream automation that relies on `describeWithdrawal`/`waitForWithdrawalCompletion` per-index results to mark a specific batched withdrawal as completed and release/credit funds (or close out a corresponding off-chain obligation) could:
- Credit/confirm withdrawal index 1 as completed using withdrawal index 0's `transfer_tx_hash`, even though index 1 went to a different destination address or amount and may still be pending or failed.
- Potentially double-credit an integrator's internal accounting keyed on hash/status if the same hash is reported for two logically distinct withdrawals.

This matches the "High" impact category: a status or hash misreport making an integrator credit or refund incorrectly for a legitimate, non-malicious batch withdrawal (no attacker action required — it's triggered by the SDK's own documented supported use case of batching same-asset withdrawals).

### Likelihood Explanation
This requires no adversarial input — it is triggered purely by using the SDK's supported batch-withdrawal API (`signAndSendWithdrawalIntent`/`processWithdrawal` with multiple `withdrawalParams` for the same `assetId` routed through POA bridge) and then polling per-index withdrawal status. Any integrator batching multiple withdrawals of the same token (a natural pattern, e.g., processing a queue of BTC/ZEC/XRP withdrawals) is exposed. The bug is also self-documented in the code comments, confirming the maintainers are aware the case is unhandled, though it is not gated/blocked anywhere (no assertion rejects batched same-asset withdrawals before submission).

### Recommendation
Disambiguate matching in both `findMatchingWithdrawal` implementations by additionally matching on `destinationAddress`/`amount` (and consuming matched entries so they cannot be reused across indices), or reject/serialize batches containing duplicate `assetId` withdrawals routed through the POA bridge until the POA API supports per-withdrawal correlation (e.g., a client-supplied nonce/index echoed back). At minimum, add a client-side guard in `sdk.ts` that throws when a batch contains multiple POA-bridge withdrawals sharing the same `assetId`, closing the gap until the API-level fix lands.

### Proof of Concept
1. Call `sdk.signAndSendWithdrawalIntent({ withdrawalParams: [ {assetId: "nep141:btc.omft.near", amount: A, destinationAddress: addr1, feeInclusive:false}, {assetId: "nep141:btc.omft.near", amount: B, destinationAddress: addr2, feeInclusive:false} ] })` — both route through `PoaBridge` (same `assetId`), producing one NEAR tx with two `ft_withdraw` intents, and two `WithdrawalIdentifier`s with `index: 0` and `index: 1`.
2. Suppose only the withdrawal to `addr1` (index 0) has actually completed on-chain, while `addr2` (index 1) is still pending at the POA relayer.
3. Call `bridge.describeWithdrawal({..., index: 0})` → returns `{status:"completed", txHash: <addr1's tx>}` (correct).
4. Call `bridge.describeWithdrawal({..., index: 1})` → `findMatchingWithdrawal` again finds the *same* `COMPLETED` record for `assetId`, returning `{status:"completed", txHash: <addr1's tx>}` — incorrectly reporting withdrawal index 1 as completed with a transaction hash that actually corresponds to `addr1`'s transfer, not `addr2`'s.

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L136-153)
```typescript
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
