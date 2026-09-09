### Title
`describeWithdrawal` misattributes `transfer_tx_hash` between same-`assetId` withdrawals in a batch - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`findMatchingWithdrawal` selects a withdrawal record purely by `nep141:{near_token_id} === assetId`, with no disambiguation by destination address, amount, or index. When a batch contains two withdrawals of the same asset (e.g., two BTC withdrawals to different destinations), `Array.prototype.find` returns the *first* matching element in the API response regardless of which `WithdrawalIdentifier.index` requested it, so both indices can resolve to the same (arbitrary) record.

### Finding Description
The broken equality is: `describeWithdrawal(wid_i).txHash` should equal `on-chain outcome of withdrawal i`, for every `i`. Instead, both `describeWithdrawal(wid_0)` and `describeWithdrawal(wid_1)` call `getWithdrawalStatusWithRetry` with the same `tx.hash` (since both withdrawals belong to the same `signAndSendWithdrawalIntent` NEAR transaction) [1](#0-0) , and `findMatchingWithdrawal` matches on `assetId` alone [2](#0-1) . If the response contains two entries with the same `near_token_id`, `Array.prototype.find` deterministically returns the same first match for both calls — meaning both `wid_0` and `wid_1` resolve to the identical `withdrawal.data.transfer_tx_hash`, rather than each index resolving to its own destination's hash.

This is explicitly acknowledged as a known limitation in the code comment: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [3](#0-2) . The same limitation and comment exist in the sibling implementation `findMatchingWithdrawal` in `waitForWithdrawalCompletion.ts` [4](#0-3) .

No existing guard prevents this: `validateWithdrawal`, `compareAddresses`, and `supports()` only validate individual withdrawal parameters at submission time and never cross-check batch uniqueness [5](#0-4) ; `createWithdrawalCompletionPromises` in `sdk.ts` builds one `WithdrawalIdentifier` per index and polls each independently via `watchWithdrawal`, with no cross-check that returned hashes are distinct per index [6](#0-5) .

Attacker input: an ordinary NEAR Intents user calls `signAndSendWithdrawalIntent`/`createWithdrawalCompletionPromises` with two `WithdrawalParams` for the same `assetId` (e.g., BTC) but different `destinationAddress` values, within a single batch/transaction. The attacker (the user itself, or any integrator who lets a user submit a multi-withdrawal batch) controls this input entirely — no bridge/relayer misbehavior is required for the effect to occur; it's a deterministic function of the SDK's own matching logic once the POA bridge API returns two records for the shared `withdrawal_hash`.

### Impact Explanation
An integrator that calls `describeWithdrawal`/`watchWithdrawal` for each index and credits/marks-complete based on the reported `(status, txHash)` can attribute withdrawal `j`'s `transfer_tx_hash` to withdrawal `i`, or report both indices as completed with the same hash while the actual per-destination completion state differs. This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category: no funds are moved incorrectly by the bridge itself, but the SDK's completion signal to the integrator is wrong, potentially causing double-crediting of one destination and indefinite "stuck" reporting for the other.

### Likelihood Explanation
Preconditions: an attacker (or an integrator on the user's behalf) must submit ≥2 withdrawals of the identical `assetId` within one batch to `PoaBridge` — no privileged access needed, and no dependence on price, chain state, or bridge relayer misbehavior. Whether this is triggered depends on the actual behavior of the POA bridge API for a NEAR tx that contains two same-asset withdrawal intents (does it actually return two distinct entries, and in what order relative to intent order?) — this is server-side behavior in `poaBridge.httpClient.getWithdrawalStatus` that isn't verifiable from the SDK repo alone. Assuming the API does return unsorted multiple entries (as the code comment states as the reason for the matching-by-assetId design), the bug is deterministic and repeatable every time a same-asset multi-withdrawal batch is watched.

### Recommendation
Disambiguate withdrawals within the same `assetId` group by also matching on `destination address`/`amount`, or reject/serialize batches containing duplicate `assetId` withdrawals until the POA API supports index-based or richer identification, as the code's own docstring suggests (sort both sides by amount, matching by relative order).

### Proof of Concept
```ts
// vitest, mocking only poaBridge.httpClient.getWithdrawalStatus
it("misattributes transfer_tx_hash between two same-asset withdrawals in a batch", async () => {
  const sharedTxHash = "near-tx-hash";
  const assetId = "nep141:btc.omft.near";

  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "btc.omft.near", transfer_tx_hash: "HASH_FOR_DEST_A", /* ... */ } },
      { status: "COMPLETED", data: { near_token_id: "btc.omft.near", transfer_tx_hash: "HASH_FOR_DEST_B", /* ... */ } },
    ],
  });

  const wid0 = bridge.createWithdrawalIdentifier({ withdrawalParams: { assetId, destinationAddress: "A", amount: 1n }, index: 0, tx: { hash: sharedTxHash } });
  const wid1 = bridge.createWithdrawalIdentifier({ withdrawalParams: { assetId, destinationAddress: "B", amount: 2n }, index: 1, tx: { hash: sharedTxHash } });

  const result0 = await bridge.describeWithdrawal(wid0);
  const result1 = await bridge.describeWithdrawal(wid1);

  // Broken equality: both resolve to the SAME (first) record instead of their own destination's hash.
  expect(result0.txHash).toBe("HASH_FOR_DEST_A"); // passes
  expect(result1.txHash).toBe("HASH_FOR_DEST_A"); // FAILS expectation of "HASH_FOR_DEST_B" — demonstrates misattribution
});
```

### Citations

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-152)
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
