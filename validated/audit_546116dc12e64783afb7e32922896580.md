## Title
Delimiter-less cache key concatenation in `DirectBridge.getCachedStorageDepositValue` causes storage-deposit fee cross-contamination between unrelated withdrawals - (File: `packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts`)

### Summary
`DirectBridge` caches NEAR storage-deposit lookups using a key built by naively concatenating `contractId` and `accountId` with no separator: `` `${contractId}${accountId}` ``. Because valid NEAR account IDs can be split at any character boundary and still form two other valid account IDs, two unrelated `(token, destination)` pairs can produce the identical cache key. This is the same bug class as the Apollo Router advisory: a shared cache whose retrieval key does not uniquely bind to the request's real inputs, so a lookup for one request silently returns data cached for a different request.

### Finding Description
`getCachedStorageDepositValue` builds its cache key like this: [1](#0-0) 

The key `` `${contractId}${accountId}` `` has no delimiter between the two components. NEAR account IDs are composed of lowercase letters, digits, `-`, `_`, and `.`, so for any pair `(contractId, accountId)` there generally exist other valid pairs `(contractId', accountId')` with `contractId' + accountId' === contractId + accountId` (e.g. `contractId="usdttoken"`, `accountId="near"` collides with `contractId="usdttokenn"`, `accountId="ear"`). Since the `LRUCache` instance (`storageDepositCache`, max 100 entries, ttl 1h) is shared across all calls made through the same `DirectBridge` instance, a collision means the cached `[minStorageBalance, userStorageBalance]` pair computed for one token/account is returned for a completely different token/account pair.

This cached tuple directly drives `estimateWithdrawalFee`'s equality check `minStorageBalance <= userStorageBalance`, which decides whether a storage-deposit fee is charged at all: [2](#0-1) 

The resulting `storageDepositFee` is then embedded verbatim into the `ft_withdraw` intent's `storage_deposit` field: [3](#0-2) 

Because the wrong `(minStorageBalance, userStorageBalance)` for the wrong account can be substituted transparently, the fee decided for withdrawal A is not the fee that should have applied to withdrawal A — breaking the equality "amount debited == amount + fee actually required for this destination/token".

### Impact Explanation
Two outcomes are possible depending on which side of the collision "wins" the cache:
- The destination account is actually *not* registered for storage on the token contract, but the colliding cached entry says it is sufficiently funded → `storageDepositFee` computed as `0`, no `storage_deposit` is attached to the `ft_withdraw` intent. On-chain, the transfer to an unregistered NEP-141 account will fail, leaving the withdrawal stuck and requiring manual intervention (High impact per rules: "a withdrawal stuck until manual intervention").
- The reverse collision causes an unnecessary storage-deposit fee to be computed and charged for an account that was already registered, resulting in a fee overcharge debited from the user (High impact per rules: "a fee overcharge").

Because the cache is shared and keyed by an ambiguous string, any user of a shared SDK instance (e.g., an integrator's backend processing many users' withdrawals) can influence what gets cached for another user's unrelated withdrawal simply by choosing a token/destination pair whose concatenation collides with a legitimate upcoming pair.

### Likelihood Explanation
Triggering requires no privileged access — any caller of `estimateWithdrawalFee` (or the withdrawal flow that invokes it) with an attacker-controlled `assetId`/`destinationAddress` can populate the shared LRU cache with an entry keyed to collide with a foreseeable or targeted victim key. Constructing a colliding pair is purely a string-concatenation exercise within the standard NEAR account-ID character set, requiring no special privileges, timing, or race condition — only knowledge (or a guess) of the victim's future `(contractId, accountId)` pair, or opportunistic collisions in high-traffic deployments given the cache holds up to 100 entries for an hour.

### Recommendation
Include an unambiguous delimiter that cannot appear as a valid boundary character sequence in NEAR account IDs, or better, use a structured/tuple key (e.g. `` `${contractId}:${accountId}` `` is still theoretically ambiguous since `:` isn't guaranteed unique either if any of these ids may include arbitrary characters in the future; safest is a hashed key over the tuple or a `Map`/nested-`Map` keyed by `contractId` then `accountId`) so that no two distinct `(contractId, accountId)` pairs can ever map to the same cache entry. Apply the same review to any other cache key built by string concatenation without a delimiter in this file and sibling bridge files (e.g. `getCachedDestinationTokenAddress` in `omni-bridge.ts` uses `` `${omniChainKind}:${contractId}` ``, which is safer since `omniChainKind` is a constrained enum, but should still be double-checked).

### Proof of Concept
1. Attacker calls `estimateWithdrawalFee` (or a flow that reaches `getCachedStorageDepositValue`) with `assetId` resolving to `contractId = "usdttokenn"` and `destinationAddress = "ear"` (both valid NEAR account ID strings). This populates `storageDepositCache` under key `"usdttokennear"` with the real `[minStorageBalance, userStorageBalance]` for that pair — say the attacker ensures `userStorageBalance >= minStorageBalance` for their own account, so the entry is cached (per the `if (result[1] >= result[0])` guard at `direct-bridge.ts:295-297`).
2. Later, a legitimate victim withdrawal is requested for `contractId = "usdttoken"`, `destinationAddress = "near"` — a different token contract and different destination account. This produces the same concatenated key `"usdttokennear"`.
3. `getCachedStorageDepositValue` at `direct-bridge.ts:277-281` finds the cache hit and returns the attacker's cached tuple instead of querying the victim's real storage balances.
4. `estimateWithdrawalFee` computes `minStorageBalance <= userStorageBalance` as `true` using the wrong data, returning `storageDepositFee: 0` even though the victim's real destination account is not registered for storage on `usdttoken`.
5. The resulting `ft_withdraw` intent omits `storage_deposit` (`direct-bridge-utils.ts:54-55`), and the on-chain transfer to the unregistered account fails, leaving the withdrawal stuck. [4](#0-3)

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L225-267)
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

		const feeAssetId = NEAR_NATIVE_ASSET_ID;
		const feeAmount = minStorageBalance - userStorageBalance;

		const feeQuote =
			args.withdrawalParams.assetId === feeAssetId
				? null
				: await getFeeQuote({
						feeAmount,
						feeAssetId,
						tokenAssetId: args.withdrawalParams.assetId,
						logger: args.logger,
						envConfig: this.envConfig,
						quoteOptions: args.quoteOptions,
						solverRelayApiKey: this.solverRelayApiKey,
					});

		return {
			amount: feeQuote ? BigInt(feeQuote.amount_in) : feeAmount,
			quote: feeQuote,
			underlyingFees: {
				[RouteEnum.NearWithdrawal]: {
					storageDepositFee: feeAmount,
				},
			},
		};
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

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts (L49-60)
```typescript
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: params.destinationAddress,
		amount: params.amount.toString(),
		storage_deposit:
			params.storageDeposit > 0n ? params.storageDeposit.toString() : undefined,
		msg: params.msg,
		// Only set min_gas when msg is not provided (simple ft_transfer).
		// When msg is present, ft_transfer_call is used and gas consumption is unpredictable.
		min_gas: params.msg == null ? MIN_GAS_AMOUNT : undefined,
	};
```
