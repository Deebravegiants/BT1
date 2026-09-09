### Title
Storage-deposit fee cache key collision causes wrong fee/storage-deposit amount for unrelated (token, destination) pairs - (File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts)

### Summary
`DirectBridge.getCachedStorageDepositValue()` builds its LRU cache key by naive string concatenation of `contractId` and `accountId` with no separator: `` `${contractId}${accountId}` ``. Because both are attacker-influenceable NEAR account-id strings, two different `(contractId, accountId)` pairs can produce the same concatenated key, causing the cached `[minStorageBalance, currentStorageBalance]` tuple computed for one token/destination pair to be silently reused for a different, unrelated token/destination pair on a shared, long-lived (`ttl: 3600000`) bridge instance. [1](#0-0) 

### Finding Description
`getCachedStorageDepositValue` is used inside `estimateWithdrawalFee` to decide whether the destination NEAR account already has sufficient NEP-141 storage deposit for the token being withdrawn, and if not, how large the `storageDepositFee` component of the withdrawal fee must be: [2](#0-1) 

The cache key is built as:
```
const key = `${contractId}${accountId}`;
``` [3](#0-2) 

Since `contractId` (the NEP-141 token contract account, e.g. `"usdc.near"`) and `accountId` (the caller-supplied `destinationAddress`) are both valid NEAR account-id strings drawn from the same character set (lowercase alphanumerics, `.`, `-`, `_`), simple concatenation is not collision-free: for two different pairs `(contractId1, accountId1) ≠ (contractId2, accountId2)`, it is possible that `contractId1 + accountId1 === contractId2 + accountId2` (e.g. `"abc" + "def.near"` equals `"abcd" + "ef.near"`, both `"abcdef.near"`). Because `DirectBridge` is instantiated once and reused for all withdrawal requests processed by the same SDK/server instance (this is the direct analog of "the same worker thread" in the Jetty report — a long-lived cache/instance shared across independent, unrelated calls), an attacker who controls their own `destinationAddress` for a supported token can:
1. Trigger a first `estimateWithdrawalFee` call that populates the cache under a key equal to `contractIdA + accountIdA`, storing a "storage already paid" (`currentStorageBalance >= minStorageBalance`) result for a chosen combination.
2. Trigger a second `estimateWithdrawalFee` call using a *different* real supported token contract `contractIdB` and a crafted `destinationAddress` `accountIdB` such that `contractIdB + accountIdB === contractIdA + accountIdA`.
3. The second call hits the poisoned cache entry and incorrectly reports that the destination already has sufficient storage deposit for `contractIdB`, even though it does not.

This breaks the equality the fee-estimation logic is supposed to preserve: the storage-deposit fee charged must correspond to the actual on-chain storage state of the actual `(token, destination)` pair being withdrawn to, not to an unrelated pair whose key happens to collide. [4](#0-3) 

### Impact Explanation
When the collision causes `getCachedStorageDepositValue` to under-report the storage requirement:
- `estimateWithdrawalFee` returns `amount: 0n` / `storageDepositFee: 0n` instead of the real required fee.
- The resulting `ft_withdraw` intent is built with `storage_deposit: undefined` (since `params.storageDeposit > 0n` is false), per `createWithdrawIntentPrimitive`. [5](#0-4) 
- If the destination account genuinely lacks sufficient NEP-141 storage on that token, the on-chain `ft_transfer`/`ft_withdraw` call will fail to register storage, and the withdrawal will fail/stall until manual intervention — a stuck-withdrawal condition. Alternately, if the protocol/relayer prefunds storage on the caller's behalf, the fee undercharge represents a direct loss to the protocol/solver, i.e., a fee-amount equality break (amount charged ≠ amount owed for a single storage deposit).

This matches the "High" impact bar: a withdrawal stuck until manual intervention, or a fee undercharge draining value from the protocol/solver.

### Likelihood Explanation
The requisite conditions — both `contractId` and `accountId` values are ordinary strings, the cache is unauthenticated and shared across all withdrawal requests processed by one `DirectBridge` instance, and it has a 1-hour TTL/100-entry LRU — are all present in code today. The blocking factor is that `contractId` is not fully free-form for the attacker (it must be one of the tokens actually supported/whitelisted for `DirectBridge`/NEAR withdrawal), so a genuine collision requires two whitelisted token account IDs whose names allow a prefix/suffix split that matches an attacker-chosen `destinationAddress`. Whether such a colliding pair currently exists among the supported NEP-141 token list could not be confirmed from the indexed code (the token whitelist/config is not part of the reviewed files), so exploitability today is plausible but not proven; regardless, the defect is a concrete equality-breaking root cause reachable through normal, unprivileged `estimateWithdrawalFee`/withdrawal calls.

### Recommendation
Use an unambiguous, delimiter-based (or length-prefixed) cache key, e.g. `` `${contractId}:${accountId}` `` (as already done correctly elsewhere in the codebase, e.g. `OmniBridge.getCachedDestinationTokenAddress`'s `` `${omniChainKind}:${contractId}` `` key) or a tuple-based cache (e.g., `Map<string, Map<string, ...>>`), so that no two distinct `(contractId, accountId)` pairs can ever map to the same cache entry. [6](#0-5) 

### Proof of Concept
1. Deploy/run a long-lived `DirectBridge` instance (as used by a server-side integrator handling many users' withdrawals).
2. User A calls `estimateWithdrawalFee` for token contract `"abc"` and `destinationAddress: "def.near"` where `"def.near"` already has ≥ min storage balance registered. This populates `storageDepositCache` with key `"abcdef.near"` → `[minBal, curBal]` where `curBal >= minBal`. [7](#0-6) 
3. Attacker (or User B) calls `estimateWithdrawalFee` for a different, real, whitelisted NEP-141 token contract `"abcd"` and `destinationAddress: "ef.near"` — an account that has NOT registered storage for `"abcd"`. Cache key is again `"abcdef.near"`.
4. `getCachedStorageDepositValue` returns the poisoned cached tuple from step 2 (`cached !== undefined`), so `estimateWithdrawalFee` reports `storageDepositFee: 0` instead of the real deposit requirement.
5. The resulting `ft_withdraw` intent omits `storage_deposit`, and the on-chain transfer to `"ef.near"` for token `"abcd"` fails at settlement due to missing storage registration, leaving the withdrawal stuck.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L225-257)
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
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L270-299)
```typescript
	/**
	 * Gets storage deposit for a token to avoid frequent RPC calls.
	 */
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
