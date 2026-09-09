### Title
POA Bridge withdrawal status matching ignores destination/amount, causing hash/status misattribution across withdrawals of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`findMatchingWithdrawal()` in the POA bridge integration matches a completed withdrawal record to a `WithdrawalIdentifier` using **only the token's `assetId`**, ignoring `index`, `destinationAddress`, and `amount`. When a single NEAR transaction contains more than one withdrawal of the same asset (e.g. two `ft_withdraw` intents of `usdc.omft.near` to two different recipients), the same first-matching record from the POA indexer is returned for every identifier that shares that `assetId`, so a caller polling completion for withdrawal #1 can receive the destination `txHash`/status that actually belongs to withdrawal #0 (or vice-versa).

### Finding Description
`describeWithdrawal()` calls: [1](#0-0) 

which delegates matching to: [2](#0-1) 

`findMatchingWithdrawal` performs `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)`, with no comparison against `destinationAddress`, `amount`, or the caller-supplied `index`. The identical bug exists in the duplicated implementation used by `waitForWithdrawalCompletion`: [3](#0-2) 

Both are explicitly acknowledged as limited to single-withdrawal-per-asset-per-tx in the code comments, but nothing in the calling code (`watchWithdrawal` in `withdrawal-watcher.ts`, or `createWithdrawalIdentifiers`) prevents multiple `WithdrawalIdentifier`s of the same `assetId` from being created and watched concurrently within one NEAR transaction: [4](#0-3) 

Because `.find()` always returns the same first record for any identifier sharing that `assetId`, two independent `watchWithdrawal()` calls (one per withdrawal index) can both resolve using the same underlying POA record, causing the identifier meant for destination B to be reported "completed" with the `txHash` and status that actually correspond to destination A's transfer.

### Impact Explanation
This breaks the equality "status/txHash reported for withdrawal identifier X" == "actual on-chain outcome for X's own destination/amount." An integrator that reconciles a withdrawal (marks it paid/credits a user/releases custody) using the `txHash` returned by `describeWithdrawal`/`waitForWithdrawalCompletion` can attribute the wrong destination's completion to the wrong withdrawal, matching the specified High-severity impact category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Requires only a normal (non-malicious) usage pattern: a single signed intent/transaction containing two or more `ft_withdraw` intents for the same token to different recipients — no privileged access or cooperation from the relayer/bridge operator is needed to trigger the mismatch. Likelihood of occurrence is moderate; it depends on user/integrator workflows that batch same-asset withdrawals in one transaction, a pattern the SDK does not prevent or warn against.

### Recommendation
Extend `findMatchingWithdrawal` (in both `poa-bridge.ts` and `waitForWithdrawalCompletion.ts`) to disambiguate by `destinationAddress` and `amount` (and consume matched records so they aren't reused for a second identifier), or reject/queue multiple same-asset withdrawals within one transaction until the POA API supports disambiguation, per the existing code comment's own suggestion.

### Proof of Concept
1. Sign one NEAR intent containing two `ft_withdraw` intents for `nep141:usdc.omft.near`: intent A → address `0xAAA...`, amount 100; intent B → address `0xBBB...`, amount 200.
2. `createWithdrawalIdentifiers` creates two `WithdrawalIdentifier`s (index 0 for A, index 1 for B) sharing the same `assetId`.
3. Call `watchWithdrawal` for both identifiers concurrently. Once the POA indexer reports both withdrawals, `findMatchingWithdrawal` for **both** identifiers returns the same first array element (say A's record with `transfer_tx_hash` for `0xAAA...`).
4. `describeWithdrawal` for identifier B (destined to `0xBBB...`) returns `{ status: "completed", txHash: <A's hash> }`, misreporting B's completion using A's transaction hash.

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
