### Title
Non-hex/garbage withdrawal status from HOT Bridge contract is misreported as "completed" - (File: `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts`)

### Summary
`HotBridge.describeWithdrawal()` treats any non-hex string returned by the HOT contract's `getGaslessWithdrawStatus` view call as a successfully completed withdrawal, even though it explicitly logs the value as "incorrect". This turns an ambiguous/invalid on-chain read into a false "completed" status, which is the same class of defect as the reported bug: the SDK's reported state diverges from the true on-chain outcome, but here it manifests as a premature success report rather than a balance drift.

### Finding Description
In the non-EVM/non-Stellar/non-TON branch of `describeWithdrawal`, the contract's status value is inspected: [1](#0-0) 

When `status` is a string but fails the `isHex()` check, the code logs a warning that "HOT Bridge incorrect destination tx hash detected" and then still returns `{ status: "completed", txHash: null }` — i.e., it reports the withdrawal as finished. This is inconsistent with the surrounding logic: `HotWithdrawStatus.Completed` (a known enum sentinel) is the legitimate "done" signal, and any other string is meant to represent a destination tx hash. A malformed/non-hex string is neither of those — it indicates the SDK could not correctly interpret the on-chain status — yet it is coerced into "completed" instead of falling through to `pending` or the API-indexer fallback that follows for the `null`/no-match case.

This breaks the equality between "value returned by `describeWithdrawal`" and "actual on-chain settlement state": callers of `watchWithdrawal` (see `packages/intents-sdk/src/core/withdrawal-watcher.ts`) resolve the withdrawal promise as soon as `status === "completed"` is observed: [2](#0-1) 

An integrator relying on this resolved promise (e.g., to credit a user's off-chain balance, release an escrow, or mark an order fulfilled) would do so based on a status that was, by the code's own admission, not correctly determined.

### Impact Explanation
This matches the "High" impact category: "a status or hash misreport making an integrator credit or refund twice." If the underlying withdrawal is actually still pending or failed on the destination chain, but the SDK reports `completed`, downstream systems consuming `waitForWithdrawalCompletion`/`watchWithdrawal` results could release funds, mark obligations settled, or stop retry/monitoring logic prematurely — leading to stuck funds or double-crediting when the transaction eventually does (or does not) land.

### Likelihood Explanation
Likelihood depends on how often the HOT contract's view method returns a non-hex string for non-EVM/Stellar/TON landing chains (e.g., transient RPC serialization issues, upgraded contract formats, or malformed encodings). The code path explicitly anticipates this case (there is a dedicated warning log for it), indicating it is a known, reachable occurrence rather than a purely theoretical one.

### Recommendation
When `status` is a string but fails `isHex()`, do not short-circuit to `{ status: "completed", txHash: null }`. Instead, fall through to the existing API-indexer fallback path (as already done for the `null` contract-status case), and only report `completed` once a verifiable hash or the `HotWithdrawStatus.Completed` sentinel is obtained.

### Proof of Concept
1. HOT Bridge contract's `getGaslessWithdrawStatus` returns a malformed string (not `HotWithdrawStatus.Completed`, not valid hex) for a pending non-EVM withdrawal.
2. `describeWithdrawal` hits the `typeof status === "string"` branch, fails `isHex(status)`, logs a warning, and returns `{ status: "completed", txHash: null }`.
3. `watchWithdrawal` immediately resolves with `{ hash: null }` as if the withdrawal succeeded.
4. An integrator polling via `sdk.createWithdrawalCompletionPromises` (per `docs/design/rfc-batch-withdrawal-granular-control.md`) marks the withdrawal as settled and credits the user, while the actual destination-chain transfer may still be pending or may never land.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```
