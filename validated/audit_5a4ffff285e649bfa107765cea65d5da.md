### Title
Status/txHash misreport for batched same-asset PoA withdrawals due to assetId-only matching in `findMatchingWithdrawal` - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain outcome of a `WithdrawalIdentifier` using `findMatchingWithdrawal`, which ignores `WithdrawalIdentifier.index` and matches purely by `assetId`. When a single NEAR transaction contains two or more PoA withdrawals of the same `assetId` to different `destinationAddress`/`amount` pairs, `Array.prototype.find` always returns the first indexer entry for that asset, so every `wid` sharing that `assetId` reports the same `status`/`txHash` regardless of which withdrawal it actually represents.

### Finding Description
The broken equality is: `describeWithdrawal({index: i, withdrawalParams: P_i}).txHash` should equal the on-chain outcome of the specific withdrawal created for `withdrawalParams[i]`, but it instead equals the outcome of whichever entry `findMatchingWithdrawal` happens to return first for that `assetId`.

Code path:
- `createWithdrawalIdentifiers` in [1](#0-0)  assigns a per-route `index` (0, 1, ...) to each `WithdrawalParams` entry in the array the caller supplies, with no requirement that same-`assetId` withdrawals be disallowed.
- `PoaBridge.describeWithdrawal` in [2](#0-1)  explicitly comments "Response list is unsorted, so we match by assetId instead of index" and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`.
- `findMatchingWithdrawal` in [3](#0-2)  does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)`, which returns the **first** array element matching the asset, independent of `index`, `amount`, or `destinationAddress`. The function's own doc-comment self-acknowledges: "multiple withdrawals of the same token in a single transaction are not supported."
- The identical logic and doc-comment exist in the sibling utility in [4](#0-3) , used by `waitForWithdrawalCompletion`.
- `watchWithdrawal` in [5](#0-4)  polls `bridge.describeWithdrawal({...args.wid, ...})` per `wid` and surfaces whatever `txHash`/status is returned as ground truth for that specific `wid`.

Attacker/user input: a `withdrawalParams` array with two PoA entries sharing `assetId = "nep141:usdt.omft.near"`, `amount = 100` to `destinationAddress = A`, and `amount = 500` to `destinationAddress = B`, submitted in one NEAR transaction. No validation anywhere in `PoaBridge` (`supports`, `validateWithdrawal`, `createWithdrawalIdentifier`) rejects or disambiguates this case — none of these check for duplicate `assetId` within a batch.

Exploit flow: the caller (or integrator on behalf of two different end users) invokes `watchWithdrawal` twice, once for `wid.index = 0` (amount 100 → A) and once for `wid.index = 1` (amount 500 → B). Both calls end up calling `describeWithdrawal` with the same `assetId`; `findMatchingWithdrawal` returns the same first-found indexer record for both calls, so both `wid`s converge on the same `status`/`txHash`, even though they represent distinct on-chain transfers to different destinations and amounts.

Existing guards don't prevent this: `validateAddress`/`compareAddresses` check destination validity per-withdrawal but don't cross-check for assetId collisions across the batch; `supports()` and `createWithdrawalIdentifier` operate per-withdrawal, not on the whole batch; there is no `assert` anywhere disallowing duplicate `assetId`s in one call.

### Impact Explanation
An integrator that batches multiple same-token PoA withdrawals to different recipients in a single NEAR transaction and relies on `watchWithdrawal`/`waitForWithdrawalCompletion` per `WithdrawalIdentifier.index` to decide when/whom to credit will misreport the destination transaction hash for at least one of the withdrawals — attributing recipient B's on-chain transfer outcome to recipient A's withdrawal record (or vice versa). This is a status/txHash misreport that can cause an integrator to credit/confirm the wrong recipient or double-credit based on the same underlying txHash for two different withdrawals. This matches the High-severity category "a status or hash misreport making an integrator credit or refund twice." It is repeatable on every batch containing duplicate `assetId`s and requires no special privilege — any ordinary user or integrator constructing a normal batched withdrawal triggers it.

### Likelihood Explanation
Preconditions: use of the PoA bridge route, two or more withdrawals of the identical `assetId` batched into one NEAR transaction with differing destination/amount, and an integrator that tracks completion per `WithdrawalIdentifier`. This is a plausible, unprivileged, ordinary usage pattern (e.g., batching withdrawals for two different customers of the same token to save gas) with no cost or special condition attacker needs to satisfy beyond calling the public SDK with such a batch. The bug is self-acknowledged as an unhandled case in code comments in both call sites, confirming it is not merely theoretical but a known-unaddressed gap in matching logic.

### Recommendation
Disambiguate same-`assetId` withdrawals within a batch, e.g., by refusing to create multiple withdrawal identifiers for the same `assetId` in a single call, or by matching indexer entries positionally after canonically sorting both the API results and `withdrawalParams` by `amount` (as suggested in the code's own comment), or by requesting/using an indexer field (e.g., a sub-index or destination address) that disambiguates multiple same-token withdrawals within one NEAR tx, and asserting `withdrawals.length === expectedCountForAsset` before matching.

### Proof of Concept
Vitest test (mocking only the POA HTTP client `getWithdrawalStatus`):
1. Mock `poaBridge.httpClient.getWithdrawalStatus` to return two `COMPLETED` entries with `near_token_id: "usdt.omft.near"`, one with `transfer_tx_hash: "hashA"` (logically corresponding to amount 500/destination B) and one with `transfer_tx_hash: "hashB"` (logically corresponding to amount 100/destination A), in reversed order relative to creation.
2. Construct `withdrawalParams = [{assetId: "nep141:usdt.omft.near", amount: 100n, destinationAddress: "A", ...}, {assetId: "nep141:usdt.omft.near", amount: 500n, destinationAddress: "B", ...}]`.
3. Call `bridge.createWithdrawalIdentifier` for index 0 and index 1 respectively, then call `bridge.describeWithdrawal` for each `wid`.
4. Assert the equality that should hold but doesn't: `describeWithdrawal(wid_index0).txHash !== describeWithdrawal(wid_index1).txHash` yet the test shows they are equal (both resolve to the same first-found entry), demonstrating the txHash reported for index 0 is not necessarily the outcome of the withdrawal signed at index 0.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-78)
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
				} catch (err: unknown) {
					if (err instanceof WithdrawalFailedError) {
						throw err;
					}

					consecutiveErrors++;
					if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
						throw new WithdrawalWatchError(err);
					}

					args.logger?.warn(
						`Transient error (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}): ${err}`,
					);
					return POLL_PENDING;
				}
			},
			{ stats, signal: args.signal },
		);
	} catch (err: unknown) {
		if (err instanceof PollTimeoutError) {
			throw new WithdrawalWatchError(err);
		}
		throw err;
	}
}
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
