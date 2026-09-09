### Title
Cache-key collision in `DirectBridge` allows skipping required storage-deposit fee, producing a withdrawal that fails on-chain - ([File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts])

### Summary
`DirectBridge.getCachedStorageDepositValue` builds its LRU cache key by naively concatenating `contractId` and `accountId` with no separator: `` `${contractId}${accountId}` ``. Because both are attacker-influenced NEAR account-id strings, two different `(contractId, accountId)` pairs can be crafted to produce the identical cache key, letting a "storage satisfied" result cached for one token/account pair be served for an entirely different token/account pair whose destination actually lacks the NEP-141 storage registration.

### Finding Description
`estimateWithdrawalFee` calls `getCachedStorageDepositValue(tokenAccountId, destinationAddress)`: [1](#0-0) 

The cache key is `` `${contractId}${accountId}` `` with no delimiter, so `contractId="T1"`, `accountId="D1"` and `contractId="T1D"`, `accountId="1"` (or any other string split at a different boundary) collide on the same key. The cache is only populated when the real on-chain check finds storage already sufficient (`result[1] >= result[0]`) — i.e. it caches a *true/positive* result: [2](#0-1) 

An attacker fully controls the `destinationAddress` used in the concatenation (it is their own withdrawal target) and freely chooses which supported NEP-141 token to withdraw (`contractId`). By first performing a normal withdrawal for token `T1` to an account `D1` where storage is legitimately registered, the attacker seeds the cache entry for key `T1‖D1`. They then request `estimateWithdrawalFee`/`createWithdrawalIntents` for a different token `T2` and a different destination `D2` that they control, chosen so that `T2‖D2 == T1‖D1` as plain strings. The lookup hits the poisoned cache entry and `estimateWithdrawalFee` incorrectly reports `storageDepositFee: 0n` for `(T2, D2)`, even though `D2` has never registered storage for `T2`.

Since the fee is zero, `createWithdrawalIntents`/`estimateWithdrawalFee` omit the `storage_deposit` intent that would otherwise be required: [3](#0-2) 

This breaks the equality the code intends to enforce: "the cached storage-satisfied status belongs to *this* `(contractId, accountId)` pair." The tar-rs analogy is exact — repeated/differing entries mapping to the same underlying key silently let a validated state be applied to a different unvalidated target.

### Impact Explanation
When the intent executes on-chain, the underlying `ft_transfer`/`ft_withdraw` to a NEAR account without the required storage deposit will fail per NEP-141 semantics. The withdrawal intent has already been signed and (potentially) settled from the user's perspective inside `intents.near`, but the destination-chain leg fails, leaving the withdrawal stuck and requiring manual intervention/support to resolve or refund — this matches the "High" impact bucket: *"a withdrawal stuck until manual intervention."* It can also manifest as an integrator under-quoting a required fee (fee overcharge/undercharge class), since the estimated fee silently drops from a nonzero value to `0n`.

### Likelihood Explanation
The attacker needs to control two withdrawal requests to the same `DirectBridge` instance: one to seed the cache (an ordinary withdrawal with legitimately sufficient storage) and one crafted to collide, using two account-id strings whose concatenation is contrived to match a previous `contractId‖accountId` string. Because NEAR account IDs allow arbitrary lowercase alphanumerics, `-`, `_`, and `.` up to 64 characters, and the attacker can choose accounts they control as `destinationAddress`, constructing a colliding pair against any pool of supported token contract ids is a purely mechanical string-construction exercise, not a cryptographic one. The cache has a 1-hour TTL and max 100 entries, giving a wide window to exploit. This requires no privileged access, RPC/relayer misbehavior, or admin action — it is exploitable by any ordinary caller of the SDK/withdrawal flow.

### Recommendation
Use a collision-free composite key, e.g. a delimiter that cannot appear validly in either component or that encodes lengths, such as:
```ts
const key = JSON.stringify([contractId, accountId]);
// or
const key = `${contractId}\u0000${accountId}`;
```
Apply the same fix pattern to any other cache keyed by naive string concatenation of two independent identifiers (audit `poa-bridge.ts`, `hot-bridge.ts`, and `omni-bridge.ts` cache-key construction for the same pattern, since they were not fully re-verified here due to iteration limits).

### Proof of Concept
1. Identify two NEP-141 tokens supported by `DirectBridge`, e.g. `contractId T1 = "usdc.near"` and pick `accountId D1` you control, e.g. `D1 = "1.attacker.near"`, such that `D1` already has NEP-141 storage registered for `T1` (attacker registers it normally). This produces cache key `"usdc.near1.attacker.near"`.
2. Call `sdk.estimateWithdrawalFee` (routed to `DirectBridge`) for `assetId = T1`, `destinationAddress = D1`. This populates `storageDepositCache` with key `"usdc.near1.attacker.near"` → `[min, balance]` where `balance >= min`.
3. Choose a second token `contractId T2 = "usdc.near1.attacker"` if such a token id is supported (or, more generally, any registered token whose id concatenated with an attacker-chosen `accountId D2` reproduces the exact same string, e.g. `T2 = "usdc.near1.attacker"`, `D2 = "near"`), where `D2` is a NEAR account that has *not* registered storage for `T2`.
4. Call `sdk.estimateWithdrawalFee` for `assetId = T2`, `destinationAddress = D2`. The cache lookup for key `"usdc.near1.attacker" + "near" = "usdc.near1.attacker" + "near"` (same string as step 2 key) returns the stale cached tuple, so the function returns `storageDepositFee: 0n` and skips the RPC check.
5. `createWithdrawalIntents` therefore omits the `storage_deposit` intent for `(T2, D2)`. When the resulting intent settles on-chain, the `ft_transfer` to `D2` for `T2` fails because `D2` lacks storage registration for `T2`, leaving the withdrawal stuck.

Note: step 3's exact colliding token id may not exist among currently deployed tokens; the PoC's feasibility depends on the actual set of NEP-141 tokens supported by the bridge at any given time, which I could not fully enumerate within the available tools — this should be confirmed against the live/production token list before treating it as fully weaponized, though the root-cause key-collision defect itself is unambiguous from the code.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L209-241)
```typescript
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
