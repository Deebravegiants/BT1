### Title
Withdrawal status/destination-hash misattribution across same-asset withdrawals in a single batch - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain completion status/hash of a withdrawal by matching PoA API results using `assetId` alone, ignoring the `index` that uniquely identifies each withdrawal within a batch NEAR transaction. When multiple withdrawals of the same asset are created in a single transaction, this can report the destination tx hash of one withdrawal as belonging to another.

### Finding Description
The `IntentsSDK.estimateWithdrawalFee`/`createWithdrawalIntents` APIs accept an array of `withdrawalParams` and assign each an `index` via `createWithdrawalIdentifier` [1](#0-0) . Each withdrawal identifier records `landingChain`, `index`, `withdrawalParams`, and `tx` (the shared NEAR transaction) as defined in `WithdrawalIdentifier` [2](#0-1) .

When resolving the final status, `describeWithdrawal()` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which selects the first PoA API record whose `near_token_id` matches the asset — it never uses `args.index` or any other value that would disambiguate multiple withdrawals of the same token within the same `tx.hash`: [3](#0-2) [4](#0-3) 

The equality this breaks is: *the withdrawal status/hash reported for `index=i` must be the on-chain outcome of withdrawal `i`* — not of any other same-asset withdrawal in the batch. If a caller creates two (or more) withdrawals of the same `assetId` in one transaction (e.g., splitting a large payout to two different destination addresses/amounts, which the array-based `withdrawalParams` API explicitly supports per `sdk.estimateWithdrawalFee.test.ts` "handles mixed success/failure in array withdrawals" tests), `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` will both resolve to the *same* matched PoA record (the first one found), because the lookup only keys on `assetId`. The exact same limitation and matching logic (also missing index) exists in the parallel `waitForWithdrawalCompletion` helper used elsewhere in the internal-utils package: [5](#0-4) .

The code itself acknowledges this as a known limitation in a comment, but does not mitigate it with a guard/assertion that would surface the ambiguity as an error rather than silently returning a matched-but-wrong record: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." [6](#0-5) 

### Impact Explanation
This falls under the High-impact category "a status or hash misreport making an integrator credit or refund twice." An integrator relying on `describeWithdrawal()` per-index to confirm which destination transaction corresponds to which withdrawal request could:
- credit/refund the wrong withdrawal as "completed" while the intended one is still pending or failed,
- report a `txHash` belonging to a different withdrawal (potentially to a different destination address) as proof of completion for a request it does not correspond to,
which can lead to double-crediting a user or wrongly closing out a withdrawal that never landed.

### Likelihood Explanation
This requires no malicious/privileged actor — it triggers whenever an ordinary user (or an integrator building batched payouts) submits ≥2 withdrawals of the same PoA-bridged asset (e.g., same `nep141:x.omft.near` token) within a single transaction via the array form of `withdrawalParams`. This is a supported SDK usage pattern (batch withdrawals array is a first-class input to `estimateWithdrawalFee`/`createWithdrawalIntents`), so the precondition is easily reached without any adversarial behavior, in contrast to the "reject" criteria the prompt excludes (this is not a DoS, RPC/relayer trust issue, or attacker-only-losing-own-funds scenario).

### Recommendation
`findMatchingWithdrawal` should disambiguate matches when multiple PoA withdrawals share the same `near_token_id` within a single `tx_hash`. Since the PoA API doesn't expose an explicit per-intent index, at minimum:
- Detect the ambiguous case (more than one PoA record matches the same `assetId` for the same `tx_hash`) and throw an explicit error instead of silently returning the first match, or
- Implement the amount/ordering-based disambiguation strategy already hinted at in the code comment (sort matched PoA records and requested `withdrawalParams` of the same asset by `amount`, matching by relative rank), so that `describeWithdrawal(index=i)` deterministically corresponds to the correct on-chain result.
Apply the same fix to `waitForWithdrawalCompletion` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`.

### Proof of Concept
1. Build withdrawal intents for two withdrawals of `nep141:usdt.tether-token.near` in one call: `withdrawalParams: [{assetId, amount: 100, destinationAddress: addrA, ...}, {assetId, amount: 200, destinationAddress: addrB, ...}]`, producing `WithdrawalIdentifier` objects with `index: 0` and `index: 1` but the same `tx.hash`.
2. After the batch NEAR tx executes, PoA bridge's `getWithdrawalStatus({withdrawal_hash: tx.hash})` returns two `COMPLETED` records, one for `addrA`→`hashA` and one for `addrB`→`hashB`, both with `near_token_id: "usdt.tether-token.near"`.
3. Call `bridge.describeWithdrawal({index: 0, tx, withdrawalParams: {assetId, amount:100, destinationAddress: addrA}})` and `bridge.describeWithdrawal({index: 1, tx, withdrawalParams: {assetId, amount:200, destinationAddress: addrB}})`.
4. `findMatchingWithdrawal` (matching only by `assetId`) returns the *same first-found record* (`hashA`) for both calls, per `Array.prototype.find` semantics in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:426`, causing the withdrawal to `addrB` to be reported as completed with `hashA` — a hash belonging to a different destination/withdrawal.

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

**File:** packages/intents-sdk/src/shared-types.ts (L434-441)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
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
