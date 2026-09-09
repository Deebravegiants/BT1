## Title
POA Bridge withdrawal status matching by asset only causes cross‑withdrawal status/tx‑hash misreport in batches - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on‑chain status of a single withdrawal by looking up the POA Bridge indexer response and matching purely on the asset (`near_token_id`/`assetId`), never on `destinationAddress`, `amount`, or the withdrawal's index/nonce. When a batch contains two or more withdrawals of the same asset (a normal, unprivileged usage pattern of the SDK's batch withdrawal API), the wrong entry's completion status and destination transaction hash can be attributed to the wrong `WithdrawalIdentifier`.

### Finding Description
`describeWithdrawal` explicitly documents that it cannot rely on index because "Response list is unsorted, so we match by assetId instead of index": [1](#0-0) 

It calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` and, if a match is found with `status === "COMPLETED"`, returns `{ status: "completed", txHash: withdrawal.data.transfer_tx_hash }` unconditionally — with no check that the matched withdrawal's `data.address` equals `args.withdrawalParams.destinationAddress` or that `data.amount` equals `args.withdrawalParams.amount`.

The regression test in the repo itself demonstrates the matching key is asset‑based (`near_token_id`), not identity based on address/amount: [2](#0-1) 

The batch withdrawal flow builds one `WithdrawalIdentifier` per index in the intent and later calls `bridge.describeWithdrawal(wid)` independently for each one, expecting each call to resolve to *that specific* withdrawal's outcome: [3](#0-2) [4](#0-3) 

The broken equality is: *the status/tx‑hash reported for withdrawal‑identifier N should equal the on‑chain outcome of the withdrawal actually sent to `withdrawalParams[N].destinationAddress`*. Because the lookup key is only the asset, if the same asset is withdrawn to two different addresses within one NEAR transaction, `findMatchingWithdrawal` can return the same (first-matching) record for both `describeWithdrawal` calls, causing:
- Both watchers to converge on the *same* `txHash`, letting an integrator believe withdrawal‑to‑address‑B completed when the on‑chain transfer actually went to address‑A, or
- One withdrawal's watcher to resolve `completed` with the wrong `txHash` while the second withdrawal's record is starved (never separately observed), effectively double‑crediting one destination's completion status to two logical withdrawals.

### Impact Explanation
This falls under the High‑severity criteria "a status or hash misreport making an integrator credit or refund twice." An integrator relying on `waitForWithdrawalCompletion`/`describeWithdrawal` per‑withdrawal-identifier to decide when to mark a specific payout as settled (e.g., release goods, mark invoice paid, stop retry/refund logic) could act on a `txHash` that does not correspond to the withdrawal it queried, misattributing completion between two legitimately batched withdrawals of the same asset.

### Likelihood Explanation
This does not require a malicious relayer, bridge operator, or price assumption — it is triggered purely by legitimate SDK usage: a batch withdrawal (`sdk.signAndSendWithdrawalIntent`/`processWithdrawal` with an array of `withdrawalParams`) where two or more entries share the same `assetId` (e.g., paying the same POA-bridged token to two different destination addresses in one transaction), which the SDK's public batch API explicitly supports.

### Recommendation
In `findMatchingWithdrawal` / `describeWithdrawal`, disambiguate matches within the same asset by also validating `data.address === args.withdrawalParams.destinationAddress` and `data.amount === args.withdrawalParams.amount` (and/or track already-consumed indices) before treating a record as the match for a given `WithdrawalIdentifier`. If multiple withdrawals share both asset and destination/amount, fall back to a positional/nonce-based correlation instead of the first asset match.

### Proof of Concept
1. Build a batch withdrawal with two entries: `{ assetId: "nep141:btc.omft.near", destinationAddress: A, amount: 100000n }` and `{ assetId: "nep141:btc.omft.near", destinationAddress: B, amount: 50000n }`, submitted in one NEAR intent.
2. The POA Bridge indexer settles the withdrawal to `A` first; its status list contains one `COMPLETED` record for `near_token_id: "btc.omft.near"` with `address: A`, `transfer_tx_hash: TX_A`. The withdrawal to `B` is still pending and absent from the response.
3. Call `describeWithdrawal` for the identifier corresponding to index 1 (destination `B`). `findMatchingWithdrawal(response.withdrawals, "nep141:btc.omft.near")` returns the only entry present — the one for `A` — because matching is asset‑only.
4. `describeWithdrawal` returns `{ status: "completed", txHash: TX_A }` for the withdrawal that was supposed to go to `B`, even though `B` has not received anything, satisfying the on‑chain-outcome misreport condition.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-337)
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1113-1158)
```typescript
		it("matches withdrawal by near_token_id when defuse_asset_identifier differs from assetId format", async () => {
			// Regression test: POA API returns defuse_asset_identifier in chain-native format
			// (e.g., "tron:mainnet:native") which differs from assetId format ("nep141:tron.omft.near").
			// Matching must use near_token_id, not defuse_asset_identifier.
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
				withdrawals: [
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "tron-tx-hash",
							chain: "tron:mainnet",
							defuse_asset_identifier: "tron:mainnet:native",
							near_token_id: "tron.omft.near",
							decimals: 6,
							amount: 474270,
							account_id: "test.near",
							address: "native",
							created: "2024-01-01T00:00:00Z",
						},
					},
				],
			});

			const bridge = new PoaBridge({
				envConfig: configsByEnvironment.production,
				xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
			});

			const result = await bridge.describeWithdrawal({
				landingChain: Chains.Tron,
				index: 0,
				withdrawalParams: {
					assetId: "nep141:tron.omft.near",
					amount: 474270n,
					destinationAddress: "TGNZdiQV31H3JvTtC1yH6yuipnqs6LN2Jv",
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
				status: "completed",
				txHash: "tron-tx-hash",
			});
		});
```

**File:** packages/intents-sdk/README.md (L521-548)
```markdown
### Batch Withdrawals

Process multiple withdrawals in a single intent:

```typescript
const withdrawalParams = [
    {
        assetId: 'nep141:usdt.tether-token.near',
        amount: 1000000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    },
    {
        assetId: 'nep245:v2_1.omni.hot.tg:137_qiStmoQJDQPTebaPjgx5VBxZv6L',
        amount: 100000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    }
]

// Method 1: Complete end-to-end batch processing
const batchResult = await sdk.processWithdrawal({
    withdrawalParams,
    // feeEstimation is optional - will be estimated automatically if not provided
});

console.log('Batch intent hash:', batchResult.intentHash);
console.log('Destination transactions:', batchResult.destinationTx); // Array of results
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
