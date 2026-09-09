### Title
`HotBridge.describeWithdrawal` reports a withdrawal as "completed" when the on-chain status value fails validation, instead of raising an error - ([File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts])

### Summary
`HotBridge.describeWithdrawal` polls the HOT contract for a withdrawal's on-chain status. For non-EVM/non-Stellar/non-TON chains, when the returned `status` is a string that is expected to be a hex-encoded destination transaction hash, the code detects that the value is *not* valid hex, logs a warning, and then reports the withdrawal as `{ status: "completed", txHash: null }` instead of treating the malformed/unexpected value as an error condition. This breaks the equality "reported status == verified on-chain outcome."

### Finding Description
`describeWithdrawal` fetches the raw status via `this.hotSdk.getGaslessWithdrawStatus(nonce.toString())` and, for the "other non-EVM networks" branch, inspects the string result: [1](#0-0) 

Specifically:
```
if (typeof status === "string") {
    // HOT returns hexified raw bytes without 0x prefix, any other value should be ignored.
    if (!isHex(status)) {
        args.logger?.warn(
            "HOT Bridge incorrect destination tx hash detected",
            { value: status },
        );
        return { status: "completed", txHash: null };
    }
    return {
        status: "completed",
        txHash: formatTxHash(status, args.landingChain),
    };
}
```

This is the same anti-pattern described in the external report: the code detects an anomaly (a status value that is not the expected hex tx hash — i.e., unparseable/unexpected data from an untrusted external source, the HOT SDK/contract) and logs it as an error/warning, but then **continues** to report the withdrawal outcome as `"completed"` rather than propagating an error or falling back to `"pending"`. The consumer of `WithdrawalStatus` (`sdk.waitForWithdrawalCompletion`, `sdk.createWithdrawalCompletionPromises`) treats `status: "completed"` as the authoritative on-chain outcome and resolves the completion promise with `txHash: null`, exactly as it would for a legitimately completed withdrawal with an unrecoverable hash. [2](#0-1) [3](#0-2) 

The `WithdrawalWatchError`/retry machinery in `watchWithdrawal` only triggers on *thrown* errors or `status: "failed"`; a value of `"completed"` short-circuits polling immediately, so there is no opportunity for the SDK to retry or surface the anomaly to the caller.

### Impact Explanation
`describeWithdrawal`'s "completed" status is used by integrators to decide when a withdrawal is settled on the destination chain (e.g., to update ledgers, release holds, notify users, or stop retry/monitoring). If the HOT API/contract ever returns a malformed or unexpected status string (a bug, an API change, a transient corrupted response, or a value from a source the SDK does not fully trust), the SDK will falsely report the withdrawal as `"completed"` with `txHash: null`, even though the destination-chain outcome was never verified. This is a status misreport that can cause an integrator to treat funds as delivered when they may not be, or to stop monitoring a withdrawal that is actually still pending or failed — a class of bug matching "a status or hash misreport making an integrator credit or refund twice" (High impact).

### Likelihood Explanation
This path only triggers for the "other non-EVM networks" fallback (chains that are not EVM, Stellar, or TON), and only when the HOT gasless-withdraw status API returns a string value that fails the `isHex` check. This depends on the reliability of an external, HOT-controlled data source, so it is not attacker-directly-controllable from this repo's code, but the code explicitly anticipates receiving such "incorrect" values (per its own comment and warning log) and still treats them as a successful completion rather than an error/pending state — indicating the developers were aware of the anomaly class but chose not to fail safe.

### Recommendation
Do not resolve `describeWithdrawal` as `"completed"` when the destination hash cannot be validated. Instead, either:
- Return `{ status: "pending" }` (matching the "unknown"/inconclusive semantics already used elsewhere in the same function, e.g. `status === HotWithdrawStatus.Canceled` and other fallback branches) so the watcher continues polling, or
- Throw/raise an explicit error (e.g., a new `HotWithdrawalInvalidStatusError`) so the caller is forced to handle the anomalous condition instead of silently treating it as a successful completion.

### Proof of Concept
Not applicable as a standalone exploit — this is a logic/data-validation defect reachable only when the upstream HOT withdrawal-status API returns a non-hex string for a non-EVM/non-Stellar/non-TON withdrawal. The defect is demonstrated purely by code inspection of `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts` lines 471-481: the `isHex(status)` check failing routes into a `return { status: "completed", txHash: null }` rather than an error path, which can be confirmed by unit-testing `describeWithdrawal` with a mocked `getGaslessWithdrawStatus` resolving to a non-hex string for a non-EVM chain (e.g., Sui/Aptos-class chain not covered by the earlier `isEvm || Stellar || isTon` branch) and observing the returned `status` field is `"completed"`.

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

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L27-41)
```typescript
	it("supports single withdrawal", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal).mockResolvedValueOnce({
			status: "completed",
			txHash: "fake-dest-hash",
		});

		const result = sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: withdrawalParams,
		});

		await expect(result).resolves.toEqual({ hash: "fake-dest-hash" });
	});
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-53)
```typescript
	try {
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

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

					return POLL_PENDING;
```
