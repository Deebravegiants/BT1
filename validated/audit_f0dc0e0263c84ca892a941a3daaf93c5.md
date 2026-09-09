## Title
POA bridge `findMatchingWithdrawal` ignores withdrawal index, causing duplicate `completed` status/txHash reports for batched same-`assetId` withdrawals - (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

## Summary
`PoaBridge.describeWithdrawal` matches a NEAR-tx's withdrawal records purely by `assetId` (`nep141:${near_token_id}`), with no use of `index` or amount. When a batched intent contains two withdrawals of the same `assetId`, both `index:0` and `index:1` calls query the same `getWithdrawalStatus` response and resolve to the **same** first-matching record, so once one of the two withdrawals is genuinely `COMPLETED`, both indices report `completed` with the identical `transfer_tx_hash`, even though only one payout actually happened on-chain.

## Finding Description
The broken equality is: `(status, txHash)` reported for withdrawal index *i* == the real on-chain outcome of withdrawal index *i*.

The relevant code: [1](#0-0) [2](#0-1) 

`describeWithdrawal` fetches `withdrawals` for the shared NEAR `tx.hash` and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which is a bare `.find()` on `assetId` equality — it never looks at `args.index`. The comment at lines 409-416 explicitly acknowledges: *"multiple withdrawals of the same token in a single transaction are not supported"*.

Both `index:0` and `index:1` `WithdrawalIdentifier`s share the same `tx.hash` (the settlement tx) and the same `assetId` when a caller submits two same-asset withdrawals in one batch (an ordinary, unrestricted usage pattern — nothing in `createWithdrawalIdentifiers` [3](#0-2)  or `Bridge.supports`/`validateWithdrawal` rejects duplicate `assetId`s in a batch). Consequently both `describeWithdrawal` calls hit the identical `getWithdrawalStatus` response and the identical `.find()` result, so `watchWithdrawal` [4](#0-3)  resolves both promises to `{status:'completed', txHash: transfer_tx_hash}` as soon as either underlying withdrawal is completed — regardless of the true status of the other index.

None of `validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()` ordering, or the intents contract's signature/nonce checks address this, because the defect is purely in the SDK's post-settlement status-matching logic, not in intent construction or signing.

## Impact Explanation
An integrator that keys custody release/crediting on withdrawal index (a supported, documented pattern per `createWithdrawalCompletionPromises` / `sdk.createWithdrawalCompletionPromises`) [5](#0-4)  will observe **both** indices report the same completed `txHash`, causing it to credit/release funds twice for a single real destination-chain payout — this matches the rules' own "High" category: *"a status or hash misreport making an integrator credit or refund twice."* This is repeatable for every batch containing duplicate `assetId` withdrawals, for as long as one of the pair remains genuinely pending or fails while the other completes.

## Likelihood Explanation
Preconditions: a caller (unprivileged, using their own funds/keys) submits a batch withdrawal containing two POA-bridge withdrawals of the same `assetId` — no privilege or contract-admin/relayer/RPC compromise required, and the SDK does not reject or dedupe this input. The attacker's cost is a single ordinary batched withdrawal transaction; the divergence appears automatically whenever the bridge completes one of the two same-asset withdrawals before (or instead of) the other.

## Recommendation
In `findMatchingWithdrawal`, disambiguate withdrawals sharing the same `assetId` by additional criteria (e.g., amount matched to `args.withdrawalParams.amount`, or destination address), or track/consume matched records so each is attributed to at most one index, as hinted in the existing code comment's proposed remediation (sort both sides by amount and pair positionally).

## Proof of Concept
Vitest test (mocking only `poaBridge.httpClient.getWithdrawalStatus`):
1. Mock `getWithdrawalStatus` to return a single `withdrawals` array with one `COMPLETED` record for `near_token_id` = `X`, `transfer_tx_hash` = `"0xreal"`.
2. Build two `WithdrawalIdentifier`s: `index:0` and `index:1`, both with `withdrawalParams.assetId = "nep141:X"` and the same `tx.hash`.
3. Call `poaBridge.describeWithdrawal(wid0)` and `poaBridge.describeWithdrawal(wid1)`.
4. Assert both resolve to `{status:'completed', txHash:'0xreal'}` — i.e. `result0.txHash === result1.txHash === "0xreal"` — demonstrating index 1 is falsely reported completed with index 0's real payout hash (equality `status(index1) == on-chain outcome(index1)` is broken).

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-47)
```typescript
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
