### Title
POA Bridge `describeWithdrawal` Matches Withdrawal Status by `assetId` Only, Misreporting Completion/Tx-Hash for Batched Same-Asset Withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain status of a specific withdrawal leg (`index`) by looking up the PoA bridge indexer response and matching purely on `args.withdrawalParams.assetId`, deliberately ignoring the withdrawal's `index` because "the response list is unsorted." When an SDK consumer submits a batch withdrawal containing multiple legs of the *same* `assetId` (e.g. splitting one token across two different destination addresses in a single NEAR transaction), `findMatchingWithdrawal` cannot disambiguate between the legs and will return whichever matching record it finds first — reporting the wrong leg's `status`/`transfer_tx_hash` for a given `index`.

### Finding Description
`describeWithdrawal` is called per-withdrawal (per `index`) by the SDK's completion-tracking logic (see `sdk.waitForWithdrawalCompletion.test.ts`, `withdrawal-watcher.ts`) so that an integrator can determine whether a specific withdrawal leg has landed and obtain its destination-chain tx hash: [1](#0-0) 

The matching function is invoked with only the `assetId`, not the `index`, `destinationAddress`, or `amount`:
```
const withdrawal = findMatchingWithdrawal(
    response.withdrawals,
    args.withdrawalParams.assetId,
);
```
This is confirmed by the accompanying regression test, which documents that matching must rely on `near_token_id`/`assetId`, not response ordering or any per-leg identifier: [2](#0-1) 

Because the PoA bridge indexer's `getWithdrawalStatus` response contains one entry per on-chain withdrawal *event* (not per SDK-side `index`), and the code explicitly matches "by assetId instead of index" due to unsorted ordering, a batch of two or more withdrawal legs sharing the same `assetId` (same token) but different `destinationAddress`/`amount` cannot be told apart. `findMatchingWithdrawal` will return the same record (or an incorrect one) for multiple `index` values, so `describeWithdrawal(index=0)` and `describeWithdrawal(index=1)` can both report `status: "completed"` with the *same* `transfer_tx_hash`, even though only one of the two legs actually landed on the destination chain, or the tx hash attributed to leg 0 may actually belong to leg 1's destination.

This breaks the equality that the report tries to protect: *status/txHash reported for withdrawal index N == the on-chain outcome for the specific transfer of index N*. The `destinationAddress` that was validated during `validateWithdrawal` (per leg) is not the one whose completion is actually being confirmed by `describeWithdrawal`.

### Impact Explanation
An integrator relying on the SDK's per-leg status/tx-hash to decide whether to credit or refund a specific withdrawal request could:
- Mark a leg as `"completed"` and release confirmation to the user while the leg's actual on-chain transfer is still pending or failed (status misreport).
- Attribute a completed transaction's tx hash to the wrong leg/destination, causing a legitimate integrator to believe funds landed at address A when the confirmed hash actually corresponds to a transfer to address B.
This matches the "status or hash misreport making an integrator credit or refund twice" High-severity impact category, since it is triggered purely by an ordinary user submitting a same-asset batch withdrawal — no admin/relayer misbehavior required.

### Likelihood Explanation
Any unprivileged SDK user who submits a batch withdrawal with two or more legs of the same `assetId` (a routine use case explicitly supported by `createWithdrawalIntents`/`WithdrawalParams[]`) will trigger the ambiguous matching path deterministically once both legs are recorded by the PoA indexer, since the code's own comment concedes the response list is unsorted and disambiguation was intentionally reduced to `assetId`.

### Recommendation
Disambiguate matching in `findMatchingWithdrawal` using additional per-leg fields returned by the indexer (e.g. `destinationAddress`/`address`, `amount`, and any withdrawal-sequence/nonce field), not `assetId` alone, so that each `index` is matched to the exact corresponding on-chain withdrawal record.

### Proof of Concept
1. Submit a batch withdrawal with two legs, both `assetId: "nep141:btc.omft.near"`, to two different destination Bitcoin addresses (`indexes 0 and 1`).
2. After the withdrawal transaction lands on NEAR, poll `describeWithdrawal({ index: 0, ... })` and `describeWithdrawal({ index: 1, ... })`.
3. Because `findMatchingWithdrawal` selects a record based solely on `assetId` matching the unsorted `response.withdrawals` array, both calls can resolve to the same underlying withdrawal record — reporting the same `status: "completed"` and `transfer_tx_hash` for both indices even though only one leg has actually settled on Bitcoin, i.e. the reported outcome for `index: 1` does not correspond to `index: 1`'s destination address/amount.

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
