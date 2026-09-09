### Title
PoA Bridge withdrawal status matched only by `assetId`, ignoring `index`/destination/amount — status/hash misreport across withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain settlement status of a specific withdrawal by looking it up via `findMatchingWithdrawal`, which matches purely on `assetId` and takes the first result returned by the POA bridge API (`response.withdrawals.find(...)`). It ignores the `index` field of `WithdrawalIdentifier` that other bridge implementations (Hot, Omni) explicitly use to disambiguate multiple withdrawals created in the same NEAR transaction. When a single NEAR transaction contains two or more withdrawals of the same token (e.g., to different destination addresses or with different amounts, all valid per the intents protocol which allows batched intents), the wrong withdrawal record can be attributed to the caller's requested withdrawal, causing the wrong status/txHash to be reported.

### Finding Description
`describeWithdrawal` at [1](#0-0)  calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which is defined as: [2](#0-1) 

The function's own comment concedes the flaw: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." Despite this, `WithdrawalIdentifier` carries an `index` field precisely for this disambiguation purpose — and is actually used for that purpose by the other bridges. For example, `HotBridge.describeWithdrawal` disambiguates using `nonces[args.index]` at [3](#0-2) , and `OmniBridge.describeWithdrawal` disambiguates using `(await this.omniBridgeAPI.getTransfer(...))[args.index]` at [4](#0-3) . `PoaBridge` silently drops `args.index` and instead relies on an unordered `.find()` by `assetId` alone, as also acknowledged in `createWithdrawalIdentifier`, which forwards the same `withdrawalParams`/`tx` without using `index` for later lookup at [5](#0-4) .

The equality broken: "status/hash reported for withdrawal N" should equal "the actual on-chain outcome of withdrawal N," but instead it equals "the on-chain outcome of whichever same-asset withdrawal happens to be first in the API's unsorted list." If a caller (or an integrator building on the SDK, e.g. `watchWithdrawal` at [6](#0-5) ) initiates two withdrawals of the same `assetId` in one NEAR transaction (to two different destination addresses, which the intents protocol permits as a batch of `ft_withdraw` intents), each polling loop for withdrawal index 0 and index 1 will hit `findMatchingWithdrawal` and can both resolve to the same underlying record — reporting one destination's real completed transfer hash for the other's still-pending or entirely different withdrawal.

### Impact Explanation
This falls under the "status or hash misreport making an integrator credit or refund twice" High-impact category from the rules. An integrator or the SDK's own `watchWithdrawal` polling loop can be told withdrawal #0 is `"completed"` with a `txHash` that actually belongs to withdrawal #1 (or vice versa), while the real withdrawal #0 may still be pending or failed. This can cause premature crediting/settlement confirmation for a withdrawal that has not actually landed on the destination chain, or attribute a completed transfer's hash to the wrong recipient's poll — both are integrity-breaking status misreports that a downstream integrator (exchange, custodian, wallet, backend ledger) could act on to release funds or mark accounts as settled incorrectly.

### Likelihood Explanation
Likelihood is moderate: it requires the caller to submit two or more withdrawals of the *same* `assetId` within a single NEAR transaction (a supported, non-malicious usage pattern — batched intents are a normal feature of the protocol, and nothing prevents a user/integrator from batching same-token withdrawals to different addresses). No malicious relayer, price manipulation, or admin action is required — this is a self-inflicted correctness bug triggered by ordinary batched usage, distinguishing it from any external trust-assumption issue.

### Recommendation
Use `args.index` to disambiguate matches in `findMatchingWithdrawal`, e.g., by sorting the withdrawals from the POA API deterministically (by creation order/amount/destination) and matching against the batch's ordinal position, or by having the POA bridge API return an index/tag matching the intent's ordinal in the transaction. At minimum, when multiple withdrawals share the same `assetId` in the response set, also match on `destinationAddress` and `amount` (and reject ambiguous matches rather than silently picking the first) to preserve the correctness of the per-index status query.

### Proof of Concept
1. Caller creates a single NEAR transaction with two `ft_withdraw` intents for the same `assetId` (`nep141:btc.omft.near`): withdrawal A to `destinationAddress: addr1`, withdrawal B to `destinationAddress: addr2`.
2. `createWithdrawalIdentifier` is called twice, producing `WithdrawalIdentifier { index: 0, ... }` and `WithdrawalIdentifier { index: 1, ... }`, both sharing the same `tx.hash`.
3. Caller (or `watchWithdrawal`) polls `describeWithdrawal` for both identifiers.
4. `getWithdrawalStatusWithRetry` returns `response.withdrawals` containing both underlying withdrawal records for that `tx.hash` (unsorted, per the code comment "Response list is unsorted").
5. `findMatchingWithdrawal(response.withdrawals, assetId)` for index 0 request returns the first array entry matching `assetId` — which, depending on API ordering, may actually be withdrawal B's record (with B's `transfer_tx_hash` for `addr2`).
6. The caller polling for withdrawal A (destined for `addr1`) receives `{ status: "completed", txHash: <B's transfer_tx_hash> }`, misreporting B's settlement as A's.

### Citations

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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L378-387)
```typescript
		const cacheKey = this.getNoncesCacheKey(args.tx);
		const nonces = await this.noncesCache.fetch(cacheKey, { context: args.tx });
		if (nonces == null) {
			throw new HotWithdrawalNotFoundError(args.tx.hash, args.index);
		}

		const nonce = nonces[args.index];
		if (nonce == null) {
			throw new HotWithdrawalNotFoundError(args.tx.hash, args.index);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-698)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];
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
