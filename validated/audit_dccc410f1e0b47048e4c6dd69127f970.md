### Title
`findMatchingWithdrawal` matches by token only, not index — duplicate-token withdrawals in one batch report each other's `txHash` - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves `WithdrawalStatus` for a `WithdrawalIdentifier` by calling `findMatchingWithdrawal`, which selects the first API-returned item whose `nep141:<near_token_id>` equals `args.withdrawalParams.assetId`, completely ignoring `WithdrawalIdentifier.index`. When a single NEAR intent batches two or more `WithdrawalParams` for the same POA-bridged token, every one of those withdrawals' `describeWithdrawal` calls hit the exact same `getWithdrawalStatus(tx.hash)` response and resolve to the same (first) matched item, so a still-pending withdrawal can be reported `completed` with another withdrawal's `txHash`.

### Finding Description
The claimed invariant is: `describeWithdrawal({index: i, ...}) → (status, txHash)` corresponds to the destination-chain transfer of the i-th `WithdrawalParams` actually signed by the user for that route. This equality is broken because `findMatchingWithdrawal` disambiguates only by asset: [1](#0-0) 

The docstring itself acknowledges the gap: *"multiple withdrawals of the same token in a single transaction are not supported"*, yet `createWithdrawalIdentifier` still assigns a per-route `index` that is never consulted here: [2](#0-1) 

`createWithdrawalIdentifiers` in `withdrawal-watcher.ts` assigns `index` purely per-route, and `watchWithdrawal` forwards `args.wid` (including `withdrawalParams.assetId` and shared `tx.hash`) straight into `bridge.describeWithdrawal` on every poll: [3](#0-2) [4](#0-3) 

**Exploit flow:** an ordinary user (or a counterparty whose withdrawal request an integrator forwards) submits a batch `withdrawalParams: [A, B]` where both `A.assetId` and `B.assetId` are the same POA NEP-141 token (e.g., splitting one token withdrawal into two different destination addresses/amounts). `sdk.signAndSendWithdrawalIntent` bundles both into one NEAR tx, so both `WithdrawalIdentifier`s share the same `tx.hash`. Once the POA relayer processes the first transfer (`A`) on the destination chain, the POA status API returns a `withdrawals` array containing at least the completed item for `A`. Polling `describeWithdrawal` for index 1 (`B`) calls `findMatchingWithdrawal(response.withdrawals, B.assetId)` — since `B.assetId === A.assetId`, `Array.find` returns the *same first matching item* (`A`'s completed record) for `B`'s identifier too. `watchWithdrawal` for index 1 therefore resolves `{ hash: A.transfer_tx_hash }` and reports `status: "completed"` for `B`, even though `B`'s actual destination transfer may still be pending or may land with a different real hash.

None of the existing guards catch this: `supports()`, `validateWithdrawal`, `compareAddresses`, and the "not-found for 3s → pending" retry logic in `getWithdrawalStatusWithRetry` (lines 345-372) all operate before or independently of this final match step, and none check `WithdrawalIdentifier.index` or verify that the returned `data.amount`/`destination_address` matches the specific `WithdrawalParams` being described.

### Impact Explanation
An integrator relying on `sdk.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` per-index results to trigger crediting, refunding, or ledger reconciliation will treat withdrawal `B` as settled using `A`'s `txHash`. If the integrator does not independently re-verify the on-chain transfer's amount/destination against `B`'s own parameters, it can credit or mark-as-paid for `B` while `B`'s funds have not actually arrived (or arrive later under a different hash), effectively causing a double-credit/double-refund situation for one real on-chain transfer reported against two logical withdrawals. This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category. The bug is deterministic and repeatable any time a batch contains ≥2 POA-bridge withdrawals of the same token.

### Likelihood Explanation
Preconditions are trivial and fully attacker/user-controlled: submit a batch of `WithdrawalParams` where two or more entries route through `PoaBridge` (`RouteEnum.PoaBridge`) and share the same `assetId`. No privileged access, no special timing, and no reliance on a malicious relayer/RPC is required — only ordinary use of the public batch-withdrawal API with normal funds. This is repeatable on every batch that includes duplicate-token POA withdrawals.

### Recommendation
In `findMatchingWithdrawal` (or `describeWithdrawal`), disambiguate matches within same-asset withdrawals using additional fields returned by the POA status API (e.g., `data.amount`, `data.recipient`/destination address, or ordering by amount as the existing comment suggests) and correlate consumed items so a single API record cannot be attributed to more than one `WithdrawalIdentifier.index` in the same poll cycle. At minimum, track already-claimed withdrawal records per `tx.hash` across concurrent `describeWithdrawal` calls so duplicate-token withdrawals cannot collide.

### Proof of Concept
Vitest plan (mock only the POA HTTP client):
1. Mock `poaBridge.httpClient.getWithdrawalStatus` to return two `withdrawals` items for the same `tx.hash`: item0 `{near_token_id: "X", status: "COMPLETED", data:{transfer_tx_hash:"HASH_A", amount:"100", ...}}` and item1 `{near_token_id: "X", status: "PENDING", data:{amount:"200", ...}}`.
2. Build two `WithdrawalIdentifier`s via `createWithdrawalIdentifier` with `index: 0` and `index: 1`, both using `assetId: "nep141:X"`, differing `amount`/`destinationAddress`, and the same `tx`.
3. Call `bridge.describeWithdrawal(wid0)` and `bridge.describeWithdrawal(wid1)`.
4. Assert the broken equality: both calls return `{status:"completed", txHash:"HASH_A"}` — i.e. `describeWithdrawal(wid1)` incorrectly equals `describeWithdrawal(wid0)`'s result instead of reflecting item1's real (pending) status.
5. Assert the expected (currently failing) invariant: `describeWithdrawal(wid1)` should report a status tied to the record whose `data.amount`/destination matches `wid1.withdrawalParams`, not `wid0`'s completed record.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-343)
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-53)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

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

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

					return POLL_PENDING;
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
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
	}

	return results;
}
```
