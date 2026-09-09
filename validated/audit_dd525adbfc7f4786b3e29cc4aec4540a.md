### Title
POA Bridge Withdrawal Status Matched Only by AssetId, Causing Cross-Withdrawal Status/Hash Misreport for Batched Same-Asset Withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain outcome of a specific withdrawal by looking up the POA bridge indexer response and matching solely on `assetId` via `findMatchingWithdrawal()`, ignoring the `index` that is otherwise threaded through the same `WithdrawalIdentifier`. When a single NEAR transaction contains more than one withdrawal of the same token (a supported, ordinary usage pattern via `sdk.createWithdrawalCompletionPromises` / `sdk.watchWithdrawals`), every one of those withdrawals resolves to the **same** matched record — the first (and only) entry found for that `assetId` — regardless of which withdrawal (destination address/amount) it actually corresponds to.

### Finding Description
`findMatchingWithdrawal` is defined as: [1](#0-0) 

and is invoked from `describeWithdrawal`: [2](#0-1) 

The `WithdrawalIdentifier` created by `createWithdrawalIdentifier()` does carry an `index` field: [3](#0-2) 

and `createWithdrawalIdentifiers()` explicitly maintains a **per-bridge-route index counter** so that multiple same-route withdrawals in one batch get distinguishable indexes: [4](#0-3) 

However `describeWithdrawal` never consults `args.index` — it matches purely on `assetId`, so index 0 and index 1 of two withdrawals of the same `nep141:*.omft.near` token both resolve to whichever single record the POA indexer response contains for that asset. The code comment itself admits the limitation:
"NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." (lines 411-416 above)

The SDK's public batching APIs (`createWithdrawalCompletionPromises`, docs in `docs/design/rfc-batch-withdrawal-granular-control.md`) do not prevent or warn against submitting multiple same-asset withdrawals in one call — this is presented as a normal, supported flow, and each returned promise is documented to correspond 1:1 by index to the input `withdrawalParams` array: [5](#0-4) 

This breaks the equality "status/txHash reported for withdrawal[i] == the on-chain outcome of withdrawal[i]". Instead, `status/txHash reported for withdrawal[i] == status/txHash of whichever same-asset withdrawal the indexer lists first`.

### Impact Explanation
If an integrator batches two withdrawals of the same POA-bridged token to two different destination addresses/amounts in a single intent transaction and awaits both completion promises, both promises can resolve to the transfer_tx_hash and completed status of only one of the two on-chain transfers. This can cause an integrator to:
- Credit or mark as settled a withdrawal that has not actually completed on the destination chain (using another withdrawal's tx hash as proof), while the real withdrawal for that destination may still be pending or could later fail/differ.
- Potentially double-credit downstream bookkeeping since both entries appear "completed" with the same tx hash even though only one destination actually received funds.

This matches the "status or hash misreport making an integrator credit or refund twice" high-impact category from the rules.

### Likelihood Explanation
No malicious actor is required — any legitimate caller performing a normal multi-withdrawal batch (e.g., paying out the same token to two different users in one settlement) via the documented `createWithdrawalCompletionPromises`/`watchWithdrawals` API triggers this. The bug is deterministic whenever ≥2 withdrawals share the same `assetId` in one batch, which is an ordinary, foreseeable usage pattern, not an edge case requiring privileged or adversarial behavior.

### Recommendation
Extend `findMatchingWithdrawal` (and the underlying POA bridge indexer query/response) to disambiguate withdrawals sharing the same `assetId` within one `tx.hash`, e.g., by additionally matching on destination address and amount, or by sorting both the withdrawal params and the API response deterministically (as the comment suggests) so each index maps to a unique on-chain transfer. Until fixed, the SDK should throw/assert when it detects multiple pending PoA-bridge withdrawals of the same `assetId` within a single `intentTx` rather than silently returning ambiguous/duplicate status data.

### Proof of Concept
1. Submit a single NEAR intents transaction containing two `ft_withdraw` intents for the same token (`nep141:usdc.omft.near`) to two different destination addresses/amounts, routed via `RouteEnum.PoaBridge`.
2. Call `sdk.createWithdrawalCompletionPromises({ withdrawalParams: [w0, w1], intentTx })`; both entries get distinct `wid.index` (0 and 1) per `createWithdrawalIdentifiers`.
3. When the POA bridge indexer lists only/first the withdrawal for `w0`'s destination as `COMPLETED` (with its `transfer_tx_hash`), `describeWithdrawal` for **both** `wid.index=0` and `wid.index=1` calls `findMatchingWithdrawal(response.withdrawals, "nep141:usdc.omft.near")`, which returns the same first matching record for both calls — reporting `w1`'s promise as `completed` with `w0`'s `transfer_tx_hash`, even though `w1`'s actual destination transfer may still be pending or distinct.

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
