### Title
Withdrawal status/tx-hash misattribution when a batch contains multiple withdrawals of the same asset - (File: `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`, `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`findMatchingWithdrawal()` in both `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` and `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` resolves the destination transaction/status for a withdrawal solely by matching `assetId` (`nep141:${near_token_id}`) against the unsorted list returned by the POA bridge API, with no disambiguation by amount, destination address, or index.

### Finding Description
`sdk.processWithdrawal()` in `packages/intents-sdk/src/sdk.ts` (lines 793-858) accepts an array of `WithdrawalParams` and executes them as a single batched intent, then calls `waitForWithdrawalCompletion({ withdrawalParams, intentTx, ... })` to resolve a status per-item. Internally, for POA-routed withdrawals, resolution goes through `describeWithdrawal()` in `poa-bridge.ts` (lines 313-343) and `waitForWithdrawalCompletion()` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (lines 35-125), both of which call `findMatchingWithdrawal()`: [1](#0-0) [2](#0-1) 

The matching logic returns the *first* element in `withdrawals` whose `near_token_id` equals the requested `assetId` — it does not use amount, destination address, or any per-withdrawal index/nonce to disambiguate. This is explicitly acknowledged in the code's own comment: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."

`sdk.processWithdrawal()` allows exactly this unsupported scenario: a caller can submit `withdrawalParams: WithdrawalParams[]` containing two (or more) entries with the same `assetId` but different `amount`/`destinationAddress` (e.g., splitting a USDC withdrawal to two different recipients in one intent). Because `Array.isArray(args.withdrawalParams)` branches simply forward the whole array through `estimateWithdrawalFee`, `signAndSendWithdrawalIntent`, and `waitForWithdrawalCompletion` without per-item uniqueness validation, nothing in the reachable code path rejects duplicate `assetId` entries in a batch.

When both withdrawals of the same token settle, `findMatchingWithdrawal()` will return the same (arbitrary/first) matching record for both items being resolved, so `destinationTx[0]` and `destinationTx[1]` in the returned `BatchWithdrawalResult` (`packages/intents-sdk/src/sdk.ts` lines 840-857) can both report the same `txHash`/status — even though only one of the two withdrawals actually has that hash, or one has completed while the other is still pending/failed.

### Impact Explanation
This breaks the equality "status/hash reported == actual on-chain outcome for that specific withdrawal item." An integrator relying on `sdk.processWithdrawal()`'s `destinationTx` array to mark per-item completion (e.g., crediting/reconciling two separate payouts of the same token in one batch) could:
- Mark both withdrawals as completed with the same destination tx hash, even though only one has actually landed, leading to premature release of downstream obligations for the still-pending/failed one.
- Attribute the wrong `transfer_tx_hash` to the wrong recipient's withdrawal record when the two withdrawals resolve to different real transactions but the matcher can't tell them apart.

This matches the "High" impact category: "a status or hash misreport making an integrator credit or refund twice." The bug is a genuine equality violation in status reporting, not a DoS/rate-limit/config issue.

### Likelihood Explanation
Likelihood is moderate: it requires the caller to construct a batch (`WithdrawalParams[]`) with two entries sharing the same `assetId`, which is a normal SDK usage pattern (batch withdrawals are a first-class, documented feature: `processWithdrawal({ withdrawalParams: [...] })`) rather than a malicious or out-of-spec input. No privilege escalation or protocol-level attack is needed — any regular user of the SDK triggering a same-token multi-recipient batch withdrawal hits this path. The code comment shows the maintainers are aware this case is unhandled, but nothing in the reachable SDK code (`processWithdrawal`, `estimateWithdrawalFee`, `signAndSendWithdrawalIntent`) validates or blocks batches with duplicate `assetId`s before they reach the flawed matcher.

### Recommendation
- In `sdk.processWithdrawal()` (`packages/intents-sdk/src/sdk.ts`), validate that `withdrawalParams[]` does not contain duplicate `assetId` entries, or explicitly document/reject this unsupported case before executing the batch.
- Alternatively, implement the disambiguation strategy already hinted at in the code comments: match withdrawals by sorting both the API response and the request params by `amount` for a given `assetId` (since relayer fees are identical for the same token) to establish a stable ordering, or extend the POA API/response to include a per-item nonce/index that can be correlated back to `withdrawalParams` index deterministically.
- Add integration tests covering a batch with two same-`assetId`, different-amount/destination withdrawals to confirm `destinationTx[]` items are attributed correctly and not silently duplicated.

### Proof of Concept
1. Call `sdk.processWithdrawal({ withdrawalParams: [ { assetId: "nep141:usdc.omft.near", amount: 100n, destinationAddress: "0xAAA...", feeInclusive: false }, { assetId: "nep141:usdc.omft.near", amount: 200n, destinationAddress: "0xBBB...", feeInclusive: false } ] })`.
2. The intent settles on NEAR in a single tx (`intentTx`), producing two POA withdrawal records with `near_token_id: "usdc.omft.near"` for both, differing in `transfer_tx_hash`/`amount`.
3. `waitForWithdrawalCompletion` → `findMatchingWithdrawal` for each of the two `WithdrawalParams` entries filters `result.withdrawals` by `nep141:${near_token_id} === assetId`, which for both entries is `"nep141:usdc.omft.near"` — the same predicate matches both API records, and `.find()` returns the *first* one for both lookups.
4. Both entries in `destinationTx[]` end up reporting the same `transfer_tx_hash`/status, even though the two withdrawals actually settled with different hashes/timings, matching one txHash to the wrong recipient's withdrawal. [3](#0-2) [4](#0-3)

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
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

**File:** packages/intents-sdk/src/sdk.ts (L793-857)
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
