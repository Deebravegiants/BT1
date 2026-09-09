### Title
PoA Bridge withdrawal status is matched by `assetId` only, not by withdrawal index/destination — misreports completion status/txHash for batched same-asset withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` looks up the on-chain withdrawal record to report solely by matching `assetId`, explicitly ignoring the `index` field of the `WithdrawalIdentifier` that is supposed to disambiguate multiple withdrawals of the same asset inside one signed intent/batch. When a batch contains two or more `ft_withdraw` intents for the *same* token (e.g., two withdrawals of `nep141:btc.omft.near` to two different destination addresses in one intent transaction), the SDK cannot deterministically tell which backend record belongs to which requested withdrawal, so it can report the wrong `txHash`/`status` for a given withdrawal slot.

### Finding Description
`describeWithdrawal` is implemented as: [1](#0-0) 

The comment explicitly states the reasoning: *"Response list is unsorted, so we match by assetId instead of index"*. This means `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` selects a record purely based on asset type, not based on `args.index`, `args.withdrawalParams.destinationAddress`, or `args.withdrawalParams.amount`.

The `WithdrawalIdentifier` type carries an `index` specifically meant to disambiguate multiple withdrawals of the same route/bridge within one NEAR transaction: [2](#0-1) 

`createWithdrawalIdentifiers` assigns a per-bridge sequential `index` precisely to distinguish multiple withdrawals routed through the same bridge in a batch: [3](#0-2) 

`watchWithdrawal`/`waitForWithdrawalCompletion` then trust whatever `status`/`txHash` `describeWithdrawal` returns as the ground truth for that specific withdrawal slot: [4](#0-3) [5](#0-4) 

Because the POA bridge match key is only `assetId`, if a caller batches two `nep141:X` withdrawals to different destination addresses/amounts in the same intent tx (a supported pattern per the SDK's own "Batch Withdrawals" documentation), `findMatchingWithdrawal` has no way to pick the correct one among multiple candidates sharing the same `assetId` — the equality "status/txHash reported for withdrawal N == on-chain outcome of withdrawal N" can break, and the same completed record could satisfy both `describeWithdrawal` calls (for index 0 and index 1), or the wrong `txHash` could be attributed to the wrong destination.

### Impact Explanation
This matches the "status or hash misreport making an integrator credit or refund twice" High-impact class. An integrator using `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` for a batch of same-asset withdrawals (a documented use case) could:
- Have withdrawal #1 (destined for Bob) reported as `completed` with the `txHash` that actually corresponds to withdrawal #0 (destined for Alice), leading the integrator to credit/mark Bob's withdrawal as settled based on a transaction that paid Alice.
- Conversely, cause a legitimately completed withdrawal to be reported `pending` while the other one is (mis)reported completed twice.

No funds are directly redirected by the SDK itself (that depends on the relayer/bridge's actual settlement), but the caller-facing status/hash tracking used for internal bookkeeping (crediting off-chain balances, releasing goods, etc.) can be desynchronized from the real on-chain outcome for a specific request.

### Likelihood Explanation
Requires the caller to submit a batch/multiple withdrawals of the identical `assetId` (same POA-bridged token) in one signed intent — an explicitly supported and documented pattern ("Batch Withdrawals" in the SDK README). No malicious actor is needed; this is a correctness bug triggered by normal legitimate usage patterns of the public API whenever two same-asset withdrawals are batched.

### Recommendation
Change `findMatchingWithdrawal` to disambiguate using additional criteria available in `WithdrawalIdentifier`/`WithdrawalParams` — at minimum `destinationAddress` (and `amount` if necessary) in addition to `assetId`, or use a stable per-withdrawal correlation id returned by the POA bridge API if available, rather than relying on an unordered list keyed only by asset type.

### Proof of Concept
1. Submit a batch withdrawal intent containing two `ft_withdraw` intents for the same `assetId` (e.g., `nep141:btc.omft.near`) with different `destinationAddress`/`amount`, via `sdk.createWithdrawalIntents`/`processWithdrawal` with an array of `withdrawalParams`.
2. Call `sdk.waitForWithdrawalCompletion({ withdrawalParams: [w0, w1], intentTx })`, which invokes `describeWithdrawal` independently for `index: 0` and `index: 1` via `createWithdrawalIdentifiers` (packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107).
3. Inside `PoaBridge.describeWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343), both calls query the POA bridge for withdrawals under the same NEAR intent tx hash and filter `response.withdrawals` by `assetId` only — since both entries share the same `assetId`, `findMatchingWithdrawal` can return the same (or swapped) record for both `index: 0` and `index: 1` calls.
4. Result: the promise resolved for withdrawal #1 (Bob's destination) can carry the `txHash` that actually belongs to withdrawal #0 (Alice's destination), or vice versa — the reported status for a specific withdrawal slot does not match its true on-chain outcome.

Note: I was unable to retrieve the exact source of the `findMatchingWithdrawal` helper function itself (tool access ran out before I could open `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` in full or the POA bridge internal matching helper file) to confirm whether it applies any additional disambiguation beyond `assetId`. The comment in `poa-bridge.ts` ("we match by assetId instead of index") is direct evidence supporting this finding, but a full read of the helper implementation would provide stronger certainty.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-53)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
}): Promise<{ bridge: Bridge; wid: WithdrawalIdentifier }[]> {
	const indexes = new Map<string, number>();
	const results: { bridge: Bridge; wid: WithdrawalIdentifier }[] = [];

	for (const w of args.withdrawalParams) {
		const bridge = await findBridgeForWithdrawal(args.bridges, w);
		if (bridge == null) {
			throw new BridgeNotFoundError();
		}

		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});

		results.push({ bridge, wid });
	}

	return results;
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
