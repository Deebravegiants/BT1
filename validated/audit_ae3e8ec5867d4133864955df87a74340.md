### Title
Withdrawal status/hash misreport for same-token, multi-destination withdrawals in a single transaction - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain outcome of a specific withdrawal by matching entries returned from the POA bridge indexer using `findMatchingWithdrawal()`, which selects a match by `assetId` only, ignoring the withdrawal's `index`. When a single NEAR transaction contains multiple withdrawal intents of the *same* token (e.g., to two different destination addresses/amounts), every `WithdrawalIdentifier` for that tx/asset pair resolves to the *same* (first) matching record, so the status and `txHash` reported for one withdrawal can actually belong to a different withdrawal in the same batch.

### Finding Description
`createWithdrawalIdentifier()` assigns each withdrawal within a transaction an `index`, intended to disambiguate multiple withdrawals produced by the same `tx.hash`: [1](#0-0) 

However, `describeWithdrawal()` never uses `index` to select which withdrawal record from the API response corresponds to which intent — it only filters by `assetId`: [2](#0-1) [3](#0-2) 

The code comment explicitly acknowledges this: "multiple withdrawals of the same token in a single transaction are not supported." Because `Array.prototype.find` returns only the first array element matching the predicate, if the transaction contains two withdrawal intents for the same `assetId` (e.g. splitting a withdrawal to two different destination addresses within one NEAR tx), calling `describeWithdrawal` for withdrawal `index: 0` and `index: 1` both resolve to the **same** underlying API record (whichever POA returns first, order is unsorted per the code comment). This breaks the equality: *the status/txHash reported for a given withdrawal index equals the true on-chain outcome for that specific withdrawal*.

`watchWithdrawal()` in `withdrawal-watcher.ts` (used by the SDK's completion-waiting flow) consumes exactly this status to decide whether a withdrawal is "completed" and to report the destination `txHash` to the caller: [4](#0-3) 

An integrator that watches multiple withdrawal identifiers for the same batch tx (each expecting its own status/hash) can be told that withdrawal B "completed" with the hash that actually belongs to withdrawal A (or vice versa), while the real state of B is unknown/different.

### Impact Explanation
This matches the "status or hash misreport" category: an integrator relying on `describeWithdrawal`/`watchWithdrawal` per-withdrawal-index could credit/confirm a withdrawal as completed using a transaction hash that actually settled a *different* withdrawal, or mark a still-pending/failed withdrawal as completed. In batch-withdrawal flows (multiple `WithdrawalParams` of the same asset processed through `sdk.ts`'s array `estimateWithdrawalFee`/`createWithdrawalIntents` paths), this can cause a wrong completion/hash record to be associated with the wrong recipient/amount — leading to double-crediting or misattributed confirmation.

### Likelihood Explanation
Requires the caller to submit more than one withdrawal of the identical `assetId` within a single NEAR transaction via the POA bridge route — a legitimate SDK usage pattern (batch withdrawals), not an attacker-controlled exploit of another party's funds. No malicious actor is needed; the bug is deterministic given that specific-but-ordinary usage pattern, and the code's own comment confirms this is a known, currently-unhandled case.

### Recommendation
- Extend the POA bridge withdrawal-status API (or client-side matching) to disambiguate by more than `near_token_id`/assetId — e.g., match by `(near_token_id, address, amount)` tuple, or require the API to return withdrawals in submission order so `index` can be used positionally.
- Until API support exists, `describeWithdrawal` should detect the ambiguous case (more than one withdrawal in the response matches the same `assetId` for a given `tx.hash`) and either: sort matches deterministically by amount/order and select by `index`, or throw/return a distinguishable "ambiguous" status rather than silently returning a status that may belong to another withdrawal.
- Add tests covering same-asset multi-destination withdrawals within a single transaction to ensure each `WithdrawalIdentifier`'s reported status/txHash corresponds to the correct withdrawal.

### Proof of Concept
1. Build a withdrawal transaction containing two `ft_withdraw` intents for the same token (`nep141:btc.omft.near`) to two different destination addresses/amounts, submitted in one NEAR transaction `tx.hash = "H"`.
2. SDK creates two `WithdrawalIdentifier`s: `{ index: 0, tx: {hash: "H"}, withdrawalParams: paramsA }` and `{ index: 1, tx: {hash: "H"}, withdrawalParams: paramsB }` via `createWithdrawalIdentifier` (`poa-bridge.ts:295-311`).
3. POA bridge indexer returns two `withdrawals` entries for `tx.hash = "H"`, both with `near_token_id = "btc.omft.near"` (one for A, one for B), in indeterminate order (per code comment at `poa-bridge.ts:412-416`).
4. Calling `describeWithdrawal({index:0, ...})` and `describeWithdrawal({index:1, ...})` both invoke `findMatchingWithdrawal(response.withdrawals, "nep141:btc.omft.near")`, which returns `withdrawals.find(...)` — the **same first-matching element** — for both calls (`poa-bridge.ts:319-322`, `418-427`).
5. Both `WithdrawalIdentifier`s report the identical `status`/`txHash`, even though they represent two distinct withdrawals with potentially different destinations/amounts/outcomes — an integrator polling via `watchWithdrawal` (`withdrawal-watcher.ts:32-53`) for each index will incorrectly treat withdrawal B as completed using A's hash (or vice versa).

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-53)
```typescript
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
