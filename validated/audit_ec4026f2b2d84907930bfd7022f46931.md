### Title
Delimiter-less cache key collision in `getCachedStorageDepositValue` causes cross-account fee misquote - (File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts)

### Summary
`DirectBridge.getCachedStorageDepositValue` builds its `LRUCache` key by naively concatenating `contractId` and `accountId` with no separator (`` `${contractId}${accountId}` ``). Two distinct `(tokenAccountId, destinationAddress)` pairs whose strings concatenate identically collide on the same cache slot, so `estimateWithdrawalFee` can return storage-deposit data belonging to an unrelated token/account pair.

### Finding Description
The broken equality is: the storage state used to compute `feeAmount = minStorageBalance - userStorageBalance` for request `(tokenAccountId_A, destinationAddress_A)` must equal the on-chain storage state for that exact pair. Instead, because the cache key is `contractId + accountId` with no delimiter, a second request `(tokenAccountId_B, destinationAddress_B)` with `tokenAccountId_B + destinationAddress_B === tokenAccountId_A + destinationAddress_A` (but different actual pairs) will hit the same cache entry [1](#0-0) .

Critically, the cache is only populated when `result[1] >= result[0]` (i.e., only "already sufficiently funded, zero-fee" outcomes are cached) [2](#0-1) . This means every possible colliding cache read yields `minStorageBalance <= userStorageBalance`, so `estimateWithdrawalFee` always short-circuits to `feeAmount = 0n` for the colliding pair [3](#0-2) . The reverse case in the audit prompt (charging a nonzero fee to an already-funded account) cannot occur, since only zero-fee entries ever get cached — but the "false zero-fee" case is real and directly reachable.

Exploit flow: an attacker (or integrator relaying attacker-controlled parameters) calls `estimateWithdrawalFee` with `assetId` (→ `tokenAccountId_1`) and `destinationAddress_1` such that they already have sufficient NEP-141 storage on that token, seeding the shared cache under key `K = tokenAccountId_1 + destinationAddress_1`. If a different, real withdrawal request for `(tokenAccountId_2, destinationAddress_2)` — where `tokenAccountId_2 + destinationAddress_2 === K` — is later estimated on the same `DirectBridge` instance (which is long-lived and shared across all callers of a hosted SDK), it receives the poisoned zero-fee result. `createWithdrawalIntents` then calls `getUnderlyingFee(..., "storageDepositFee")` and builds the `ft_withdraw` intent with `storage_deposit = 0` [4](#0-3) , even though the destination account actually lacks the storage. The signed intent is submitted, and `ft_withdraw` fails on-chain post-signature because storage was never deposited, stranding the withdrawal.

Existing guards do not prevent this: `validateWithdrawal` only checks address format, token/destination mismatch, and (for explicit accounts) mere existence via a separately-keyed `accountExistenceCache` [5](#0-4)  — it never re-validates the storage-deposit numbers computed in `estimateWithdrawalFee`. `sdk.ts`'s `_estimateWithdrawalFee`/`createWithdrawalIntents` simply consume the bridge's `FeeEstimation` as ground truth [6](#0-5) .

### Impact Explanation
The consequence is an `ft_withdraw` intent signed and submitted with an incorrect (zero) `storage_deposit` amount for an account that actually requires one. The intent is valid and gets published/settled at the intents-contract layer, but the withdrawal fails on the destination NEAR contract due to missing storage, leaving the withdrawal stuck requiring manual intervention — matching the High severity category ("a withdrawal stuck until manual intervention"). Because the collision is a deterministic function of two account-id strings, it is fully repeatable: once a colliding pair is identified, it can be triggered on demand as long as the `DirectBridge` instance's cache is shared/long-lived across requests (typical for a server-side SDK deployment).

### Likelihood Explanation
Exploitability requires: (1) the attacker/integrator to control the `assetId`→`tokenAccountId` and `destinationAddress` strings for two separate `estimateWithdrawalFee` calls processed by the same long-lived `DirectBridge` instance, and (2) finding two `(contractId, accountId)` pairs whose raw string concatenation collides. Since `accountId` (the destination) is fully attacker-controlled and can be any syntactically valid NEAR account string, and NEP-141 token contract ids are drawn from a set of supported tokens (not a single fixed string), constructing a collision is a matter of choosing a destination string whose prefix matches another supported token's contract id (or vice versa) — a straightforward string-construction exercise, not one requiring any privileged access. The victim side just needs to be a legitimate future withdrawal that lands on the same collided key with a genuinely nonzero required storage deposit. This is plausible in any deployment where one SDK/bridge instance serves multiple withdrawal requests over time (the 1-hour TTL and 100-entry LRU make the window realistic).

### Recommendation
Use a collision-free cache key, e.g. include a delimiter and explicit lengths/hash: `` `${contractId.length}:${contractId}:${accountId}` ``, or use a tuple-based cache/Map keyed by `[contractId, accountId]`, or simply hash `contractId` and `accountId` separately before concatenating with a delimiter that cannot appear validly in a NEAR account id boundary ambiguity (e.g. `` `${contractId}\u0000${accountId}` `` combined with strict NEAR-account-id charset validation, or safer: always insert a fixed non-account-id character between them, such as `":"`, since NEAR account ids cannot contain `:`).

### Proof of Concept
```ts
// vitest test plan for packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.test.ts
// Mock getNearNep141MinStorageBalance / getNearNep141StorageBalance (HTTP-level mocks only).

it("cache key collision returns wrong storage-deposit result for a different (contractId, accountId) pair", async () => {
  const bridge = new DirectBridge({ envConfig, nearProvider, solverRelayApiKey: undefined });

  // Pair A: contractId = "a", accountId = "bc.near"  -> already funded (zero fee)
  mockMinStorageBalance("a", 1_250_000_000_000_000_000n);
  mockUserStorageBalance("a", "bc.near", 2_000_000_000_000_000_000n); // funded

  const feeA = await bridge.estimateWithdrawalFee({
    withdrawalParams: { assetId: "nep141:a", destinationAddress: "bc.near" },
  });
  expect(feeA.amount).toBe(0n); // correct: A is genuinely funded

  // Pair B: contractId = "ab", accountId = "c.near" -> concatenation collides: "a"+"bc.near" === "ab"+"c.near"
  // B is NOT actually funded on-chain.
  mockMinStorageBalance("ab", 1_250_000_000_000_000_000n);
  mockUserStorageBalance("ab", "c.near", 0n); // NOT funded, real fee should be 1_250_000_000_000_000_000n

  const feeB = await bridge.estimateWithdrawalFee({
    withdrawalParams: { assetId: "nep141:ab", destinationAddress: "c.near" },
  });

  // Equality that should hold: feeB.amount should reflect B's real storage deficit.
  // Because of the cache collision, it does not:
  expect(feeB.amount).toBe(0n);          // BUG: actually returned (wrong, from cache)
  // expect(feeB.amount).toBe(1_250_000_000_000_000_000n); // what it SHOULD be

  // Confirm the underlying HTTP mock for B's storage balance was never even called,
  // proving the cached (wrong) value for A was served instead.
  expect(userStorageBalanceMock).not.toHaveBeenCalledWith(
    expect.objectContaining({ contractId: "ab", accountId: "c.near" }),
  );
});
```
This demonstrates that `feeB.amount` (and thus the `storage_deposit` later embedded by `createWithdrawalIntents`) is computed from account A's storage state instead of account B's, violating the required equality between the quoted `feeEstimation.amount`/`storageDepositFee` and the true on-chain storage deficit for the requested `(tokenAccountId, destinationAddress)`.

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

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L154-192)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		if (validateAddress(args.destinationAddress, Chains.Near) === false) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				Chains.Near,
			);
		}

		const { contractId: tokenAccountId } = utils.parseDefuseAssetId(
			args.assetId,
		);

		if (
			compareAddresses(tokenAccountId, args.destinationAddress, Chains.Near)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenAccountId,
				args.assetId,
			);
		}

		// Only check account existence for explicit (named) accounts
		if (
			utils.isImplicitAccount(args.destinationAddress) === false &&
			(await this.getCachedAccountExistenceCheck(args.destinationAddress)) ===
				false
		) {
			throw new DestinationExplicitNearAccountDoesntExistError(
				args.destinationAddress,
			);
		}

		return;
	}
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

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L273-281)
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
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L295-297)
```typescript
		if (result[1] >= result[0]) {
			this.storageDepositCache.set(key, result);
		}
```

**File:** packages/intents-sdk/src/sdk.ts (L408-453)
```typescript
	protected async _estimateWithdrawalFee(args: {
		withdrawalParams: WithdrawalParams;
		quoteOptions?: QuoteOptions;
		logger?: ILogger;
	}): Promise<FeeEstimation> {
		for (const bridge of this.bridges) {
			if (await bridge.supports(args.withdrawalParams)) {
				const fee = await bridge.estimateWithdrawalFee({
					withdrawalParams: args.withdrawalParams,
					quoteOptions: args.quoteOptions,
					logger: args.logger,
				});

				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
				}
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - fee.amount
					: args.withdrawalParams.amount;

				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					feeEstimation: fee,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
					destinationMemo: args.withdrawalParams.destinationMemo,
					// When estimating fees before the exact amount is known, skip minimum amount validation while keeping all other validation intact.
					skipMinAmountValidation:
						args.withdrawalParams.amount === 0n &&
						args.withdrawalParams.feeInclusive === false,
				});

				return fee;
			}
		}

		throw new Error(
			`Cannot determine bridge for withdrawal = ${stringify(
				args.withdrawalParams,
			)}`,
		);
	}
```
