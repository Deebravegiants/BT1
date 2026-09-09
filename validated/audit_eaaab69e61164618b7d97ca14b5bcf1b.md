Based on my investigation, I found a valid analog in this codebase.

### Title
POA Bridge withdrawal status matched only by `assetId`, causing status/tx-hash misreport for batch withdrawals of the same token - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
The external report's bug class — "retrieval/action not linked to the specific signed transaction it belongs to" — has an analog here: `PoaBridge.describeWithdrawal()` and the shared `findMatchingWithdrawal()` helper resolve a withdrawal's on-chain completion status by matching **only the token's `assetId`**, not the specific amount, destination address, or any per-withdrawal nonce/index. When a batch withdrawal (`sdk.processWithdrawal` / `sdk.waitForWithdrawalCompletion` with an array of `WithdrawalParams`) contains two or more withdrawals of the *same token* to *different destinations/amounts*, the code cannot distinguish between them and will report the first API result matching that token for every one of them.

### Finding Description
`findMatchingWithdrawal` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` filters the POA bridge's returned withdrawals array using only `nep141:${w.data.near_token_id} === criteria.assetId`: [1](#0-0) 

The comment directly above the function acknowledges the limitation but the code proceeds anyway instead of refusing to resolve an ambiguous match: [2](#0-1) 

The SDK-level bridge implementation, `PoaBridge.describeWithdrawal()`, has the identical pattern — it explicitly matches "by assetId instead of index" and returns whatever `transfer_tx_hash` and `status` belong to the first API entry for that asset, regardless of which of several withdrawal identifiers (by amount/destination) it was actually asked about: [3](#0-2) 

This same shape exists for the raw completion-tracking function used outside the SDK bridge abstraction: [4](#0-3) 

The equality broken: "status/tx-hash reported for withdrawal index N" should equal "the actual on-chain outcome of the specific signed `ft_withdraw` intent corresponding to index N's amount/destination," but instead it equals "the first entry with a matching token from an unsorted API response," which can belong to a completely different withdrawal in the same batch.

### Impact Explanation
This matches the rule's High-severity category "a status or hash misreport making an integrator credit or refund twice." Concretely: if a caller withdraws the same NEP-141 token twice in one `processWithdrawal` batch call — e.g., 100 USDT to address A and 50 USDT to address B — `waitForWithdrawalCompletion`/`describeWithdrawal` for *both* entries may resolve to the same underlying POA withdrawal record (whichever one the unsorted API happens to return first). An integrator relying on the SDK's per-index `destinationTx` result to mark a withdrawal "completed" and release funds/credit downstream could:
- Report withdrawal B as "completed" with a `txHash` that actually corresponds to withdrawal A (or vice versa), and
- Report the other withdrawal in the batch as permanently "pending" (silently stuck) even though it settled on-chain with a different transfer hash.

This is a genuine status-authenticity break, not merely a UX inconvenience, and can cause an integrator to double-credit one destination while failing to ever credit / release funds tied to the other.

### Likelihood Explanation
Requires no malicious actor — any legitimate caller doing a batch withdrawal of the same token to multiple destinations/amounts in a single `processWithdrawal`/`createWithdrawalCompletionPromises` call triggers it. Batch withdrawals are a first-class, documented SDK feature (`README.md` "Batch Withdrawals" section, `sdk.ts` `processWithdrawal(WithdrawalParams[])`), and same-token multi-destination batches are a plausible real-world usage pattern (e.g., payroll-like fan-out of the same asset). The code has a known, explicit comment acknowledging the ambiguity but does not guard against it (no error thrown, no amount/destination disambiguation attempted).

### Recommendation
Do not resolve ambiguous matches silently. When multiple POA bridge withdrawals share the same `assetId` in a single batch:
- Extend `findMatchingWithdrawal` / `WithdrawalCriteria` to also require matching `amount` and `destinationAddress` (and consume matched entries so they can't be reused for another index in the same batch), similar to how the code already appends `near_token_id` fallback matching for other bridges.
- If disambiguation still isn't possible from the POA API response alone, fail loudly (throw an invariant error) rather than reporting a plausible-but-wrong status/tx-hash, so integrators don't act on an incorrect completion signal.
- Track already-consumed withdrawal entries across the batch to prevent the same on-chain withdrawal record from being reported as the completion for two different requested withdrawals.

### Proof of Concept
1. Call `sdk.processWithdrawal({ withdrawalParams: [ {assetId: "nep141:eth.omft.near", amount: 100n, destinationAddress: "0xAAA...", feeInclusive:false}, {assetId: "nep141:eth.omft.near", amount: 50n, destinationAddress: "0xBBB...", feeInclusive:false} ] })`.
2. Both withdrawals settle on NEAR in the batch intent transaction; POA bridge later processes both and returns an unsorted `withdrawals` array containing both records for `near_token_id = "eth.omft.near"`.
3. `waitForWithdrawalCompletion`/`describeWithdrawal` is invoked once per index (0 and 1) with `withdrawalCriteria = { assetId: "nep141:eth.omft.near" }` for both — identical criteria regardless of index.
4. `findMatchingWithdrawal` returns `withdrawals[0]` (e.g., the 0xAAA/100 record) for *both* index 0 and index 1 queries (as demonstrated by the existing unit test `"matches withdrawal by assetId, not by index"` at [5](#0-4)  — that test only shows the safe case of *different* assetIds resolving correctly by asset rather than positional index; it does not cover — and the implementation does not handle — the same-assetId multi-destination case).
5. `destinationTx[1]` in the SDK's `BatchWithdrawalResult` ends up reporting the 0xAAA transfer hash even though it was queried for the 0xBBB/50 withdrawal, misleading any integrator logic keyed on `destinationTx[index]`.

### Citations

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L35-87)
```typescript
export async function waitForWithdrawalCompletion({
	txHash,
	withdrawalCriteria,
	signal,
	baseURL,
	retryOptions = RETRY_CONFIGS.TWO_MINS_GRADUAL,
	logger,
}: {
	txHash: string;
	withdrawalCriteria: WithdrawalCriteria;
	signal: AbortSignal;
	baseURL?: string;
	retryOptions?: RetryOptions;
	logger?: ILogger;
}): Promise<WaitForWithdrawalCompletionOkType> {
	return retry(
		async () => {
			const result = await getWithdrawalStatus(
				{ withdrawal_hash: txHash },
				{ baseURL, fetchOptions: { signal }, logger },
			);

			const withdrawal = findMatchingWithdrawal(
				result.withdrawals,
				withdrawalCriteria,
			);
			if (withdrawal == null) {
				throw new PoaWithdrawalInvariantError(
					"POA Bridge didn't return withdrawal matching criteria",
					result,
					txHash,
					withdrawalCriteria,
				);
			}

			if (withdrawal.status === "COMPLETED") {
				if (withdrawal.data.transfer_tx_hash == null) {
					throw new PoaWithdrawalInvariantError(
						"POA Bridge didn't return transfer_tx_hash for COMPLETED withdrawal",
						result,
						txHash,
						withdrawalCriteria,
					);
				}

				return {
					destinationTxHash: withdrawal.data.transfer_tx_hash,
					chain: withdrawal.data.chain,
				};
			}

			throw new PoaWithdrawalPendingError(result, txHash, withdrawalCriteria);
		},
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
