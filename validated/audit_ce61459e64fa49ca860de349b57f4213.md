### Title
Withdrawal status confirmed without validating returned `chain_id` against requested landing chain - ([File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts])

### Summary
`HotBridge.describeWithdrawal` resolves withdrawal completion by matching bridge-indexer/HOT-API records solely on `nonce`, while both data sources also carry an explicit `chain_id` field that is parsed but never compared against the chain the withdrawal was actually meant to land on (`args.landingChain`).

### Finding Description
`describeWithdrawal` looks up the nonce for the requested withdrawal index and then calls `fetchWithdrawalHashBridgeIndexer` / `fetchWithdrawalHashFromApi` to resolve the destination tx hash: [1](#0-0) 

The bridge-indexer lookup selects the record by nonce alone (`withdrawal.nonce === nonce`), ignoring the `chain_id` field that the response schema explicitly carries: [2](#0-1) 

Likewise, the HOT-API fallback selects by nonce only, and formats the resolved hash using the locally expected `args.landingChain`, never checking the `chain_id` on the matched record against it: [3](#0-2) 

`chain_id` is present in both response schemas — `HotApiWithdrawalSchema` and `BridgeIndexerResponseSchema` — precisely because a nonce is not guaranteed to disambiguate the destination chain of a settlement record: [4](#0-3) 

The caller then blindly reports `{ status: "completed", txHash }`, formatting the hash for `args.landingChain` (the chain the SDK expects), even though the record it matched could belong to a different chain: [5](#0-4) 

This mirrors the reported bug class exactly: the module has the field needed to validate the settlement's origin/target chain (`chain_id`) in scope, but the equality `record.chain_id === request.landingChain` is never enforced before the withdrawal is reported as completed with a specific `txHash`.

### Impact Explanation
If the indexer or HOT API ever returns/matches a withdrawal record whose `nonce` coincides with the polled nonce but whose `chain_id` differs from the requested `landingChain` (e.g., due to a backend indexing bug, replay, or nonce reuse across networks), the SDK will report the withdrawal as `completed` with a `txHash` that does not correspond to the actual destination chain the user is expecting funds on. Consumers of this SDK (integrators) would treat the withdrawal as settled and stop tracking it, while the real transfer on the correct chain may still be pending or never occur — a stuck-withdrawal / misreported-status condition with no automatic recourse, matching the High-impact bucket ("a status or hash misreport making an integrator credit or refund twice", "a withdrawal stuck until manual intervention").

### Likelihood Explanation
Likelihood is Low, since it requires the backend (bridge indexer or HOT API) to return an inconsistent/incorrect `chain_id` for a matching nonce, and the SDK itself does not decide which chain to pay — it only decides whether to trust the returned record without cross-checking chain identity, exactly the same "trusted-but-unchecked field" pattern the referenced report flagged for `chain_hash`.

### Recommendation
Enforce the chain equality check that the schemas already provide the data for: after matching a record by `nonce` in both `fetchWithdrawalHashBridgeIndexer` and `fetchWithdrawalHashFromApi`, additionally require `withdrawal.chain_id === toHotNetworkId(args.landingChain)` (or the equivalent CAIP-2 comparison) before accepting the hash as completed; otherwise treat it as `pending`/log a chain-mismatch warning instead of reporting completion.

### Proof of Concept
1. A withdrawal is created with `landingChain = eip155:1` (Ethereum) via `createWithdrawalIdentifier`.
2. `describeWithdrawal` resolves `nonce = N` for this withdrawal via `parseWithdrawalNonces`.
3. The bridge indexer (or HOT API) returns a withdrawal record with `nonce = N` but `chain_id` corresponding to a different chain (e.g., BSC `56`), due to a backend inconsistency.
4. `fetchWithdrawalHashBridgeIndexer`/`fetchWithdrawalHashFromApi` match on `nonce` only, ignore `chain_id`, and return the record's `hash`.
5. `describeWithdrawal` returns `{ status: "completed", txHash: formatTxHash(hash, "eip155:1") }`, misreporting an Ethereum withdrawal as completed using a hash/record that actually pertains to BSC, even though `chain_id` in the payload proves the mismatch was detectable.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L53-66)
```typescript
const HotApiWithdrawalSchema = v.object({
	hash: v.nullable(v.string()),
	nonce: v.string(),
	near_trx: v.string(),
	verified_withdraw: v.boolean(),
	chain_id: v.number(),
});

const HotApiWithdrawalResponseSchema = v.object({
	hash: v.nullable(v.string()),
	nonce: v.string(),
	near_trx: v.string(),
	withdrawals: v.array(HotApiWithdrawalSchema),
});
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L415-462)
```typescript
				if (bridgeIndexerHash !== null) {
					args.logger?.info("Bridge indexer found withdrawal hash", {
						withdrawalHash: bridgeIndexerHash,
						nearTxHash: args.tx.hash,
						nonce: nonce.toString(),
					});
					return {
						status: "completed",
						txHash: bridgeIndexerHash,
					};
				}
			} catch (error) {
				if (isTon) {
					args.logger?.error(
						"Bridge indexer failed unexpectedly, keeping TON withdrawal pending",
						{
							nearTxHash: args.tx.hash,
							nonce: nonce.toString(),
							error,
						},
					);
					return { status: "pending" };
				}

				// Bridge indexer failed, fallback to HOT API
				args.logger?.error(
					"Bridge indexer failed unexpectedly, trying HOT API fallback",
					{
						nearTxHash: args.tx.hash,
						nonce: nonce.toString(),
						error,
					},
				);
				const apiHash = await this.fetchWithdrawalHashFromApi(
					args.tx.hash,
					nonce,
					args.logger,
				);
				if (apiHash != null) {
					args.logger?.info("HOT API fallback found withdrawal hash", {
						withdrawalHash: apiHash,
						nearTxHash: args.tx.hash,
						nonce: nonce.toString(),
					});
					return {
						status: "completed",
						txHash: formatTxHash(apiHash, args.landingChain),
					};
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L505-539)
```typescript
	private async fetchWithdrawalHashBridgeIndexer(
		nearTxHash: string,
		nonce: string,
		logger?: ILogger,
	): Promise<string | null> {
		const { withdrawals } =
			await bridgeIndexer.httpClient.withdrawalsByNearTxHash(nearTxHash, {
				timeout: typeof window !== "undefined" ? 10_000 : 3000,
				logger,
			});

		const withdrawal = withdrawals.find((withdrawal) => {
			return withdrawal.nonce === nonce;
		});

		if (withdrawal === undefined) {
			logger?.info("HOT Bridge indexer withdrawal hash not found", {
				nearTxHash,
				nonce: nonce.toString(),
			});
			return null;
		}

		if (withdrawal.hash === null || withdrawal.hash === "") {
			logger?.info(
				`HOT Bridge returned invalid hash, expected a non empty string, got ${withdrawal.hash}`,
				{
					nearTxHash,
					nonce: nonce.toString(),
				},
			);
			return null;
		}

		return withdrawal.hash;
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L541-584)
```typescript
	private async fetchWithdrawalHashFromApi(
		nearTxHash: string,
		nonce: bigint,
		logger?: ILogger,
	): Promise<string | null> {
		try {
			const response = await withTimeout(
				() =>
					this.hotSdk.api.requestApi(
						`/api/v1/evm/bridge_withdrawal_hash?near_trx=${nearTxHash}`,
						{ method: "GET" },
					),
				{ timeout: HotBridge.API_FALLBACK_TIMEOUT_MS },
			);
			const data: unknown = await response.json();

			const parseResult = v.safeParse(HotApiWithdrawalResponseSchema, data);
			if (!parseResult.success) {
				logger?.debug("HOT API response parse failed", {
					issues: parseResult.issues,
				});
				return null;
			}

			const withdrawal = parseResult.output.withdrawals.find(
				(w) => w.nonce === nonce.toString(),
			);

			if (withdrawal?.hash) {
				const hash = withdrawal.hash.replace(/^0x/, "");
				if (isHex(hash)) {
					logger?.info("HOT withdrawal hash found via API fallback", {
						nearTxHash,
						nonce: nonce.toString(),
					});
					return hash;
				}
			}
			return null;
		} catch (error) {
			logger?.debug("HOT API fallback failed", { error, nearTxHash });
			return null;
		}
	}
```

**File:** packages/internal-utils/src/bridgeIndexer/bridgeIndexerHttpClient/types.ts (L13-25)
```typescript
const WithdrawalSchema = v.object({
	hash: v.nullable(v.string()),
	nonce: v.string(),
	chain_id: v.nullable(v.number()),
	withdraw_asset: v.nullable(v.string()),
	withdraw_token: v.nullable(v.string()),
	withdraw_amount: v.nullable(v.string()),
	receiver_address: v.nullable(v.string()),
	signature: v.nullable(v.string()),
	near_tx_time: v.nullable(v.string()),
	near_tx_block: v.nullable(v.string()),
	destination_chain_block: v.nullable(v.string()),
});
```
