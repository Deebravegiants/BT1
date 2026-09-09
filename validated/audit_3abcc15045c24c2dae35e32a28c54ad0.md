## Title
`HotBridge.describeWithdrawal` misreports withdrawal as `completed` for any non-hex contract status string - (File: `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts`)

### Summary
`HotBridge.describeWithdrawal` uses an unbounded `typeof status === "string"` check as the "non-EVM chain" fallback branch when it should only trust the contract view method's status when it actually represents a settled hash. Any string that isn't a recognized enum value and isn't a valid hex tx hash still gets reported as `status: "completed"`, contradicting the code's own comment that such values "should be ignored."

### Finding Description
In `describeWithdrawal`, the value returned by `this.hotSdk.getGaslessWithdrawStatus(...)` is typed as `unknown` and only two enum values are explicitly handled (`Completed`, `Canceled`): [1](#0-0) 

In the fallback branch for non-EVM/non-Stellar/non-TON chains, the contract view-method result is consulted as the "Primary source" of truth: [2](#0-1) 

The comment explicitly states "HOT returns hexified raw bytes without 0x prefix, any other value should be ignored," implying that a non-hex string should NOT be treated as a completed withdrawal. However, the code does the opposite: regardless of whether `isHex(status)` is true or false, the function always returns `{ status: "completed", ... }` for any string value — the only difference is whether `txHash` is `null` or a formatted hash. There is no branch that returns `{ status: "pending" }` when the status string is not a recognized terminal state and not a valid hex hash. So any status string the contract might return that is not `COMPLETED`, `CANCELED`, or a valid hex hash (e.g., an in-progress/queued marker, or a malformed/garbage value) is misreported as `"completed"`.

This breaks the intended equality: **status returned to caller == actual on-chain settlement outcome**. The caller (an integrator polling `describeWithdrawal`) has no way to distinguish a genuinely settled withdrawal from one that is still pending, because both paths return `"completed"`.

### Impact Explanation
`describeWithdrawal` results are consumed by callers/integrators (e.g., via `waitForWithdrawalCompletion`-style flows) to determine when to stop polling and treat funds as delivered. A premature `"completed"` report for a withdrawal that has not actually settled on-chain can cause an integrator to credit the user or release downstream funds before the withdrawal is actually finalized — a status misreport matching the "High" impact category ("a status or hash misreport making an integrator credit or refund twice").

### Likelihood Explanation
This path executes for every non-EVM, non-Stellar, non-TON chain that falls through to the "Fallback for other non EVM networks" branch whenever the bridge indexer/API paths aren't used, and is driven entirely by whatever value the external HOT contract's view method returns — a value the SDK does not fully control or validate. Any deviation from the two expected enum strings or a valid hex string (which is plausible for an evolving external contract) silently degrades to a false "completed" report, without needing malicious behavior from any actor.

### Recommendation
- **Short term:** In the fallback branch, only return `{ status: "completed", ... }` when `status` matches `HotWithdrawStatus.Completed` or is a valid hex hash. For any other string that isn't recognized (including the current "ignored" case), return `{ status: "pending" }` instead of `"completed"`.
- **Long term:** Type and validate the return value of `getGaslessWithdrawStatus` with a schema (similar to `HotApiWithdrawalResponseSchema`), enumerating all statuses the contract can legitimately return, and map unknown/unexpected values to `"pending"` (fail-safe) rather than `"completed"` (fail-open).

### Proof of Concept
1. Withdrawal is submitted on a non-EVM/non-Stellar/non-TON chain covered by the `else` branch (e.g., a chain relying purely on the contract view method).
2. `this.hotSdk.getGaslessWithdrawStatus(nonce)` returns a string that is neither `"COMPLETED"`, `"CANCELED"`, nor valid hex (e.g., an intermediate/queued marker used by a future contract version, or corrupted API data).
3. Code path: `typeof status === "string"` is true, `isHex(status)` is false, so it logs a warning but still returns `{ status: "completed", txHash: null }`. [3](#0-2) 
4. The integrator polling `describeWithdrawal` sees `status: "completed"` and stops polling / credits the withdrawal, even though the funds have not actually landed on the destination chain.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L389-398)
```typescript
		const status: unknown = await this.hotSdk.getGaslessWithdrawStatus(
			nonce.toString(),
		);
		// stop polling in case withdrawal is cancelled
		if (status === HotWithdrawStatus.Canceled) {
			return {
				status: "failed",
				reason: "Withdrawal was cancelled",
			};
		}
```

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
