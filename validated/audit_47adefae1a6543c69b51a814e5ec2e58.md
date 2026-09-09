Based on my investigation, I found a concrete unpatched analog in the HOT bridge's API fallback status logic.

### Title
Withdrawal status "completed" reported without checking `verified_withdraw` on-chain verification flag - (File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts)

### Summary
`HotBridge.fetchWithdrawalHashFromApi` parses a HOT API response that explicitly carries a `verified_withdraw: boolean` field per withdrawal record, but never reads or checks that field before treating the withdrawal as `completed`. The equality broken is: *status reported* (`"completed"`) *must equal the on-chain verified outcome*, but here it is derived solely from "hash present and hex-formatted", independent of whether HOT itself considers the withdrawal `verified_withdraw: true`.

### Finding Description
The schema declares the field but the consuming logic ignores it entirely: [1](#0-0) 

In `fetchWithdrawalHashFromApi`, the code finds the withdrawal by `nonce` match and returns the hash as soon as it is non-null and passes `isHex`, with no reference to `withdrawal.verified_withdraw`: [2](#0-1) 

This is reachable from `describeWithdrawal`, which is the primary fallback path used for EVM/Stellar/TON withdrawals when the bridge indexer fails, and for other non-EVM chains when the contract view method returns null: [3](#0-2) [4](#0-3) 

The existing test suite only exercises `verified_withdraw: true` cases, so nothing currently catches the gap: [5](#0-4) 

### Impact Explanation
An integrator/relayer/consumer of this SDK calls `describeWithdrawal` to decide whether a cross-chain withdrawal has landed on the destination chain, in order to release funds, mark an order complete, or unblock the next step in a flow. If the HOT API returns a withdrawal entry with a hash but `verified_withdraw: false` (e.g., a submitted-but-not-yet-confirmed, or later reversed/invalid relay attempt), the SDK will still report `{ status: "completed", txHash }`. A caller that treats "completed" as final can credit or release funds based on a transfer that HOT itself has not verified as landed — this matches the High-severity impact class "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
This path only triggers under specific but realistic conditions: the bridge indexer must fail/return no hash (already a supported fallback branch) or the on-chain view method must return null, and the HOT API fallback must return a hash before verification completes. Given the schema explicitly transmits `verified_withdraw` (implying HOT's backend distinguishes verified vs. unverified withdrawals), it's plausible the field is populated `false` in real transient states, making this reachable in normal fallback operation, not merely a theoretical adversarial condition.

### Recommendation
In `fetchWithdrawalHashFromApi`, require `withdrawal.verified_withdraw === true` in addition to a valid hex hash before returning the hash / reporting `completed`; otherwise return `null` (fall through to `pending`), consistent with how `parsedError`/`bridgeIndexer` paths already avoid reporting completion on unconfirmed data.

### Proof of Concept
1. Mock `hotSDK.near.parseWithdrawalNonces` to resolve to `[1n]` and `hotSDK.getGaslessWithdrawStatus` to resolve `null`.
2. Force the bridge indexer path to fail (as in `mockBridgeIndexerFailure()`).
3. Mock `hotSDK.api.requestApi` to resolve a `Response` whose JSON body is:
```json
{
  "hash": "0xDEADBEEF",
  "nonce": "1",
  "near_trx": "txhash",
  "withdrawals": [
    { "hash": "0xDEADBEEF", "nonce": "1", "near_trx": "txhash", "verified_withdraw": false, "chain_id": 56 }
  ]
}
```
4. Call `bridge.describeWithdrawal(wid)`.
5. Observe the result is `{ status: "completed", txHash: "0xDEADBEEF" }` even though `verified_withdraw` is `false` — demonstrating the status/hash is reported without regard to HOT's own verification flag.

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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L488-500)
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
		}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L565-583)
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
		} catch (error) {
			logger?.debug("HOT API fallback failed", { error, nearTxHash });
			return null;
		}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.test.ts (L471-490)
```typescript
			const requestApiSpy = vi
				.spyOn(hotSDK.api, "requestApi")
				.mockResolvedValue(
					new Response(
						JSON.stringify({
							hash: "4a810b9459ce2e73d74b497598744e3cb54f50715f90ef07a66397468a60b121",
							nonce: "1",
							near_trx: "near-tx-hash",
							withdrawals: [
								{
									hash: "4a810b9459ce2e73d74b497598744e3cb54f50715f90ef07a66397468a60b121",
									nonce: "1",
									near_trx: "near-tx-hash",
									verified_withdraw: true,
									chain_id: 1117,
								},
							],
						}),
					),
				);
```
