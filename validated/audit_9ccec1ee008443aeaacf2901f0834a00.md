### Title
Batch withdrawals of the same token report the wrong destination tx hash/status via the POA bridge - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`IntentsSDK.processWithdrawal`/`waitForWithdrawalCompletion` support batching multiple `WithdrawalParams` in a single signed intent transaction [1](#0-0) , each tracked by index via `createWithdrawalIdentifiers`/`createWithdrawalCompletionPromises` [2](#0-1) . For the POA bridge, `describeWithdrawal` resolves the on-chain status for a given withdrawal by calling `findMatchingWithdrawal`, which selects the withdrawal record purely by `assetId`, ignoring the `index`/amount/destination that uniquely identifies which of the several same-token withdrawals in the batch it should report on: [3](#0-2) [4](#0-3) .

### Finding Description
`WithdrawalIdentifier` includes an `index` field specifically because "Response list is unsorted, so we match by assetId instead of index" — but that comment (line 318) is itself the bug: `findMatchingWithdrawal` only matches on `nep141:${w.data.near_token_id} === assetId`, with no disambiguation by amount, destination address, or position [5](#0-4) . `Array.prototype.find` always returns the **first** array element that matches the assetId, regardless of which `index` (0, 1, 2, …) the caller queried for.

If a single intent transaction contains two or more `ft_withdraw` intents for the same POA token (e.g., two BTC withdrawals to different destination addresses, submitted via the documented batch API `signAndSendWithdrawalIntent`/`processWithdrawal` with a `WithdrawalParams[]`), then every `describeWithdrawal` call for that assetId — irrespective of the requested `index` — returns the *same* withdrawal record from the POA API response. This breaks the equality that must hold: "the status/txHash reported for withdrawal `index` must correspond to the on-chain outcome of withdrawal `index`."

Concretely:
- Withdrawal #0 → destination A, amount X — actually completes with `transfer_tx_hash = H0`.
- Withdrawal #1 → destination B, amount Y — actually completes (or is still pending/failed) with a different `transfer_tx_hash = H1`.
- Both `describeWithdrawal({index:0, ...})` and `describeWithdrawal({index:1, ...})` call `findMatchingWithdrawal(withdrawals, "nep141:...")`, which returns the same single matched entry (e.g., the one containing H0) for both queries.

The caller (`watchWithdrawal` in `core/withdrawal-watcher.ts`, invoked by `createWithdrawalCompletionPromises`) then resolves withdrawal #1's `TxInfo` with `H0` — the transaction hash of a completely different transfer — and reports `status: "completed"` for withdrawal #1 even though its actual destination transfer may still be pending, failed, or landed with a different hash [6](#0-5) .

### Impact Explanation
This is a status/hash misreport, not a data-integrity issue confined to the caller's own funds:
- An integrator using `sdk.processWithdrawal`/`waitForWithdrawalCompletion` with batched same-token withdrawals will receive an incorrect `txHash` for at least one of the withdrawals in the batch, wrongly attributing another withdrawal's transaction hash to it.
- This can cause the integrator to mark a withdrawal "completed" for the wrong on-chain transaction — e.g., recording the wrong destination transfer, mismatching reconciliation records, or (depending on integrator logic) crediting/closing out a withdrawal request based on a transaction that doesn't correspond to it. If the mis-attributed withdrawal is actually still pending/failed, the integrator’s bookkeeping is now permanently wrong for that batch entry with no automated way to detect or recover, since the SDK reports "completed" unconditionally.
- This matches the "High" impact bucket for this scan: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Batching multiple withdrawals in one intent transaction is an explicit, documented, first-class SDK feature (`WithdrawalParams[]`, `signAndSendWithdrawalIntent`, `processWithdrawal`, `createWithdrawalCompletionPromises`). Any integrator batching two withdrawals of the *same* POA-bridged asset (e.g., two BTC withdrawals in one call) — a very plausible usage pattern for efficiency — will trigger this. The code's own comment acknowledges the limitation but the fallback behavior silently mis-reports rather than throwing/erroring, so the bug is not opt-in-safe; it will be hit under normal batch usage without any error signal.

### Recommendation
`findMatchingWithdrawal` should disambiguate between multiple same-asset withdrawals in a batch rather than always returning the first match. At minimum:
- Track which withdrawal records have already been consumed/matched (e.g., maintain a per-transaction-hash "claimed" set) so subsequent `describeWithdrawal` calls for the same assetId don't return an already-assigned record.
- Prefer matching by amount as well as assetId when multiple candidates exist (the code comment already proposes sorting both sides by amount since fees are equal for the same token) — implement that ordering-based disambiguation instead of leaving it as a known limitation.
- If disambiguation isn't possible (e.g., duplicate amount + same asset), throw/return `pending` rather than confidently reporting `completed` with a possibly-wrong tx hash, to avoid silent misattribution.

### Proof of Concept
1. Call `sdk.processWithdrawal` (or `signAndSendWithdrawalIntent` + `waitForWithdrawalCompletion`) with `withdrawalParams: [wp0, wp1]` where both `wp0.assetId` and `wp1.assetId` equal the same POA-bridged token (e.g., `nep141:btc.omft.near`), with different `destinationAddress`.
2. This produces one NEAR intent transaction containing two `ft_withdraw` intents for the same token.
3. On the POA bridge indexer side, both withdrawals eventually appear in the `withdrawals` array returned by `getWithdrawalStatus({ withdrawal_hash: tx.hash })`, each carrying its own `transfer_tx_hash`.
4. `createWithdrawalCompletionPromises` calls `describeWithdrawal` once for `index: 0` and once for `index: 1`. Both calls invoke `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns `withdrawals[0]` (the first element satisfying the predicate) in both cases [3](#0-2) .
5. Result: the promise for withdrawal index 1 resolves with `{ hash: withdrawals[0].data.transfer_tx_hash }` — i.e., the destination chain tx hash that actually belongs to withdrawal index 0 — while the true transfer for withdrawal index 1 may be at a different hash or still pending.

### Citations

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

**File:** packages/intents-sdk/src/sdk.ts (L557-609)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
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
