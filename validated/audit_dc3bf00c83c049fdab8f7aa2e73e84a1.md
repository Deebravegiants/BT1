### Title
PoaBridge misreports withdrawal status/txHash when a batch contains multiple withdrawals of the same asset — (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves a specific withdrawal's on-chain outcome by matching the bridge API's withdrawal list using only the token `assetId`, ignoring the per-withdrawal `index` that was supposed to disambiguate multiple withdrawals within the same NEAR transaction. When a single signed intent contains two or more POA-bridge withdrawals of the same asset, every `WithdrawalIdentifier` for that asset resolves to the same matched record, so the SDK reports the identical `status`/`txHash` for withdrawals that are actually distinct on-chain transfers.

### Finding Description
`createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` assigns each withdrawal a per-bridge `index` intended to keep withdrawals belonging to the same NEAR transaction distinguishable: [1](#0-0) 

`PoaBridge.createWithdrawalIdentifier` stores that `index` in the resulting `WithdrawalIdentifier`: [2](#0-1) 

However `describeWithdrawal` never uses `index` to disambiguate; it fetches the withdrawal list for the NEAR tx hash and hands off matching to `findMatchingWithdrawal`, which is keyed purely on `assetId`: [3](#0-2) [4](#0-3) 

`Array.prototype.find` returns the first element whose `near_token_id` maps to the requested `assetId`. Because `assetId` alone is not a unique identifier when a NEAR transaction contains more than one POA-bridge withdrawal of the same token, both `WithdrawalIdentifier`s (`index: 0` and `index: 1`, same `tx.hash`, same `assetId`) collide on the exact same matched API record. The code even documents this as a known limitation but ships it as the production matching strategy rather than gating on it: [5](#0-4) 

This is the same bug class as the mistune advisory: an identifier (`toc_N` there, "the withdrawal matched for this assetId" here) is derived from a coarse, non-unique key rather than from the specific entity it is meant to identify, so two distinct entities collapse onto one identity and callers relying on that identity get the wrong one.

### Impact Explanation
`watchWithdrawal` (packages/intents-sdk/src/core/withdrawal-watcher.ts) is polled independently for each `WithdrawalIdentifier` returned from `createWithdrawalIdentifiers`, and its result (`{ status: "completed", txHash }`) is what integrators use to confirm a withdrawal completed and to credit/refund users. If a user submits an intent with two POA-bridge withdrawals of the same asset (e.g. two withdrawals of `usdc.omft.near` to two different destination addresses in one signed transaction), both `describeWithdrawal` calls will match the same API record and report the same `completed` status with the same destination `txHash` for both withdrawals — even though only one real transfer occurred (or the two transfers went to different addresses on-chain). An integrator that treats a reported `txHash` as proof-of-delivery for a given withdrawal could credit/refund the second withdrawal using the first withdrawal's transfer receipt, i.e., a status/hash misreport enabling double credit — the exact "status reported that is not the on-chain outcome" case called out as in-scope.

### Likelihood Explanation
No privileged actor is required — any user (or integrator building a batch withdrawal) who withdraws the same asset twice in a single intent transaction via the POA bridge route triggers this. Multi-withdrawal batches of the same token are a normal usage pattern (e.g., splitting a payout to two addresses), not an exotic edge case, and the code path is reached purely through standard SDK usage of `sdk.signAndSendWithdrawalIntent` / multi-withdrawal builders feeding into `createWithdrawalIdentifiers` → `PoaBridge.describeWithdrawal`.

### Recommendation
Disambiguate withdrawals within the same NEAR tx using more than `assetId`: match on `(assetId, destinationAddress, amount)` or, if the POA bridge API preserves per-call ordering/`nonce`/creation-order fields, incorporate the `index` into the match (e.g., filter by `assetId` then select the Nth remaining unmatched entry consistent with the order withdrawals were included in the transaction, mirroring the ordering approach already suggested in the code's own comment). At minimum, when multiple withdrawals share the same `assetId` in one transaction, either refuse to report `completed` until the match is provably unique (fall back to `pending`) or surface an explicit error so integrators don't silently double-credit.

### Proof of Concept
1. Build an intent with two `ft_withdraw` POA-bridge withdrawals of the same asset (e.g. `usdc.omft.near`) to two different destination addresses, both submitted in a single signed NEAR transaction.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` to the two `WithdrawalIdentifier`s for the POA bridge route (`packages/intents-sdk/src/core/withdrawal-watcher.ts:94-101`).
3. Call `watchWithdrawal` for both identifiers concurrently. Each calls `PoaBridge.describeWithdrawal`, which fetches `getWithdrawalStatus({ withdrawal_hash: tx.hash })` and runs `findMatchingWithdrawal(response.withdrawals, assetId)` (`poa-bridge.ts:313-343, 409-427`).
4. Because both calls use the same `tx.hash` and the same `assetId`, `Array.prototype.find` returns the same withdrawal record for both `index: 0` and `index: 1`.
5. Both `watchWithdrawal` calls resolve to `{ hash: <same txHash> }`, even though two separate destination-chain transfers occurred — demonstrating the status/hash misreport.

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
