### Title
POA Bridge Withdrawal Status Misattribution for Batched Same-Asset Withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves a withdrawal's on-chain status by matching entries returned from the POA Bridge API using `findMatchingWithdrawal()`, which keys solely on `assetId` via `Array.prototype.find`. When a single NEAR intents transaction contains more than one withdrawal of the same asset (a batch of `ft_withdraw` intents to the POA bridge for the same token but different destinations/amounts), every `describeWithdrawal` call for that asset in that transaction returns the exact same (first) matching record. This breaks the equality "status/txHash reported == the actual on-chain outcome of *this* withdrawal."

### Finding Description
`findMatchingWithdrawal` is defined as: [1](#0-0) 

and is invoked from `describeWithdrawal`: [2](#0-1) 

The matching logic only compares `assetId` (`nep141:${w.data.near_token_id}`) and ignores the withdrawal's `index`, `amount`, or `destinationAddress`. The code comment even acknowledges: "multiple withdrawals of the same token in a single transaction are not supported."

However, the SDK's public batching APIs do not prevent this scenario. `IntentsSDK.createWithdrawalCompletionPromises` / `waitForWithdrawalCompletion` accept an array of `WithdrawalParams` and independently create a `WithdrawalIdentifier` (with a per-bridge `index`) for each entry: [3](#0-2) [4](#0-3) 

Nothing in `createWithdrawalIdentifiers`/`findBridgeForWithdrawal` rejects two withdrawals of the same `assetId` going through `PoaBridge` in the same `intentTx`. Each resulting `WithdrawalIdentifier` carries its own `withdrawalParams` (its own destination/amount) and `index`, but `PoaBridge.describeWithdrawal` never uses `index` (unlike `createWithdrawalIdentifier`, which sets it but it's dead for matching purposes) — it always calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, so both polling loops converge on the identical API record.

### Impact Explanation
If an integrator batches two POA-bridge withdrawals of the same asset (e.g., BTC to user A and BTC to user B) inside one NEAR intents transaction and tracks completion via `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`, both promises will resolve using the same underlying POA API record:
- Both withdrawals can be reported `completed` with the identical `txHash`, even though only one of the two destination transfers has actually settled on-chain.
- An integrator that credits/finalizes user-facing state (e.g., marks an order fulfilled, releases custody, or notifies a user their funds arrived) based on this status will do so for a withdrawal that has not actually landed on the destination chain, or attribute the wrong destination tx hash to the wrong recipient.

This falls under the "status or hash misreport making an integrator credit or refund twice" — a High-impact analog of the reported bug class (data used to release/settle funds does not match on-chain truth).

### Likelihood Explanation
No malicious relayer/RPC/price-feed behavior is required — this triggers under entirely legitimate, unprivileged usage: a caller (or the integrator building on `IntentsSDK`) simply needs to submit ≥2 POA-bridge withdrawals of the same `assetId` in one NEAR transaction and then track completion with the SDK's own batch APIs (`createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion`), which explicitly support arrays of `WithdrawalParams` without validating asset uniqueness per bridge route.

### Recommendation
In `findMatchingWithdrawal`, disambiguate multiple same-asset withdrawals — e.g., sort both the API's `withdrawals` list and the caller-supplied `withdrawalParams` deterministically (as the existing comment suggests, by amount, since POA relayer fees are identical per token) and match by `(assetId, index)` rather than `assetId` alone. Until then, `createWithdrawalIdentifiers`/`PoaBridge.supports` should reject (or the SDK should explicitly document/guard against) batches containing more than one POA-bridge withdrawal for the same `assetId` within a single `intentTx`, so callers cannot silently receive a misattributed status/txHash.

### Proof of Concept
1. Build and send a NEAR intents transaction containing two `ft_withdraw` intents for `nep141:btc.omft.near`: one `receiver_id`/withdrawal to address A, one to address B (both routed through `PoaBridge`, e.g., via two separate `createWithdrawalIntents` calls merged into one signed transaction/`intentTx`).
2. Call:
```ts
const [resultA, resultB] = await sdk.waitForWithdrawalCompletion({
  withdrawalParams: [
    { assetId: "nep141:btc.omft.near", amount: amtA, destinationAddress: addrA, feeInclusive: false },
    { assetId: "nep141:btc.omft.near", amount: amtB, destinationAddress: addrB, feeInclusive: false },
  ],
  intentTx,
});
```
3. Once the POA relayer has processed only the withdrawal to `addrA` (status `COMPLETED` in its API), both `resultA` and `resultB` resolve as `{ hash: <addrA's transfer_tx_hash> }`, because `findMatchingWithdrawal` returns the same first matching record (keyed only on `nep141:btc.omft.near`) for both `describeWithdrawal` calls — see `poa-bridge.ts` lines 313-343 and 409-427 above. `resultB` is falsely reported complete with `addrA`'s tx hash while the actual transfer to `addrB` may still be pending or use a different hash entirely.

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
