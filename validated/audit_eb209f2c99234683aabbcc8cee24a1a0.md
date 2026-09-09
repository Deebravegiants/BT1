### Title
Withdrawal reported as `completed` when destination status is unparsable, without asset-level confirmation - (File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts)

### Summary
`HotBridge.describeWithdrawal` reports a withdrawal as `"completed"` in cases where the on-chain destination outcome could not actually be verified, breaking the equality "status reported == actual on-chain outcome" called out as an analog class in the report.

### Finding Description
In `HotBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts:375-503`), for non-EVM/Stellar/TON chains the code falls back to a raw contract view-call result (`status`, typed as `unknown`) returned by `this.hotSdk.getGaslessWithdrawStatus` [1](#0-0) . When that value is a string but fails the `isHex` check — i.e. it is not a valid destination transaction hash — the code logs a warning and still returns `{ status: "completed", txHash: null }` instead of treating it as unresolved/pending: [2](#0-1) 

This means "completed" is reported purely because the contract returned *some* non-empty string, not because a verified destination transfer hash was obtained. The consumer of this status, `watchWithdrawal` in `packages/intents-sdk/src/core/withdrawal-watcher.ts`, treats `status === "completed"` as terminal success and immediately resolves the awaited promise with `{ hash: status.txHash }` (here `null`), stopping all further polling: [3](#0-2) 

### Impact Explanation
An integrator relying on `sdk.waitForWithdrawalCompletion` / `watchWithdrawal` to decide whether to credit a user or release custody would treat this withdrawal as finalized based on an unverifiable contract response, even though no destination hash was confirmed and the tokens may not have actually landed. This matches the report's "status or hash misreport making an integrator credit or refund twice" impact category (High), since polling stops and no further verification is attempted once "completed" is returned.

### Likelihood Explanation
This path is reached only for non-EVM/Stellar/TON chains when the bridge indexer/API fallback is not used and the underlying HOT contract view method returns a malformed/garbage string instead of `HotWithdrawStatus.Completed`, `Canceled`, or a valid hex hash. This is a corner case dependent on the external HOT contract/API behavior, which is a third-party dependency outside this repo's control — reducing the likelihood that this is an easily triggerable, in-scope root cause versus an edge-case defensive branch.

### Recommendation
When the raw status value fails `isHex` validation, return `{ status: "pending" }` (or a dedicated unknown/failed status) instead of `{ status: "completed", txHash: null }`, and continue polling or fall back to the HOT API before declaring completion.

### Proof of Concept
Not independently reproducible from this repo alone: triggering the branch requires the external HOT bridge contract's `getGaslessWithdrawStatus` to return a non-hex string value, which is controlled by a third-party (HOT) system outside this codebase's scope. This weakens confidence that it is a concretely exploitable, in-scope defect rather than a defensive-but-imperfect fallback for an assumed-well-behaved external dependency.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L389-391)
```typescript
		const status: unknown = await this.hotSdk.getGaslessWithdrawStatus(
			nonce.toString(),
		);
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L471-486)
```typescript
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```
