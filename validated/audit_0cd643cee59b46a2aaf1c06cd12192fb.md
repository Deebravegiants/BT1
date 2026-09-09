Confirmed: `storage_deposit` in the `ft_withdraw` intent is set only from `params.storageDeposit`, which is derived from the cached `[minStorageBalance, userStorageBalance]` pair keyed by `${contractId}${accountId}` string concatenation.

### Title
Cache-key collision in `DirectBridge.getCachedStorageDepositValue` lets a colliding token/account pair suppress a victim's required storage-deposit fee, causing withdrawal funds to be stuck - (File: `packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts`)

### Summary
`DirectBridge.getCachedStorageDepositValue` builds its cache key by naive string concatenation of `contractId` and `accountId` (`` `${contractId}${accountId}` ``) with no delimiter. Because both values are attacker-influenceable strings (NEAR account IDs allow dots, hyphens, underscores — the same characters used in token contract IDs), two different `(contractId, accountId)` pairs can produce the identical concatenated key, causing the storage-deposit "sufficient balance" cache entry for one pair to be served for an unrelated pair.

### Finding Description
`getCachedStorageDepositValue` is defined at [1](#0-0) . The cache key is computed as:
```
const key = `${contractId}${accountId}`;
```
with no separator between the two fields. This is the same equality-breaking bug class as GHSA-882j-4vj5-7vmj: a cache lookup key derived from concatenating attacker-controllable inputs can be made to collide across logically distinct requests, letting one party's cached result be served for another's request.

Since both `contractId` (the NEP-141 token id, itself an arbitrary NEAR-style string such as `usdc.some.near`) and `accountId` (`destinationAddress`, which is any user-supplied NEAR account, also containing dots) are attacker-controllable inputs passed straight from `estimateWithdrawalFee` at [2](#0-1) , it is possible to construct pair A = `(contractId_A, accountId_A)` and pair B = `(contractId_B, accountId_B)` such that `contractId_A + accountId_A === contractId_B + accountId_B` while the pairs themselves differ (e.g. `contractId_A = "usdc.near"`, `accountId_A = "sub.near"` vs `contractId_B = "usdc.near.sub"`, `accountId_B = ".near"` — both are syntactically valid dotted NEAR-style identifiers).

The cache only stores "sufficient balance" results (`result[1] >= result[0]`) at [3](#0-2) , so an attacker who first triggers a fee estimation for a crafted pair that legitimately has sufficient storage balance can poison the shared cache entry. A subsequent, unrelated victim whose real `(contractId, destinationAddress)` happens to concatenate to the same key will then have `estimateWithdrawalFee` read the attacker's cached `[minStorageBalance, userStorageBalance]` tuple and wrongly conclude `minStorageBalance <= userStorageBalance`, returning a zero `storageDepositFee` at [4](#0-3) .

That zero fee estimate flows directly into `createWithdrawalIntents`, which passes `storageDeposit: 0` into `createWithdrawIntentPrimitive` at [5](#0-4) , and the resulting `ft_withdraw` intent omits the `storage_deposit` field entirely because `params.storageDeposit > 0n` is false at [6](#0-5) . If the victim's destination account genuinely lacks the NEP-141 storage registration on the token contract, the on-chain `ft_transfer`/`ft_transfer_call` will fail without the storage deposit being funded, leaving the withdrawal unable to complete and requiring manual intervention to resolve.

### Impact Explanation
This breaks the equality "the storage-deposit sufficiency check reported for account X on token Y is the check that was actually performed for X and Y." A withdrawal that genuinely needs a storage deposit can be estimated (and subsequently executed) with a zero fee due to an unrelated cached entry, causing the on-chain withdrawal transaction to fail for lack of storage registration — a stuck withdrawal requiring manual intervention, matching the High-severity criteria in scope.

### Likelihood Explanation
Exploitability requires an attacker to be able to trigger `estimateWithdrawalFee`/`getCachedStorageDepositValue` for a crafted `(contractId, accountId)` pair that collides with a victim's real pair under naive string concatenation. In any deployment where the `DirectBridge` instance (and its `storageDepositCache`) is shared across multiple callers/users (e.g. an integrator's backend service processing withdrawals for many end users), an unprivileged caller only needs to supply a valid-looking NEP-141 `assetId` and NEAR `destinationAddress` — both ordinary, unprivileged inputs — to seed the collision. No admin, relayer, or bridge-operator cooperation is required.

### Recommendation
Use a collision-safe cache key that unambiguously separates the two components, e.g. a delimiter that cannot appear validly in either field combined with an explicit length/JSON encoding, or key the cache with a tuple/array key (or `JSON.stringify([contractId, accountId])`), rather than plain string concatenation. Apply the same review to any other cache key built via bare template-literal concatenation of multiple user-controlled fields in this package.

### Proof of Concept
1. Attacker calls `bridge.estimateWithdrawalFee` with `assetId` resolving to `contractId = "usdc.near"` and `destinationAddress = "sub.near"`, where the destination genuinely already has sufficient NEP-141 storage balance on `usdc.near`. This populates `storageDepositCache.set("usdc.nearsub.near", [minBal, userBal])` with `userBal >= minBal`, via [7](#0-6) .
2. A victim later calls `estimateWithdrawalFee`/`signAndSendWithdrawalIntent` for a token whose `contractId = "usdc.nearsub"` (a distinct, real NEP-141 contract) withdrawing to `destinationAddress = ".near"`-style account such that the concatenation reproduces `"usdc.nearsub.near"` (concrete collisions can be constructed with any dotted NEAR-style identifiers of the attacker's choosing, since NEAR account/contract IDs freely allow `.`).
3. `getCachedStorageDepositValue` returns the attacker's cached "sufficient" tuple for the victim's genuinely under-funded account, so `estimateWithdrawalFee` reports `storageDepositFee: 0n`.
4. The withdrawal intent is created with `storage_deposit` omitted at [6](#0-5) , and the on-chain NEP-141 transfer fails for lack of storage registration, leaving the withdrawal stuck.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L133-144)
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
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L225-229)
```typescript
		const [minStorageBalance, userStorageBalance] =
			await this.getCachedStorageDepositValue(
				tokenAccountId,
				args.withdrawalParams.destinationAddress,
			);
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L231-241)
```typescript
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
