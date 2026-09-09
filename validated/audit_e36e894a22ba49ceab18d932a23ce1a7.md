This confirms the RFC explicitly documents that batch withdrawals (e.g., "USDC to Solana + BTC refund to Bitcoin") are a supported use case, with the SDK exposing per-index promises where "Array index of returned promise matches array index of input `withdrawalParams`." The `poa-bridge.ts` implementation breaks this guarantee whenever two withdrawal entries in the same batch share an `assetId`.

### Title
`findMatchingWithdrawal` collapses distinct same-asset withdrawals to one status/txHash, causing duplicate credit/refund - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain status/txHash for a withdrawal by matching only on `assetId` via `findMatchingWithdrawal`, using `Array.prototype.find`, which always returns the first indexer entry for that `nep141:<near_token_id>` regardless of the requested `WithdrawalIdentifier.index`. When a single signed intent contains two POA-bridge withdrawals of the same token (different `amount`/`destinationAddress`), both `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` return the identical status/`txHash`, even though they are different withdrawals routed to different destinations.

### Finding Description
The broken equality: `describeWithdrawal({index:1}).txHash` should reflect withdrawal 1's own on-chain outcome, but instead equals `describeWithdrawal({index:0}).txHash`. Root cause is in `findMatchingWithdrawal` [1](#0-0) , which is called from `describeWithdrawal` without ever consulting `args.index` [2](#0-1) . The `withdrawal_hash` used to fetch the indexer's withdrawal list is `args.tx.hash` — the shared NEAR intent transaction hash for the whole batch — so a single API response contains all withdrawals of that intent, and when two of them share `assetId`, `.find()` deterministically picks whichever the indexer lists first for both index-0 and index-1 lookups.

Attacker input: an ordinary user (or a permissionless counterparty whose withdrawal params an integrator forwards) submits one signed intent with `withdrawalParams = [{assetId:"nep141:btc.omft.near", amount:A1, destinationAddress:D1}, {assetId:"nep141:btc.omft.near", amount:A2, destinationAddress:D2}]`. This is a fully legitimate, supported batch-withdrawal pattern per the RFC's own example (`USDC to Solana + BTC refund to Bitcoin`) [3](#0-2) , and nothing in `supports()`, `validateWithdrawal()`, or `createWithdrawalIntents()` rejects duplicate `assetId` within a batch.

Exploit flow: `createWithdrawalIdentifiers` assigns per-route sequential indexes (0 and 1) to the two same-asset withdrawals [4](#0-3) . `watchWithdrawal`/`createWithdrawalCompletionPromises` then poll `describeWithdrawal` independently for each entry, each carrying its own `index` [5](#0-4) . Both calls hit the same indexer response and `findMatchingWithdrawal` returns the same first match for both, so both promises resolve to the same `txHash`.

Existing guards do not catch this: `validateWithdrawal`, `compareAddresses`, and `supports()` validate per-withdrawal address/amount correctness but never check for duplicate `assetId` across the batch; the code's own comment at lines 409-416 explicitly acknowledges "multiple withdrawals of the same token in a single transaction are not supported" — i.e., this is a known, unresolved limitation with no compensating control anywhere in the call path.

### Impact Explanation
An integrator relying on `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` per-index results (as documented in the RFC, e.g. `if (index === 0) quoteEntity.destinationTx = tx.hash; if (index === 1) quoteEntity.refundTx = tx.hash;`) will record withdrawal 1's completion using withdrawal 0's `txHash`. This causes the integrator to credit or refund a user twice off one real on-chain transfer, while withdrawal 1's actual destination transfer status is never independently observed. This matches the High-severity category "a status or hash misreport making an integrator credit or refund twice." It is repeatable on every batch that contains ≥2 POA-bridge withdrawals of the same token.

### Likelihood Explanation
Precondition is simply constructing one signed intent with two (or more) POA-bridge withdrawal legs sharing the same `assetId` — a normal, unprivileged action requiring no special access, cost is one intent submission, and the RFC's own usage examples show this exact multi-leg pattern is an intended feature. It is deterministically reproducible every time such a batch is submitted, not a rare timing race.

### Recommendation
Disambiguate withdrawals sharing the same `assetId` in `findMatchingWithdrawal`, e.g., by sorting both the API's `withdrawals` list and the batch's same-asset entries by `amount` (fees are equal for a given token, so relative amount ordering should be preserved as noted in the existing code comment) and pairing them positionally, or by rejecting/disallowing duplicate-`assetId` batches at `validateWithdrawal`/`createWithdrawalIntents` time until the POA indexer API supports per-withdrawal correlation identifiers.

### Proof of Concept
```ts
// poa-bridge.test.ts
it("misreports index:1 status/txHash when batch has two same-asset withdrawals", async () => {
  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });

  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "btc.omft.near", transfer_tx_hash: "onchain-hash-for-leg-0" } },
    ],
  });

  const paramsLeg0 = { assetId: "nep141:btc.omft.near", amount: 100n, destinationAddress: "addrA" };
  const paramsLeg1 = { assetId: "nep141:btc.omft.near", amount: 200n, destinationAddress: "addrB" };

  const result0 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin, index: 0, withdrawalParams: paramsLeg0,
    tx: { hash: "shared-near-tx", accountId: "user.near" },
  });
  const result1 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin, index: 1, withdrawalParams: paramsLeg1,
    tx: { hash: "shared-near-tx", accountId: "user.near" },
  });

  // BROKEN EQUALITY: leg 1's reported txHash equals leg 0's, though they are different withdrawals
  expect(result1).toEqual(result0);
  expect(result1).toEqual({ status: "completed", txHash: "onchain-hash-for-leg-0" });
});
```

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L418-427)
```typescript
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

**File:** docs/design/rfc-batch-withdrawal-granular-control.md (L11-19)
```markdown
## Problem Statement

The SDK supports batch withdrawals - multiple tokens withdrawn in a single intent. For example: USDC to Solana + BTC refund to Bitcoin.

Current `waitForWithdrawalCompletion` has limitations:

1. **Waits for slowest** - Fast withdrawal (Solana ~2s) blocked by slow withdrawal (Bitcoin ~1hr)
2. **All-or-nothing failure** - If one withdrawal fails, entire function throws
3. **No progress visibility** - Can't know which withdrawals completed until all finish
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

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
```
