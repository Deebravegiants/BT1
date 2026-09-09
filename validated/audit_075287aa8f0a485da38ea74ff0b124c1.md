This confirms a concrete, code-documented equality-collapse bug in `PoaBridge.describeWithdrawal`: when a batch withdrawal contains two withdrawals of the same PoA token (e.g., two `nep141:btc.omft.near` withdrawals to different destinations/amounts in one `processWithdrawal` batch), `findMatchingWithdrawal` uses `Array.find` matching only on `assetId`, ignoring `index`, so withdrawal index 1 will be reported with the status/txHash belonging to withdrawal index 0 (or vice versa) — the exact "status reported that is not the on-chain outcome" bug class from the prompt.

### Title
Same-Asset Batch Withdrawals Misreport Wrong Destination Status/TxHash in PoA Bridge - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain outcome of a specific withdrawal (identified by `index`) using `findMatchingWithdrawal`, which matches purely by `assetId` and ignores the caller-supplied `index`/`WithdrawalIdentifier`. When a batch of withdrawals contains more than one withdrawal of the same PoA-bridged token, `Array.find` always returns the first matching entry from the (unsorted) API response, so callers polling for withdrawal index 1's status can receive index 0's status/tx hash instead.

### Finding Description
`describeWithdrawal` is called per-index by `watchWithdrawal`/`createWithdrawalCompletionPromises` with a `WithdrawalIdentifier` that carries `index` <cite repo="Alyssadaypin/sdk-monorepo--016" path="packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts" start="295="311" end="311" />. Inside `describeWithdrawal`, however, the actual withdrawal record is selected only by `assetId`: [1](#0-0) 

The matching helper is explicit about this limitation in its own docstring: [2](#0-1) 

The identical limitation is duplicated in `@defuse-protocol/internal-utils`'s legacy `waitForWithdrawalCompletion` path: [3](#0-2) .

The SDK explicitly supports batch withdrawals containing multiple entries, and each withdrawal is tracked/polled independently by index, e.g. `createWithdrawalIdentifiers` assigns a separate incrementing `index` per bridge route [4](#0-3) , and `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` poll `describeWithdrawal` per withdrawal, keyed by `index`, expecting the status/txHash returned to correspond to that specific withdrawal (`amount`, `destinationAddress`) [5](#0-4) . Because `findMatchingWithdrawal` ignores both `index` and `destinationAddress`/`amount`, this equality (status/txHash reported == on-chain outcome of *this* withdrawal) breaks whenever two same-asset PoA withdrawals are batched together — a scenario the SDK's own public API and README explicitly enable ("Process multiple withdrawals in a single intent").

### Impact Explanation
If a batch contains two withdrawals of the same `.omft.near` token to different destination addresses/amounts (e.g., refunding the same asset to two different users, or a withdraw+refund of the same token in one intent), the second withdrawal's poller will be handed the first withdrawal's `status`/`transfer_tx_hash` as soon as the first entry appears "COMPLETED" in the unsorted API response. An integrator relying on `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` to know when funds landed at a given destination could:
- Mark/credit the second withdrawal as completed using the first withdrawal's destination tx hash (wrong txHash reported for a real transfer that actually went to a different address/amount), or
- Report "completed" for a withdrawal that has not actually happened on-chain while the true withdrawal is still pending or failed.

This matches the "High" bucket: a status/hash misreport that can cause an integrator to credit/refund based on the wrong transaction.

### Likelihood Explanation
This requires no malicious relayer, bridge operator, or adversarial input — it triggers under the SDK's own documented and supported "Batch Withdrawals" feature whenever an unprivileged caller includes two withdrawals of the same PoA-bridged asset in one `processWithdrawal`/`signAndSendWithdrawalIntent` call, which is an entirely normal usage pattern (e.g., two payouts in the same token to two different users). No special permissions or code changes on the attacker/integrator's part are needed to hit this collapse; it's inherent to the SDK's matching logic.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId` — incorporate `amount` and/or `destinationAddress` (and ideally a stable ordering/sorting strategy as already suggested in the code's own comment) so that each `index` maps deterministically to the withdrawal record that corresponds to it. At minimum, detect the case of multiple same-asset withdrawals in a batch and throw/require additional disambiguating data rather than silently returning a possibly-wrong record.

### Proof of Concept
1. Call `sdk.processWithdrawal` with `withdrawalParams = [ {assetId:"nep141:btc.omft.near", amount:100000n, destinationAddress:"addrA", feeInclusive:false}, {assetId:"nep141:btc.omft.near", amount:50000n, destinationAddress:"addrB", feeInclusive:false} ]`.
2. Both intents settle in the same NEAR tx; the POA bridge indexer eventually returns both withdrawals in its `withdrawals` array, unsorted, e.g. `[{near_token_id:"btc.omft.near", status:"COMPLETED", transfer_tx_hash:"hash-for-addrA", amount:100000}, {near_token_id:"btc.omft.near", status:"PENDING", transfer_tx_hash:null, amount:50000}]`.
3. `describeWithdrawal({index:1, withdrawalParams: {..., destinationAddress:"addrB", amount:50000n}})` still calls `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns the **first** array element (`hash-for-addrA`, amount 100000) regardless of `index`.
4. The caller polling for withdrawal index 1 (destined for `addrB`) receives `{status:"completed", txHash:"hash-for-addrA"}` — a hash/status belonging to a different withdrawal — before `addrB`'s payment has actually landed.

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
