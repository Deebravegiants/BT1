### Title
Storage-deposit cache key collision lets an attacker force a withdrawal to skip its required NEAR storage deposit - ([File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts])

### Summary
`DirectBridge.getCachedStorageDepositValue` builds its cache key by naive string concatenation of `contractId` and `accountId` with no delimiter. Two different `(contractId, accountId)` pairs can produce an identical key string, so a cached "storage deposit sufficient, no fee needed" result computed for one token/account pair can be served back for an entirely different token/account pair, causing `estimateWithdrawalFee` to omit the required `storage_deposit` for an account that actually needs it.

### Finding Description
`getCachedStorageDepositValue` computes: [1](#0-0) 

The key is `` `${contractId}${accountId}` `` with no separator, so `contractId="ab", accountId="cd"` and `contractId="a", accountId="bcd"` both hash to `"abcd"`. Both `contractId` (derived from the attacker-supplied `assetId`) and `accountId` (the attacker-supplied `destinationAddress`) are caller-controlled inputs to `estimateWithdrawalFee`: [2](#0-1) 

Only "sufficient storage" results are cached (`result[1] >= result[0]`, i.e. `userStorageBalance >= minStorageBalance`): [3](#0-2) 

An attacker can pick a `(contractId_A, accountId_A)` pair they control (with storage already registered, so the "sufficient" branch caches) whose concatenation collides with a victim's real `(contractId_B, accountId_B)` pair. Once cached, any later call to `estimateWithdrawalFee` for the colliding key returns `storageDepositFee: 0` regardless of whether `accountId_B` actually has storage registered on `contractId_B`. This zero fee flows directly into the withdrawal intent construction: [4](#0-3) 

Because `storage_deposit` becomes `undefined` (not the attacker-relevant amount), the on-chain `ft_withdraw` intent is submitted without the storage deposit the receiver actually needs.

### Impact Explanation
This breaks the equality "the storage-sufficiency check validated is for the same `(token, destination-account)` pair as the withdrawal being executed." When the collision is exploited, a legitimate withdrawal to an account lacking NEP-141 storage registration on the destination token contract will be executed with `storage_deposit` omitted. The underlying NEAR `ft_transfer`/`ft_transfer_call` will revert for lack of storage on the receiver, leaving the withdrawal intent executed on the intents side without a successful token delivery — funds get stuck in the bridge/intents flow and require manual intervention/retry, matching the "withdrawal stuck until manual intervention" High-impact bucket.

### Likelihood Explanation
Both components of the vulnerable key (`assetId`/`contractId` and `destinationAddress`/`accountId`) are supplied by the caller of `estimateWithdrawalFee`, and the cache (`storageDepositCache`, `max: 100, ttl: 3600000`) is shared per `DirectBridge` instance across all requests handled by that instance (e.g., a shared backend service processing many users' withdrawals). An attacker who can invoke `estimateWithdrawalFee` (or trigger a withdrawal flow that calls it) with a crafted `assetId`/`destinationAddress` pair engineered to collide with a legitimate pair can poison the shared cache. Because NEAR account/contract IDs allow variable-length alphanumeric strings with `.`/`_`/`-`, constructing a colliding pair is straightforward.

### Recommendation
Use a delimiter that cannot appear ambiguously in the concatenation, or better, use a structured key (e.g., `` `${contractId}:${accountId}` `` is still ambiguous if the delimiter char is allowed in identifiers, so prefer a tuple-based key, hashing both parts independently, or storing a `Map<contractId, Map<accountId, result>>`). Apply the same fix pattern already used correctly elsewhere in the codebase for two-part cache keys.

### Proof of Concept
1. Attacker calls `estimateWithdrawalFee` with `assetId` mapping to `contractId_A = "ab"` and `destinationAddress = "cd"` (an account already registered/storage-sufficient on `contractId_A`). This caches key `"abcd"` → `[min, sufficientBalance]`.
2. A legitimate withdrawal request later resolves to `contractId_B = "a"`, `destinationAddress = "bcd"` (an account that is NOT storage-registered on `contractId_B`). Its cache key is also `"abcd"`.
3. `getCachedStorageDepositValue` returns the cached (wrong) "sufficient" result; `estimateWithdrawalFee` reports `storageDepositFee: 0`.
4. `createWithdrawalIntents` builds an `ft_withdraw` intent with `storage_deposit: undefined` for the victim's real withdrawal.
5. On-chain execution fails to deliver tokens to the unregistered account, leaving the withdrawal stuck.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L204-229)
```typescript
		const { contractId: tokenAccountId, standard } = utils.parseDefuseAssetId(
			args.withdrawalParams.assetId,
		);
		assert(standard === "nep141", "Only NEP-141 is supported");

		if (
			// We don't directly withdraw `wrap.near`, we unwrap it first, so it doesn't require storage
			args.withdrawalParams.assetId === NEAR_NATIVE_ASSET_ID &&
			// Ensure `msg` is not passed, because `native_withdraw` intent doesn't support `msg`
			args.withdrawalParams.routeConfig?.msg === undefined
		)
			return {
				amount: 0n,
				quote: null,
				underlyingFees: {
					[RouteEnum.NearWithdrawal]: {
						storageDepositFee: 0n,
					},
				},
			};

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
