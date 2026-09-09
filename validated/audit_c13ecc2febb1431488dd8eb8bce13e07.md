### Title
POA Bridge `describeWithdrawal` matches by `assetId` only, causing status/hash misreport for batched same-token withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
The SDK's `IntentsSDK` supports batch withdrawals (multiple `WithdrawalParams` settled in a single NEAR intent transaction) and tracks each withdrawal individually via `createWithdrawalIdentifiers`/`watchWithdrawal`, which assigns each withdrawal a distinct `index` [1](#0-0) . For the POA Bridge, however, `describeWithdrawal` deliberately ignores that `index` and instead resolves the withdrawal status purely by matching `assetId` against the POA API response, per the comment in `findMatchingWithdrawal` [2](#0-1) .

### Finding Description
`PoaBridge.describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which returns `withdrawals.find((w) => "nep141:${w.data.near_token_id}" === assetId)` [3](#0-2) . This function returns the **first** withdrawal in the API response whose token matches, with no use of `index`, `amount`, or `destinationAddress` to disambiguate. The code comment explicitly acknowledges: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [4](#0-3) .

Despite this known limitation, the SDK's public API explicitly advertises "Batch Processing: Process multiple withdrawals at a time" for withdrawals [5](#0-4) , and the generic withdrawal-identifier creation logic (`createWithdrawalIdentifiers`) supports multiple withdrawals routed to the same bridge, assigning them separate per-bridge indices [1](#0-0) . Nothing in the SDK prevents a caller from submitting two POA-bridge withdrawals of the same token (e.g., same `nep141:btc.omft.near`) to two different destination addresses within one settlement. When `watchWithdrawal` is invoked for withdrawal index 0 and index 1, both calls to `PoaBridge.describeWithdrawal` will call the same `findMatchingWithdrawal` and return the identical first-matching record — the equality that breaks is: "the destination tx hash / completion status reported for withdrawal #2 is not the on-chain outcome of withdrawal #2, but rather that of withdrawal #1."

### Impact Explanation
This breaks the reported-status-equals-actual-outcome invariant. If an integrator (or the SDK's own `waitForWithdrawalCompletion`) uses `describeWithdrawal`'s returned `txHash`/`status: "completed"` to decide when a specific withdrawal has landed and to release/credit downstream funds or mark idempotent completion, a batch of two same-token POA withdrawals would cause the second withdrawal to be reported "completed" with the transaction hash belonging to the first withdrawal (or vice versa depending on API ordering, which is explicitly documented as unsorted: "Response list is unsorted, so we match by assetId instead of index"). This is a status/hash misreport that can make an integrator believe a withdrawal completed (and with which destination chain tx) when it actually reflects a different withdrawal's outcome — matching the rule's High-impact category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Likelihood is dependent on an ordinary/unprivileged user submitting two withdrawals of the same POA-bridged asset in a single batch — a use case explicitly supported and advertised by the SDK (batch withdrawals) and not blocked by any validation in `createWithdrawalIntents`, `estimateWithdrawalFee`, or `supports()` for the POA bridge. No malicious actor or privileged party is required — a normal caller triggers this by legitimate use of the documented batch-withdrawal feature. The devs' own comment shows they were aware of the gap but the SDK does not guard against triggering it (e.g., no validation rejecting duplicate-asset batches to the POA route).

### Recommendation
- Reject (or explicitly warn/throw) at `createWithdrawalIntents`/`processWithdrawal` time when multiple withdrawals in the same batch route to the POA bridge with the same `assetId`, until the POA API/matching logic can disambiguate them.
- Alternatively, disambiguate `findMatchingWithdrawal` using additional fields returned by the POA API (e.g., `amount`, `address`) matched against `withdrawalParams.amount`/`destinationAddress`, in addition to `assetId`, to avoid returning the wrong withdrawal record for a given index.
- Surface an explicit unsupported/ambiguous-status result (rather than a possibly-wrong "completed" + wrong `txHash`) whenever multiple same-asset withdrawals cannot be safely disambiguated.

### Proof of Concept
1. Caller submits one intent transaction containing two POA-bridge NEP-141 withdrawals of `nep141:btc.omft.near`: withdrawal A to `destinationAddress = X` and withdrawal B to `destinationAddress = Y`.
2. `createWithdrawalIdentifiers` assigns index 0 to A and index 1 to B for the `PoaBridge` route [1](#0-0) .
3. Both withdrawals settle on POA and the bridge's `getWithdrawalStatus` API returns an unsorted list containing both completed records (one to X, one to Y).
4. `watchWithdrawal` calls `PoaBridge.describeWithdrawal` for index 0 and index 1. In both calls, `findMatchingWithdrawal` filters purely by `assetId === "nep141:btc.omft.near"` and returns the **same first match** (say, the record for X) [6](#0-5) .
5. Both index 0 and index 1 report `status: "completed", txHash: <X's tx hash>` — withdrawal B (to Y) is misreported as completed with X's transaction hash, even though B's actual on-chain outcome (destination Y, its own tx hash) differs.

### Citations

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

**File:** packages/intents-sdk/README.md (L194-203)
```markdown
### Withdrawals

Complete withdrawal functionality from Near Intents to external chains:

- **Cross-Chain Transfers**: Withdraw to 20+ supported blockchains
- **Multi-Bridge Support**: Hot Bridge, PoA Bridge, Omni Bridge
- **Batch Processing**: Process multiple withdrawals at a time
- **Fee Management**: Automatic fee estimation with quote support
- **Validation**: Built-in validation for withdrawal constraints
- **Status Tracking**: End-to-end monitoring from intent to destination
```
