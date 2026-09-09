### Title
Delimiter-less cache key allows storage-deposit fee bypass across different token/destination pairs - (File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts)

### Summary
`DirectBridge.getCachedStorageDepositValue` builds its LRU cache key by naive string concatenation of `contractId` and `accountId` with no delimiter, so two distinct `(tokenAccountId, destinationAddress)` pairs that yield the same concatenated string share one cache slot. This mirrors the Wasmtime pooling-allocator bug class: state established for one "instance" (one real token/account pair) is left in a shared slot and can be handed, unrefreshed, to a different instance whose actual on-chain storage-deposit state was never checked.

### Finding Description
`estimateWithdrawalFee` calls: [1](#0-0) 

which resolves through: [2](#0-1) 

The cache key is `` `${contractId}${accountId}` `` with no separator. `contractId` comes from the caller-supplied `assetId` (via `utils.parseDefuseAssetId`) and `accountId` is the caller-supplied `destinationAddress`. Because NEAR account IDs freely use `.`/`-`/`_` characters, two different valid `(contractId, accountId)` splits can concatenate to the identical string, e.g. `contractId="usdc.near"`, `accountId="bob.near"` produces the same key as some other pair `contractId2`, `accountId2` whose concatenation is byte-identical. The cache only stores entries when `result[1] >= result[0]` (i.e., "destination already has sufficient storage deposit for that token") at line 295-297. Once such a "sufficient" entry is cached under a colliding key, any later call for the *different* real pair that happens to hash to the same key reads that stale/foreign result at lines 278-281 without ever querying the real on-chain storage balance for the new pair.

This breaks the equality the code is meant to enforce: *"the fee estimate for withdrawal (token X, destination Y) reflects Y's actual on-chain storage balance for X."* Instead it can silently substitute another (token, destination) pair's cached state.

### Impact Explanation
If the stale/collided cache entry indicates sufficient storage balance, `estimateWithdrawalFee` returns `feeAmount = 0` / `storageDepositFee: 0n` (lines 231-241), so `createWithdrawIntentPrimitive` is built with no storage-deposit top-up (line 137-144). When the resulting near_withdraw intent executes on-chain, the destination account may in fact lack the NEP-141 storage registration for that token, causing the transfer to fail. Since intents SDK withdrawals are typically fire-and-forget once submitted, this results in a withdrawal that gets stuck/fails after the user's funds have already been debited from their intents balance, requiring manual intervention/support — matching the "withdrawal stuck until manual intervention" High-impact category. It is not an attacker gaining someone else's funds; it is a caller-supplied-input class of self-inflicted fee bypass leading to a failed/stuck withdrawal for whichever party triggers the colliding key (the same withdrawing party in practice, since the SDK is used per end-user request), so realistic exploitation impact is bounded.

### Likelihood Explanation
Triggering an exact collision requires finding two real, RPC-resolvable NEP-141 contract IDs and destination account IDs whose concatenation matches, and requires the first (donor) pair to have already been queried and cached with a "sufficient" result. This is a non-trivial but purely mechanical string-construction exercise (no cryptography, no privileged access) reachable simply by calling the public `estimateWithdrawalFee` twice with attacker-chosen `assetId`/`destinationAddress` values, matching the "hand-crafted module" precondition described in the Wasmtime advisory.

### Recommendation
Use an unambiguous, delimiter-safe cache key, e.g. `` `${contractId}:${accountId}` `` (with a character guaranteed not to appear un-escaped in either segment) or a composite key structure (array/tuple key, or a `Map` keyed by `contractId` whose value is itself a `Map` keyed by `accountId`) instead of raw string concatenation, in `getCachedStorageDepositValue`.

### Proof of Concept
1. Call `directBridge.estimateWithdrawalFee({ withdrawalParams: { assetId: "nep141:usdc.near", destinationAddress: "bob.near", ... } })`. Suppose `bob.near` already has sufficient storage for `usdc.near`; the result is cached under key `"usdc.nearbob.near"` with `feeAmount = 0`.
2. Call `estimateWithdrawalFee` again with a different, real token contract `contractId2` and destination `accountId2` such that `contractId2 + accountId2 === "usdc.nearbob.near"` (e.g., a token contract literally named `"usdc.nearbob"` paired with destination `"near"`, if such a token is supported by the deployment).
3. The second call hits `storageDepositCache.get("usdc.nearbob.near")` and returns the first call's cached `[minStorageBalance, userStorageBalance]` without ever querying `getNearNep141StorageBalance` for `(contractId2, accountId2)`, so `estimateWithdrawalFee` reports `feeAmount = 0` even though the real destination/token pair may lack storage — the subsequent on-chain withdrawal intent is built without the required storage-deposit fee.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L225-229)
```typescript
		const [minStorageBalance, userStorageBalance] =
			await this.getCachedStorageDepositValue(
				tokenAccountId,
				args.withdrawalParams.destinationAddress,
			);
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L273-300)
```typescript
	private async getCachedStorageDepositValue(
		contractId: string,
		accountId: string,
	): Promise<[MinStorageBalance, StorageDepositBalance]> {
		const key = `${contractId}${accountId}`;
		const cached = this.storageDepositCache.get(key);
		if (cached !== undefined) {
			return cached;
		}

		const result = await Promise.all([
			getNearNep141MinStorageBalance({
				contractId: contractId,
				nearProvider: this.nearProvider,
			}),
			getNearNep141StorageBalance({
				contractId: contractId,
				accountId: accountId,
				nearProvider: this.nearProvider,
			}),
		]);

		if (result[1] >= result[0]) {
			this.storageDepositCache.set(key, result);
		}

		return result;
	}
```
