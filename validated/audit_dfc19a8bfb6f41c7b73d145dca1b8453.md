Confirmed: `parseDefuseAssetId` in `packages/internal-utils/src/utils/tokenUtils.ts` only validates that `tokenContractId` passes `validateNearAddress` — it does **not** check the token against a registry/allowlist at this layer. The `contractId` is fully attacker-controlled as long as it is a syntactically valid NEAR account id (letters, digits, `.`, `_`, `-`). Combined with `destinationAddress` (also attacker-controlled, only required to pass `validateAddress`), the attacker fully controls both operands of the unsalted, unseparated string-concatenation cache key in `DirectBridge.getCachedStorageDepositValue`.

### Title
Unsalted cache-key concatenation lets an attacker collide storage-deposit fee estimates across different tokens/destinations - (File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts)

### Summary
`DirectBridge.getCachedStorageDepositValue` builds its LRU cache key as `` `${contractId}${accountId}` `` with no delimiter [1](#0-0) . Because `contractId` (from `parseDefuseAssetId`) and `accountId` (`destinationAddress`) are both attacker-influenced strings validated only for NEAR-account syntax [2](#0-1) , two different `(contractId, accountId)` pairs can be crafted to produce an identical concatenated key, exactly mirroring the reported global-state offset collision (two logically distinct values mapping to the same storage slot/key).

### Finding Description
`estimateWithdrawalFee` calls `getCachedStorageDepositValue(tokenAccountId, destinationAddress)`, which caches `[minStorageBalance, userStorageBalance]` under `key = contractId + accountId` and only caches when `userStorageBalance >= minStorageBalance` (i.e., "storage is sufficient, no fee needed") [3](#0-2) .

Because there is no separator, `contractId_A + accountId_A` can equal `contractId_B + accountId_B` for `contractId_A ≠ contractId_B` whenever `contractId_A` is a prefix of `contractId_B` and the caller picks `accountId_A = suffix(contractId_B) + accountId_B`. Both operands satisfy only the generic NEAR-account-id regex check in `parseDefuseAssetId`/`validateNearAddress` [2](#0-1)  and `validateAddress` in `validateWithdrawal` — neither ties `contractId` to a fixed registry length or format that prevents prefix relationships between two real/whitelisted token contract ids.

An attacker who controls a low-cost withdrawal on token A can pre-populate the shared cache (the `DirectBridge` instance and its `storageDepositCache`/`accountExistenceCache` are long-lived and shared across all SDK callers, e.g., a relayer service handling many users) with a "sufficient storage" entry keyed by the colliding string. When a legitimate call for token B / a real destination later computes to the same key, `estimateWithdrawalFee` will short-circuit to `storageDepositFee: 0` [4](#0-3) , even though the destination account genuinely lacks storage registration on token B's NEP-141 contract.

This equality break — "an amount debited (storage deposit fee) that is not the amount actually required" — mirrors the reported analog: two semantically different values (storage state for token/account pair) colliding on the same key due to an under-specified encoding.

### Impact Explanation
The resulting `IntentFtWithdraw` is built with `storage_deposit: undefined` (since `feeAmount` from the poisoned entry is `0`) via `createWithdrawIntentPrimitive` [5](#0-4) . On-chain, the `ft_transfer`/`ft_withdraw` to a destination account without NEP-141 storage registration fails, leaving the withdrawal stuck and requiring manual intervention/re-processing — matching the High-impact category "a withdrawal stuck until manual intervention." A symmetric collision (mapping a real "insufficient storage" entry onto an unrelated query) could instead force an unnecessary/incorrect fee to be charged.

### Likelihood Explanation
Exploitability requires a specific string relationship between the involved `contractId`s (one being a prefix of the concatenation formed by another `contractId`+`accountId`); with real deployed NEP-141 token account ids this constrains, but does not rule out, viable collisions, and the attacker has full latitude to choose `accountId`/`destinationAddress` on both sides. Because the cache is shared per bridge instance across all callers/withdrawals processed by that instance, a single attacker-supplied estimation call is enough to poison state that could later be read by an unrelated legitimate request. This matches the "High difficulty" rating of the original analog report, since a real-world trigger depends on the coincidental existence of two supported token ids with the needed prefix relationship — which cannot be exhaustively confirmed from the indexed code alone (the live token allowlist/registry is not available in this index).

### Recommendation
Use a delimiter that cannot appear in either component (e.g., `` `${contractId}:${accountId}` ``, mirroring the safer pattern already used in `HotBridge.getNoncesCacheKey` and `OmniBridge.getCachedDestinationTokenAddress` [6](#0-5) [7](#0-6) ), or better, use a composite key such as `JSON.stringify([contractId, accountId])` or a `Map<string, Map<string, ...>>` keyed independently per component so no character-level ambiguity is possible.

### Proof of Concept
1. Choose two whitelisted NEP-141 `contractId`s such that `contractId_A` is a string prefix of `contractId_B` (e.g. hypothetically `contractId_A = "usdc.near"`, `contractId_B = "usdc.nearx.token.near"`, where `"x.token.near"` matches the suffix format needed).
2. Call `estimateWithdrawalFee` for asset A with `destinationAddress_A = "x.token.near" + accountId_B` where the attacker actually holds sufficient storage on contractId_A for that constructed account string, causing the cache to store a "0 fee" entry keyed `contractId_A + destinationAddress_A`.
3. Because `contractId_A + destinationAddress_A === contractId_B + accountId_B`, a later legitimate `estimateWithdrawalFee` call for asset B and real destination `accountId_B` (who has no storage registered on token B) reads the poisoned cache entry and returns `storageDepositFee: 0`.
4. The subsequent withdrawal intent for token B is built without `storage_deposit`, and the on-chain `ft_transfer` to `accountId_B` fails because the destination lacks storage registration, stranding the withdrawal. [3](#0-2)

### Citations

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

**File:** packages/internal-utils/src/utils/tokenUtils.ts (L403-418)
```typescript
export function parseDefuseAssetId(
	assetId: string,
): ParseDefuseAssetIdReturnType {
	const [tokenStandard, tokenContractId, multiTokenId] = assetId.split(":");

	assert(
		tokenContractId != null && validateNearAddress(tokenContractId),
		"Incorrect format of assetId",
	);

	switch (tokenStandard) {
		case "nep141":
			return {
				standard: "nep141",
				contractId: tokenContractId,
			};
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

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L104-106)
```typescript
	private getNoncesCacheKey(tx: NearTxInfo): `${string}:${string}` {
		return `${tx.hash}:${tx.accountId}`;
	}
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
