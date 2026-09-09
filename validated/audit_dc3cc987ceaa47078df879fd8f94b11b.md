### Title
Browser `describeWithdrawal` reports UTXO withdrawals as `completed` using a non-final `pending_sign_id`, terminating polling and misreporting the settled txid - ([File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts])

### Summary
For UTXO destination chains, `OmniBridge.describeWithdrawal` returns `status: "completed"` with `transfer.utxo_meta?.pending_sign_id` as `txHash` whenever `typeof window !== "undefined"`, even though the code's own comment states this value is not the finalized tx hash and can change if the BTC broadcast fails and is re-signed. Since `watchWithdrawal` (the SDK's polling driver) stops polling as soon as `status === "completed"` and resolves the caller's promise with that `txHash`, a browser-embedded integrator gets a terminal "completed" event bound to a hash that may never confirm on-chain, with no mechanism to reconcile it against the eventual real hash.

### Finding Description
The broken equality is: `txHash` returned to the caller as `status: "completed"` == the final settled destination transaction hash.

Code path:
- `describeWithdrawal` in [1](#0-0)  selects `transfer.utxo_meta?.pending_sign_id` as `txHash` for UTXO chains when running in a browser context, explicitly noting in the comment that "pending_sign_id is not the finalised tx hash. In rare cases, the hash may change if the BTC transfer fails to be submitted."
- It then unconditionally returns `{ status: "completed", txHash }` at [2](#0-1) , with no distinction from a truly finalized status.
- The `WithdrawalStatus` type documents `completed` as terminal, borrowing AWS "describe" API semantics ("I checked, and the withdrawal succeeded") at [3](#0-2) .
- The SDK's own polling driver `watchWithdrawal` treats `status === "completed"` as terminal and immediately resolves/returns `{ hash: status.txHash }`, ending the poll loop at [4](#0-3) .

Because the poll loop exits on the first "completed" response, if the same withdrawal's `pending_sign_id` later changes (e.g., broadcast fails, relayer re-signs and gets a new id/hash) or is superseded by `transfer.finalised?.transaction_hash`, the SDK never issues a follow-up check and never surfaces the corrected hash to a browser-context caller — the earlier "completed" emission is not invalidated, and there is no reconciliation event. An integrator who consumed the promise resolution (or a UI/callback fed by `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` in-browser) will treat the `pending_sign_id` as the settled txid.

No existing guard prevents this: `validateWithdrawal`, `compareAddresses`, `FeeExceedsAmountError`, `matchesRequest`, and the intents contract's own signature/nonce checks operate on intent construction and asset movement — none of them validate that a bridge's reported destination `txHash` is actually final. The UTXO branch's browser/non-browser split at lines 718-721 is the sole and intentional source of this divergence; it is not neutralized anywhere downstream.

### Impact Explanation
This is a status/hash misreport that can cause an integrator to treat a withdrawal as settled at a specific destination txid based on `pending_sign_id`, when the actual on-chain settlement may occur under a different hash (or fail to occur promptly). If the integrator credits internal ledgers, notifies users, or reconciles based on the "completed" event's `txHash`, and the real broadcast later differs, the same logical withdrawal can end up associated with two different "completed" hashes across separate reads (once from a browser-context caller, once from a backend re-check), with no signal in the SDK that the first was provisional. This matches the "status or hash misreport making an integrator credit or refund twice" impact bucket (High per the given severity taxonomy), rather than direct fund misdirection or intent manipulation. It is repeatable for every UTXO-chain withdrawal processed in a browser context whenever the underlying BTC broadcast has to be resubmitted.

### Likelihood Explanation
Preconditions: the withdrawal must land on a UTXO chain (e.g., Bitcoin) routed through `OmniBridge`, and the SDK's `describeWithdrawal`/`watchWithdrawal`/`createWithdrawalCompletionPromises` must be invoked in a browser-like environment (`typeof window !== "undefined"`) — e.g., a dApp frontend directly using `@defuse-protocol/intents-sdk`. The BTC re-sign/rebroadcast scenario is explicitly called out as occurring "in rare cases" by the code's own comment, i.e., it is an acknowledged, non-attacker-triggered but real occurrence of the underlying bridge's operation, not requiring a malicious relayer. No special privilege or cost is needed by the withdrawing user; it happens as a natural consequence of normal BTC broadcast failure/retry, and it is repeatable across any number of UTXO withdrawals executed in-browser.

### Recommendation
Do not report UTXO withdrawals as `completed` in browser contexts based solely on `pending_sign_id`. Options: (a) introduce a distinct non-terminal status (e.g., `"pending_broadcast"` with an advisory `txHash`) so `watchWithdrawal` keeps polling until `transfer.finalised?.transaction_hash` is available even in browser contexts; or (b) always resolve `completed` only from `transfer.finalised?.transaction_hash` regardless of environment, and expose the provisional `pending_sign_id` via a separate, explicitly non-terminal callback/field for UI "fast feedback" purposes, decoupled from the `WithdrawalStatus.completed` contract that `watchWithdrawal` treats as final.

### Proof of Concept
Vitest plan (mocking only HTTP via `BridgeAPI.prototype.getTransfer`):
1. Set `globalThis.window = {}` to simulate browser environment.
2. First call: mock `getTransfer` to return a transfer for `args.tx.hash`/`args.index` with `utxo_meta: { pending_sign_id: "A" }` and no `finalised`. Call `bridge.describeWithdrawal(wid)` and assert `{ status: "completed", txHash: "A" }`.
3. Second call (same `wid`, i.e., identical `landingChain`/`index`/`tx.hash` identity): mock `getTransfer` to now return `finalised: { transaction_hash: "B" }` (different value) with no `utxo_meta.pending_sign_id` or a changed one. Call `bridge.describeWithdrawal(wid)` again and assert `{ status: "completed", txHash: "B" }`.
4. Assert `"A" !== "B"` for the identical withdrawal identity, and that the SDK exposes no state/event indicating the first "completed" emission (`txHash: "A"`) was invalidated — i.e., both calls independently returned a terminal `completed` status with different `txHash` values for the same `WithdrawalIdentifier`.
5. Additionally, wrap step 2's mock in `watchWithdrawal`/`createWithdrawalCompletionPromises` to show the poll loop resolves and terminates on the first `"completed"` response (`txHash: "A"`), confirming no reconciliation path exists to reach `"B"` once the browser-context caller has already resolved.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L714-721)
```typescript
		} else if (isUtxoChain(destinationChain)) {
			// pending_sign_id is not the finalised tx hash. In rare cases, the hash may
			// change if the BTC transfer fails to be submitted. We return fast hash for FE and
			// wait for final one (transfer.finalised?.transaction_hash) for BE.
			txHash =
				typeof window !== "undefined"
					? transfer.utxo_meta?.pending_sign_id
					: transfer.finalised?.transaction_hash;
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L726-730)
```typescript
		if (!txHash) {
			return { status: "pending" };
		}

		return { status: "completed", txHash };
```

**File:** packages/intents-sdk/src/shared-types.ts (L443-457)
```typescript
/**
 * Represents the current state of a withdrawal as returned by bridge adapters.
 *
 * Error handling follows AWS SDK "describe" API patterns:
 * - **Thrown errors**: Infrastructure failures (network, auth, service unavailable).
 *   Meaning: "I couldn't check the status."
 * - **`failed` status**: Job-level failure reported by the bridge.
 *   Meaning: "I checked, and the withdrawal failed."
 *
 * @see https://docs.aws.amazon.com/AmazonS3/latest/userguide/batch-ops-job-status.html
 */
export type WithdrawalStatus =
	| { status: "pending" }
	| { status: "completed"; txHash: string | null }
	| { status: "failed"; reason: string };
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```
