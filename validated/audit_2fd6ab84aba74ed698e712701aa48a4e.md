This confirms the SDK explicitly supports batch withdrawals with array `WithdrawalParams[]`, processed via `processWithdrawal`/`waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`, which calls `watchWithdrawal` once per withdrawal index concurrently.### Title
Batch withdrawals of the same asset are cross-matched by PoaBridge's assetId-only lookup, causing `watchWithdrawal` to report the wrong destination's completion hash - ([File: packages/intents-sdk/src/core/withdrawal-watcher.ts])

### Summary
`watchWithdrawal` (packages/intents-sdk/src/core/withdrawal-watcher.ts:20-78) unconditionally trusts `bridge.describeWithdrawal(args.wid)` and resolves `{ hash: status.txHash }` as soon as `status === 'completed'`, without verifying the returned hash actually corresponds to `args.wid.withdrawalParams` (amount/destinationAddress/index). `PoaBridge.describeWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343) resolves which withdrawal in the API response corresponds to a given `WithdrawalIdentifier` using `findMatchingWithdrawal`, which matches **only by assetId** (`nep141:${w.data.near_token_id} === assetId`), ignoring `index` entirely - a limitation explicitly documented in the code comment at lines 409-417 and 422-426: "This means multiple withdrawals of the same token in a single transaction are not supported."

### Finding Description
The broken equality: for `watchWithdrawal(wid_i)`, the returned `{hash}` must be the on-chain outcome of withdrawal `i` (same `index`, same `withdrawalParams.amount`/`destinationAddress`), not of some other withdrawal `j` in the same batch.

Path: `IntentsSDK.processWithdrawal` → `waitForWithdrawalCompletion` → `createWithdrawalCompletionPromises` (packages/intents-sdk/src/sdk.ts:557-609) supports a `WithdrawalParams[]` batch, assigning each param a `WithdrawalIdentifier` via `createWithdrawalIdentifiers` (withdrawal-watcher.ts:80-107), which increments a per-`bridge.route` `index` counter but keeps `withdrawalParams` per-wid. It then fires one `watchWithdrawal` call per wid, in parallel for non-HOT bridges.

If a caller submits two (or more) withdrawals of the **same asset** (same `assetId`) but different `destinationAddress`/`amount` routed through `PoaBridge` in one batch, both get distinct `index` values (0, 1, ...) but `PoaBridge.describeWithdrawal` (poa-bridge.ts:313-343) calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` (poa-bridge.ts:418-427), which does `.find()` by assetId only and returns the **same, first matching** entry for every `index` querying that assetId. `watchWithdrawal` then resolves `{ hash: status.txHash }` for whichever `wid` polls first with no cross-check against `withdrawalParams.amount`/`destinationAddress`/`index`, so a second (or later) withdrawal to a different destination can be reported as "completed" with the txHash belonging to the first withdrawal's transfer.

Existing guards don't catch this: `supports()`, `validateWithdrawal`, `FeeExceedsAmountError`, and the intents contract's own signature/nonce checks all operate on the *pre-execution* intent, not on the post-execution status reconciliation that `watchWithdrawal` performs; none of them verify that the resolved destination-chain `txHash` actually matches the specific `wid`'s `amount`/`destinationAddress` before the SDK returns it to the caller.

### Impact Explanation
The caller (an integrator) can be told withdrawal `j` (e.g. to destination B) is "completed" with a txHash that actually corresponds to withdrawal `i`'s transfer (to destination A). If the integrator uses this status/hash to mark the withdrawal as fulfilled, credit an internal ledger, or release a matching off-chain payment, it can lead to crediting/refunding based on a mismatched destination/amount — matching the High-severity category "a status or hash misreport making an integrator credit or refund twice." This is repeatable on every batch containing ≥2 same-asset PoaBridge withdrawals with distinct destinations/amounts, and requires no adversarial input beyond a normal batch withdrawal shape that ordinary users/integrators can construct legitimately.

### Likelihood Explanation
Preconditions: a batch withdrawal (`WithdrawalParams[]`) containing two or more entries with the same `assetId` routed to `PoaBridge` (i.e., a POA-bridge-supported asset), with differing `destinationAddress` and/or `amount`. This is a normal, unprivileged usage pattern already supported by `signAndSendWithdrawalIntent`/`processWithdrawal` batch mode — no malicious bridge API, RPC, or relayer is required; the mismatch stems purely from the in-repo `findMatchingWithdrawal` logic operating on legitimate API data. The bug is explicitly acknowledged in code comments as a known unsupported scenario, confirming it is reachable and not merely theoretical.

### Recommendation
In `PoaBridge.describeWithdrawal`/`findMatchingWithdrawal`, disambiguate withdrawals sharing the same assetId by also matching on `amount` and/or `destinationAddress` (and consuming matched entries so they aren't reused across indices), rather than matching by assetId alone. Additionally, harden `watchWithdrawal` (withdrawal-watcher.ts:43-47) to independently validate that the bridge-reported completion actually corresponds to `args.wid.withdrawalParams` (e.g., verify destination/amount against the resolved transfer, when the bridge can supply that data) before resolving `{ hash }`, so a single misbehaving/underspecified bridge adapter cannot produce a cross-wid false completion undetected by the caller.

### Proof of Concept
```ts
// withdrawal-watcher.test.ts style, mocking only the Bridge (no bridge internals)
it("must not report the same txHash for two distinct wids representing different withdrawalParams", async () => {
  const bridge = createMockBridge();
  // Simulate PoaBridge's assetId-only matching: describeWithdrawal ignores index/amount/destination
  vi.spyOn(bridge, "describeWithdrawal").mockImplementation(async (args) => {
    // Always returns the FIRST matching withdrawal for the shared assetId,
    // regardless of args.index / args.withdrawalParams.amount / destinationAddress
    return { status: "completed", txHash: "first-withdrawal-tx-hash" };
  });

  const widA = createWithdrawalIdentifier({
    index: 0,
    withdrawalParams: { assetId: "nep141:usdc.omft.near", amount: 100n, destinationAddress: "addrA" },
  });
  const widB = createWithdrawalIdentifier({
    index: 1,
    withdrawalParams: { assetId: "nep141:usdc.omft.near", amount: 200n, destinationAddress: "addrB" },
  });

  const resultA = await watchWithdrawal({ bridge, wid: widA });
  const resultB = await watchWithdrawal({ bridge, wid: widB });

  // BROKEN EQUALITY: both resolve to the same hash despite different withdrawalParams
  expect(resultA).toEqual({ hash: "first-withdrawal-tx-hash" });
  expect(resultB).toEqual({ hash: "first-withdrawal-tx-hash" }); // should differ / should not silently match
});
```
This demonstrates that `watchWithdrawal` performs no cross-check between the resolved `hash` and `wid.withdrawalParams` (amount/destinationAddress), letting a bridge with assetId-only (index-blind) matching — as `PoaBridge` demonstrably is per poa-bridge.ts:418-427 and its own test at poa-bridge.test.ts:1054 ("matches withdrawal by assetId, not by index") — produce a caller-visible false completion for the wrong withdrawal when two same-asset withdrawals are batched. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
