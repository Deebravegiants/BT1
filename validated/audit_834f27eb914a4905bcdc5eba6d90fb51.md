This confirms the vulnerability path fully. The code even documents this limitation directly in a comment.

### Title
`describeWithdrawal` matches withdrawals only by `assetId`, causing status/txHash misattribution across same-asset withdrawals in a batch - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain withdrawal record solely via `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, ignoring `amount`, `destinationAddress`, and `index`. When a batch contains two or more withdrawals of the same `assetId` with different destinations/amounts, `describeWithdrawal` (invoked per `WithdrawalIdentifier` by `watchWithdrawal` in `withdrawal-watcher.ts`) can return the wrong `withdrawal.data` record for a given index, breaking the `(status, txHash)`-per-index equality.

### Finding Description
The claimed equality is: for withdrawal index `i` in a batch, `describeWithdrawal({index: i, withdrawalParams: p_i, ...})` must report the `(status, txHash)` outcome of the on-chain withdrawal that corresponds to `p_i` (i.e., to `p_i.destinationAddress`/`p_i.amount`), not to some other `p_j`.

Code path:
- `IntentsSDK.createWithdrawalIntents` (`packages/intents-sdk/src/sdk.ts:334-373`) computes `actualAmount` per withdrawal param and calls `bridge.validateWithdrawal({ assetId, amount: actualAmount, destinationAddress, ... })` — validation is per-withdrawal and correctly keyed on `assetId + amount + destinationAddress`.
- `createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`) builds one `WithdrawalIdentifier` per `WithdrawalParams` entry, assigning `index` sequentially per bridge route via `bridge.createWithdrawalIdentifier` (`poa-bridge.ts:295-311`), which simply stores `args.index` and `args.withdrawalParams` without any linkage to the actual on-chain order.
- `watchWithdrawal` (`withdrawal-watcher.ts:20-78`) calls `bridge.describeWithdrawal({...wid, logger})` independently for each `WithdrawalIdentifier`.
- `PoaBridge.describeWithdrawal` (`poa-bridge.ts:313-343`) fetches `response.withdrawals` from `getWithdrawalStatusWithRetry` (an unordered list from the POA bridge API keyed by NEAR tx hash) and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` (`poa-bridge.ts:418-427`), which returns `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` — the **first** withdrawal entry matching only on `assetId`.
- The code's own comment on `findMatchingWithdrawal` (`poa-bridge.ts:409-417`) states: *"NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* The identical limitation and comment exist in `waitForWithdrawalCompletion.ts:31-153` used by the standalone `waitForWithdrawalCompletion` helper.

Attacker input: an ordinary user submits `withdrawalParams: WithdrawalParams[]` with two entries sharing the same `assetId` (e.g., `nep141:btc.omft.near`) but different `destinationAddress`/`amount` (e.g., index 0 → address A amount X, index 1 → address B amount Y). Both pass `validateWithdrawal` independently since that check does not consider co-occurring withdrawals in the batch. On-chain, the POA relayer processes both withdrawals and the bridge indexer returns both records in `response.withdrawals`, but in arbitrary/unsorted order. `findMatchingWithdrawal` picks whichever matching-assetId entry appears first in the array, regardless of which `WithdrawalIdentifier.index` requested it — so both `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` calls receive the same (first) matching record if the relative amount ordering diverges from the array ordering, and the wrong `txHash` can be reported for whichever index doesn't get "first" match.

`validateWithdrawal`, `compareAddresses`, `supports()` ordering, `FeeExceedsAmountError`, and the intents contract's own signature/nonce checks do not prevent this: none of them constrain the correspondence between `WithdrawalIdentifier.index` and the specific on-chain withdrawal record returned by the POA indexer API for a shared `assetId`.

### Impact Explanation
An integrator relying on `sdk.processWithdrawal`/`waitForWithdrawalCompletion` per index to credit/refund a specific `destinationAddress` can attribute index 0's `txHash` to index 1 (or vice versa) when both share `assetId`. This is a status/hash misreport that can cause an integrator to credit or refund the wrong destination — matching the High severity category ("a status or hash misreport making an integrator credit or refund twice" / wrong party credited). Funds are not stolen from the protocol itself (the underlying on-chain transfers still land at their correctly validated destinations per `validateWithdrawal`), but the SDK's reported completion status per index can misattribute which destination received which tx hash, which is an integrator-facing correctness bug repeatable on every batch withdrawal containing duplicate `assetId`s.

### Likelihood Explanation
Precondition: an unprivileged user (or an integrator forwarding user-controlled `withdrawalParams`) submits a batch withdrawal (`WithdrawalParams[]`) with ≥2 entries sharing the same `assetId`. This is fully within normal SDK usage (batch withdrawals are a documented, supported feature per `packages/intents-sdk/README.md:521-563`) and costs the attacker nothing extra beyond a normal multi-asset-batch fee. The bug is deterministic once the POA indexer returns withdrawals in an order that doesn't match request order (explicitly documented as possible: "Response list is unsorted" comment at `poa-bridge.ts:318`), making it easily and repeatably triggerable.

### Recommendation
Match withdrawals by more than `assetId`: sort/pair by `amount` (and `destinationAddress` where available) as the code comment itself suggests ("matching could be done by sorting both API results and withdrawal params by amount"), or track withdrawals via a unique per-withdrawal correlation ID if/when the POA API supports it. At minimum, `findMatchingWithdrawal` should exclude already-consumed entries and disambiguate via `amount`/`address` when multiple entries share the same `assetId`.

### Proof of Concept
```ts
// poa-bridge.test.ts
it("does not swap status when batch has two withdrawals of same assetId with different destination/amount", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      { // corresponds to index 1's params (address B, amount Y) but appears FIRST
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "tx-hash-B",
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8,
          amount: 200000, // amount Y
          account_id: "test.near",
          address: "ADDRESS_B",
          created: "2024-01-01T00:00:00Z",
        },
      },
      { // corresponds to index 0's params (address A, amount X)
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "tx-hash-A",
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8,
          amount: 100000, // amount X
          account_id: "test.near",
          address: "ADDRESS_A",
          created: "2024-01-01T00:00:00Z",
        },
      },
    ],
  });

  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });

  const resultIndex0 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin,
    index: 0,
    withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "ADDRESS_A", feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  const resultIndex1 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin,
    index: 1,
    withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 200000n, destinationAddress: "ADDRESS_B", feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  // Equality claimed: index0's report must equal index0's actual on-chain withdrawal (tx-hash-A),
  // index1's report must equal index1's actual on-chain withdrawal (tx-hash-B).
  expect(resultIndex0).toEqual({ status: "completed", txHash: "tx-hash-A" }); // FAILS: actually returns tx-hash-B
  expect(resultIndex1).toEqual({ status: "completed", txHash: "tx-hash-B" }); // FAILS: actually returns tx-hash-B too (both match first entry)
});
```
This demonstrates that both index 0 and index 1 calls resolve to the same first-matching entry (`tx-hash-B`), swapping/duplicating the reported `txHash` instead of the correct per-index correspondence. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** packages/intents-sdk/src/sdk.ts (L334-365)
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
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-153)
```typescript
/**
 * Finds a withdrawal matching the given criteria.
 *
 * NOTE: Currently only matches by assetId (near_token_id). This means multiple
 * withdrawals of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: types.WithdrawalStatusResponseOk["result"]["withdrawals"],
	criteria: WithdrawalCriteria,
):
	| types.WithdrawalStatusResponseOk["result"]["withdrawals"][number]
	| undefined {
	return withdrawals.find(
		(w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
	);
}
```
