### Title
POA Bridge `describeWithdrawal` matches withdrawals by `assetId` only, causing status/hash misreport for multiple same-asset withdrawals in one transaction - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` and `waitForWithdrawalCompletion` resolve the on-chain destination status of a specific withdrawal by matching the POA Bridge API's returned list of withdrawals to the caller's `withdrawalParams` using only `assetId` (via `near_token_id`), with no disambiguation by destination address, amount, or withdrawal index. This breaks the equality "status/txHash reported == the on-chain outcome of *this* particular withdrawal" when a single NEAR transaction contains more than one withdrawal of the same token.

### Finding Description
`findMatchingWithdrawal` in [1](#0-0)  selects the *first* withdrawal in the API response whose `near_token_id` matches the requested `assetId`:

```
return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
```

The same pattern exists in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`: [2](#0-1) .

The code comment explicitly acknowledges the limitation: [3](#0-2) , but this is a "documented limitation," not a mitigation — the lookup still silently returns whichever matching withdrawal comes first, rather than throwing or refusing to resolve ambiguous cases. `describeWithdrawal` then reports that result as `completed` with a `txHash` taken from the matched entry: [4](#0-3) .

Each call site (`createWithdrawalIdentifier` / `describeWithdrawal`) is keyed by `WithdrawalIdentifier { landingChain, index, withdrawalParams, tx }`, i.e., the caller does track a distinct `index` per withdrawal within a NEAR transaction — but `describeWithdrawal` never uses `index` to disambiguate, only `assetId`: [5](#0-4) .

Consequently, if a single NEAR withdrawal transaction contains two (or more) withdrawals of the same token to two different destination addresses (e.g., a batch withdrawal feature, referenced in `docs/design/rfc-batch-withdrawal-granular-control.md`), calling `describeWithdrawal` for withdrawal index 1 can return the status/txHash that actually belongs to withdrawal index 0 (or vice versa), because both share the same `assetId` and the matcher just picks the first list entry that matches on token.

### Impact Explanation
This breaks the "status reported == actual on-chain outcome for this withdrawal" equality. Concretely:
- An integrator polling withdrawal #2 (e.g., to bank.address B) could receive the `txHash`/`completed` status that actually corresponds to withdrawal #1 (to address A). If the integrator credits/finalizes based on this misreported hash, it may mark withdrawal #2 as completed based on a transfer that only fulfilled withdrawal #1, potentially crediting/refunding the wrong withdrawal or crediting twice while withdrawal #2 is still pending/failed.
- Because `waitForWithdrawalCompletion` in `internal-utils` treats a matched `COMPLETED` withdrawal as a definitive terminal signal (no further check that it's the *correct* index/destination), this is a hash misreport that maps directly to the rules' High-impact category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Likelihood requires: (1) same `assetId` withdrawn more than once within a single NEAR transaction, and (2) the POA Bridge API returning both entries such that ordering/lookup picks the wrong one relative to caller's index. This is plausible for legitimate multi-recipient/batch withdrawal flows (a documented upcoming/existing use case per the RFC doc), not merely a contrived attacker-crafted input — no malicious actor action is required, only a normal usage pattern (two same-asset withdrawals in one tx), making this a realistic latent defect rather than a purely theoretical one. However, I could not fully confirm from the indexed files whether the SDK currently exposes/allows two same-asset withdrawals to different addresses within one NEAR transaction today (this depends on `sdk.signAndSendWithdrawalIntent` and the batch-withdrawal RFC feature, whose full implementation I could not completely verify within index limits).

### Recommendation
Disambiguate `findMatchingWithdrawal` using more than `assetId`: match on `assetId` + `destinationAddress` + `amount` (and/or track already-consumed entries per index so repeated calls for different indices don't return the same matched withdrawal). Alternatively, if the POA API guarantees ordering, use `index` positionally within the assetId-filtered subset instead of always taking the first match.

### Proof of Concept
1. Submit one NEAR transaction with two POA withdrawals of the same token (`nep141:eth.omft.near`): index 0 → address A (amount 1), index 1 → address B (amount 2).
2. POA Bridge completes withdrawal to address B first (e.g., due to processing order), returning `withdrawals: [{near_token_id: "eth.omft.near", transfer_tx_hash: "0xB", ...address: B}, {near_token_id: "eth.omft.near", status: "PENDING", ...address: A}]`.
3. Caller calls `describeWithdrawal({ index: 0, withdrawalParams: { assetId: "nep141:eth.omft.near", destinationAddress: A, ... } })`.
4. `findMatchingWithdrawal` returns the *first* array entry matching `assetId` — the completed withdrawal to B — and `describeWithdrawal` reports `{ status: "completed", txHash: "0xB" }` for what the caller believes is withdrawal index 0 (destined for A), even though A's withdrawal is still pending. [4](#0-3) [6](#0-5)

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-343)
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
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
