### Title
Multiple same-asset withdrawals in one intent tx can be cross-matched, causing status/hash misreport - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the status of a specific withdrawal by matching the POA bridge API response against `args.withdrawalParams.assetId` only, ignoring the `index` that uniquely identifies which withdrawal within a batched intent transaction the caller is asking about. When an intent transaction contains more than one withdrawal of the same asset (e.g., two withdrawals of the same NEP-141 token to different destination addresses/amounts in one `update`/intent submission), `findMatchingWithdrawal` cannot distinguish between them and will attribute the wrong (or same) API entry to both withdrawal identifiers.

### Finding Description
`createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` assigns each withdrawal an `index` per bridge route (`indexes.get(bridge.route) ?? 0`), and `PoaBridge.createWithdrawalIdentifier` stores that `index` on the returned `WithdrawalIdentifier`: [1](#0-0) [2](#0-1) 

However, `describeWithdrawal` never uses `args.index` to disambiguate; it calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which simply returns the first entry in the (explicitly unsorted) API response whose `near_token_id` matches the asset: [3](#0-2) [4](#0-3) 

The code comment on `findMatchingWithdrawal` explicitly acknowledges: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." This is exactly the same root-cause shape as the analog report: two independent "positions" (here, two withdrawal legs of the same intent) are supposed to be tracked/settled independently by identity, but the code collapses them onto a single lookup key, so the wrong on-chain outcome (status/hash) can be reported for a given identifier — breaking the equality "status reported for withdrawal X == the actual on-chain outcome for withdrawal X".

### Impact Explanation
If a caller submits an intent with two (or more) withdrawals of the same asset to different destination addresses (a legitimate batching pattern supported by `WithdrawalParams[]` throughout `sdk.ts` / `withdrawal-watcher.ts`), `watchWithdrawal`/`describeWithdrawal` for each of those withdrawal identifiers can resolve to the same or a swapped API entry. This can make the SDK/integrator report withdrawal A as `"completed"` with a `txHash` that actually corresponds to withdrawal B's transfer (or report both as completed off a single API entry). An integrator that finalizes internal ledger/credit for a withdrawal based on this SDK-reported completion status could credit the wrong destination as settled and/or double-credit one leg while leaving the other unresolved — matching the "status or hash misreport making an integrator credit or refund twice" High-severity impact category.

### Likelihood Explanation
This requires only an ordinary (non-privileged) user action: submitting one intent transaction containing two withdrawal legs of the same NEP-141 asset, e.g. to two different destination addresses. Nothing prevents `WithdrawalParams[]` from containing duplicate `assetId`s, and the code path is on by default for the PoA bridge route — no attacker capability beyond normal SDK usage is needed. The bug is explicitly acknowledged as a known gap in the code comment rather than a merely theoretical edge case, though it may occur infrequently in practice since it only manifests for multi-withdrawal batches of the identical token.

### Recommendation
Do not rely solely on `assetId` for matching. Either:
1. Extend the POA bridge status API usage to match by a unique per-withdrawal key (e.g., pair `assetId` with `destinationAddress` and `amount`, or an index/nonce returned by the bridge), rejecting ambiguous matches instead of silently picking the first one; or
2. If the POA API truly cannot disambiguate multiple same-asset withdrawals in one tx, `describeWithdrawal`/`createWithdrawalIdentifier` should detect this ambiguity (more than one param with same assetId in the batch) and explicitly fail closed (throw an unsupported-batch error) rather than silently returning a potentially mismatched status, so integrators are never given a false completion signal.

### Proof of Concept
1. User submits one NEAR intent transaction containing `withdrawalParams = [{assetId: "nep141:zec.omft.near", destinationAddress: A, amount: 100}, {assetId: "nep141:zec.omft.near", destinationAddress: B, amount: 50}]` via the SDK, both routed to `PoaBridge`.
2. `createWithdrawalIdentifiers` produces two `WithdrawalIdentifier`s with `index: 0` and `index: 1`, both for the same `assetId`.
3. `PoaBridge.describeWithdrawal` is called for each identifier; both calls invoke `findMatchingWithdrawal(response.withdrawals, "nep141:zec.omft.near")`, which returns the same first-matching entry (say, the one corresponding to destination A's completed transfer) for both `index: 0` and `index: 1` lookups.
4. Both `watchWithdrawal` calls (`packages/intents-sdk/src/core/withdrawal-watcher.ts:36-47`) resolve to `{ status: "completed", txHash: <A's tx hash> }`, even though withdrawal to B has not actually completed (or completed with a different hash) — an integrator polling per-identifier status is told both legs succeeded with the same hash, which can drive incorrect double-crediting/refund logic downstream.

### Citations

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
