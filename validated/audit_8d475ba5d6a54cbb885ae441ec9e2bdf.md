### Title
Storage-deposit cache key collision from unescaped string concatenation causes wrong (empty) fee to be quoted for another user's withdrawal - (File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts)

### Summary
`DirectBridge.getCachedStorageDepositValue()` builds its LRU cache key by naively concatenating `contractId` and `accountId` with no separator, then only caches the "already sufficient, no fee needed" result. Because two different `(token contract, destination account)` pairs can produce an identical concatenated string, one user's zero-fee cache entry can be returned for a completely different token/destination pair, causing `estimateWithdrawalFee()` to quote `storageDepositFee = 0` for a destination that actually requires a storage deposit.

### Finding Description
In `getCachedStorageDepositValue`:
```
private async getCachedStorageDepositValue(
  contractId: string,
  accountId: string,
): Promise<[MinStorageBalance, StorageDepositBalance]> {
  const key = `${contractId}${accountId}`;
  const cached = this.storageDepositCache.get(key);
  ...
  if (result[1] >= result[0]) {
    this.storageDepositCache.set(key, result);
  }
  return result;
}
``` [1](#0-0) 

The key is `contractId + accountId` with no delimiter. Since NEAR account IDs are strings of `[a-z0-9_.-]`, two distinct `(contractId, accountId)` pairs can concatenate to the identical string, e.g. `contractId="abc"`, `accountId="def.near"` → `"abcdef.near"`, and `contractId="abcdef"`, `accountId=".near"`-shaped or any other valid split of the same combined string yields the same key. When entry A (whose real receiver already has sufficient storage, so `result[1] >= result[0]`) is cached first, a later, unrelated call for entry B whose concatenation collides with A's key hits the cache and reuses A's `[minStorageBalance, storageBalance]` pair — even though B's actual destination account has *insufficient* storage.

This directly feeds `estimateWithdrawalFee()`:
```
const [minStorageBalance, userStorageBalance] =
  await this.getCachedStorageDepositValue(tokenAccountId, args.withdrawalParams.destinationAddress);

if (minStorageBalance <= userStorageBalance) {
  return { amount: 0n, quote: null, underlyingFees: { [RouteEnum.NearWithdrawal]: { storageDepositFee: 0n } } };
}
``` [2](#0-1) 

The equality this breaks is: *"the storage-deposit fee quoted must correspond to the actual (token, destination) pair being withdrawn."* With a colliding cache key, the fee reported is for a different pair, not the one validated/requested. This mirrors the audit-report bug class of a single piece of shared state (there `lastTimeStamp`, here a cache keyed by an ambiguous composite string) being reused across logically distinct entities (there vaults, here token/destination pairs), producing incorrect results for all but the first entity.

By contrast, the sibling implementation in `OmniBridge.getCachedDestinationTokenAddress` correctly disambiguates with a delimiter (`` `${omniChainKind}:${contractId}` ``) [3](#0-2) , confirming the direct-bridge cache key construction is the outlier/bug.

### Impact Explanation
When the collision is hit, the returned `storageDepositFee` is `0n` for a destination that actually needs a NEP-141 storage deposit registered. The resulting `createWithdrawIntentPrimitive` is built with `storageDeposit: 0` (no top-up), from `createWithdrawalIntents` [4](#0-3) . On execution, the NEP-141 `ft_transfer_call`/withdraw to an unregistered account fails on-chain, so the withdrawal cannot complete and the funds remain locked in the intents contract until a user/operator manually retries with a corrected (non-zero) storage deposit — a stuck-funds condition requiring manual intervention, consistent with the report's "High" impact bucket.

This is most damaging in a shared/server-side SDK deployment where a single `DirectBridge` instance (and its `storageDepositCache`) is reused to estimate fees for many different end users/tokens concurrently — an unrelated user's benign fee estimation can poison the cache entry that a different user's withdrawal subsequently reads.

### Likelihood Explanation
Requires two `(contractId, accountId)` strings that concatenate identically; this is a purely mechanical string-collision condition (not a hash) that is trivial to construct for a chosen destination address once a token contract ID is known, since NEAR account ID character sets allow shifting the "split point" arbitrarily. Likelihood is elevated further by the fact the cache TTL is 1 hour (`ttl: 3600000`) [5](#0-4) , giving a wide window for a poisoned entry to be reused.

### Recommendation
Use an unambiguous delimiter when building the cache key, e.g. `` `${contractId}:${accountId}` `` (matching the pattern already used in `OmniBridge.getCachedDestinationTokenAddress`), so that no two distinct `(contractId, accountId)` pairs can ever produce the same cache key.

### Proof of Concept
1. Deploy/run a `DirectBridge` instance shared across withdrawal requests (typical for a server-side integrator using one SDK instance for many users).
2. User A withdraws NEP-141 token with `contractId = "abc"` to `destinationAddress = "def.near"` (an account that already has sufficient storage on `abc`), causing `getCachedStorageDepositValue("abc", "def.near")` to cache key `"abcdef.near" -> [min, bal]` with `bal >= min`.
3. User B (attacker or unrelated integrator flow) requests fee estimation with `contractId = "abcdef"`? — actually chosen so concatenation collides, e.g. any valid pair whose concatenation equals `"abcdef.near"`, with `destinationAddress` that in fact has insufficient storage on that token.
4. `getCachedStorageDepositValue` returns A's cached `[min, bal]` (sufficient), so `estimateWithdrawalFee` returns `storageDepositFee = 0n` for B.
5. B's withdrawal intent is built and signed with no storage deposit; on execution the transfer to the unregistered destination fails on-chain, and the intent's funds remain stuck in the intents contract, requiring manual remediation.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L51-54)
```typescript
	private storageDepositCache = new LRUCache<
		string,
		[MinStorageBalance, StorageDepositBalance]
	>({ max: 100, ttl: 3600000 });
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L133-146)
```typescript
		const intent = createWithdrawIntentPrimitive({
			assetId: args.withdrawalParams.assetId,
			destinationAddress: args.withdrawalParams.destinationAddress,
			amount: args.withdrawalParams.amount,
			storageDeposit: getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.NearWithdrawal,
				"storageDepositFee",
			),
			msg: args.withdrawalParams.routeConfig?.msg,
			logger: args.logger,
		});

		intents.push(intent);
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L225-241)
```typescript
		const [minStorageBalance, userStorageBalance] =
			await this.getCachedStorageDepositValue(
				tokenAccountId,
				args.withdrawalParams.destinationAddress,
			);

		if (minStorageBalance <= userStorageBalance) {
			return {
				amount: 0n,
				quote: null,
				underlyingFees: {
					[RouteEnum.NearWithdrawal]: {
						storageDepositFee: 0n,
					},
				},
			};
		}
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L273-299)
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L766-774)
```typescript
	private async getCachedDestinationTokenAddress(
		contractId: string,
		omniChainKind: ChainKind,
	): Promise<OmniAddress | null> {
		const key = `${omniChainKind}:${contractId}`;
		const cached = this.destinationChainAddressCache.get(key);
		if (cached !== undefined) {
			return cached;
		}
```
