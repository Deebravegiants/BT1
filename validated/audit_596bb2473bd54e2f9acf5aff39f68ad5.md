## Analysis

The reachable bug class matches the "**a status reported that is not the on-chain outcome**" equality break, found in the PoA bridge's withdrawal status matching logic.

### Title
Batch withdrawals of the same asset via PoA Bridge can be cross-matched, causing a wrong completion status/txHash to be reported - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain outcome of a withdrawal by calling `findMatchingWithdrawal()`, which selects an entry from the bridge API's `withdrawals` array purely by `assetId`, ignoring `destinationAddress`, `amount`, and the withdrawal's `index`. [1](#0-0) [2](#0-1) 

### Finding Description
When a caller submits a batch of withdrawal intents that includes two withdrawals of the **same asset** (e.g., same `nep141:usdt.tether-token.near`) to **different destination addresses/amounts** in one transaction — an explicitly supported flow per the SDK's own "Batch Intents" feature — `createWithdrawalIdentifiers()` assigns each withdrawal a sequential per-bridge `index` (0, 1, …) but that index is never used by the PoA bridge to disambiguate matches. [3](#0-2) 

`findMatchingWithdrawal()` only compares `nep141:${w.data.near_token_id} === assetId`; the code comment itself acknowledges this limitation ("multiple withdrawals of the same token in a single transaction are not supported"), yet nothing upstream prevents or detects this exact scenario before calling `describeWithdrawal`. Since the PoA API's `withdrawals` array is unsorted, `.find()` returns whichever matching entry appears first — regardless of which of the two batched withdrawals it actually corresponds to. [4](#0-3) 

This breaks the equality that the status/txHash reported for withdrawal *N* must be the on-chain outcome of withdrawal *N*: both `describeWithdrawal` calls (for index 0 and index 1) can resolve to the same array entry, so one withdrawal's real destination address/amount ends up reported under the other's identifier.

### Impact Explanation
`watchWithdrawal()` in the withdrawal watcher directly surfaces this status/hash to callers as the authoritative completion result. [5](#0-4)  An integrator relying on `sdk.processWithdrawal`/`waitForWithdrawalCompletion` for withdrawal #2 (destined to address B) can receive `{status: "completed", txHash: <hash belonging to address A's transfer>}` while B's actual transfer is still pending, failed, or has a different hash — a hash misreport that can cause the integrator to credit/refund the wrong leg of a batch or double-count a single on-chain transfer against two logical withdrawals.

### Likelihood Explanation
No malicious action or privilege escalation is required — an ordinary user/integrator invoking the SDK's documented batch-withdrawal capability with two same-asset withdrawals in one call triggers this deterministically once the PoA API returns unsorted, same-`near_token_id` entries. [6](#0-5) 

### Recommendation
Disambiguate matches in `findMatchingWithdrawal()` using `destinationAddress` and `amount` (and reject/queue ambiguous batches with duplicate `assetId` entries), or have `createWithdrawalIdentifiers` detect and reject/serialize same-asset batches for bridges (like PoA) that cannot correlate multiple withdrawals of one token per transaction, rather than silently returning a possibly-wrong match.

### Proof of Concept
1. Call `sdk.signAndSendWithdrawalIntent` (or batch equivalent) with `withdrawalParams: [{assetId: 'nep141:usdt.tether-token.near', amount: 100n, destinationAddress: A}, {assetId: 'nep141:usdt.tether-token.near', amount: 200n, destinationAddress: B}]` in a single NEAR transaction.
2. `createWithdrawalIdentifiers` assigns `index: 0` to A's withdrawal and `index: 1` to B's withdrawal, both routed through `PoaBridge`. [7](#0-6) 
3. Once the transfer to A completes, the PoA API's `withdrawals` array contains an entry with `near_token_id: "usdt.tether-token.near"` and `transfer_tx_hash` for A's transfer.
4. Calling `watchWithdrawal`/`describeWithdrawal` for B's `WithdrawalIdentifier` (index 1) still matches on assetId alone and returns `{status: "completed", txHash: <A's hash>}`, even though B's own transfer may not have happened yet.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-47)
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

**File:** packages/intents-sdk/README.md (L164-172)
```markdown
### Intent Execution

The primary functionality of the SDK - execute custom intents on Near Intents:

- **Sign Intents**: Create and sign intent payloads with various signer types
- **Submit Intents**: Publish intents to the Near Intents relayer network
- **Track Status**: Monitor intent settlement and execution status
- **Batch Intents**: Execute multiple intents in a single transaction
- **Custom Logic**: Support for any intent type supported by the protocol
```
