### Title
Wrong POA-bridge withdrawal status/tx-hash reported when a NEAR transaction batches multiple withdrawals of the same asset - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` matches the on-chain withdrawal record for a given `WithdrawalIdentifier` by `assetId` alone via `findMatchingWithdrawal`, ignoring the per-bridge `index` that `createWithdrawalIdentifiers` assigns to disambiguate multiple withdrawals of the same asset in one NEAR transaction. `Array.prototype.find` returns only the first record whose `near_token_id` matches, so when a single transaction contains two or more POA withdrawals of the same token (e.g., two different destination addresses/amounts), every one of those withdrawal identifiers resolves to the *same* underlying record.

### Finding Description
`createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`) assigns a per-route `index` (0, 1, 2 …) to each withdrawal in a batch so bridges can later look up the correct on-chain result for each leg. [1](#0-0) 

`PoaBridge.createWithdrawalIdentifier` stores that `index` in the identifier, but `describeWithdrawal` never uses it — it calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which matches purely on `assetId` (`nep141:${near_token_id}`): [2](#0-1) [3](#0-2) 

The same pattern exists in the lower-level helper `waitForWithdrawalCompletion`, whose `findMatchingWithdrawal` also matches solely by `assetId`: [4](#0-3) 

Both implementations are explicitly documented as only handling a single withdrawal per asset per transaction ("multiple withdrawals of the same token in a single transaction are not supported"), yet nothing in `createWithdrawalIntents`, `createWithdrawalIdentifiers`, or the public SDK surface prevents a caller from constructing a batch with two POA withdrawals of the same `assetId` but different `destinationAddress`/`amount` (this is exactly the scenario `RouteEnum.PoaBridge` batching supports for other asset combinations). When the underlying POA API returns multiple `COMPLETED`/`PENDING`/`FAILED` records for that asset in the transaction, `.find()` deterministically returns the first one for *every* index that shares the same `assetId`, so:
- withdrawal index 1's status/`txHash` will be reported using the record that actually belongs to withdrawal index 0 (or vice versa), and
- `watchWithdrawal` (via `withdrawal-watcher.ts`) will resolve the wrong leg as `completed` with the wrong `txHash`, or resolve as `failed`/`pending` incorrectly for a leg that actually succeeded/failed independently.

This breaks the equality "status/hash reported == actual on-chain outcome for that specific withdrawal", which is precisely the class of misreport the report class targets (report class analog to the referenced CVE's broken authorization/identity check — here the broken identity check is index vs. assetId matching).

### Impact Explanation
An integrator that credits or refunds a user based on the `txHash`/status returned by `describeWithdrawal` for each leg of a batched withdrawal could attribute the wrong destination transaction to the wrong leg. Concretely: if leg A (small amount, address X) is `PENDING`/`FAILED` and leg B (large amount, address Y) is `COMPLETED`, an integrator polling leg A's `WithdrawalIdentifier` could receive leg B's `COMPLETED` status and `txHash`, causing it to mark leg A as completed and release funds/credit twice (once incorrectly for A, once correctly for B) — a double-credit scenario. This matches the "High" impact bucket ("a status or hash misreport making an integrator credit or refund twice").

### Likelihood Explanation
This requires no privileged access and no malicious external actor: it triggers purely from a legitimate SDK caller submitting a batch of withdrawals where two or more legs route through `PoaBridge` for the same `assetId`. Nothing in `supports()`/`createWithdrawalIntents()` rejects this combination, so the vulnerable code path is reachable through normal SDK usage.

### Recommendation
Change `findMatchingWithdrawal` in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` to disambiguate same-asset withdrawals deterministically (e.g., sort both the API's `withdrawals` list and the locally tracked per-route index by amount/creation order, and match by position rather than by `assetId` alone), or reject/serialize batches containing multiple same-asset POA legs until the POA API itself exposes a stable per-leg identifier.

### Proof of Concept
1. Build a withdrawal batch with two `WithdrawalParams` entries for the same POA-bridge asset (e.g., `nep141:btc.omft.near`), different `destinationAddress`/`amount`.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` for these two entries (`packages/intents-sdk/src/core/withdrawal-watcher.ts:94-101`).
3. Submit the intent; the POA API returns two withdrawal records for `nep141:btc.omft.near` in that NEAR tx (one `COMPLETED` with `transfer_tx_hash: "tx-B"`, one `PENDING`).
4. Call `describeWithdrawal` for the `index: 0` identifier and for the `index: 1` identifier — both calls go through `findMatchingWithdrawal(response.withdrawals, "nep141:btc.omft.near")`, which returns the *same first match* for both, so both legs report identical status/`txHash` even though only one of them actually completed with that hash.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L84-103)
```typescript
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
