### Title
POA bridge and internal-utils `findMatchingWithdrawal` match by `assetId` only, causing two same-asset withdrawals in one batch to report the same `transfer_tx_hash` - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts, packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts)

### Summary
`PoaBridge.describeWithdrawal` and `waitForWithdrawalCompletion` (internal-utils) both resolve the destination tx hash for a withdrawal via `findMatchingWithdrawal(withdrawals, assetId)`, which does `Array.prototype.find` matching purely on `nep141:${near_token_id} === assetId`, ignoring `destinationAddress`/index entirely. When `IntentsSDK.processWithdrawal` is called with a `withdrawalParams` array containing two PoA-route entries sharing the same `assetId` but different `destinationAddress`, both `WithdrawalIdentifier`s (index 0 and index 1) query the same PoA endpoint and both get matched to the *first* withdrawal record found for that `assetId`, so both resolve to the identical `transfer_tx_hash`.

### Finding Description
The broken equality: `describeWithdrawal(wid_index0).txHash` should differ from `describeWithdrawal(wid_index1).txHash` when `destinationAddress` differs, but both equal the same `transfer_tx_hash` because matching disregards `destinationAddress` and `index`.

Code path:
- `IntentsSDK.processWithdrawal` accepts `withdrawalParams: WithdrawalParams[]` and forwards them unchanged through `signAndSendWithdrawalIntent` → intents get submitted → `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` → `watchWithdrawal` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:20-77`) polls `bridge.describeWithdrawal(wid)` for each `WithdrawalIdentifier`.
- `createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`) assigns per-route sequence numbers (`index`), so two PoA withdrawals with the same `assetId` get `index: 0` and `index: 1`, both carrying identical `withdrawalParams.assetId` but different `destinationAddress`.
- `PoaBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`) calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, and the matcher (`poa-bridge.ts:409-427`) only filters on `assetId`, explicitly commented: *"multiple withdrawals of the same token in a single transaction are not supported"*.
- The same limitation exists independently in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts:144-153`.
- Because the POA HTTP response list is unsorted and unindexed by which of the batch's withdrawals it corresponds to, both `describeWithdrawal` calls (index 0 and index 1) converge on the same array element returned by `.find()`, yielding the same `transfer_tx_hash` for both.

Root cause: the matching key (`assetId`) is not unique across the batch when a user deliberately withdraws the same asset to two different destinations in one `processWithdrawal` call — nothing in `supports()`, `validateWithdrawal`, or `createWithdrawalIdentifiers` rejects or deduplicates same-`assetId` PoA withdrawals in a batch; the docstrings themselves acknowledge this as a known, unhandled limitation rather than a guarded/rejected case.

Attacker's exact input: an ordinary user calls `sdk.processWithdrawal({ withdrawalParams: [{assetId: X, destinationAddress: A, ...}, {assetId: X, destinationAddress: B, ...}] })` where both entries route through PoA bridge (`supports()` returns true for both, e.g., same NEP-141 asset to two different landing addresses on the same chain).

### Impact Explanation
Both `destinationTx[0]` and `destinationTx[1]` returned by `processWithdrawal`/`waitForWithdrawalCompletion` report the same `txHash`, even though only one on-chain payout actually exists for that hash (or, in the worst case, only one recipient truly received funds while the other is still pending/unrouted). An integrator that keys "withdrawal completed" bookkeeping off `destinationTx[i].hash` will mark **both** withdrawals as completed and credit/settle both, when in reality one destination may not have received funds — this is the "status or hash misreport making an integrator credit or refund twice" category (High per the defined severity list), reachable by any unprivileged user simply by submitting a batch withdrawal with a repeated `assetId`. It is repeatable on every batch containing duplicate `assetId` entries.

### Likelihood Explanation
Preconditions: attacker only needs to call the public `processWithdrawal`/`createWithdrawalCompletionPromises` API with a `withdrawalParams` array containing ≥2 entries with identical `assetId` (any PoA-supported NEP-141 token) and different `destinationAddress`. No privileged role, no relayer/RPC compromise, and no escape hatch misuse is required — this is a directly reachable, always-available combination of documented parameters. The bug is explicitly acknowledged as unresolved in the code comments, confirming there is no compensating guard. Feasibility is high and the cost is a single batch withdrawal transaction.

### Recommendation
Match POA withdrawal records deterministically per batch entry instead of by `assetId` alone — e.g., sort both the withdrawal params and the POA API's returned withdrawals by `(assetId, amount)` (as the existing comment suggests) or, if POA API adds request/response correlation (e.g., destination address or per-request nonce), use that to bind each `WithdrawalIdentifier.index` to a unique record. Until POA API support lands, `createWithdrawalIdentifiers`/`processWithdrawal` should detect and reject (or refuse to batch) multiple PoA-route withdrawals sharing the same `assetId` to prevent silently returning ambiguous/duplicate status.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.duplicate-asset.test.ts
it("BUG: two same-assetId withdrawals with different destinations resolve to the same txHash", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "shared-tx-hash", // single real payout
          chain: "eth",
          defuse_asset_identifier: "nep141:eth.omft.near",
          near_token_id: "eth.omft.near",
          decimals: 18,
          amount: 1000000,
          account_id: "test.near",
          address: "0xAAAA...", // only recipient A actually
          created: "2024-01-01T00:00:00Z",
        },
      },
    ],
  });

  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}) });

  const widA = { landingChain: Chains.Ethereum, index: 0,
    withdrawalParams: { assetId: "nep141:eth.omft.near", amount: 1000000n, destinationAddress: "0xAAAA...", feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" } };

  const widB = { landingChain: Chains.Ethereum, index: 1,
    withdrawalParams: { assetId: "nep141:eth.omft.near", amount: 1000000n, destinationAddress: "0xBBBB...", feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" } };

  const resultA = await bridge.describeWithdrawal(widA);
  const resultB = await bridge.describeWithdrawal(widB);

  // Broken equality: both resolve to the SAME txHash despite different destinationAddress
  expect(resultA).toEqual({ status: "completed", txHash: "shared-tx-hash" });
  expect(resultB).toEqual({ status: "completed", txHash: "shared-tx-hash" });
  expect(resultA.txHash).toBe(resultB.txHash); // should NOT be equal for different recipients
});
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L1-77)
```typescript
import {
	BaseError,
	type ILogger,
	poll,
	POLL_PENDING,
	PollTimeoutError,
} from "@defuse-protocol/internal-utils";
import type {
	Bridge,
	NearTxInfo,
	TxInfo,
	TxNoInfo,
	WithdrawalIdentifier,
	WithdrawalParams,
} from "../shared-types";
import { getWithdrawalStatsForChain } from "../constants/withdrawal-timing";

const MAX_CONSECUTIVE_ERRORS = 5;

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

**File:** packages/intents-sdk/src/sdk.ts (L785-857)
```typescript
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
