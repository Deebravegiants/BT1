### Title
POA Bridge `describeWithdrawal` matches by `assetId` only, ignoring `index`, causing status/txHash misreport across multiple same-asset withdrawals in a batch - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
The `Oracle.status()` bug is a class of "an equality check based on the wrong identity/index" causing a status/settlement to be attributed to the wrong entity. The nearest in-scope analog is `PoaBridge.describeWithdrawal`, which is supposed to report the status of the withdrawal identified by `WithdrawalIdentifier.index`/`tx`, but the actual lookup (`findMatchingWithdrawal`) ignores `index` entirely and matches purely by `assetId`.

### Finding Description
`WithdrawalIdentifier` is explicitly designed to disambiguate multiple withdrawals within the same intent transaction via the `index` field ("Per-bridge withdrawal sequence number"): [1](#0-0) 

However, `PoaBridge.describeWithdrawal` never uses `args.index`; it only filters the API's withdrawal list by `assetId`: [2](#0-1) [3](#0-2) 

The same pattern (matching by `assetId`/`near_token_id` only, no positional disambiguation) exists in the sibling polling helper used for the "one-shot vs poll" completion path: [4](#0-3) 

When a single intent transaction contains two or more withdrawals of the same token (same `assetId`) to different destination addresses/amounts — a normal, non-malicious usage pattern supported by `CreateWithdrawalCompletionPromisesParams` (`withdrawalParams: WithdrawalParams[]`) and `sdk.createWithdrawalCompletionPromises` — `findMatchingWithdrawal` will return `withdrawals.find(...)`, i.e. the **first** matching entry in an **unsorted** response list, for every one of the same-asset `WithdrawalIdentifier`s regardless of which `index` was requested. The code comment itself acknowledges the list is unsorted and that same-token multi-withdrawals are unsupported: [5](#0-4) 

This breaks the equality "status reported for withdrawal N == on-chain status of withdrawal N": both `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` for the same `assetId` can resolve to the identical bridge-side withdrawal record, so one caller-visible promise reports `completed` with a `txHash` that actually belongs to the *other* withdrawal, while the true status of that other withdrawal is misrepresented or left permanently `pending`.

### Impact Explanation
This is a status/hash misreport, not a fund-authorization bypass, but it directly matches the accepted "High" impact category: *"a status or hash misreport making an integrator credit or refund twice."* An integrator that uses `describeWithdrawal`/`createWithdrawalCompletionPromises` to detect completion for multiple same-token withdrawals within one intent could:
- Mark withdrawal B as completed using withdrawal A's `transfer_tx_hash`, prematurely releasing custody/crediting for B while A is still unsettled.
- Never observe completion for the second withdrawal (stuck until manual reconciliation) because the same record keeps matching the first request.

### Likelihood Explanation
Requires no malicious actor — only a legitimate batch withdrawal containing two entries with the same `assetId` (e.g. same token routed to two different destination addresses/amounts in one call to `signAndSendWithdrawalIntent`/`processWithdrawal`). The code comments confirm the authors are aware this scenario is not correctly handled, indicating it is a real, currently-reachable gap rather than a hypothetical one.

### Recommendation
Disambiguate by `index` in addition to `assetId`, consistent with the documented approach in the code comment (sort withdrawals and requested params deterministically, e.g. by amount, since fees are identical for the same token) instead of returning the first `assetId` match. Until POA API supports per-withdrawal identifiers, `PoaBridge` (and `waitForWithdrawalCompletion`) should either: (a) reject/guard batches containing duplicate `assetId`s, or (b) implement the sort-by-amount pairing the comment proposes, ensuring each `index` maps to a unique withdrawal record.

### Proof of Concept
1. Submit one intent with `withdrawalParams = [{assetId: "nep141:X", amount: 100, destinationAddress: A}, {assetId: "nep141:X", amount: 200, destinationAddress: B}]` via a route that uses `PoaBridge`.
2. Two `WithdrawalIdentifier`s are created with `index: 0` and `index: 1`, both same `assetId`.
3. Call `describeWithdrawal` for both identifiers concurrently while the POA bridge API returns both withdrawal records (order not guaranteed) — `findMatchingWithdrawal` in [6](#0-5)  returns the same first-matching record for both calls.
4. Both `index: 0` and `index: 1` promises resolve to the same `transfer_tx_hash`/status, even though they correspond to distinct on-chain withdrawals (A's 100 and B's 200), causing an integrator to mis-attribute settlement.

### Citations

**File:** packages/intents-sdk/src/shared-types.ts (L434-441)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}
```

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
