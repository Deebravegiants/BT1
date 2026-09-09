### Title
HOT Bridge reports a withdrawal as "completed" using an unverified API-reported hash, ignoring the `verified_withdraw` flag - (File: `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts`)

### Summary
`HotBridge.describeWithdrawal` falls back to the HOT Labs REST API (`/api/v1/evm/bridge_withdrawal_hash`) whenever the on-chain contract view (`getGaslessWithdrawStatus`) and the bridge indexer cannot confirm a withdrawal. The API's response schema explicitly carries a `verified_withdraw` boolean per withdrawal entry, but `fetchWithdrawalHashFromApi` never reads or checks that field before the SDK reports `status: "completed"` with the API-supplied `txHash`.

### Finding Description
The Zod/valibot schema for the HOT API response models the field that is supposed to indicate whether the destination-chain transfer was actually verified: [1](#0-0) 

However, `fetchWithdrawalHashFromApi` only looks up the matching `nonce` and returns `withdrawal.hash` if present and hex-formatted — it never inspects `withdrawal.verified_withdraw`: [2](#0-1) 

That unverified hash is then propagated straight into a `"completed"` status by the caller, for both the EVM/Stellar/TON path and the "other chains" fallback path: [3](#0-2) [4](#0-3) 

The unit test explicitly demonstrates this: even though the sample fixture sets `verified_withdraw: true`, the field is not asserted or filtered on anywhere in the implementation, meaning the same code path would equally accept `verified_withdraw: false`: [5](#0-4) 

The equality broken here is: *a status reported by the SDK ("completed", with a specific `txHash`) is not guaranteed to be the actual on-chain outcome*, because the API is a third-party, off-chain data source and the SDK discards the one signal (`verified_withdraw`) that would let it distinguish a confirmed transfer from an unconfirmed/pending one.

### Impact Explanation
An integrator that calls `sdk.waitForWithdrawalCompletion` (which ultimately calls `describeWithdrawal`) receives `{ status: "completed", txHash }` and, per the SDK's documented contract, may treat the withdrawal as finalized — e.g., releasing a corresponding off-chain credit, marking an order as fulfilled, or stopping any compensating action — while the underlying transfer may not actually be verified on the destination chain. This matches the "status or hash misreport making an integrator credit or refund twice" impact category (High), since the same nonce being reported "completed" prematurely, followed by an eventual real settlement (possibly with a different hash if the initial one referenced an invalid/duplicate broadcast), can cause double crediting or reliance on a hash that never lands.

### Likelihood Explanation
This code path is only reached when both the primary on-chain check (`getGaslessWithdrawStatus`) and the bridge indexer fail or return null/pending — a plausible, unprivileged condition during indexer downtime, network partition, or normal propagation delay, not requiring any malicious actor. No attacker action is needed: any caller polling `describeWithdrawal` during a window where the bridge indexer is behind or erroring will hit this fallback and can receive a "completed" status based solely on the third-party API's optimistic/unverified record.

### Recommendation
In `fetchWithdrawalHashFromApi`, propagate and check `withdrawal.verified_withdraw` before returning a hash; if `verified_withdraw` is `false`, return `null` (or a distinct "pending/unverified" signal) instead of treating the hash as confirming a completed withdrawal. Ensure `describeWithdrawal` only reports `"completed"` when the hash source has verified the transfer (bridge indexer, on-chain contract state, or `verified_withdraw === true`).

### Proof of Concept
1. Trigger the fallback path: mock `getGaslessWithdrawStatus` to return `null` and make the bridge indexer fail (as in the existing test setup at `hot-bridge.test.ts:679-704`).
2. Have the HOT API return a withdrawal entry with `hash: "0xDEADBEEF"` and `verified_withdraw: false`.
3. Call `bridge.describeWithdrawal(wid)`.
4. Observe the result is still `{ status: "completed", txHash: "0xDEADBEEF" }`, identical to the `verified_withdraw: true` case in the existing test at `hot-bridge.test.ts:717-719`, proving the flag has no effect on the reported status.

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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.test.ts (L684-719)
```typescript
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
```
