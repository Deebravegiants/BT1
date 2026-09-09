### Title
HOT Bridge API fallback reports withdrawal as "completed" without checking `verified_withdraw` flag - (File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts)

### Summary
`HotBridge.fetchWithdrawalHashFromApi` parses the HOT API response with `HotApiWithdrawalResponseSchema`, which includes a `verified_withdraw: boolean` field per withdrawal entry, but the method never inspects that flag before returning the hash as proof of completion. `describeWithdrawal` then reports `{ status: "completed", txHash }` to the caller purely because a `hash` string exists, regardless of whether HOT has actually verified the withdrawal on the destination chain.

### Finding Description
In `fetchWithdrawalHashFromApi` [1](#0-0) , the code validates the response shape via `v.safeParse(HotApiWithdrawalResponseSchema, data)` and finds the matching withdrawal by `nonce`, then returns `withdrawal.hash` as soon as it is a non-empty hex string — the sibling `verified_withdraw` field carried by the same schema is read into `parseResult.output` but never checked. The schema itself explicitly models this field: [2](#0-1) .

The caller, `describeWithdrawal`, uses this unconditional hash to report the withdrawal as fully `"completed"` on both the EVM/Stellar/TON bridge-indexer-fallback path [3](#0-2)  and the generic non-EVM fallback path [4](#0-3) . This is the "status reported that is not the on-chain outcome" equality break: the caller-visible status (`completed`) is asserted based only on the presence of a hex string hash, not on the field the API uses to indicate the withdrawal was actually verified/finalized on the destination chain.

This mirrors the report's bug class at the abstraction level requested: a value taken from an untrusted/administrative-adjacent source (here, the HOT bridge API, analogous to the `organization.alias` value) is consumed for a security-relevant decision (reporting completion) while a companion field meant to gate/qualify that value (`verified_withdraw`, analogous to proper escaping before use) is silently dropped.

### Impact Explanation
`watchWithdrawal` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` stops polling and returns a final transaction hash the moment `describeWithdrawal` reports `"completed"` [5](#0-4) . If HOT's API returns a `hash` for a withdrawal whose `verified_withdraw` is `false` (e.g. broadcast but not yet confirmed/finalized on the destination chain, or later reverted), an integrator relying on this SDK will treat the withdrawal as done — potentially crediting a user, releasing a corresponding off-chain balance, or unlocking downstream funds — before the withdrawal is actually settled. This falls into the "status or hash misreport making an integrator credit or refund twice" High-impact category from the rules.

### Likelihood Explanation
No malicious actor input is required — this is triggered purely by the normal HOT API response shape during the ordinary fallback path (used whenever the primary contract view or bridge indexer is unavailable/returns null, which the existing tests show is a supported, reachable code path). Any withdrawal that has a `hash` assigned before verification completes will trigger the misreport.

### Recommendation
In `fetchWithdrawalHashFromApi`, check `withdrawal.verified_withdraw === true` before returning the hash as proof of completion; if `verified_withdraw` is `false`, treat the withdrawal as still pending (return `null`) rather than surfacing a hash that implies finality.

### Proof of Concept
1. Contract view (`getGaslessWithdrawStatus`) returns `null`/pending and the bridge indexer has no record (as in the existing test `"returns completed via API fallback when contract returns null but API has hash"` at [6](#0-5) ).
2. HOT API `/api/v1/evm/bridge_withdrawal_hash` responds with a withdrawal entry containing a `hash` but `verified_withdraw: false` (e.g. a broadcast-but-unconfirmed or since-orphaned transaction).
3. `fetchWithdrawalHashFromApi` returns the hash unconditionally since it only checks `withdrawal?.hash` and `isHex(hash)`.
4. `describeWithdrawal` returns `{ status: "completed", txHash: formatTxHash(apiHash, ...) }`.
5. `watchWithdrawal` resolves as completed, and any integrator logic gated on this SDK's completion status (e.g., releasing custody or crediting a ledger) proceeds despite the withdrawal not being verified on-chain.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L53-59)
```typescript
const HotApiWithdrawalSchema = v.object({
	hash: v.nullable(v.string()),
	nonce: v.string(),
	near_trx: v.string(),
	verified_withdraw: v.boolean(),
	chain_id: v.number(),
});
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L448-463)
```typescript
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
				}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L489-499)
```typescript
			const apiHash = await this.fetchWithdrawalHashFromApi(
				args.tx.hash,
				nonce,
				args.logger,
			);
			if (apiHash != null) {
				return {
					status: "completed",
					txHash: formatTxHash(apiHash, args.landingChain),
				};
			}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L541-579)
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
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.test.ts (L669-720)
```typescript
		it("returns completed via API fallback when contract returns null but API has hash", async () => {
			const hotSDK = new HotOmniSdk({
				logger: console,
				evmRpc: {},
				nearRpc: [],
				async executeNearTransaction() {
					throw new Error("not implemented");
				},
			});

			const bridge = new HotBridge({
				envConfig: configsByEnvironment.production,
				hotSdk: hotSDK,
			});

			vi.spyOn(hotSDK.near, "parseWithdrawalNonces").mockResolvedValue([1n]);
			vi.spyOn(hotSDK, "getGaslessWithdrawStatus").mockResolvedValue(null);
			mockBridgeIndexerFailure();
			vi.spyOn(hotSDK.api, "requestApi").mockResolvedValue(
				new Response(
					JSON.stringify({
						hash: "0xDEADBEEF",
						nonce: "1",
						near_trx: "txhash",
						withdrawals: [
							{
								hash: "0xDEADBEEF",
								nonce: "1",
								near_trx: "txhash",
								verified_withdraw: true,
								chain_id: 56,
							},
						],
					}),
				),
			);

			const wid = bridge.createWithdrawalIdentifier({
				withdrawalParams: {
					assetId: BNB_NATIVE_ASSET_ID,
					amount: 100n,
					destinationAddress: zeroAddress,
					feeInclusive: false,
				},
				index: 0,
				tx: { hash: "txhash", accountId: "test.near" },
			});

			const result = await bridge.describeWithdrawal(wid);

			expect(result).toEqual({ status: "completed", txHash: "0xDEADBEEF" });
		});
```
