### Title
POA Bridge withdrawal status misattribution when a NEAR intent batches multiple withdrawals of the same asset - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain status of a specific withdrawal purely by matching `assetId` against the PoA indexer response, ignoring the withdrawal's `index`/amount. When a single NEAR intents transaction contains two or more `ft_withdraw` intents for the same PoA asset (a normal, unprivileged usage pattern supported by the SDK's batching API), all of those withdrawals resolve to the same matched record, so status and `txHash` from one withdrawal get reported for another.

### Finding Description
`createWithdrawalIdentifiers()` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` assigns each withdrawal in a batch a sequential `index` per bridge route [1](#0-0) , and `PoaBridge.createWithdrawalIdentifier()` stores that index in the resulting `WithdrawalIdentifier`, along with `landingChain` derived only from asset blockchain [2](#0-1) .

However, when `watchWithdrawal()` later polls `describeWithdrawal()` for each identifier [3](#0-2) , `PoaBridge.describeWithdrawal()` does **not** use `args.index` (or amount) to disambiguate — it calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does a `.find()` keyed only on `assetId`: [4](#0-3) [5](#0-4) 

The code comment itself acknowledges the gap: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." [6](#0-5) 

Because `.find()` always returns the first array element satisfying the predicate, every `WithdrawalIdentifier` for the same `assetId` (regardless of its distinct `index`, destination address, or amount) resolves to the identical indexer record. This breaks the equality that the status/hash reported for withdrawal N must correspond to the on-chain outcome for withdrawal N specifically — instead it reports the first matching record's outcome for all same-asset withdrawals in the batch.

### Impact Explanation
This is a status/hash misreport: if a batch contains two `ft_withdraw` intents of the same `nep141:*.omft.near` asset to two different destination addresses/amounts, both `watchWithdrawal()` calls converge on one PoA record. Consequences reachable by an ordinary integrator (no malicious actor needed):
- The second withdrawal is reported `"completed"` with the `txHash` that actually belongs to the first withdrawal (or vice versa depending on API ordering), causing an integrator that credits/marks-paid based on `describeWithdrawal`/`waitForWithdrawalCompletion` results to credit or refund the wrong withdrawal, or credit twice off a single real completion.
- Conversely, a withdrawal that has genuinely failed or is still pending could be reported `"completed"` because the matching one already completed, causing premature settlement/credit.

This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category since the impact is on funds-tracking logic downstream (SDK consumers commonly gate ledger updates on withdrawal completion status), not merely a display bug.

### Likelihood Explanation
Reachable via completely ordinary API usage: any integrator that calls the SDK's batch-withdrawal APIs (`createWithdrawalIntents`/`waitForWithdrawalCompletion`, batch `withdrawalParams` arrays) with two withdrawals of the same PoA asset in one transaction will hit this path. No adversarial input or privileged action is required — it is a straightforward correctness bug in matching logic, triggered by a supported feature (multiple withdrawal params per NEAR tx).

### Recommendation
Disambiguate `findMatchingWithdrawal` using more than `assetId` — e.g., match by `assetId` **and** amount (and consume matched entries so they cannot be reused for a subsequent `index`), or request that the PoA indexer API return a stable per-withdrawal correlation id/index that `describeWithdrawal` can match against `args.index`. At minimum, track already-consumed indexer records within a single poll cycle so two withdrawal identifiers never resolve to the same underlying record.

### Proof of Concept
1. Build a NEAR intents transaction with two `ft_withdraw` intents for `nep141:zec.omft.near`: withdrawal A (amount 100000, destination X) and withdrawal B (amount 200000, destination Y), submitted via `sdk.createWithdrawalIntents`/batch APIs.
2. `createWithdrawalIdentifiers` assigns `index: 0` to A and `index: 1` to B (both `landingChain` = zcash) [1](#0-0) .
3. Call `sdk.waitForWithdrawalCompletion` (or directly `bridge.describeWithdrawal`) for both identifiers.
4. Inside `describeWithdrawal`, `findMatchingWithdrawal(response.withdrawals, "nep141:zec.omft.near")` is invoked for both A and B; `.find()` returns the same first-matching element from `response.withdrawals` for both calls [7](#0-6) .
5. Both A and B report the same `status`/`txHash`, even though they are distinct on-chain withdrawals with different amounts and destinations — demonstrating the misreport.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-39)
```typescript
		return await poll(
			async () => {
				try {
					const status = await args.bridge.describeWithdrawal({
						...args.wid,
						logger: args.logger,
					});
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L88-104)
```typescript
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-311)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		const assetInfo = this.parseAssetId(args.withdrawalParams.assetId);
		assert(assetInfo != null, "Asset is not supported");

		const landingChain = assetInfo.blockchain;

		return {
			landingChain,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
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
