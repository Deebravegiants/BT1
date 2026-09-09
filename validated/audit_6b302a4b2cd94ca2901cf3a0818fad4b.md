## Title
Batch withdrawals of the same token are mismatched to the wrong index, causing a completed withdrawal's status/hash to be misreported for a still-pending withdrawal - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` and the analogous `waitForWithdrawalCompletion` helper in `internal-utils` resolve the status of a specific withdrawal leg by matching **only on `assetId`**, ignoring the caller-supplied `index`/destination. When a single intent contains two or more withdrawals of the same token (a legitimate batch-withdrawal use case the SDK explicitly documents and supports via `createWithdrawalIdentifiers`), the first matching entry in the bridge API's response is returned for *every* leg that shares that `assetId`, regardless of which physical withdrawal actually completed.

### Finding Description
`findMatchingWithdrawal` in `poa-bridge.ts` only checks `` `nep141:${w.data.near_token_id}` === assetId ``: [1](#0-0) 

`describeWithdrawal` uses this to resolve status/tx hash for a `WithdrawalIdentifier` that includes an `index`, but the `index` is never used to disambiguate: [2](#0-1) 

The same limitation exists in `internal-utils`'s `waitForWithdrawalCompletion`, whose `findMatchingWithdrawal` also matches by `assetId` alone: [3](#0-2) 

The code even contains an explicit comment acknowledging the gap:
> "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."

However, batch withdrawals of the *same* token are a real, reachable path: `createWithdrawalIdentifiers` assigns per-route `index` values expecting to disambiguate multiple withdrawal legs, and nothing in `WithdrawalParams`/`sdk.ts` prevents a caller from submitting two withdrawal legs with the same `assetId` but different `destinationAddress` (e.g., splitting a payout of the same token to two different recipients in one intent): [4](#0-3) 

When the POA bridge API returns multiple withdrawal records for the same `near_token_id` (one `COMPLETED` with `transfer_tx_hash: "hashA"`, one still `PENDING`), `findMatchingWithdrawal` will deterministically return the *first* array element for **both** logical withdrawal indices. Consequently:
- Index 0 (destination A, actually completed) correctly reports `{status: "completed", txHash: "hashA"}`.
- Index 1 (destination B, still pending on-chain) **also** reports `{status: "completed", txHash: "hashA"}`, because the matcher can't tell the two apart.

This breaks the equality "status/hash reported == actual on-chain outcome for that specific withdrawal index." An integrator relying on `watchWithdrawal`/`waitForWithdrawalCompletion` to gate payout confirmation, refunds, or ledger reconciliation would treat both legs as settled with the same (wrong) destination transaction hash, when in fact only one leg landed.

### Impact Explanation
This matches the "High" category: "a status or hash misreport making an integrator credit or refund twice." An integrator processing a batch withdrawal (e.g., a service that splits a large withdrawal of the same token to two addresses, or refunds using the same token in one intent) can be told the second leg is `completed` with a transaction hash that actually belongs to the first leg. Downstream systems that mark an order/payout as done based on this false completion signal can under-deliver or double-account funds without any additional relayer/admin misbehavior — it's a direct SDK response integrity defect, not a trust-assumption issue with the POA bridge itself (the POA bridge correctly reports two separate records; the SDK loses the ability to tell them apart).

### Likelihood Explanation
Likelihood is limited by how often callers submit batch withdrawals containing two-or-more legs with the *same* `assetId` (as opposed to different assets, which the RFC's own examples show, e.g. "USDC to Solana + BTC refund to Bitcoin"). This is an edge case, but it is a fully caller-controlled, unprivileged input — no malicious relayer, bridge operator, or attacker required. It's explicitly a known, acknowledged gap in the code, so it's realistic rather than purely theoretical, and it silently produces an incorrect answer instead of failing loudly.

### Recommendation
Disambiguate withdrawals of the same `assetId` by additional criteria available in both the request and the bridge API response — e.g., `destinationAddress`/`address`, `amount`, or ordinal position when the API guarantees a stable submission order — before falling back to "first match". At minimum, when more than one record matches the same `assetId`, the SDK should refuse to resolve (throw/`pending`) rather than picking an arbitrary one, so integrators aren't given a false "completed" signal for the wrong leg. Track this in `poa-bridge.ts`'s `findMatchingWithdrawal` and `internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`'s `findMatchingWithdrawal`.

### Proof of Concept
1. Submit one NEAR intent containing two `ft_withdraw` legs for `nep141:usdc.omft.near`: leg 0 → `destinationAddress = "0xAAA..."`, leg 1 → `destinationAddress = "0xBBB..."`.
2. Call `sdk.createWithdrawalCompletionPromises` (or `watchWithdrawal` directly) for both legs; each gets a `WithdrawalIdentifier` with `index: 0` and `index: 1` respectively per `createWithdrawalIdentifiers`.
3. Suppose the POA bridge processes leg 0 first and it completes (`status: COMPLETED, transfer_tx_hash: "hashA"`), while leg 1 is still `PENDING`.
4. `poaBridge.httpClient.getWithdrawalStatus` returns both records tagged with the same `near_token_id: "usdc.omft.near"`.
5. `PoaBridge.describeWithdrawal({ index: 1, withdrawalParams: { assetId: "nep141:usdc.omft.near", ... } })` calls `findMatchingWithdrawal(withdrawals, "nep141:usdc.omft.near")`, which returns the *first* array entry — the `COMPLETED` one for leg 0 — even though it was invoked for `index: 1`.
6. `watchWithdrawal` resolves the promise for leg 1 with `{ hash: "hashA" }`, falsely reporting leg 1 (destination `0xBBB...`) as completed with a transaction hash that actually paid `0xAAA...`. [2](#0-1) [1](#0-0) [4](#0-3)

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
