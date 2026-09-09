### Title
POA Bridge withdrawal status matched only by `assetId`, causing wrong-withdrawal status/hash to be reported for batched same-token withdrawals - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal()` and `waitForWithdrawalCompletion()` resolve which withdrawal status/tx-hash to report for a given `WithdrawalIdentifier` by scanning the POA bridge's unsorted `withdrawals` array and returning the **first** entry whose `near_token_id` matches the requested `assetId` — it never checks `amount`, `destinationAddress`, or the `index` of the withdrawal actually being tracked.

### Finding Description
`findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (lines 409-427) is documented as intentionally matching only by `assetId`:

```
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```
This is consumed by `describeWithdrawal` (lines 313-343), which returns `{ status: "completed", txHash: withdrawal.data.transfer_tx_hash }` for whichever entry matches first. The exact same pattern is duplicated in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (`findMatchingWithdrawal`, lines 144-153), which is used to resolve `destinationTxHash` for a caller waiting on a specific withdrawal.

When a single NEAR transaction produces **multiple withdrawals of the same token** (e.g., a batch withdrawal to two different destination addresses, or two withdrawals with different amounts, both indexed 0 and 1 in `withdrawalParams`), both `WithdrawalIdentifier`s share the same `assetId`. Because matching ignores `destinationAddress`, `amount`, and the withdrawal's position, `describeWithdrawal({ index: 1, ... })` can return the status and `txHash` that actually belongs to the withdrawal at `index: 0` (or vice versa), since the POA API list is explicitly documented as "unsorted."

This breaks the equality that the "status reported" must equal the actual on-chain outcome for *that specific* withdrawal identifier: the caller polling for withdrawal B's completion can be told "completed, txHash=X" where X is the destination transaction of withdrawal A, while B's real transfer may still be pending, may go to a different address, or may fail.

### Impact Explanation
This is a status/hash misreport as described in the rules ("a status or hash misreport making an integrator credit or refund twice"). Any integrator (e.g., `withdrawal-watcher.ts`'s `watchWithdrawal`, or `waitForWithdrawalCompletion`) that uses the returned `status`/`txHash` to decide when to release funds, mark an off-chain ledger entry as settled, or refund a user could:
- Prematurely mark withdrawal B as completed using A's txHash, potentially crediting/settling B while its actual on-chain transfer hasn't happened (or went to a different recipient), leading to double-credit or incorrect settlement records tied to the wrong destination transaction.
- Never move on for A even though A completed if A's entry is returned repeatedly for both indices.

The bug is explicitly acknowledged in code comments as a known limitation ("multiple withdrawals of the same token in a single transaction are not supported"), which supports that this is a real, currently-reachable gap rather than a hypothetical.

### Likelihood Explanation
Likelihood depends on how commonly multi-withdrawal-same-token-in-one-tx flows are used through the SDK; the codebase's `createWithdrawalIntents` and batching support in `sdk.ts` do allow multiple withdrawal params to be included in one call/transaction. Because POA is a real, reachable route (`RouteEnum.PoaBridge`) and the mis-match requires no malicious actor — just two legitimate same-asset withdrawals in one NEAR tx — this is a plausible, low-effort-to-trigger scenario for normal usage, not requiring an adversarial input.

### Recommendation
Extend `findMatchingWithdrawal` (in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate matches using additional fields available on the withdrawal data (e.g., `amount`, `address`/destination, and matching order/index against the caller's ordered list of same-asset withdrawal params) rather than relying solely on `assetId`. At minimum, when more than one candidate withdrawal matches the same `assetId`, correlate by `amount` and `destinationAddress` before falling back to positional matching, and treat an ambiguous match as `pending`/`unknown` rather than confidently reporting `completed` with a potentially wrong `txHash`.

### Proof of Concept
1. Submit one NEAR transaction containing two POA withdrawal intents for the same `assetId` (e.g. `nep141:btc.omft.near`): index 0 → destination A, amount 100000; index 1 → destination B, amount 50000.
2. POA bridge processes withdrawal for destination A first and reports it as `COMPLETED` with `transfer_tx_hash: "tx-A"`; withdrawal to B is still `PENDING`.
3. Call `bridge.describeWithdrawal({ landingChain, index: 1, withdrawalParams: { assetId, amount: 50000n, destinationAddress: B, feeInclusive:false }, tx })`.
4. `findMatchingWithdrawal` returns the first entry with matching `near_token_id` (A's completed entry), so `describeWithdrawal` returns `{ status: "completed", txHash: "tx-A" }` for the withdrawal actually destined to B — even though B's funds have not moved. [1](#0-0) [2](#0-1) [3](#0-2)

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
