### Title
Same-`assetId` batched withdrawals in `processWithdrawal` cause `PoaBridge.describeWithdrawal` to misreport a wrong `txHash` for the wrong index - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`processWithdrawal`/`createWithdrawalCompletionPromises` map bridge status results back to `withdrawalParams[index]` purely by array position [1](#0-0) , but `PoaBridge.describeWithdrawal` resolves each `WithdrawalIdentifier` by looking up the POA API's unsorted withdrawal list via `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, matching only on `assetId`, not on a unique withdrawal id [2](#0-1) . When a caller batches two withdrawals with the same `assetId` but different `destinationAddress` values, both indexes resolve independently to the same `find()` call and can both return the **same** (arbitrary, first-matching) entry from the unsorted list, so the caller can end up crediting index 0 with the `txHash` that actually belongs to index 1's on-chain transfer (to a different address).

### Finding Description
- Broken equality: `describeWithdrawal` result assigned to `destinationTx[index]` should correspond to the on-chain withdrawal actually sent to `withdrawalParams[index].destinationAddress`. In reality, `findMatchingWithdrawal` selects `withdrawals.find(w => nep141:${w.data.near_token_id} === assetId)` [3](#0-2)  — the very first element in the (unsorted) API response matching that `assetId`, independent of `destinationAddress`, amount, or any withdrawal-specific id.
- The code's own comment documents this: "Response list is unsorted, so we match by assetId instead of index" and "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [4](#0-3) .
- Exact reachable path: `sdk.processWithdrawal` (packages/intents-sdk/src/sdk.ts:793-857) accepts `withdrawalParams: WithdrawalParams[]` with no dedup/validation on `assetId` combinations [5](#0-4) . `createWithdrawalIdentifiers` builds one `WithdrawalIdentifier` per input element, assigning `index` only as a per-bridge-route counter, and does not check for duplicate `assetId`+different `destinationAddress` combos [6](#0-5) . `createWithdrawalCompletionPromises` then maps `withdrawalParams.map((_, index) => ...)` and calls `watchWithdrawal` per index, each independently calling `bridge.describeWithdrawal` [1](#0-0) , [7](#0-6) .
- Existing guards do not prevent this: `validateAddress`/`compareAddresses`/`validateWithdrawal` in `PoaBridge` only validate a single withdrawal's own destination against blockchain format and the token's own contract address [8](#0-7) ; none of them cross-check batch entries against each other for duplicate `assetId`. `supports()` and `findBridgeForWithdrawal` only determine which bridge handles an asset, not per-index disambiguation [9](#0-8) .
- Attacker input: submit `processWithdrawal({ withdrawalParams: [{assetId: A, destinationAddress: addr1, amount: x}, {assetId: A, destinationAddress: addr2, amount: y}], ... })` for their own funds. Exploit flow: after the intent settles on NEAR and POA bridge relays both withdrawals on-chain, `describeWithdrawal` for index 0 and index 1 both query the same `withdrawal_hash` (the shared NEAR intent tx) and both apply `findMatchingWithdrawal` filtered only by `assetId === A`; if the API returns both entries, `.find()` returns the same (first) match for both indexes, so both polling loops can resolve to the identical `txHash`, and depending on ordering/timing an integrator could report index 0 as completed with the `txHash` that actually corresponds to the on-chain transfer sent to `addr2` (index 1's destination).

### Impact Explanation
This is a status/hash misreport: an integrator relying on `destinationTx[i].hash` to prove a specific withdrawal reached `withdrawalParams[i].destinationAddress` could be shown a transaction hash that instead paid the OTHER batched destination address. This does not move funds the user did not authorize and does not cause a double-spend of contract funds, but it can cause an integrator to incorrectly attribute/credit a completion (e.g., mark index-0's withdrawal to `addr1` as "confirmed" using a hash that actually paid `addr2`), matching the High category "a status or hash misreport making an integrator credit or refund twice." Repeatable on every batch containing duplicate `assetId` with distinct destinations for tokens routed to `PoaBridge`.

### Likelihood Explanation
Preconditions: attacker must control (or have forwarded to them) a batch call to `processWithdrawal`/`createWithdrawalCompletionPromises` containing ≥2 entries sharing the same `assetId`, routed to `PoaBridge` (NEP-141 POA-bridged tokens), with different `destinationAddress`. No special privileges required — any SDK caller can construct such a batch with their own funds. Feasibility is high given the code comment explicitly acknowledges this limitation; the only uncertainty is whether the POA bridge HTTP API can, in practice, return more than one entry for the same NEAR tx hash with the same `assetId` (this depends on API/indexer behavior, but the SDK code path itself performs no ordering/dedup and would misbehave the moment the API returns such a list).

### Recommendation
Match by a stable, unique identifier instead of `assetId`. If the POA API doesn't expose a unique per-withdrawal id in the response, disambiguate multiple same-`assetId` withdrawals by sorting both the API response and the withdrawal params deterministically (e.g., by `amount`, since relayer fees are equal for same-asset transfers) as suggested in the existing code comment, or reject/merge duplicate `assetId` entries in a batch at `processWithdrawal`/`createWithdrawalIdentifiers` time and require callers to submit same-asset withdrawals in separate calls until the POA API supports unique ids.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (new test)
import { describe, it, expect, vi } from "vitest";
import { poaBridge } from "@defuse-protocol/internal-utils";
// ... existing imports/setup for PoaBridge instance

it("misattributes txHash when batch has duplicate assetId with different destinations", async () => {
  const assetId = "nep141:usdc.omft.near";
  const tx = { hash: "near-tx-hash", accountId: "user.near" };

  const wid0 = bridge.createWithdrawalIdentifier({
    withdrawalParams: { assetId, destinationAddress: "addr1", amount: 100n },
    index: 0,
    tx,
  });
  const wid1 = bridge.createWithdrawalIdentifier({
    withdrawalParams: { assetId, destinationAddress: "addr2", amount: 200n },
    index: 1,
    tx,
  });

  // Mock HTTP client to return both withdrawals unsorted, same assetId, different data
  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", transfer_tx_hash: "hash-for-addr2" /* actually addr2's payout */ } },
      { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", transfer_tx_hash: "hash-for-addr1" } },
    ],
  });

  const status0 = await bridge.describeWithdrawal({ ...wid0, tx });
  const status1 = await bridge.describeWithdrawal({ ...wid1, tx });

  // EQUALITY UNDER TEST:
  // status0.txHash should equal the hash that actually paid addr1 ("hash-for-addr1")
  // status1.txHash should equal the hash that actually paid addr2 ("hash-for-addr2")
  // Because findMatchingWithdrawal only filters by assetId, both calls return
  // the SAME first match ("hash-for-addr2"), breaking the equality:
  expect(status0.txHash).toBe("hash-for-addr2"); // WRONG: should be "hash-for-addr1"
  expect(status1.txHash).toBe("hash-for-addr2"); // both indexes collide on same entry
});
```
This demonstrates that `findMatchingWithdrawal` returns an identical, non-index-aware result for both batched entries sharing `assetId`, confirming the STATUS_TRUTH break described in the question.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L573-608)
```typescript
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
```

**File:** packages/intents-sdk/src/sdk.ts (L793-838)
```typescript
	async processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams | WithdrawalParams[]>,
	): Promise<WithdrawalResult | BatchWithdrawalResult> {
		const withdrawalParams = Array.isArray(args.withdrawalParams)
			? args.withdrawalParams
			: [args.withdrawalParams];

		// Step 1: Estimate fee
		const feeEstimation = await (() => {
			if (args.feeEstimation != null) {
				return Array.isArray(args.feeEstimation)
					? args.feeEstimation
					: [args.feeEstimation];
			}

			return this.estimateWithdrawalFee({
				withdrawalParams,
				logger: args.logger,
			});
		})();

		// Step 2: Sign and send intent
		const { intentHash } = await this.signAndSendWithdrawalIntent({
			withdrawalParams,
			feeEstimation,
			referral: args.referral,
			intent: args.intent,
			logger: args.logger,
		});

		args.logger?.info("Intent published", { intentHash });

		// Step 3: Wait for intent settlement
		const intentTx = await this.waitForIntentSettlement({
			intentHash: intentHash,
			logger: args.logger,
		});

		args.logger?.info("Intent settled", { txHash: intentTx.hash });

		// Step 4: Wait for withdrawal completion
		const destinationTx = await this.waitForWithdrawalCompletion({
			withdrawalParams,
			intentTx,
			logger: args.logger,
		});
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L81-106)
```typescript
	async supports(
		params: Pick<WithdrawalParams, "assetId" | "routeConfig">,
	): Promise<boolean> {
		if (params.routeConfig != null && !this.is(params.routeConfig)) {
			return false;
		}

		const assetInfo = this.parseAssetId(params.assetId);
		const isValid = assetInfo != null;

		if (!isValid && params.routeConfig != null) {
			throw new UnsupportedAssetIdError(
				params.assetId,
				"`assetId` does not match `routeConfig`.",
			);
		}

		if (
			assetInfo != null &&
			POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE[assetInfo.contractId] !== undefined
		) {
			return false;
		}

		return isValid;
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-230)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
		destinationMemo?: string;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		// Use cached getSupportedTokens to avoid frequent API calls
		const { tokens } = await this.getCachedSupportedTokens(
			[toPoaNetwork(assetInfo.blockchain)],
			args.logger,
		);

		const tokenInfo = tokens.find(
			(token) => token.intents_token_id === args.assetId,
		);

		if (tokenInfo == null) {
			throw new UnsupportedAssetIdError(
				args.assetId,
				"`assetId` is not supported in PoA bridge.",
			);
		}

		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}

		if (!args.skipMinAmountValidation) {
			const minWithdrawalAmount = BigInt(tokenInfo.min_withdrawal_amount);
			if (args.amount < minWithdrawalAmount) {
				throw new MinWithdrawalAmountError(
					minWithdrawalAmount,
					args.amount,
					args.assetId,
				);
			}
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-416)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-47)
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
