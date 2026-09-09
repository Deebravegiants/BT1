## Title
Batch withdrawal status matched only by `assetId` (ignoring index) can misreport completion status/txHash for same-asset withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`, `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`)

## Summary
### Finding Description
This is a direct analog of the `estimatedAPR()` bug class: a value reported by a "status/estimation" function that does not correspond to the actual on-chain outcome for the specific entity being queried, because the lookup key used is coarser than the real identity of the thing being tracked.

`PoaBridge.describeWithdrawal()` is supposed to report the completion status/txHash for a *specific* withdrawal identified by `{ index, tx, withdrawalParams }` [1](#0-0) . Internally it calls `findMatchingWithdrawal`, which — by explicit design/comment — ignores `index` entirely and matches purely by `assetId` (via `near_token_id`): [2](#0-1) 

The identical pattern exists in `waitForWithdrawalCompletion()` in `internal-utils`, whose `WithdrawalCriteria` type only carries `assetId`, and whose `findMatchingWithdrawal` similarly matches by `near_token_id` alone: [3](#0-2) [4](#0-3) 

When a caller submits a batch withdrawal (supported first-class via `sdk.processWithdrawal`/`sdk.waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`, see [5](#0-4)  and [6](#0-5) ) containing **two or more withdrawals of the same `assetId` but different destination addresses/amounts** in a single NEAR intent transaction, `Array.find()` returns the **first** array entry whose `near_token_id` matches — regardless of which logical withdrawal (index 0 or index 1) it actually corresponds to. Since "Response list is unsorted" (per the code's own comment), the entry returned for `describeWithdrawal(index: 0)` and `describeWithdrawal(index: 1)` can be the **same** underlying API record, or the record belonging to the *other* index's withdrawal.

The equality that should hold is:
`describeWithdrawal({index: i}).txHash == the real destination tx hash of withdrawal i`

This equality is broken here because the match key (`assetId`) does not uniquely identify `i` when multiple same-asset withdrawals exist in the batch.

### Impact Explanation
`createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` is the mechanism integrators use to learn when/where funds landed and to trigger downstream actions (crediting a ledger, releasing a corresponding fiat/other-asset leg, marking an internal withdrawal record "done"). If withdrawal at index 0 (destination A, amount X) and index 1 (destination B, amount Y) share the same `assetId`, and only one of the two has actually completed on-chain, the SDK can report **both** indices as `"completed"` with the **same** `txHash`, or attribute index 0's completion event (and hash) to index 1 (and vice versa).

Consequences for an integrator relying on this API:
- Marking withdrawal 0 as completed with a `txHash` that actually belongs to a different withdrawal (wrong destination/amount attribution) — a misreport of the on-chain outcome for that specific withdrawal.
- Prematurely treating a still-pending withdrawal as `"completed"` (because the array-find matched an unrelated completed entry for the same asset), causing the integrator to release/credit funds on the other leg of the flow before the actual transfer for that specific request has happened.
- In a system that reconciles "one txHash per withdrawal," the same `txHash` being reported for two different indices can cause a double-credit/double-close of two distinct withdrawal records from a single destination transaction.

This matches the "status reported that is not the on-chain outcome" class explicitly called out as in-scope, with High-tier impact ("a status or hash misreport making an integrator credit or refund twice").

### Likelihood Explanation
This requires only an ordinary, unprivileged usage pattern already documented as first-class SDK functionality: a batch withdrawal (`processWithdrawal`/`signAndSendWithdrawalIntent` with an array of `withdrawalParams`) where two entries share the same `assetId`. No malicious relayer, attacker-controlled RPC, or admin action is required — it is triggered purely by normal caller input (multiple withdrawals of the same token to different destinations in one call), which the SDK's own public API and README explicitly support for batches. The code's own comment acknowledges the limitation ("multiple withdrawals of the same token in a single transaction are not supported"), confirming the root cause is real and reachable, though it is not surfaced to callers as a validation error — the SDK silently returns a value that can be wrong rather than rejecting the unsupported case.

### Recommendation
- In `createWithdrawalIdentifiers`/`describeWithdrawal`, either (a) reject/detect batches with duplicate `assetId` entries and throw an explicit "unsupported: duplicate asset in batch" error instead of silently returning a possibly-wrong match, or (b) disambiguate matches using additional fields returned by the POA API (e.g., `amount`, `address`/destination, and/or an ordering scheme) rather than `assetId` alone, as hinted in the existing code comment.
- Apply the same fix to `findMatchingWithdrawal` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`, since it has the identical single-field matching flaw.
- Add regression tests covering multiple same-asset withdrawals in one batch to ensure each index resolves to the correct destination `txHash`, not just to "some" completed record.

### Proof of Concept
1. Caller submits a batch withdrawal via `sdk.processWithdrawal({ withdrawalParams: [ {assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addrA"}, {assetId: "nep141:btc.omft.near", amount: 50000n, destinationAddress: "addrB"} ] })`.
2. Both withdrawals route through `PoaBridge`, producing `WithdrawalIdentifier`s with `index: 0` and `index: 1`, both `assetId = "nep141:btc.omft.near"`.
3. POA bridge's `getWithdrawalStatus` returns two entries for the same NEAR tx hash, both with `near_token_id: "btc.omft.near"` (one `COMPLETED` with `transfer_tx_hash: "tx-for-addrA"`, the other still `PENDING`).
4. `describeWithdrawal({index: 1, ...})` calls `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which via `Array.find` returns the **first** matching entry — the one actually completed for index 0's withdrawal to `addrA` — and reports `{status: "completed", txHash: "tx-for-addrA"}` for the withdrawal that should have gone to `addrB`.
5. The integrator, trusting the per-index result, incorrectly marks the `addrB` withdrawal as completed using a hash that actually corresponds to the `addrA` transfer. [7](#0-6) [8](#0-7)

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L31-33)
```typescript
export type WithdrawalCriteria = {
	assetId: string;
};
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

**File:** packages/intents-sdk/src/sdk.ts (L486-521)
```typescript
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

**File:** packages/intents-sdk/src/sdk.ts (L783-857)
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
