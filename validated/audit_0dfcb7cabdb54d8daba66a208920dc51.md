### Title
Batch withdrawal status/txHash misattribution across same-asset withdrawals in a single settlement tx - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`, `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`)

### Summary
For batch withdrawals processed via `processWithdrawal`/`waitForWithdrawalCompletion` with multiple `WithdrawalParams` entries, the POA bridge's status-matching logic (`findMatchingWithdrawal`) identifies which on-chain withdrawal record corresponds to which requested withdrawal **only by `assetId`**, not by `destinationAddress`, `amount`, or index. When a batch contains two or more withdrawals of the same token (same `assetId`) to different destination addresses in a single NEAR settlement transaction, the lookup can return the wrong record, causing the SDK to report a `txHash`/`completed` status for the wrong withdrawal entry.

### Finding Description
`poa-bridge.ts`'s `describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which finds the first withdrawal in the API's unsorted list whose `near_token_id` matches the requested `assetId`: [1](#0-0) [2](#0-1) 

The same limitation exists in the internal-utils implementation used by `waitForWithdrawalCompletion`: [3](#0-2) 

The code comment explicitly acknowledges: "This means multiple withdrawals of the same token in a single transaction are not supported," but the public batch API (`processWithdrawal`/`waitForWithdrawalCompletion` accepting `WithdrawalParams[]`) does not reject or guard against this scenario — callers can freely submit multiple same-asset withdrawals with different `destinationAddress` values in one batch, as shown in `sdk.ts`'s `processWithdrawal`: [4](#0-3) 
and the `IIntentsSDK.waitForWithdrawalCompletion` overload accepting an array: [5](#0-4) 

Since `findMatchingWithdrawal` ignores `destinationAddress`/`amount`, when two batch entries share the same `assetId`, each call for either entry's `WithdrawalIdentifier` will match by asset only and can resolve to the *same* underlying API record (or the wrong one), so the `txHash`/`status` returned for entry A can actually belong to entry B's on-chain transfer, breaking the equality "status/hash reported == the on-chain outcome for that specific withdrawal."

### Impact Explanation
An integrator relying on `destinationTx[i]` from `waitForWithdrawalCompletion`/`processWithdrawal` to confirm which specific destination address/amount was paid could credit the wrong withdrawal as completed, or report the same destination tx hash for two different recipients — a status/hash misreport that can lead to a double credit or a wrongly-confirmed payment to an address that did not actually receive funds. This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
Requires no privileged access — any caller of the public SDK API can construct a batch of `WithdrawalParams` with two entries sharing the same `assetId` but different `destinationAddress` (a common real use case, e.g., paying out to two different users in the same token). The bug is already known and documented as a limitation in comments/tests, confirming it is a real, currently-existing gap rather than a hypothetical one, though it is explicitly scoped as "not supported" rather than fixed or blocked at the API layer.

### Recommendation
Either (a) validate/reject batches containing multiple withdrawals with the same `assetId` at the `processWithdrawal`/`waitForWithdrawalCompletion` API boundary until proper disambiguation is implemented, or (b) implement the matching-by-amount-ordering approach already suggested in the code comments (sorting both API results and withdrawal params by amount, since fees are equal for the same token so relative ordering is preserved) so each requested withdrawal is matched to the correct on-chain record.

### Proof of Concept
1. Call `sdk.processWithdrawal({ withdrawalParams: [ {assetId: "nep141:usdc.omft.near", amount: 100n, destinationAddress: "addrA", feeInclusive:false}, {assetId: "nep141:usdc.omft.near", amount: 200n, destinationAddress: "addrB", feeInclusive:false} ] })`.
2. Both entries settle in the same NEAR tx; the POA bridge API returns two withdrawal records for `usdc.omft.near`.
3. `findMatchingWithdrawal` for index 0 (`addrA`) and index 1 (`addrB`) both search only by `assetId === "nep141:usdc.omft.near"` via `.find(...)`, returning the first match for both lookups (or an unsorted, index-independent match), so `destinationTx[0]` and `destinationTx[1]` can report an incorrect/duplicate `txHash` relative to the actual `destinationAddress` paid, as demonstrated by the existing regression test `poa-bridge.test.ts:1054` ("matches withdrawal by assetId, not by index") which only proves single-entry correctness by asset but does not cover the same-asset multi-recipient batch case.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L405-427)
```typescript
type WithdrawalStatusResponse = Awaited<
	ReturnType<typeof poaBridge.httpClient.getWithdrawalStatus>
>;

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

**File:** packages/intents-sdk/src/shared-types.ts (L182-198)
```typescript
	waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams;
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<TxInfo | TxNoInfo>;

	waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams[];
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<Array<TxInfo | TxNoInfo>>;

	createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>>;
```
