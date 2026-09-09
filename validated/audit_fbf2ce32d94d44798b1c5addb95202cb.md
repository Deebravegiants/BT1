### Title
HOT Bridge trusts unverified withdrawal hash from fallback API, reporting "completed" without checking `verified_withdraw` - (File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts)

### Summary
`HotBridge.fetchWithdrawalHashFromApi` parses the HOT API response with a schema that includes a `verified_withdraw: boolean` field, but never inspects that field before returning the withdrawal hash as authoritative. As a result, `describeWithdrawal` can report `{ status: "completed", txHash }` for a withdrawal that the HOT API itself has not marked as verified, breaking the equality between "reported status" and "actual on-chain outcome" that the caller (integrator/relayer) relies on to credit or close out a withdrawal.

### Finding Description
`HotApiWithdrawalSchema` explicitly models `verified_withdraw` and `chain_id`: [1](#0-0) 

However, `fetchWithdrawalHashFromApi` only matches by `nonce` and checks that `withdrawal.hash` is present/hex — it never reads or asserts on `withdrawal.verified_withdraw`: [2](#0-1) 

This function is used as the fallback source of truth in `describeWithdrawal` in two places: once when the bridge indexer throws for EVM/Stellar/TON chains, and once as the fallback for non-EVM chains when the on-chain contract view returns null/pending: [3](#0-2) [4](#0-3) 

In both call sites, the returned hash is treated as proof of completion (`status: "completed"`) with no gating on `verified_withdraw`. Since `getGaslessWithdrawStatus` (the primary/contract-level source) can legitimately be pending/null while the withdrawal has only been submitted (not yet confirmed as executed on the destination chain), a HOT API response with `verified_withdraw: false` for that nonce would still cause the SDK to declare the withdrawal `"completed"` with a hash, purely because a hash string exists in the response.

### Impact Explanation
`describeWithdrawal`'s output feeds `watchWithdrawal`/`waitForWithdrawalCompletion`-style polling used by integrators to decide when funds have arrived and to release/credit downstream state: [5](#0-4) . If the reported "completed" status does not correspond to what actually happened on-chain (an unverified withdrawal misreported as verified), an integrator could credit the withdrawal, release additional funds, or close monitoring prematurely, matching the "status or hash misreport making an integrator credit or refund twice" High-impact category from the rules.

### Likelihood Explanation
This path is only reachable in specific fallback conditions (bridge indexer failure for EVM/Stellar/TON, or contract view returning null for other non-EVM chains), and requires the third-party HOT API to actually return a withdrawal entry with `hash` set but `verified_withdraw: false` for the queried nonce — a response shape controlled by the HOT bridge's own API/relayer, not by an arbitrary unprivileged attacker. This weakens confidence that it is an easily-triggerable, in-scope-only bug versus a defect stemming from trusting the HOT API's data model, which the exclusion rules classify as "trust assumptions about ... bridge APIs" and out of scope. I could not find any test in `hot-bridge.test.ts` exercising `verified_withdraw: false`, so it's unclear whether this is a known/accepted behavior or an oversight, and I could not fully verify whether the HOT SDK/relayer ever legitimately returns `hash` with `verified_withdraw: false` in practice.

### Recommendation
In `fetchWithdrawalHashFromApi`, only treat a withdrawal hash as authoritative when `withdrawal.verified_withdraw === true`; otherwise fall through and return `null` (letting `describeWithdrawal` return `"pending"`). Additionally, cross-check `withdrawal.chain_id` against the expected destination chain for the asset being withdrawn before trusting the hash.

### Proof of Concept
Given a mocked HOT API response for a matching `nonce` with `hash` set but `verified_withdraw: false` and correct `chain_id`, `fetchWithdrawalHashFromApi` currently returns the hash unconditionally (see lines 565–579), causing `describeWithdrawal` to return `{ status: "completed", txHash }` instead of `{ status: "pending" }`. This mirrors the existing test pattern at [6](#0-5)  but with `verified_withdraw: false` substituted, which the current implementation does not distinguish from the `true` case.

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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L439-463)
```typescript
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
				}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L488-499)
```typescript
			// Fallback: API indexer (when contract returns null/pending)
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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L565-579)
```typescript
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-47)
```typescript
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
