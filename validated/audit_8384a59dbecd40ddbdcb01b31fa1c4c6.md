This confirms the finding. `describeWithdrawal` matches only by `assetId` via `findMatchingWithdrawal`, with the same `index` and `withdrawalParams` passed through but never consulted in the match. The code even documents this limitation explicitly at [1](#0-0) , and `.find()` returns the first array match for both index 0 and index 1 lookups [2](#0-1) . `watchWithdrawal` calls `describeWithdrawal` per `WithdrawalIdentifier` independently and reports whatever `status`/`txHash` comes back with no cross-check against other identifiers in the batch [3](#0-2) . `createWithdrawalIdentifiers` assigns sequential per-route indices (0, 1, ...) for withdrawals sharing the same bridge route, confirming two same-asset withdrawals get indices 0 and 1 under `PoaBridge` [4](#0-3) .

### Title
Duplicate-asset POA withdrawals resolve to the same on-chain tx hash, causing double-credit/refund - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` matches PoA bridge API withdrawal records solely by `nep141:{near_token_id} === assetId`, ignoring `index`, `amount`, and `destinationAddress`. When a single signed intent contains two withdrawals of the same PoA asset, both `watchWithdrawal` calls independently invoke `findMatchingWithdrawal` and both receive the first matching record's `status`/`txHash`, regardless of which withdrawal (0 or 1) actually produced that transaction.

### Finding Description
The claimed equality — `(status, txHash) reported for withdrawal i == outcome of withdrawal i` — is broken. `createWithdrawalIdentifiers` in [5](#0-4)  assigns per-route sequential indices, so two same-asset PoA withdrawals in one `MultiPayload` get `index: 0` and `index: 1` but identical `withdrawalParams.assetId`. In `describeWithdrawal` ( [6](#0-5) ), the only discriminator used against the API's `response.withdrawals` array is `assetId`, via `findMatchingWithdrawal` ( [2](#0-1) ), which is `Array.prototype.find` — always returning the first array element matching the assetId, irrespective of which `index` was requested. The `WithdrawalIdentifier.index` is never read anywhere in this function. When the PoA bridge API returns two `COMPLETED` records for the same `near_token_id` with distinct `transfer_tx_hash` values (one per real on-chain transfer, to different destination addresses), both `index:0` and `index:1` calls resolve to whichever record is first in the array — the same `status` and `txHash` for both. `watchWithdrawal` ( [7](#0-6) ) has no independent cross-check (no de-duplication of `txHash` across sibling identifiers, no comparison against `withdrawalParams.amount`/`destinationAddress`), so this misreport propagates directly to the caller/integrator. No existing guard (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()`, `assert` checks) touches this matching logic; the source code itself documents the limitation as a known gap ("multiple withdrawals of the same token in a single transaction are not supported") but the SDK does not reject or warn on this input — it silently returns incorrect status for one of the two withdrawals.

### Impact Explanation
An integrator relying on `sdk.createWithdrawalCompletionPromises` / `waitForWithdrawalCompletion` to confirm on-chain settlement per withdrawal will receive the identical `txHash` for both withdrawal 0 and withdrawal 1. If an integrator credits a user's off-chain ledger or releases held funds keyed on "withdrawal i completed with txHash X," it will do so for both withdrawals using the same on-chain transfer as proof — effectively crediting one destination address's withdrawal twice (once legitimately, once erroneously) while the actual second on-chain payment's real hash is silently dropped. This matches the Critical category: a status/hash misreport causing an integrator to double-credit, with real user/integrator funds affected. It is fully repeatable for any signer who submits two same-asset PoA withdrawals in a single `MultiPayload`.

### Likelihood Explanation
Preconditions are trivial for an ordinary NEAR Intents user: sign one `MultiPayload` intent containing two withdrawal primitives for the same `nep141:*.omft.near` asset to two different destination addresses, submit via any public SDK entrypoint that produces a `WithdrawalParams[]` array with duplicate PoA assets. No privileged access, no cooperation from the bridge/relayer beyond normal operation is needed — the PoA bridge processes both withdrawals normally and returns two independent records in `bridge_status`; the bug is purely in how the SDK client-side attributes those records back to identifiers. Attacker cost is one signed intent; the bug reproduces on every such duplicate-asset batch.

### Recommendation
In `findMatchingWithdrawal`, disambiguate matches using more than `assetId`: track already-consumed API records per `describeWithdrawal` batch call (e.g., pass all sibling `WithdrawalIdentifier`s together and match by sorting withdrawals and identifiers by `amount` as the code comment suggests, or by `destinationAddress`), and/or throw/mark as `unsupported` when multiple same-asset withdrawals are detected in one intent transaction rather than silently returning ambiguous results.

### Proof of Concept
Vitest test mocking `poaBridge.httpClient.getWithdrawalStatus` to return `{ withdrawals: [ {status:"COMPLETED", data:{near_token_id:"usdc.omft.near", transfer_tx_hash:"HASH_A"}}, {status:"COMPLETED", data:{near_token_id:"usdc.omft.near", transfer_tx_hash:"HASH_B"}} ] }`. Call `poaBridge.describeWithdrawal({index:0, withdrawalParams:{assetId:"nep141:usdc.omft.near", destinationAddress:"addrA", ...}, tx, landingChain})` and `describeWithdrawal({index:1, withdrawalParams:{assetId:"nep141:usdc.omft.near", destinationAddress:"addrB", ...}, tx, landingChain})`. Assert `result0.txHash === "HASH_A"` (correct) but observe `result1.txHash === "HASH_A"` too (bug), instead of the expected `"HASH_B"` — i.e. assert `result0.txHash !== result1.txHash` fails, demonstrating both indices report the same outcome.

### Citations

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
