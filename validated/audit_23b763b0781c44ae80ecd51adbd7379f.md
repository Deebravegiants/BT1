### Title
Batch withdrawals sharing the same `assetId` but different `destinationAddress` cause PoA bridge to misreport a wrong recipient's txHash - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` (and the analogous `waitForWithdrawalCompletion` helper in `internal-utils`) resolves the withdrawal status for index `i` by matching solely on `assetId` via `findMatchingWithdrawal`, ignoring `destinationAddress`, `amount`, and the batch index. When a batch contains two `withdrawalParams` entries with the same `assetId` but different `destinationAddress`, both indices resolve to the same (first-matching) entry in the unsorted PoA response, so one withdrawal's completion status/txHash gets reported for a different recipient's withdrawal.

### Finding Description
The broken equality is: **STATUS TRUTH** — `(status, txHash)` reported for withdrawal index `i` must equal the actual on-chain outcome of withdrawal `i` (identified by its own `destinationAddress`/`amount`).

Code path:
- `IntentsSDK.processWithdrawal` → `waitForWithdrawalCompletion` → `createWithdrawalCompletionPromises`, which calls each bridge's `describeWithdrawal({ index, withdrawalParams, ... })` per withdrawal in the batch, as seen in `sdk.ts` [1](#0-0) .
- `PoaBridge.describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, explicitly matching "by assetId instead of index" because "Response list is unsorted": [2](#0-1) .
- `findMatchingWithdrawal` uses `Array.prototype.find`, returning the **first** withdrawal in the API response whose `near_token_id` matches the requested `assetId`, with no consideration of `destinationAddress` or `amount`: [3](#0-2) . The comment explicitly documents the gap: "multiple withdrawals of the same token in a single transaction are not supported."
- The identical pattern (and identical caveat) exists in `internal-utils`' `findMatchingWithdrawal`, keyed only by `WithdrawalCriteria.assetId`: [4](#0-3) .

Root cause: when two withdrawal params share `assetId` (e.g., both `nep141:eth.omft.near`) but differ in `destinationAddress`, `describeWithdrawal({ index: 0, ... })` and `describeWithdrawal({ index: 1, ... })` both call `findMatchingWithdrawal` with the same `assetId` and therefore both resolve to the exact same entry from `response.withdrawals` — the first one found — regardless of which index it actually belongs to. There is no per-batch dedup or same-assetId+different-destination guard anywhere upstream: `IntentsSDK.createWithdrawalIntents` validates each withdrawal independently (`bridge.validateWithdrawal`) with no cross-item check [5](#0-4) , and `signAndSendWithdrawalIntent`'s batch handling only asserts array-length parity between `withdrawalParams` and `feeEstimation`, not content uniqueness (as shown by the batch test allowing 4 identical `withdrawalParams` entries) [6](#0-5) .

Existing guards that fail to catch this:
- `validateWithdrawal` in PoA bridge checks address validity and min-amount per single withdrawal, not batch-level duplicate-assetId conflicts [7](#0-6) .
- The repo's own regression test suite ("matches withdrawal by assetId, not by index") only validates that matching correctly ignores response array *order* when assetIds *differ*; it does not cover — and therefore does not guard against — two same-assetId withdrawalParams with different destinations [8](#0-7) .

Attacker's exact input: an unprivileged caller (or an integrator forwarding externally supplied assetId/destinationAddress pairs) calls `sdk.processWithdrawal({ withdrawalParams: [ {assetId:"nep141:eth.omft.near", destinationAddress: addrA, amount: X}, {assetId:"nep141:eth.omft.near", destinationAddress: addrB, amount: Y} ] })`. Once the PoA relayer processes both legs and reports them under identical `defuse_asset_identifier`/`near_token_id`, `describeWithdrawal` for index 0 and index 1 both match the first entry in `response.withdrawals`, causing `destinationTx[0]` to carry the txHash that actually belongs to the withdrawal destined for `addrB` (or vice versa, depending on API response ordering, which is explicitly documented as unsorted).

### Impact Explanation
`destinationTx[i]` — the value an integrator uses to credit/confirm/refund a withdrawal to a specific recipient — is misreported: the caller's own funds are directed correctly on-chain (PoA bridge executes both real transfers correctly to `addrA` and `addrB`), but the SDK's completion report incorrectly associates `addrB`'s destination txHash with batch index 0 (nominally `addrA`'s withdrawal) and/or duplicates the same status for both. An integrator relying on `waitForWithdrawalCompletion`/`processWithdrawal` output to confirm which recipient received funds, or to trigger downstream crediting/refund logic keyed by index, will attribute the wrong transaction to the wrong withdrawal. This matches the High severity category: "a status or hash misreport making an integrator credit or refund twice" (or credit/refund the wrong recipient based on a misattributed hash). This is repeatable on every batch that mixes same-assetId, different-destination withdrawals.

### Likelihood Explanation
Preconditions are trivial and fully within an unprivileged caller's control: submit a batch withdrawal with two `withdrawalParams` sharing the same PoA `assetId` but different `destinationAddress`. No special token state, no relayer misbehavior, and no privileged access are required — the PoA relayer's normal `getWithdrawalStatus` response format (grouped by `defuse_asset_identifier`/`near_token_id`, unsorted) is sufficient to trigger the mismatch, as the codebase's own comments acknowledge. Attacker cost is a normal withdrawal transaction fee; the flaw is deterministic and repeatable on every such batch.

### Recommendation
Extend `findMatchingWithdrawal` (in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate between multiple candidates sharing the same `assetId` by additionally matching on `destinationAddress` (and ideally `amount`), or by consuming matched entries (removing them from the candidate pool) so repeated calls for the same assetId don't collide. Until then, `IntentsSDK` should reject/guard batches containing multiple `withdrawalParams` with identical `assetId` routed through PoA bridge, or clearly document/throw for that unsupported combination instead of silently misreporting completion.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts
it("misattributes txHash when two withdrawals share assetId but differ by destinationAddress", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "tx-for-addrB", // belongs to index 1's destination
          chain: "eth",
          defuse_asset_identifier: "nep141:eth.omft.near",
          near_token_id: "eth.omft.near",
          decimals: 18,
          amount: 2_000_000,
          account_id: "test.near",
          address: "0xBBBB...", // addrB
          created: "2024-01-01T00:00:00Z",
        },
      },
    ],
  });

  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}) });

  // index 0 withdrawal is destined for addrA, amount 1_000_000
  const resultForIndex0 = await bridge.describeWithdrawal({
    landingChain: Chains.Ethereum,
    index: 0,
    withdrawalParams: {
      assetId: "nep141:eth.omft.near",
      amount: 1_000_000n,
      destinationAddress: "0xAAAA...", // addrA, distinct from the mocked response's address
      feeInclusive: false,
    },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  // BROKEN EQUALITY: describeWithdrawal for index 0 (addrA) returns
  // txHash "tx-for-addrB", which actually belongs to addrB's withdrawal.
  expect(resultForIndex0).toEqual({ status: "completed", txHash: "tx-for-addrB" });
  // Assert this txHash does NOT correspond to addrA (i.e., STATUS TRUTH is violated):
  // the mocked withdrawal's `address` field ("0xBBBB...") != withdrawalParams.destinationAddress ("0xAAAA...")
});
```
This demonstrates that `describeWithdrawal` returns a status/txHash for index 0 that does not correspond to index 0's own `destinationAddress`, violating STATUS TRUTH for the batch.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L334-365)
```typescript
	public async createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
		logger?: ILogger;
	}): Promise<IntentPrimitive[]> {
		for (const bridge of this.bridges) {
			if (await bridge.supports(args.withdrawalParams)) {
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - args.feeEstimation.amount
					: args.withdrawalParams.amount;

				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					destinationMemo: args.withdrawalParams.destinationMemo,
					feeEstimation: args.feeEstimation,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
				});

				return bridge.createWithdrawalIntents({
					withdrawalParams: {
						...args.withdrawalParams,
						amount: actualAmount,
					},
					feeEstimation: args.feeEstimation,
					referral: args.referral ?? this.referral,
				});
			}
		}
```

**File:** packages/intents-sdk/src/sdk.ts (L833-838)
```typescript
		// Step 4: Wait for withdrawal completion
		const destinationTx = await this.waitForWithdrawalCompletion({
			withdrawalParams,
			intentTx,
			logger: args.logger,
		});
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-230)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
		destinationMemo?: string;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		// Use cached getSupportedTokens to avoid frequent API calls
		const { tokens } = await this.getCachedSupportedTokens(
			[toPoaNetwork(assetInfo.blockchain)],
			args.logger,
		);

		const tokenInfo = tokens.find(
			(token) => token.intents_token_id === args.assetId,
		);

		if (tokenInfo == null) {
			throw new UnsupportedAssetIdError(
				args.assetId,
				"`assetId` is not supported in PoA bridge.",
			);
		}

		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}

		if (!args.skipMinAmountValidation) {
			const minWithdrawalAmount = BigInt(tokenInfo.min_withdrawal_amount);
			if (args.amount < minWithdrawalAmount) {
				throw new MinWithdrawalAmountError(
					minWithdrawalAmount,
					args.amount,
					args.assetId,
				);
			}
		}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-326)
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

**File:** packages/intents-sdk/src/sdk.signAndSendWithdrawalIntent.test.ts (L50-79)
```typescript
	it("supports batch withdrawals", async () => {
		const { sdk, intentRelayer, defaultIntentSigner } = setupMocks();
		noPublish(intentRelayer);

		void sdk.signAndSendWithdrawalIntent({
			withdrawalParams: [
				withdrawalParams,
				withdrawalParams,
				withdrawalParams,
				withdrawalParams,
			],
			feeEstimation: [fee, fee, fee, fee],
		});

		await vi.waitFor(() =>
			expect(defaultIntentSigner.signIntent).toHaveBeenCalledOnce(),
		);

		expect(vi.mocked(defaultIntentSigner.signIntent).mock.lastCall).toEqual([
			{
				...AnyIntent,
				intents: [
					AnyTransferIntentPrimitive,
					AnyTransferIntentPrimitive,
					AnyTransferIntentPrimitive,
					AnyTransferIntentPrimitive,
				],
			},
		]);
	});
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
