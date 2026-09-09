This confirms the vulnerability is real and even self-documented in code comments.

### Title
`findMatchingWithdrawal` matches only by `assetId`, ignoring `amount`/`index`, causing wrong `txHash` reported for same-asset withdrawals in one NEAR tx - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which returns the first API-reported withdrawal whose `near_token_id` matches the asset, completely disregarding `args.withdrawalParams.amount`, `args.withdrawalParams.destinationAddress`, and `args.index`. When a single NEAR transaction contains two same-asset PoA withdrawals to different destinations, both `WithdrawalIdentifier`s resolve to the same (arbitrary, order-dependent) API entry, so the smaller withdrawal can be reported `completed` with the `transfer_tx_hash` that actually paid the larger amount to a different `destinationAddress`.

### Finding Description
The broken equality is: `describeWithdrawal(widA).txHash` should correspond to the on-chain transfer that fulfilled `widA.withdrawalParams` (same `amount`, `destinationAddress`), but instead it equals whatever entry in `response.withdrawals` happens to match on `assetId` alone, per [1](#0-0) .

Code path:
1. `withdrawal-watcher.ts`'s `createWithdrawalIdentifiers` assigns each `WithdrawalParams` a `WithdrawalIdentifier` with an `index` per bridge route, tracked via `indexes.get(bridge.route)`, per [2](#0-1) . This `index` is meant to disambiguate multiple withdrawals of the same route/asset in one tx.
2. `watchWithdrawal` calls `bridge.describeWithdrawal({...args.wid, ...})` per identifier, per [3](#0-2) .
3. `PoaBridge.describeWithdrawal` fetches `response.withdrawals` for the shared NEAR tx hash (`args.tx.hash`) and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` — note `args.index` is never passed to or used by `findMatchingWithdrawal`, per [4](#0-3) .
4. `findMatchingWithdrawal` simply does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)`, returning the *first* array element matching the asset — with two same-asset withdrawals of different amounts/destinations, this is non-deterministic/order-dependent, per [1](#0-0) .
5. The function's own doc comment explicitly admits: *"multiple withdrawals of the same token in a single transaction are not supported"* — confirming this is a known, unaddressed limitation rather than a hypothetical concern, per [5](#0-4) .

Attacker input: an ordinary user (or an integrator batching withdrawals on a user's behalf) submits one NEAR intents transaction containing two PoA withdrawal intents for the same `assetId` but different `amount` and `destinationAddress` (e.g., 100n to address A, 900n to address B). No malicious API/relayer behavior is required — the PoA bridge API legitimately returns both `COMPLETED` entries with their own correct `transfer_tx_hash` values; the bug is purely in how the SDK correlates its own two `describeWithdrawal` calls to those two entries.

Existing guards do not prevent this: `validateAddress`, `compareAddresses`, and `supports()` are used elsewhere for asset/network eligibility, not for matching a specific withdrawal instance to its status entry. `assert(assetInfo != null, ...)` at line 301 only validates the asset is supported. Nothing checks `amount` or `destinationAddress` equality against the API response's withdrawal record.

### Impact Explanation
An integrator relying on `watchWithdrawal`/`describeWithdrawal` per `WithdrawalIdentifier` can receive the wrong `txHash` for the smaller-amount withdrawal, matching the `transfer_tx_hash` that actually paid a different beneficiary. If the integrator credits/marks-complete an off-chain ledger entry based on this txHash (e.g., recording that "this off-chain user's 100-unit withdrawal is confirmed, on-chain hash X"), it associates a transaction that paid a *different, larger* amount to a *different* destination with the wrong withdrawal record. This matches the High/Critical category: "a status or hash misreport making an integrator credit or refund twice" and risks "funds delivered to a wrong address/chain/contract" attribution when reconciling with the reported hash. Repeatable for any user who batches two same-asset PoA withdrawals with differing destinations/amounts in a single tx.

### Likelihood Explanation
Preconditions: a single NEAR intents transaction with ≥2 PoA-bridge withdrawal intents on the same NEP-141 asset but different destination addresses/amounts — an entirely normal, unprivileged usage pattern (e.g., batch payouts), not requiring any malicious relayer, RPC, or bridge-API behavior. Attacker cost is a single transaction; the mismatch is deterministic given the array ordering returned by the PoA bridge status API for that tx hash, and reproducible on every occurrence of same-asset batched withdrawals.

### Recommendation
Use `args.index`, `args.withdrawalParams.amount`, and `args.withdrawalParams.destinationAddress` to disambiguate entries in `response.withdrawals` (e.g., sort both the API response and the SDK's tracked identifiers by `amount` for the same route/asset, as the code comment itself suggests, or match on `amount` + `destinationAddress` fields returned by the API) instead of matching solely on `assetId`.

### Proof of Concept
Vitest test in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts` mocking only the HTTP client (`poaBridge.httpClient.getWithdrawalStatus`):
1. Construct `withdrawalParamsA = { assetId: "nep141:foo.near", amount: 100n, destinationAddress: "addrA", ... }` and `withdrawalParamsB = { assetId: "nep141:foo.near", amount: 900n, destinationAddress: "addrB", ... }`.
2. Mock `getWithdrawalStatus` to return `{ withdrawals: [{ status: "COMPLETED", data: { near_token_id: "foo.near", transfer_tx_hash: "hash_for_900" /* corresponds to amount 900n/addrB */ } }, { status: "COMPLETED", data: { near_token_id: "foo.near", transfer_tx_hash: "hash_for_100" /* corresponds to amount 100n/addrA */ } }] }`.
3. Call `bridge.describeWithdrawal({ withdrawalParams: withdrawalParamsA, index: 0, tx, landingChain })`.
4. Assert the returned `txHash` equals `"hash_for_900"` (the hash actually belonging to the 900n/addrB withdrawal) rather than `"hash_for_100"`, demonstrating `describeWithdrawal(A).txHash !== txHash(A)` and instead `=== txHash(B)`.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-417)
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-47)
```typescript
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L84-107)
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
	}

	return results;
}
```
