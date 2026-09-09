### Title
POA Bridge withdrawal status misattributed to wrong destination when batching same-asset withdrawals in one transaction - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain status/tx-hash of a withdrawal by matching the POA Bridge API's returned withdrawal list solely on `assetId`, ignoring the withdrawal's index, amount, or destination address. When a single NEAR transaction batches more than one withdrawal of the *same* asset (e.g., two `ft_withdraw` intents for `nep141:btc.omft.near` to two different destination addresses), the matcher returns the same withdrawal record for every same-asset query, so a caller asking about withdrawal `index=1` (destination B) can receive the completed status/hash that actually belongs to withdrawal `index=0` (destination A), or vice versa.

### Finding Description
`findMatchingWithdrawal` is documented in-code as a known limitation: [1](#0-0) 

`describeWithdrawal` calls it with only `args.withdrawalParams.assetId`, never `args.index`, `args.withdrawalParams.destinationAddress`, or `args.withdrawalParams.amount`: [2](#0-1) 

`createWithdrawalIdentifier` similarly derives a `WithdrawalIdentifier` per-withdrawal that carries `index` but that index is not used for matching against the API response, since the POA API response array order isn't guaranteed to align with intent order (the code comment explicitly states "Response list is unsorted, so we match by assetId instead of index").

The equality this breaks is: *the withdrawal status/hash reported for withdrawal `i` (with specific destination address and amount) must correspond to the on-chain outcome of withdrawal `i`* — not to any other same-asset withdrawal bundled in the same transaction. With only `assetId` used as the key, two or more withdrawals of the same token bundled in one transaction are indistinguishable to `findMatchingWithdrawal`, and `Array.prototype.find` will always return the first matching entry in API response order (which is admittedly unsorted/undetermined) regardless of which specific withdrawal (destination/amount) the caller is asking about.

The existing test suite only demonstrates the safe case — different assets (`eth` vs `btc`) resolve correctly regardless of order: [3](#0-2) 
There is no test covering two same-asset withdrawals in one tx, which is exactly the gap the code comment flags as unsupported.

### Impact Explanation
`watchWithdrawal`/`withdrawal-watcher.ts` treats the `describeWithdrawal` result as the ground truth for whether a specific withdrawal (by index) has completed and to what destination tx hash: [4](#0-3) 

If an integrator batches two withdrawals of the same asset to two different addresses in a single NEAR transaction (which `IntentPrimitive`/`ft_withdraw` batching mechanics in `createWithdrawalIntents` do not prevent), polling for withdrawal `index=0` and `index=1` separately can both resolve to the same underlying record. This can cause:
- A misreport of `txHash`, leading an integrator to believe withdrawal B (to address B) completed with the tx hash that actually corresponds to withdrawal A (to address A), i.e., a status/hash misreport that could make an integrator credit or refund the wrong withdrawal, matching the "High" impact bar for misreported status/hash causing wrongful credit or refund.
- Because the mismatch is silent (no error is thrown; a valid-looking `completed` status is returned), it can lead to double-crediting or refund decisions made based on the wrong transaction hash without on-chain verification.

### Likelihood Explanation
This requires the caller/integrator to build a single NEAR transaction with two or more `ft_withdraw` (or equivalent POA-routed) intents for the *same* `assetId` — the SDK does not prevent this pattern, and the `WithdrawalIdentifier.index` field exists precisely to distinguish per-intent statuses, implying multi-withdrawal batching is an anticipated usage. No malicious actor input is required; this is triggered by ordinary caller usage of the SDK's own batching capability, not by an attacker manipulating validated data. This somewhat reduces confidence that it's "unprivileged"-attacker-triggered in the strict sense demanded by the rules (it's a caller/integrator-side latent bug rather than something an external attacker can trigger against a victim without control over the withdrawal request), and the code explicitly flags it as a known, documented limitation rather than an undiscovered defect.

### Recommendation
Extend `findMatchingWithdrawal` to disambiguate among same-asset withdrawals in the same transaction — for example, by using `destination address` + `amount` in addition to `near_token_id`, or by requesting that the POA Bridge API return withdrawals in submission order and matching by array position (`index`) once the API guarantees ordering. At minimum, `describeWithdrawal` should detect the ambiguous case (multiple same-asset withdrawals with matching status in the response) and throw/return an explicit "cannot disambiguate" error rather than silently returning a status that may belong to a different withdrawal.

### Proof of Concept
Not independently verified end-to-end against a live POA Bridge API (this would require constructing an actual batched NEAR transaction with two `ft_withdraw` intents for the same `nep141:btc.omft.near` asset to two distinct destination addresses, and observing the API's `getWithdrawalStatus` response). Based on static analysis of `findMatchingWithdrawal`/`describeWithdrawal` alone:
1. Build `withdrawalParams` for two withdrawals of `nep141:btc.omft.near` — destination `X` and destination `Y` — batched in one `createWithdrawalIntents` call/transaction.
2. Call `describeWithdrawal({ ..., index: 0, withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: X, ... } })` and `describeWithdrawal({ ..., index: 1, withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: Y, ... } })`.
3. Given a POA API response array containing two `COMPLETED` entries with `near_token_id: "btc.omft.near"` (one for each), `findMatchingWithdrawal` returns `withdrawals[0]` (i.e., `.find()`'s first match) for *both* calls — regardless of `index`, `X`, or `Y` — since it filters only on `` `nep141:${w.data.near_token_id}` === assetId ``, illustrated directly by the matcher implementation cited above. [5](#0-4)

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1111)
```typescript
		it("matches withdrawal by assetId, not by index", async () => {
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
				withdrawals: [
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "other-tx-hash",
							chain: "eth",
							defuse_asset_identifier: "nep141:eth.omft.near",
							near_token_id: "eth.omft.near",
							decimals: 18,
							amount: 1000000,
							account_id: "test.near",
							address: zeroAddress,
							created: "2024-01-01T00:00:00Z",
						},
					},
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "btc-tx-hash",
							chain: "btc",
							defuse_asset_identifier: "nep141:btc.omft.near",
							near_token_id: "btc.omft.near",
							decimals: 8,
							amount: 100000,
							account_id: "test.near",
							address: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
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
				landingChain: Chains.Bitcoin,
				index: 0,
				withdrawalParams: {
					assetId: "nep141:btc.omft.near",
					amount: 100000n,
					destinationAddress: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
				status: "completed",
				txHash: "btc-tx-hash",
			});
		});
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
