### Title
POA Bridge withdrawal status/hash misreport for batches containing duplicate-asset withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` and the shared `waitForWithdrawalCompletion` helper resolve which on-chain withdrawal record belongs to a given batch item by matching on `assetId` alone (`findMatchingWithdrawal`), never on the withdrawal's index or amount. When a single batched intent contains two or more withdrawals of the same token, every `describeWithdrawal`/`waitForWithdrawalCompletion` call for that token returns the *first* record found in the (unsorted) API response, regardless of which of the several same-asset withdrawals it actually corresponds to.

### Finding Description
`findMatchingWithdrawal` in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (lines 418-427) and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (lines 144-153) is implemented as:
```ts
function findMatchingWithdrawal(withdrawals, assetId) {
  return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
``` [1](#0-0) 

`describeWithdrawal` uses this lookup keyed only by `args.withdrawalParams.assetId`, with an explicit comment acknowledging the response list is unsorted and matching is done by asset only: [2](#0-1) 

The SDK explicitly supports batch withdrawals where multiple `WithdrawalParams` entries are signed into one intent and later polled independently, one promise per input index, via `sdk.createWithdrawalCompletionPromises` / `sdk.waitForWithdrawalCompletion` / `sdk.processWithdrawal`: [3](#0-2) [4](#0-3) 

Nothing in `signAndSendWithdrawalIntent`, `createWithdrawalIdentifiers`, or `createWithdrawalCompletionPromises` rejects or de-duplicates batches containing two withdrawals of the same `assetId` (e.g., two USDC withdrawals to different destination addresses/amounts within one intent, as shown in the README's own batch example using two different-token withdrawals — nothing prevents the same-token case). Both call sites carry the same caveat comment: "multiple withdrawals of the same token in a single transaction are not supported" — i.e., the authors are aware the matching is not index/amount-aware, but the SDK still allows constructing such batches and reports a status/hash for each index independently.

The equality broken here is: *the status/hash reported for withdrawal index N* should equal *the on-chain outcome for withdrawal index N specifically*. Because the match key is only `assetId`, `describeWithdrawal({index: 0, assetId: X})` and `describeWithdrawal({index: 1, assetId: X})` both resolve to the exact same array element (the first same-asset record the POA API returns), even though the two withdrawals may have gone to different addresses/amounts and only one may actually have completed.

### Impact Explanation
An integrator using `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` for a batch withdrawal containing two same-token entries will see the *same* `txHash`/`status` reported for both indices. If withdrawal[0] (e.g., refund to address A) fails or is still pending while withdrawal[1] (payout to address B, same token) has completed, the integrator's promise for index 0 can resolve as "completed" using withdrawal[1]'s `transfer_tx_hash` — a status/hash misreport that does not match the actual on-chain outcome for that specific withdrawal. This falls into the "status or hash misreport making an integrator credit or refund twice" category (High impact): the integrator could mark the wrong withdrawal (to the wrong destination) as completed and credit/refund based on a transaction that has nothing to do with that specific withdrawal request.

### Likelihood Explanation
Likelihood is constrained by the fact that this requires the caller (the integrator building withdrawal batches, not an external attacker) to construct a batch containing two or more withdrawals of the identical `assetId`. The SDK does not prevent this, and the code's own comments confirm the authors recognized the ambiguity but left it unhandled ("not supported" rather than validated/rejected). There is no external attacker action needed beyond normal usage of the batch withdrawal API with same-token entries, making this a latent, easily-triggered correctness bug rather than a hardened security boundary.

### Recommendation
Reject (throw) when constructing a batch withdrawal (`signAndSendWithdrawalIntent`/`processWithdrawal`) if `withdrawalParams` contains more than one entry with the same `assetId`, until POA bridge API/matching supports disambiguating same-asset withdrawals by index/amount. Alternatively, implement the ordering-based matching suggested in the existing code comments (sort both the API response and the local withdrawal params by amount, since fees are equal for same-token entries) before shipping this as a supported feature, and add regression tests covering batches with duplicate `assetId` entries.

### Proof of Concept
1. Submit a batch withdrawal intent with two withdrawal params for the same token but different destinations, e.g.:
```ts
withdrawalParams: [
  { assetId: "nep141:usdt.tether-token.near", amount: 100n, destinationAddress: "0xAAA..." },
  { assetId: "nep141:usdt.tether-token.near", amount: 50n,  destinationAddress: "0xBBB..." },
]
```
2. Call `sdk.createWithdrawalCompletionPromises({ withdrawalParams, intentTx })`.
3. Have the POA bridge process/settle only the second withdrawal (to `0xBBB...`) while the first (to `0xAAA...`) is still pending/failed.
4. Observe that `describeWithdrawal` for index 0 (via `findMatchingWithdrawal` matching only on `assetId`) returns the `COMPLETED` status and `transfer_tx_hash` belonging to the withdrawal actually sent to `0xBBB...`, causing `promises[0]` to resolve as completed with a transaction hash that does not correspond to the withdrawal to `0xAAA...`. [2](#0-1) [5](#0-4)

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

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
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
```

**File:** packages/intents-sdk/src/sdk.ts (L783-858)
```typescript
	// Orchestrated functions

	public processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams>,
	): Promise<WithdrawalResult>;

	public processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams[]>,
	): Promise<BatchWithdrawalResult>;

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

		if (!Array.isArray(args.withdrawalParams)) {
			return {
				// biome-ignore lint/style/noNonNullAssertion: single withdrawal returns single-element arrays
				feeEstimation: feeEstimation[0]!,
				intentHash,
				intentTx,
				// biome-ignore lint/style/noNonNullAssertion: single withdrawal returns single-element arrays
				destinationTx: destinationTx[0]!,
			};
		}

		return {
			feeEstimation,
			intentHash,
			intentTx,
			destinationTx,
		};
	}
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
