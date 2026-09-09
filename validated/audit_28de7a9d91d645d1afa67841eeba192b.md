### Title
POA Bridge withdrawal status/hash misreported when batching multiple withdrawals of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`findMatchingWithdrawal` in the POA bridge status lookup matches a withdrawal record solely by `assetId` (`nep141:${w.data.near_token_id}`), ignoring the withdrawal's `index`, `destinationAddress`, and `amount`. When a caller batches multiple withdrawals of the same token (a supported SDK feature) in one NEAR transaction to different destination addresses, `describeWithdrawal()`/`waitForWithdrawalCompletion()` can report the destination chain tx hash of one withdrawal as the status for a different withdrawal index, breaking the equality between "the withdrawal being queried" and "the withdrawal whose outcome is returned."

### Finding Description
The `PoaBridge.describeWithdrawal` implementation retrieves the list of withdrawals for a NEAR transaction and picks the entry matching only by asset id:
<cite repo="Alyssadaypin/sdk-monorepo--004" path="packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts" start="313\" end="343" /> [1](#0-0) 

The comment explicitly documents the limitation: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." The same pattern (and same documented limitation) exists independently in the internal-utils package used by other consumers: [2](#0-1) 

The SDK explicitly supports batching multiple withdrawals in a single call (`sdk.signAndSendWithdrawalIntent`, `sdk.waitForWithdrawalCompletion`, `sdk.createWithdrawalCompletionPromises`), and `createWithdrawalIdentifier` assigns each withdrawal an `index` within the batch: [3](#0-2) 

However, when the destination chain (POA bridge) status API returns multiple withdrawal records for the same NEAR tx (e.g., two withdrawals of `nep141:usdc.token.near` to two different destination addresses), `findMatchingWithdrawal` returns the **first** matching record regardless of which index/destination the caller is actually asking about. Both `describeWithdrawal` calls (for index 0 and index 1) would therefore resolve to the same withdrawal record, i.e., the same destination-chain `transfer_tx_hash`, even though the two withdrawals target different addresses.

### Impact Explanation
This breaks the equality "status/hash reported for withdrawal at index N == on-chain outcome of the withdrawal actually initiated at index N (to destinationAddress N)." A consumer that trusts `describeWithdrawal`/`waitForWithdrawalCompletion` output per index/withdrawal to confirm completion (e.g., to release custody, mark an order fulfilled, or reconcile ledgers) could:
- Report withdrawal #2 (to address B) as "completed" using the tx hash that actually corresponds to withdrawal #1 (to address A), i.e., a wrong-destination status misreport that could cause double crediting or incorrect reconciliation by an integrator.
- Conversely, a genuinely completed withdrawal could remain unmatched/misattributed if ordering differs from expectations.

This matches the "status or hash misreport making an integrator credit or refund twice" category. The severity is bounded by the fact that: (1) the SDK does not itself release additional funds based on this value — it only surfaces a hash/status to the caller; (2) exploitation requires the caller to batch multiple withdrawals of the identical token in one transaction, a legitimate and explicitly supported usage pattern, not an attacker-injected value. The bug is a data-integrity/matching defect rather than an authorization bypass; the maintainers already documented it as a known limitation.

### Likelihood Explanation
Likelihood is moderate: it requires no malicious input — it is triggered by ordinary use of the documented "batch withdrawals" feature when two or more withdrawals of the same asset are included in a single NEAR transaction. Given multi-token batch withdrawals are a first-class supported use case, and same-token batching is not defensively blocked anywhere in `sdk.ts` or `poa-bridge.ts`, this is realistically reachable by any SDK consumer, without any privileged access.

### Recommendation
Extend `findMatchingWithdrawal` (in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate among multiple same-asset withdrawals — e.g., match on `assetId` **and** `destinationAddress` (and `amount` where available), or track per-record consumption so the same withdrawal record cannot satisfy two different requested indices, and add an explicit check/error when multiple unresolved candidates remain instead of silently returning the first match.

### Proof of Concept
1. Call `sdk.signAndSendWithdrawalIntent` with a batch of two withdrawals of the same asset `nep141:usdc.token.near`: one to `destinationAddress: "0xAAA..."` and one to `destinationAddress: "0xBBB..."`.
2. The resulting NEAR transaction produces two POA-bridge withdrawal records with the same `near_token_id` but different destination addresses/amounts, e.g.:
   ```json
   { "status": "COMPLETED", "data": { "near_token_id": "usdc.token.near", "address": "0xAAA...", "transfer_tx_hash": "0xhashA" } },
   { "status": "COMPLETED", "data": { "near_token_id": "usdc.token.near", "address": "0xBBB...", "transfer_tx_hash": "0xhashB" } }
   ```
3. Call `bridge.describeWithdrawal` for index 0 (destination `0xAAA...`) and index 1 (destination `0xBBB...`).
4. Because `findMatchingWithdrawal` only checks `nep141:${near_token_id} === assetId`, both calls resolve to the **same** first-matching record (`0xhashA`), so the withdrawal actually destined for `0xBBB...` is reported completed with `0xhashA` — a tx hash belonging to a different destination address.

Note: I could not fully verify how far-downstream integrators (outside the scanned scope) act on this reported `txHash`/status, since that logic lives outside `packages/intents-sdk`, `packages/internal-utils`, and `packages/crosschain-assetid`; the concrete "double credit" impact depends on that external consumption, which is acknowledged as an assumption above.

### Citations

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

**File:** packages/intents-sdk/src/sdk.ts (L481-521)
```typescript
	public waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams;
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<TxInfo | TxNoInfo>;

	public waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams[];
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<Array<TxInfo | TxNoInfo>>;

	public async waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams | WithdrawalParams[];
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<(TxInfo | TxNoInfo) | Array<TxInfo | TxNoInfo>> {
		const withdrawalParamsArray = Array.isArray(args.withdrawalParams)
			? args.withdrawalParams
			: [args.withdrawalParams];

		const promises = this.createWithdrawalCompletionPromises({
			withdrawalParams: withdrawalParamsArray,
			intentTx: args.intentTx,
			signal: args.signal,
			logger: args.logger,
		});

		const result = await Promise.all(promises);

		if (Array.isArray(args.withdrawalParams)) {
			return result;
		}

		assert(result.length === 1, "Unexpected result length");
		// biome-ignore lint/style/noNonNullAssertion: length asserted above
		return result[0]!;
	}
```
