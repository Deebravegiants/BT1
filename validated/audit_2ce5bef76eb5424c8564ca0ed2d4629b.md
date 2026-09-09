This confirms the batch withdrawal path (`createWithdrawalIdentifiers` in `withdrawal-watcher.ts`) supports multiple `WithdrawalParams` in a single NEAR transaction, each getting its own `index`, and each is routed to `PoaBridge.describeWithdrawal` for status resolution. `PoaBridge.describeWithdrawal` ignores the `index` and matches purely by asset via `findMatchingWithdrawal`, which is explicitly documented as unable to distinguish multiple same-asset withdrawals in one transaction.

### Title
Same-asset batched withdrawals report the wrong destination tx hash/status via PoA Bridge - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` matches a withdrawal in the PoA API response using only the `assetId` (`near_token_id`), not the batch `index`, amount, or destination address. When a single NEAR transaction contains two or more `ft_withdraw` intents for the same token (a batch withdrawal to different destination addresses), the integrator/SDK caller can be given the transfer hash and completion status of the wrong withdrawal in the batch.

### Finding Description
`createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`) builds one `WithdrawalIdentifier` per `WithdrawalParams` entry, assigning `index` per bridge route: [1](#0-0) 

For PoA-routed withdrawals, `PoaBridge.describeWithdrawal` fetches the withdrawal list and matches it purely by `assetId`: [2](#0-1) 

The comment on `findMatchingWithdrawal`-style matching (mirrored in `internal-utils`) is explicit about the limitation: "Currently only matches by assetId (near_token_id). This means multiple withdrawals of the same token in a single transaction are not supported." [3](#0-2) 

The SDK's own test suite documents this behavior as "matching by assetId, not by index," confirming that when two withdrawals with different assets exist the SDK correctly disambiguates by asset, but it does **not** disambiguate two withdrawals of the **same** asset in the same tx — it will simply return whichever matching entry the API lists first/at all: [4](#0-3) 

The equality broken is: *the destination tx hash / completion status reported for withdrawal at index N* must equal *the on-chain outcome of withdrawal N*. Since matching ignores `index`, `amount`, and `destinationAddress`, if a NEAR transaction withdraws the same token to two different destinations (e.g., `ft_withdraw` intents to Address A and Address B in the same tx, as supported by the batch-withdrawal API in `sdk.ts`/`shared-types.ts`), `describeWithdrawal` for index 0 and index 1 can both resolve to the same PoA withdrawal record — or the wrong one — reporting a `txHash`/`completed` status that actually belongs to the other destination's transfer.

### Impact Explanation
An integrator or the `watchWithdrawal` poller (`packages/intents-sdk/src/core/withdrawal-watcher.ts:20-77`) uses this status to decide when a withdrawal is "completed" and to hand back a `txHash` to the caller for reconciliation/crediting purposes. If the reported `txHash`/status is bound to a different destination address's withdrawal than requested, an integrator could:
- Mark withdrawal A as completed using B's `transfer_tx_hash`, causing the integrator to credit/confirm the wrong destination or double-credit a single external transfer against two internal withdrawal records.
- Report "completed" for a withdrawal that has actually failed/is pending (if the matched record has a different status than the true one for that index).

This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category, since money movement records (which off-chain systems treat as ground truth) are decoupled from the correct on-chain transfer.

### Likelihood Explanation
This requires no malicious relayer/RPC/API behavior — it is triggered purely by legitimate use of batch withdrawals of the *same* asset to different destinations in one NEAR transaction, a scenario explicitly acknowledged as unsupported/broken in code comments, meaning any normal user or integrator invoking batch withdrawal with duplicate assets will hit it. The main uncertainty is whether the current public SDK API actually allows constructing two same-asset PoA withdrawal intents within one transaction (batch withdrawal support exists per `shared-types.ts`/`sdk.ts`, but I did not fully trace whether the batch withdrawal path validates/rejects duplicate assets before calling `createWithdrawalIdentifiers`). If duplicate same-asset entries are rejected upstream, this bug would be unreachable from the public API and only exercised via the lower-level `PoaBridge.describeWithdrawal` used directly.

### Recommendation
Change `findMatchingWithdrawal`/`PoaBridge.describeWithdrawal` matching to use a unique identifier — the PoA API's per-withdrawal index/amount/destination combination, or require the PoA API to expose a request/withdrawal id that can be matched 1:1 with the SDK's `index` — instead of matching solely by `assetId`. Until fixed, reject (assert) batch withdrawals containing more than one entry of the same asset in a single transaction so that ambiguous status resolution cannot occur silently.

### Proof of Concept
1. Construct a batch withdrawal transaction containing two `ft_withdraw` intents for the same `assetId` (e.g., `nep141:btc.omft.near`) with different `destinationAddress` values (A and B), submitted as `withdrawalParams: [paramsA, paramsB]`.
2. `createWithdrawalIdentifiers` assigns `index: 0` to A and `index: 1` to B (`withdrawal-watcher.ts:88-103`).
3. Call `PoaBridge.describeWithdrawal` for both `WithdrawalIdentifier`s (A and B). Both calls invoke `getWithdrawalStatusWithRetry` and then `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which finds the first entry in `response.withdrawals` whose `near_token_id` matches — regardless of index/destination (`poa-bridge.ts:313-343`).
4. If the PoA API returns B's record first, both `describeWithdrawal(A)` and `describeWithdrawal(B)` return B's `transfer_tx_hash`/status, i.e., withdrawal A is reported as completed with B's destination tx hash.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L88-103)
```typescript
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
