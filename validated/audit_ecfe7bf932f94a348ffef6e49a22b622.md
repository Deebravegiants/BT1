This confirms the finding: there is no mechanism anywhere in `createWithdrawalIntents`, `validateWithdrawal`, or `createWithdrawalIdentifiers`/`watchWithdrawal` that prevents or accounts for a batch containing two POA-bridge withdrawals of the same `assetId` to different destinations. `findMatchingWithdrawal` uses `.find()` keyed only on `nep141:<near_token_id>`, ignoring `index`/amount/address entirely, so both watchers converge on the same array entry.### Title
`describeWithdrawal` misreports destination tx hash for batches with duplicate `assetId` on PoaBridge - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the status of a specific withdrawal in a batch using `findMatchingWithdrawal`, which matches purely by `nep141:<near_token_id>` (i.e., by `assetId`) and ignores the withdrawal's `index`, destination address, or amount. When a `processWithdrawal` batch contains two POA-bridge withdrawals of the *same* token to two *different* destination addresses, both `watchWithdrawal` calls converge on the same array entry, so an integrator can be told a withdrawal to address B "completed" with the transaction hash that actually corresponds to the transfer sent to address A.

### Finding Description
The equality that must hold is: for withdrawal `wid[i]` (with `withdrawalParams.destinationAddress = D_i`, `amount = A_i`), `describeWithdrawal({..., index: i})` must report the on-chain status/`txHash` of *the transfer that actually went to `D_i` for amount `A_i`*, not of some other batch member's transfer.

Code path:
- `IntentsSDK.processWithdrawal` (`packages/intents-sdk/src/sdk.ts:793-857`) accepts `withdrawalParams: WithdrawalParams[]`, estimates fees, signs/sends the intent, and calls `waitForWithdrawalCompletion`, which uses `createWithdrawalIdentifiers` and `watchWithdrawal` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:20-107`).
- `createWithdrawalIdentifiers` assigns a per-bridge-route `index` counter (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`); for two POA-bridge withdrawals of the same token, `index` is `0` and `1` respectively, and both `WithdrawalIdentifier`s carry the correct, distinct `withdrawalParams` (including `destinationAddress` and `amount`).
- `watchWithdrawal` polls `bridge.describeWithdrawal({...wid, logger})` independently for each `WithdrawalIdentifier` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:36-39`).
- `PoaBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`) calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which is:
```
function findMatchingWithdrawal(withdrawals, assetId) {
  return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```
(`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427`). This uses `Array.prototype.find`, which always returns the *first* array element matching the `assetId`, regardless of `args.index`, `args.withdrawalParams.destinationAddress`, or `args.withdrawalParams.amount`. The comment explicitly documents the limitation: "This means multiple withdrawals of the same token in a single transaction are not supported."

Exploit flow:
1. Attacker (an unprivileged caller / integrator-forwarded params) calls `sdk.processWithdrawal({ withdrawalParams: [ { assetId: "nep141:eth.omft.near", amount: A1, destinationAddress: D1 }, { assetId: "nep141:eth.omft.near", amount: A2, destinationAddress: D2 } ] })`.
2. Both withdrawals pass `PoaBridge.validateWithdrawal` and `createWithdrawalIntents` independently — nothing in `IntentsSDK.createWithdrawalIntents` (`packages/intents-sdk/src/sdk.ts:334-372`) rejects duplicate `assetId` entries in a batch.
3. The signed intent is published and settles; POA bridge processes both transfers to `D1` and `D2`.
4. `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` spawns two independent `watchWithdrawal` polls, one for `index:0` (expecting `D1`), one for `index:1` (expecting `D2`).
5. `poaBridge.httpClient.getWithdrawalStatus` returns an *unsorted* list containing both withdrawal records. `findMatchingWithdrawal` on each call returns the array's first matching element by `assetId` — i.e., **the same record for both `index:0` and `index:1` calls** unless the array happens to be ordered so it doesn't overlap (which is not guaranteed, and the code comment states it explicitly is not deduplicated by index).
6. As a result, both watchers can report `completed` with the *same* `txHash` (e.g., the transfer to `D1`), even though the second withdrawal to `D2` is a physically distinct, separately settled transfer with its own `transfer_tx_hash`.

Existing guards do not catch this:
- `validateAddress`/`compareAddresses` only check a single withdrawal's own address validity, not cross-batch collisions.
- `validateWithdrawal` has no batch-level dedupe check.
- No `assert` anywhere compares the reported recipient/amount to the intended `destinationAddress`/`amount` of the specific `index`.
- The intents contract's own signature/nonce verification governs on-chain fund movement (funds do go to the correct on-chain addresses via `ft_withdraw`/POA bridge relayer), but does not affect this SDK-side *status reporting* bug.

### Impact Explanation
No funds are misrouted on-chain — the underlying POA relayer still sends `A1` to `D1` and `A2` to `D2` correctly (assuming the relayer processes the withdrawals faithfully, which is a bridge API trust assumption out of scope here). What is *misreported* to the caller of `processWithdrawal`/`waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` is which `txHash` belongs to which requested `index`. An integrator that keys off `destinationTx[index].hash` to credit accounts, mark orders as fulfilled, or release goods/services could attribute the wrong on-chain transaction to the wrong withdrawal request, potentially causing it to credit/refund the wrong withdrawal twice (if it later cross-checks the tx hash against a different on-chain explorer and finds a mismatch) or to incorrectly resolve a support/dispute claim about which withdrawal completed. This matches the High category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Preconditions: an unprivileged caller/integrator submits a `processWithdrawal` batch with **two or more POA-bridge withdrawals sharing the same `assetId`** to different destinations — a completely normal, unprivileged use of the public batch API (no special permissions, no malicious relayer/RPC required). Cost is a single batch of ordinary withdrawal amounts. It is repeatable on every batch containing duplicate-asset withdrawals via PoaBridge, and the codebase's own comments confirm awareness that this scenario is unhandled ("not supported").

### Recommendation
In `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`, either:
1. Reject batches containing duplicate `assetId` withdrawals routed to PoaBridge at `validateWithdrawal`/`createWithdrawalIntents` time (fail closed until multi-match is supported), or
2. Implement proper index-aware matching in `findMatchingWithdrawal` — e.g., sort both the API response and the requested withdrawals by `amount` (as the existing comment suggests) and match positionally, additionally verifying `destinationAddress`/`amount` in the returned `data.address`/`data.amount` fields against the expected `withdrawalParams` before returning `completed`, and only report `completed` when this cross-check equality holds; otherwise keep the withdrawal `pending` or raise an explicit ambiguity error.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.dup-asset.test.ts
it("describeWithdrawal misreports txHash for duplicate-assetId batch entries", async () => {
  const D1 = "0x1111111111111111111111111111111111111111";
  const D2 = "0x2222222222222222222222222222222222222222";

  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: {
          tx_hash: "near-tx-hash", transfer_tx_hash: "tx-for-D1",
          chain: "eth", defuse_asset_identifier: "nep141:eth.omft.near",
          near_token_id: "eth.omft.near", decimals: 18, amount: 1000,
          account_id: "test.near", address: D1, created: "2024-01-01T00:00:00Z",
      }},
      { status: "COMPLETED", data: {
          tx_hash: "near-tx-hash", transfer_tx_hash: "tx-for-D2",
          chain: "eth", defuse_asset_identifier: "nep141:eth.omft.near",
          near_token_id: "eth.omft.near", decimals: 18, amount: 2000,
          account_id: "test.near", address: D2, created: "2024-01-01T00:00:00Z",
      }},
    ],
  });

  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });

  const resultForIndex0 = await bridge.describeWithdrawal({
    landingChain: Chains.Ethereum, index: 0,
    withdrawalParams: { assetId: "nep141:eth.omft.near", amount: 1000n, destinationAddress: D1, feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  const resultForIndex1 = await bridge.describeWithdrawal({
    landingChain: Chains.Ethereum, index: 1,
    withdrawalParams: { assetId: "nep141:eth.omft.near", amount: 2000n, destinationAddress: D2, feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  // BROKEN INVARIANT: both report the SAME txHash ("tx-for-D1"), even though
  // index 1's signed intent targeted D2/amount 2000, not D1/amount 1000.
  expect(resultForIndex0.txHash).toBe("tx-for-D1");
  expect(resultForIndex1.txHash).toBe("tx-for-D1"); // should be "tx-for-D2" but isn't
  expect(resultForIndex0.txHash).toEqual(resultForIndex1.txHash); // demonstrates reported != signed for index 1
});
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-343)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const response = await this.getWithdrawalStatusWithRetry(args);

		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);

		if (withdrawal == null) {
			return { status: "pending" };
		}

		if (withdrawal.status === "PENDING") {
			return { status: "pending" };
		}

		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
		}

		return {
			status: "failed",
			reason: withdrawal.status,
		};
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-427)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	// POA bridge only supports NEP-141 tokens. The API returns `near_token_id`
	// (e.g., "zec.omft.near") which we prefix with "nep141:" to match assetId format.
	// Note: `defuse_asset_identifier` cannot be used as it contains chain-native
	// format (e.g., "zec:mainnet:native") which differs from the assetId format.
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-39)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

	try {
		return await poll(
			async () => {
				try {
					const status = await args.bridge.describeWithdrawal({
						...args.wid,
						logger: args.logger,
					});
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
}): Promise<{ bridge: Bridge; wid: WithdrawalIdentifier }[]> {
	const indexes = new Map<string, number>();
	const results: { bridge: Bridge; wid: WithdrawalIdentifier }[] = [];

	for (const w of args.withdrawalParams) {
		const bridge = await findBridgeForWithdrawal(args.bridges, w);
		if (bridge == null) {
			throw new BridgeNotFoundError();
		}

		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});

		results.push({ bridge, wid });
	}

	return results;
}
```

**File:** packages/intents-sdk/src/sdk.ts (L334-372)
```typescript
	public async createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
		logger?: ILogger;
	}): Promise<IntentPrimitive[]> {
		for (const bridge of this.bridges) {
			if (await bridge.supports(args.withdrawalParams)) {
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - args.feeEstimation.amount
					: args.withdrawalParams.amount;

				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					destinationMemo: args.withdrawalParams.destinationMemo,
					feeEstimation: args.feeEstimation,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
				});

				return bridge.createWithdrawalIntents({
					withdrawalParams: {
						...args.withdrawalParams,
						amount: actualAmount,
					},
					feeEstimation: args.feeEstimation,
					referral: args.referral ?? this.referral,
				});
			}
		}

		throw new Error(
			`Cannot determine bridge for withdrawal = ${stringify(
				args.withdrawalParams,
			)}`,
		);
	}
```

**File:** packages/intents-sdk/src/sdk.ts (L793-857)
```typescript
	async processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams | WithdrawalParams[]>,
	): Promise<WithdrawalResult | BatchWithdrawalResult> {
		const withdrawalParams = Array.isArray(args.withdrawalParams)
			? args.withdrawalParams
			: [args.withdrawalParams];

		// Step 1: Estimate fee
		const feeEstimation = await (() => {
			if (args.feeEstimation != null) {
				return Array.isArray(args.feeEstimation)
					? args.feeEstimation
					: [args.feeEstimation];
			}

			return this.estimateWithdrawalFee({
				withdrawalParams,
				logger: args.logger,
			});
		})();

		// Step 2: Sign and send intent
		const { intentHash } = await this.signAndSendWithdrawalIntent({
			withdrawalParams,
			feeEstimation,
			referral: args.referral,
			intent: args.intent,
			logger: args.logger,
		});

		args.logger?.info("Intent published", { intentHash });

		// Step 3: Wait for intent settlement
		const intentTx = await this.waitForIntentSettlement({
			intentHash: intentHash,
			logger: args.logger,
		});

		args.logger?.info("Intent settled", { txHash: intentTx.hash });

		// Step 4: Wait for withdrawal completion
		const destinationTx = await this.waitForWithdrawalCompletion({
			withdrawalParams,
			intentTx,
			logger: args.logger,
		});

		if (!Array.isArray(args.withdrawalParams)) {
			return {
				// biome-ignore lint/style/noNonNullAssertion: single withdrawal returns single-element arrays
				feeEstimation: feeEstimation[0]!,
				intentHash,
				intentTx,
				// biome-ignore lint/style/noNonNullAssertion: single withdrawal returns single-element arrays
				destinationTx: destinationTx[0]!,
			};
		}

		return {
			feeEstimation,
			intentHash,
			intentTx,
			destinationTx,
		};
	}
```
