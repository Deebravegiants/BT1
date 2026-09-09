### Title
HOT Bridge `describeWithdrawal` reports `status: "completed"` for withdrawals whose on-chain status is neither `COMPLETED` nor a valid tx hash - ([File: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts])

### Summary
`HotBridge.describeWithdrawal` treats any unexpected, non-hex status string returned by the HOT contract view method as a completed withdrawal, breaking the equality "status reported == on-chain outcome." An integrator relying on this SDK call to decide whether to credit/refund a user can be told a withdrawal is `"completed"` while the destination-chain transfer never actually finalized.

### Finding Description
For non-EVM/non-Stellar/non-TON landing chains, `describeWithdrawal` uses the on-chain contract view (`hotSdk.getGaslessWithdrawStatus`) as the primary source of truth: [1](#0-0) 

```
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
                { value: status },
            );
            return { status: "completed", txHash: null };
        }
        ...
```

The enum only defines two known values, `COMPLETED` and `CANCELED`: [2](#0-1) 

The code's own comment states that "any other value should be ignored," yet the implementation does the opposite: whenever `status` is some string that is neither `COMPLETED` nor a valid hex tx-hash (e.g. an intermediate/pending state string, or any unexpected value the underlying `@hot-labs/omni-sdk` view method returns), the function still returns `{ status: "completed", txHash: null }` instead of falling through to `pending` or the API fallback (`fetchWithdrawalHashFromApi`, already used a few lines below for the `status == null` case). This maps an unverified/unknown on-chain outcome onto the "completed" status the caller consumes to decide on crediting the user or releasing downstream funds.

### Impact Explanation
`WithdrawalStatus` returned by `describeWithdrawal` is the canonical signal intents-sdk integrators use to determine whether a withdrawal has landed on the destination chain (see the equivalent EVM/Stellar/TON branch, which only reports `"completed"` once a real tx hash is found via bridge indexer or API — [3](#0-2) ). Reporting `"completed"` for a withdrawal whose actual on-chain status is unknown/unverified can cause an integrator to treat the withdrawal as finalized (e.g., stop retry/refund flows, or trigger downstream crediting) even though funds have not landed on the destination chain — matching the "status ... misreport making an integrator credit or refund twice" impact category.

### Likelihood Explanation
This path is reached automatically whenever the HOT contract view method returns any string value that is not the literal `"COMPLETED"`/`"CANCELED"` and not valid hex — no attacker action, privilege, or malicious input is required from the caller; it depends only on values legitimately produced by the third-party HOT view method for non-EVM chains (Bitcoin, TON-excluded set, Zcash-like chains, etc., i.e. any chain not in the `isEvm || Stellar || isTon` branch at line 404). Since the code path is explicitly reachable in normal operation (it is the intended fallback branch, just with the wrong terminal action), likelihood is moderate-to-high.

### Recommendation
Change the non-hex branch to return `{ status: "pending" }` (or route through the API fallback path already used elsewhere in the function) instead of `{ status: "completed", txHash: null }`, consistent with the code's own comment that unrecognized values "should be ignored." Only report `"completed"` when the status is verified as `HotWithdrawStatus.Completed` or a valid destination tx hash is obtained.

### Proof of Concept
1. Configure a `HotBridge` for a non-EVM/non-Stellar/non-TON landing chain (e.g. Bitcoin).
2. Mock `hotSdk.getGaslessWithdrawStatus` to resolve with a string that is not `"COMPLETED"`/`"CANCELED"` and not valid hex, e.g. `"pending_broadcast"`.
3. Call `bridge.describeWithdrawal(...)`.
4. Observe the returned value is `{ status: "completed", txHash: null }` even though the withdrawal never actually finalized on-chain — an integrator consuming this result would incorrectly treat the withdrawal as settled.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L404-463)
```typescript
		if (isEvm || args.landingChain === Chains.Stellar || isTon) {
			try {
				args.logger?.info("Fetching withdrawal hash from bridge indexer", {
					nearTxHash: args.tx.hash,
					nonce: nonce.toString(),
				});
				const bridgeIndexerHash = await this.fetchWithdrawalHashBridgeIndexer(
					args.tx.hash,
					nonce.toString(),
					args.logger,
				);
				if (bridgeIndexerHash !== null) {
					args.logger?.info("Bridge indexer found withdrawal hash", {
						withdrawalHash: bridgeIndexerHash,
						nearTxHash: args.tx.hash,
						nonce: nonce.toString(),
					});
					return {
						status: "completed",
						txHash: bridgeIndexerHash,
					};
				}
			} catch (error) {
				if (isTon) {
					args.logger?.error(
						"Bridge indexer failed unexpectedly, keeping TON withdrawal pending",
						{
							nearTxHash: args.tx.hash,
							nonce: nonce.toString(),
							error,
						},
					);
					return { status: "pending" };
				}

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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge-constants.ts (L1-4)
```typescript
export const HotWithdrawStatus = {
	Completed: "COMPLETED",
	Canceled: "CANCELED",
} as const;
```
