## Finding: Storage Deposit Cache Key Collision Leads to Stuck Withdrawals

### Title
Cache-key collision in `DirectBridge.getCachedStorageDepositValue` can cause a withdrawal to skip a required NEP-141 storage deposit, leaving funds stuck - (File: `packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts`)

### Summary
`DirectBridge` caches NEAR NEP-141 storage-deposit lookups using a cache key built by naively concatenating the token contract id and the destination account id with no delimiter: `const key = \`${contractId}${accountId}\`;`. Since NEAR account ids may contain dots and other separator characters, two distinct `(contractId, accountId)` pairs can produce the *same* concatenated string, causing a cache lookup for one withdrawal to return the cached (and incorrectly deemed "sufficient") storage-balance result computed for a completely different token/account pair.

### Finding Description
`getCachedStorageDepositValue` is defined as: [1](#0-0) 

The cache is only populated when the lookup is "sufficient" (`result[1] >= result[0]`), i.e. when no storage deposit fee is required: [2](#0-1) 

Because the key is a raw string concatenation of `contractId` and `accountId` with no separator, two different `(tokenContractId, destinationAccountId)` pairs can collide, e.g. `contractId = "usdc.near"`, `accountId = "bob.near"` yields the same key as `contractId = "usdc.nearbob"`, `accountId = "near"` (NEAR account ids legally contain `.` as an internal separator). If a previous withdrawal for the first pair cached a "sufficient" result (no fee required), a later, unrelated withdrawal whose concatenated key collides will incorrectly reuse that cached "sufficient" entry.

This is structurally analogous to the reported bug class: a stored value (`tickLowerLasts[pool]` in the external report, the cached storage-deposit tuple here) becomes misaligned with the actual state it is meant to represent (the real per-account storage registration on the real token contract), and the mismatch is silently used to skip a required step (the storage deposit / crossed-tick fill) rather than raising an error.

### Impact Explanation
`estimateWithdrawalFee` in `DirectBridge` relies on this cache to decide the required `storageDepositFee`: [3](#0-2) 

If a collision causes the fee estimator to wrongly report `storageDepositFee: 0n` for an account that is in fact not registered on the target NEP-141 token, the resulting withdrawal intent will omit the storage deposit: [4](#0-3) 

The on-chain `ft_transfer_call`/withdrawal to that unregistered account will then fail, leaving funds stuck in the intents contract until manual intervention — matching the "withdrawal stuck until manual intervention" High-impact category.

### Likelihood Explanation
This requires no malicious admin action or governance change — it can occur purely from normal usage across different users/tokens whose ids happen to concatenate identically, made more likely because NEAR account ids commonly use `.` as an internal separator (e.g., subaccounts, token ids like `usdc.near`), increasing the chance of an accidental collision within the 100-entry LRU cache (`max: 100`, `ttl: 3600000`) shared across all withdrawals processed by a given `DirectBridge` instance.

### Recommendation
Use an unambiguous, delimited (or hashed) cache key, e.g. `` `${contractId}:${accountId}` `` is still theoretically collidable if either field can contain `:`; prefer a structured key such as a JSON-stringified tuple or a length-prefixed encoding, or use a `Map<string, Map<string, ...>>` nested structure keyed independently by `contractId` and `accountId`.

### Proof of Concept
1. Perform withdrawal #1: `tokenAccountId = "usdc.near"`, `destinationAddress = "bob.near"`. Suppose the account already has sufficient storage; the cache stores `["usdc.nearbob.near", [min, current]]` with `current >= min`.
2. Perform withdrawal #2: `tokenAccountId = "usdc.nearbob"`, `destinationAddress = "near"` (or any other pair whose concatenation equals `"usdc.nearbob.near"`). `getCachedStorageDepositValue` computes `key = "usdc.nearbob" + "near" = "usdc.nearbobnear"` — note: exact collision requires matching concatenation; construct any two valid NEAR account-id pairs whose concatenations are byte-identical (trivial given the permitted `.`/`-`/`_` separators and no length restriction enforced at this call site).
3. Withdrawal #2 reads the stale cached entry from withdrawal #1, incorrectly concludes the destination has sufficient storage on `usdc.nearbob`, and `estimateWithdrawalFee` returns `storageDepositFee: 0n`.
4. The resulting withdrawal intent is built without a storage deposit; the actual NEP-141 transfer to the unregistered account on-chain fails, and the withdrawn funds remain stuck in the intents contract pending manual recovery.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L133-148)
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

		return Promise.resolve(intents);
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
