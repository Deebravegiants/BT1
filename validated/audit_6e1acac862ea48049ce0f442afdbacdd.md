### Title
Withdrawal status/txHash misattributed when multiple same-asset withdrawals occur in one transaction - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` matches a specific withdrawal's on-chain completion status by `assetId` alone, not by index/amount/destination. When a single NEAR transaction contains two or more `ft_withdraw` intents for the same POA asset (e.g. two BTC withdrawals to different addresses/amounts in one batched intent execution), the function can report the `txHash`/`status` belonging to a *different* withdrawal than the one the caller actually asked about.

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal`, which is explicitly documented to only match by `assetId`: [1](#0-0) [2](#0-1) 

The `withdrawal_hash` used to fetch status is the *NEAR transaction hash* (`args.tx.hash`), not a withdrawal-specific identifier, and the POA bridge API returns an unsorted list of withdrawals for that transaction. `findMatchingWithdrawal` picks the *first* entry whose `near_token_id` matches `assetId`, ignoring `args.withdrawalParams.amount`, `args.withdrawalParams.destinationAddress`, and `args.index`. The code comment itself acknowledges: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [3](#0-2) .

This mirrors the underlying bug class in the report: an inferred/looked-up value (here, "the withdrawal that corresponds to this call") is derived from an under-constrained match (asset type only) instead of the caller-supplied specifics (amount, destination, index), so the reported outcome does not necessarily correspond to the actual withdrawal being queried — breaking the equality "status reported == on-chain outcome for *this* withdrawal".

### Impact Explanation
If a batch of intents produces two `ft_withdraw`s of the same NEP-141 asset in one NEAR transaction (e.g., withdrawal #0 to address A for 1 BTC, withdrawal #1 to address B for 2 BTC), calling `describeWithdrawal` for index 0 can return the `COMPLETED` status and `transfer_tx_hash` that actually belongs to withdrawal #1 (to address B), while withdrawal #0 may still be pending or failed. An integrator polling per-index status could therefore credit/confirm withdrawal #0 as completed using a transaction hash and value that never delivered funds to address A — a status misreport that leads to crediting or refunding based on the wrong on-chain outcome (matches the High-impact category "a status or hash misreport making an integrator credit or refund twice").

### Likelihood Explanation
This requires the caller/integrator to submit more than one withdrawal for the same asset within a single NEAR transaction (a legitimate, supported use case, since `sdk.createWithdrawalIntents`/batch execution allow multiple intents in one call) and to then track completion by index for each. No malicious relayer, RPC, or bridge operator behavior is required — an ordinary batched withdrawal of the same token to two different addresses triggers it.

### Recommendation
Match withdrawals using more than `assetId`: additionally disambiguate by amount and/or destination address (and ideally use a real POA-side identifier that ties 1:1 to an intent, if the API exposes one) before returning `completed`/`txHash`. Until the POA API supports per-intent identifiers, at minimum validate that the matched withdrawal's `amount`/`address` correspond to `args.withdrawalParams`, and treat ambiguous matches (multiple withdrawals of the same asset in the same tx) as `pending` rather than guessing.

### Proof of Concept
1. Build and sign a NEAR transaction with two `ft_withdraw` intents for `nep141:btc.omft.near`: index 0 → 1 BTC to address A, index 1 → 2 BTC to address B.
2. POA indexes both withdrawals under the same `tx.hash`; withdrawal to B completes first.
3. Call `bridge.describeWithdrawal({ index: 0, withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 1_BTC, destinationAddress: A, ... }, tx })`.
4. `findMatchingWithdrawal` returns the first entry with `near_token_id === "btc.omft.near"`, which may be the completed transfer to B, so the caller receives `{ status: "completed", txHash: <B's tx hash> }` for a withdrawal that was actually meant for A — as validated by the existing test `"matches withdrawal by assetId, not by index"` [4](#0-3)  (that test only distinguishes different assetIds; it does not cover — and the code comment admits it cannot correctly handle — two withdrawals of the *same* assetId in one tx).

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
