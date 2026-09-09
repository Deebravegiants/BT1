### Title
Withdrawal reported as `completed` despite an unparseable/invalid destination tx hash - ([File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts])

### Summary
In `HotBridge.describeWithdrawal`, for non-EVM/non-Stellar/non-TON chains, when the on-chain contract's `getGaslessWithdrawStatus` call returns a string value that fails the `isHex` sanity check, the code explicitly logs that an "incorrect destination tx hash" was detected, yet still returns `{ status: "completed", txHash: null }` instead of treating the outcome as unresolved (`pending`) or failed.

### Finding Description
`describeWithdrawal` polls `this.hotSdk.getGaslessWithdrawStatus(nonce)` and branches on the returned `status`. For the non-EVM fallback branch: [1](#0-0) 

When `status` is a string that is not valid hex, the comment states "HOT returns hexified raw bytes without 0x prefix, any other value should be ignored," and a warning is logged that an "incorrect destination tx hash" was detected — yet the function still returns a `completed` status (with `txHash: null`) rather than falling through to `pending`/`failed` or attempting the API-indexer fallback that the `null`/`undefined` case below it uses. This breaks the equality between "status reported" and "actual on-chain outcome": the caller is told the withdrawal completed even though the value obtained could not be validated as a genuine destination transaction hash.

Contrast this with the branch immediately below it, which is reached only when `status` is not a string at all (e.g., `null`/`undefined`) and correctly falls back to the API indexer before ultimately returning `pending`: [2](#0-1) 

So a case that is explicitly known to be suspect (a non-hex string, logged as "incorrect") is treated more optimistically (`completed`) than a case that is merely absent (`null`, treated cautiously with an API-fallback check and default to `pending`). This is inconsistent and effectively means an ambiguous/invalid contract response is reported as a confirmed completion.

### Impact Explanation
`describeWithdrawal`'s `WithdrawalStatus` return value is consumed by SDK callers such as `sdk.waitForWithdrawalCompletion` to decide whether a withdrawal has settled on the destination chain. Per the report's list, this matches "a status or hash misreport making an integrator credit or refund twice": if an integrator treats `completed` as authoritative (as the naming and other branches encourage) and the underlying contract value was actually corrupted/invalid data rather than a genuine confirmation, the integrator could credit the withdrawal as done while funds have not actually settled on the destination chain, or fail to retry/investigate a stuck withdrawal.

### Likelihood Explanation
This path is reached whenever the HOT gasless-withdraw contract returns a status value for a non-EVM/non-Stellar/non-TON landing chain that is a string but fails `isHex`. The code comment itself acknowledges this is an anomalous/unexpected value ("any other value should be ignored"), implying it does occur in practice (e.g., malformed indexing, contract encoding changes, or non-hash sentinel values), and the current handling turns that anomaly into a `completed` report instead of `pending`.

### Recommendation
When `status` is a string that fails `isHex`, do not report `completed`. Instead, treat it the same as the `null`/`undefined` case: fall back to `fetchWithdrawalHashFromApi`, and if that also fails to resolve, return `{ status: "pending" }` (or a distinct `unknown`/`failed` status if warranted) rather than asserting completion with a `null` tx hash.

### Proof of Concept
1. Configure a withdrawal to a non-EVM, non-Stellar, non-TON chain (e.g., a chain other than those matched by `isEvm`/`Chains.Stellar`/`Chains.TON`).
2. Have `hotSdk.getGaslessWithdrawStatus` return a string value that is not valid hex (simulating corrupted/unexpected contract data), e.g., a non-hex string.
3. Call `describeWithdrawal`; observe the warning "HOT Bridge incorrect destination tx hash detected" is logged, but the function still resolves as `{ status: "completed", txHash: null }`. [3](#0-2) 
4. A caller/integrator relying on this status (e.g., via `waitForWithdrawalCompletion`) will treat the withdrawal as settled despite no verified destination transaction hash.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L465-486)
```typescript
		} else {
			// Fallback for other non EVM networks
			// Primary source: contract view method
			if (status === HotWithdrawStatus.Completed) {
				return { status: "completed", txHash: null };
			}
			if (typeof status === "string") {
				// HOT returns hexified raw bytes without 0x prefix, any other value should be ignored.
				if (!isHex(status)) {
					args.logger?.warn(
						"HOT Bridge incorrect destination tx hash detected",
						{
							value: status,
						},
					);
					return { status: "completed", txHash: null };
				}
				return {
					status: "completed",
					txHash: formatTxHash(status, args.landingChain),
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
