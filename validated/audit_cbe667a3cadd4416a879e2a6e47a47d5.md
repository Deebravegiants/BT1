### Title
POA Bridge `describeWithdrawal`/`waitForWithdrawalCompletion` mis-report withdrawal status/hash by matching only on `assetId`, letting one batched withdrawal's completion be misattributed to another - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
The reported OpenClaw bug class resolves a caller-supplied identifier to a canonical key *after* an authorization/visibility decision, so the check and the identity it protects can diverge. The closest reachable analog here is `findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (duplicated in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`): the caller supplies a `WithdrawalIdentifier` that includes a specific `index` (uniquely identifying one withdrawal within a batch NEAR transaction), but the function that reports its on-chain outcome ignores `index` and matches purely by `assetId`, silently returning the first withdrawal record with that asset from an "unsorted" API response.

### Finding Description
`PoaBridge.describeWithdrawal` is the equality boundary between "the withdrawal the SDK/integrator asked about" (identified by `tx.hash` + `index`, see `createWithdrawalIdentifier`, [1](#0-0) ) and "the withdrawal record the SDK reports status/hash for": [2](#0-1) 

The matching helper explicitly documents that it drops the disambiguating factor (`index`) and keys only on `assetId`: [3](#0-2) 

The equality that should hold is: *the txHash/status returned for withdrawal `(tx.hash, index)` corresponds to the on-chain outcome of that specific withdrawal*. Because the API's withdrawal list is unsorted and matching is done by `assetId` alone, two distinct withdrawals in the same batched NEAR transaction that transfer the **same asset** (e.g. two BTC withdrawals to two different destination addresses, submitted via `processWithdrawal`'s batch mode / `signAndSendWithdrawalIntent` array mode) will both resolve to whichever matching record `Array.prototype.find` returns first — regardless of which one it actually is. `describeWithdrawal({ ..., index: 0 })` and `describeWithdrawal({ ..., index: 1 })` can therefore return the exact same `{status: "completed", txHash: ...}` even though only one of the two withdrawals has actually settled to its destination, or the returned `txHash` belongs to the other withdrawal entirely.

The identical bug exists in the internal-utils helper used by lower-level completion waiting: [4](#0-3) 

This is consumed by `watchWithdrawal`/`waitForWithdrawalCompletion` in the orchestration layer, which trusts the returned `txHash` as authoritative proof of completion for the specific withdrawal it is polling for: [5](#0-4) 

Before/after comparison of the equality:
- Before attacker/legitimate multi-withdrawal input: single withdrawal per asset per tx → `find()` returns the unique match → status/hash correctly bound to that withdrawal.
- After: batch with ≥2 withdrawals of the same `assetId` in one NEAR tx → `find()` returns an arbitrary (first) match for *every* index sharing that asset → the reported `txHash`/`status` for index N is not guaranteed to be the on-chain outcome of index N's withdrawal.

### Impact Explanation
This falls under "a status or hash misreport making an integrator credit or refund twice." An integrator using `processWithdrawal`/`waitForWithdrawalCompletion` on a batch containing two same-asset withdrawals to different addresses can have the second withdrawal falsely marked `completed` with the first withdrawal's `destinationTxHash`, or vice versa — before the second withdrawal has actually landed on-chain. Since the SDK's own promise/polling API (`createWithdrawalCompletionPromises`, `watchWithdrawal`) treats this reported hash as ground truth for resolving that specific withdrawal's promise, downstream integrators can prematurely treat/settle a withdrawal as done, associate a legitimate destination transfer with the wrong logical withdrawal request, or in the reverse case leave a truly-completed withdrawal appearing stuck while an unrelated hash is attributed elsewhere. This satisfies the High-severity bar ("a status or hash misreport making an integrator credit or refund twice").

### Likelihood Explanation
Likelihood is moderate: it requires no malicious relayer/bridge/API behavior — a legitimate integrator batching two withdrawals of the same NEP-141 asset (e.g., two BTC withdrawals to two users in one call to `processWithdrawal`/`signAndSendWithdrawalIntent` with an array of `WithdrawalParams`) via the POA bridge route triggers it deterministically once both withdrawals are indexed by the POA API in the same response. The code's own comment ("Response list is unsorted, so we match by assetId instead of index" / "multiple withdrawals of the same token in a single transaction are not supported") confirms the authors are aware the mapping is not disambiguated, but the SDK does not block or warn callers from constructing such a batch — `createWithdrawalIdentifiers` in `withdrawal-watcher.ts` happily assigns distinct `index` values to same-asset, same-route withdrawals without any guard against this exact scenario.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId`: incorporate the withdrawal's destination address/amount (or, once the POA API supports it, deterministic ordering/pairing as the existing comment suggests — sort both API results and requested withdrawals by amount) so each `index` maps to a unique withdrawal record. Until the POA API can return an index-stable identifier, the SDK should detect and reject/flag batches containing multiple same-`assetId` POA withdrawals in a single transaction rather than silently returning an unverified match, in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`.

### Proof of Concept
1. Call `sdk.processWithdrawal` (or `signAndSendWithdrawalIntent` in batch mode) with `withdrawalParams: [{assetId: "nep141:btc.omft.near", destinationAddress: "addrA", amount: 100000n, ...}, {assetId: "nep141:btc.omft.near", destinationAddress: "addrB", amount: 50000n, ...}]` routed through `PoaBridge`.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` to the two withdrawals sharing `landingChain`/route (see `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`).
3. The POA API's `getWithdrawalStatus` for the shared NEAR tx hash eventually returns two `withdrawals[]` entries, both with `defuse_asset_identifier`/`near_token_id` resolving to `nep141:btc.omft.near`, in unspecified order — e.g. entry[0] with `transfer_tx_hash: "hash-for-addrB"` (COMPLETED) and entry[1] pending.
4. `bridge.describeWithdrawal({index:0, withdrawalParams:{assetId:"nep141:btc.omft.near", destinationAddress:"addrA", ...}, tx})` calls `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns `withdrawals.find(...)` → entry[0] (the one actually destined for `addrB`), returning `{status:"completed", txHash:"hash-for-addrB"}` for the withdrawal that was supposed to go to `addrA`.
5. `describeWithdrawal({index:1, ...})` performed independently reaches the exact same code path with the exact same `assetId`, and also matches entry[0] (or whichever the `.find()` locates first), so both index 0 and index 1 can report the same `txHash`/`completed` status even though only one of the two on-chain transfers has actually finalized — an unverified status/hash misreport as described above (existing repo test `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts:1054-1111` — "matches withdrawal by assetId, not by index" — demonstrates exactly this matching-by-assetId behavior, though it only shows the two-different-assets, single-batch case working correctly; the same-`assetId`-in-one-batch case is unhandled per the code's own documented limitation at lines 409-417).

### Citations

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-47)
```typescript
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
```
