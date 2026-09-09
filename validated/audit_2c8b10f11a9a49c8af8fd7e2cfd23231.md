### Title
Withdrawal completion status/tx-hash misreported when multiple withdrawals of the same asset are batched in one intent - (File: packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts)

### Summary
`findMatchingWithdrawal` in the POA-bridge withdrawal-completion poller matches a withdrawal record returned by the POA Bridge API to a caller's specific withdrawal solely by `assetId` (`near_token_id`), ignoring amount, destination address, or any per-withdrawal index/id. When a single NEAR intent transaction contains more than one withdrawal of the same asset (e.g. two `ft_withdraw` intents for the same token to different destination addresses in one batch), every one of the SDK's `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` calls for that `txHash` + `assetId` resolves against the same matched record.

### Finding Description
`findMatchingWithdrawal` returns the first withdrawal entry whose `near_token_id` matches the criteria's `assetId`: [1](#0-0) 

This function is invoked from `waitForWithdrawalCompletion`, which returns `destinationTxHash`/`chain` for whichever withdrawal record happened to match: [2](#0-1) 

The equality that should hold is: *the tx hash/status reported for withdrawal #N of a batch corresponds to the on-chain settlement of withdrawal #N specifically*. Because matching only keys off `assetId`, when two withdrawals of the same token exist in one intent, both `createWithdrawalCompletionPromises` calls (one per `WithdrawalIdentifier`, driven from `packages/intents-sdk/src/sdk.ts` `createWithdrawalCompletionPromises`) will independently invoke the POA `waitForWithdrawalCompletion` with the *same* `assetId` criteria and get matched to the *same* record — typically the first one found — regardless of which withdrawal actually corresponds to which destination/amount: [3](#0-2) 

The code comment on `findMatchingWithdrawal` explicitly acknowledges the gap ("multiple withdrawals of the same token in a single transaction are not supported") but the SDK does not guard against or reject this case at the `validateWithdrawal`/`createWithdrawalIntents` level for POA bridge batches — it silently returns whatever the first matching record is.

### Impact Explanation
If an integrator processes a batch containing two withdrawals of the same asset (e.g. sending the same token to two different users, or splitting a large withdrawal across two destination addresses to avoid a limit), `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` can report the *same* destination tx hash and `COMPLETED` status for both withdrawal promises even though only one has actually settled on-chain. An integrator relying on this status to mark a withdrawal complete and release/credit downstream (e.g., mark an off-chain ledger entry paid, notify a user their funds arrived) could credit/confirm two distinct withdrawals based on one on-chain completion — a status misreport that can cause a double credit, matching the "status or hash misreport making an integrator credit or refund twice" High-severity class from the rules.

### Likelihood Explanation
This requires the caller to have batched more than one POA-bridge withdrawal of the *same* `assetId` within a single NEAR intent transaction, which the SDK's `createWithdrawalIntents`/`processWithdrawal` flows do not appear to explicitly block. This is a legitimate use pattern the SDK's own `createWithdrawalCompletionPromises` API is designed to support (multiple `withdrawalParams` against one `intentTx`), so the likelihood of triggering the bug through normal SDK usage (no malicious actor required) is credible, not purely theoretical.

### Recommendation
Extend `WithdrawalCriteria` (and `findMatchingWithdrawal`) to disambiguate between multiple withdrawals of the same asset within one `txHash` — e.g., matching by `amount` and `destinationAddress` in addition to `assetId`, or by a stable per-withdrawal index/id if the POA Bridge API exposes one — and fail closed (throw an invariant error) instead of returning the first match when ambiguity remains.

### Proof of Concept
1. Build an intent with two `ft_withdraw` primitives for the same `assetId` (e.g. `usdc.token.near`) to two different `destinationAddress`es, submit via `sdk.processWithdrawal`/`signAndSendWithdrawalIntent`.
2. Call `sdk.createWithdrawalCompletionPromises({ withdrawalParams: [wd1, wd2], intentTx })`.
3. Mock/observe the POA Bridge `getWithdrawalStatus` response containing two `withdrawals` entries with the same `near_token_id` but different `transfer_tx_hash`/destination.
4. `findMatchingWithdrawal` (called independently for `wd1` and `wd2`, both with identical `{assetId}` criteria) returns the same first-matching record for both promises, so both `waitForWithdrawalCompletion` calls resolve with the same `destinationTxHash`, even though only one of the two withdrawals corresponds to that hash — as already reflected in the module's own doc comment: [4](#0-3)

### Citations

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L50-84)
```typescript
	return retry(
		async () => {
			const result = await getWithdrawalStatus(
				{ withdrawal_hash: txHash },
				{ baseURL, fetchOptions: { signal }, logger },
			);

			const withdrawal = findMatchingWithdrawal(
				result.withdrawals,
				withdrawalCriteria,
			);
			if (withdrawal == null) {
				throw new PoaWithdrawalInvariantError(
					"POA Bridge didn't return withdrawal matching criteria",
					result,
					txHash,
					withdrawalCriteria,
				);
			}

			if (withdrawal.status === "COMPLETED") {
				if (withdrawal.data.transfer_tx_hash == null) {
					throw new PoaWithdrawalInvariantError(
						"POA Bridge didn't return transfer_tx_hash for COMPLETED withdrawal",
						result,
						txHash,
						withdrawalCriteria,
					);
				}

				return {
					destinationTxHash: withdrawal.data.transfer_tx_hash,
					chain: withdrawal.data.chain,
				};
			}
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-143)
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
