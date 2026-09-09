Confirmed: this repo explicitly supports batch withdrawals of multiple assets in a single intent/transaction (`sdk.processWithdrawal`, `sdk.signAndSendWithdrawalIntent` with `WithdrawalParams[]`), and `PoaBridge.describeWithdrawal` resolves each withdrawal's destination status by matching **only on `assetId`**, not on amount, destination address, or index.

### Title
POA bridge withdrawal status/txHash misreport when a batch contains multiple withdrawals of the same token - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`findMatchingWithdrawal` in `poa-bridge.ts` selects a withdrawal record from the POA relayer's response purely by matching `nep141:${near_token_id}` to `withdrawalParams.assetId`, ignoring `index`, `amount`, and `destinationAddress`. When a batch withdrawal (explicitly supported via `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` with `WithdrawalParams[]`) contains two or more entries with the same `assetId` but different destination addresses/amounts, `Array.find` always returns the **first** matching entry in the relayer's response for every query, regardless of which of the identical-asset withdrawals is actually being queried. [1](#0-0) 

### Finding Description
`describeWithdrawal` is called once per `WithdrawalIdentifier` (one per batch item, keyed by `index`) via `watchWithdrawal`/`waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`. For POA-bridge assets it delegates matching entirely to `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`: [2](#0-1) 

The code comment even acknowledges: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." If a caller submits a batch such as `[{assetId: TOKEN, amount: 100, dest: A}, {assetId: TOKEN, amount: 200, dest: B}]` via `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` (both explicitly support `WithdrawalParams[]`), both `WithdrawalIdentifier`s share the same `assetId`, so both queries for `describeWithdrawal` will resolve to the same relayer record (the first one that matches by asset), reporting the same `status`/`txHash` for two distinct withdrawals to different addresses/amounts.

This breaks the equality "status/txHash reported == on-chain outcome for that specific withdrawal": the caller integrating this SDK (e.g. `promises[0]`/`promises[1]` from `createWithdrawalCompletionPromises`, or `destinationTx[]` from `waitForWithdrawalCompletion`) would receive the identical destination tx hash for both withdrawal legs, even though only one of them actually completed on-chain, or the wrong one is reported as completed for a given index/destination.

### Impact Explanation
This is a status/hash misreport for a bridge-mediated batch withdrawal — an integrator relying on `destinationTx[i]`/`promises[i]` to confirm and credit/release funds per-leg (e.g., mark both a USDC withdrawal to address A and a USDC refund to address B as "completed" using the same txHash) could credit or consider a withdrawal completed when it has not actually landed, or duplicate a completion confirmation across two distinct withdrawals. This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
Likelihood is Medium: it requires the integrator to build a batch withdrawal (an explicitly documented and supported feature) with two or more entries sharing the same `assetId` for a POA-bridge-routed token — a realistic pattern (e.g., splitting one token withdrawal to two destinations, or an amount + refund of the same token). No malicious actor is needed; a normal batch usage pattern triggers it.

### Recommendation
Extend `findMatchingWithdrawal` (and its counterpart in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate withdrawals sharing the same `assetId` by additional criteria (e.g., `amount` and `destinationAddress`, or by tracking already-consumed relayer records so each is matched at most once per batch), rather than returning the first `assetId` match unconditionally. At minimum, throw/guard when multiple relayer entries match the same `assetId` within a single batch instead of silently returning the first.

### Proof of Concept
1. Call `sdk.processWithdrawal` (or `signAndSendWithdrawalIntent`) with `withdrawalParams = [{assetId: "nep141:usdt.tether-token.near", amount: 100n, destinationAddress: "0xA...", feeInclusive:false}, {assetId: "nep141:usdt.tether-token.near", amount: 200n, destinationAddress: "0xB...", feeInclusive:false}]`.
2. Both legs settle on NEAR in one intent/tx and the POA relayer eventually returns two entries in `getWithdrawalStatus` for `near_token_id: "usdt.tether-token.near"` — one COMPLETED with `transfer_tx_hash: "tx-A"`, another still PENDING.
3. `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` calls `describeWithdrawal` independently for `index: 0` and `index: 1`; both invoke `findMatchingWithdrawal(response.withdrawals, "nep141:usdt.tether-token.near")`, which returns the same first entry (`tx-A`, COMPLETED) for both indices.
4. The integrator observes `destinationTx[0]` and `destinationTx[1]` both reporting `status: "completed", txHash: "tx-A"`, incorrectly signaling that the withdrawal to `0xB` also completed with that hash, even though it is still pending or landed with a different hash. [3](#0-2)

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
