### Title
`PoaBridge.findMatchingWithdrawal` matches by `assetId` only, ignoring `index`, causing identical `txHash`/status to be reported for two distinct withdrawals of the same token in one intent - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`describeWithdrawal` resolves the POA on-chain payout for a `WithdrawalIdentifier` purely via `findMatchingWithdrawal`, which selects the first API record whose `nep141:${near_token_id}` equals `args.withdrawalParams.assetId`, never consulting `args.index`. When an intent transaction contains two `WithdrawalParams` for the same `assetId` (e.g. two `nep141:btc.omft.near` withdrawals to different `destinationAddress`), both `WithdrawalIdentifier{index:0}` and `{index:1}` resolve to the same (or an ambiguous) API record, so `watchWithdrawal` reports the same `{status:'completed', txHash}` for both withdrawals.

### Finding Description
Broken equality: `(status, txHash)` reported by `describeWithdrawal(index=0)` should equal the outcome of on-chain withdrawal #0, and `describeWithdrawal(index=1)` should equal the outcome of withdrawal #1, independently. In the vulnerable code, both calls query `poaBridge.httpClient.getWithdrawalStatus({withdrawal_hash: args.tx.hash})` (same NEAR intent tx hash for all indices), which returns a list of individual withdrawal payouts. `findMatchingWithdrawal` then does: [1](#0-0) 

This selects `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` — the *first* matching record by asset only, with no use of `args.index`, `destinationAddress`, or `amount` to disambiguate which physical payout corresponds to which `WithdrawalParams` entry. `describeWithdrawal` at [2](#0-1)  then returns `{status:'completed', txHash: withdrawal.data.transfer_tx_hash}` built from this single ambiguous match.

The code itself documents this limitation: [3](#0-2) 

An identical pattern (root cause shared) exists in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`'s `findMatchingWithdrawal` [4](#0-3) .

Exploit flow: an unprivileged NEAR Intents user (or an integrator forwarding user-supplied `withdrawalParams`) submits an intent with two `WithdrawalParams` entries sharing `assetId: "nep141:btc.omft.near"`, `feeInclusive:false`, but different `destinationAddress` values. `createWithdrawalIdentifiers` assigns per-route sequential indices (`index:0`, `index:1`) [5](#0-4) , but nothing in that indexing logic, nor in `PoaBridge.createWithdrawalIdentifier` [6](#0-5) , nor in `supports`/`validateWithdrawal`, rejects or disambiguates duplicate `assetId` withdrawals within one transaction. When both payouts are later resolved via the POA bridge indexer, the same `.find()` result (or same first-hit record) is returned for both `index:0` and `index:1` calls of `watchWithdrawal`/`describeWithdrawal`, so `TxInfo.hash` is identical for both, even though on-chain there are two distinct destination transactions.

None of the existing guards (`validateAddress`, `compareAddresses`, `validateWithdrawal`'s min-amount/XRPL checks, `supports()` ordering, `FeeExceedsAmountError`, `assert` sanity checks) address this because they operate on a single `WithdrawalParams` at creation/estimation time and never cross-check multiple withdrawal params for `assetId` collisions, nor does the intents contract itself constrain off-chain status reporting.

### Impact Explanation
An integrator (or the SDK's own `createWithdrawalCompletionPromises` / `waitForWithdrawalCompletion`) that credits or clears a per-index ledger entry based on `describeWithdrawal`/`watchWithdrawal` output will mark **both** withdrawals as completed with the same `txHash`, even though only one on-chain transfer actually occurred (or the wrong one is attributed). This is a status/hash misreport that can cause the integrator to double-credit funds to a user, double-clear a liability, or refund twice — matching the **High** impact category ("a status or hash misreport making an integrator credit or refund twice"). It is repeatable for every intent transaction containing ≥2 same-asset withdrawals routed through POA bridge.

### Likelihood Explanation
Preconditions: the attacker needs only to submit a normal NEAR intents transaction (as any ordinary user/integrator-forwarded input) containing two `WithdrawalParams` with the same POA-bridge-supported `assetId` and distinct `destinationAddress`. No privileged access, no contract admin, no malicious relayer/RPC required — this is triggered purely through the documented public SDK surface (`createWithdrawalCompletionPromises`, `waitForWithdrawalCompletion`, or direct `PoaBridge.describeWithdrawal` calls). Cost is a single normal transaction; the ambiguity is deterministic and reproducible every time duplicate-asset withdrawals are batched, as explicitly acknowledged by the code comment.

### Recommendation
Disambiguate matches using more than `assetId`: include `destinationAddress` (and/or `amount`, adjusted for fees) in the match criteria, or — as the code comment suggests — sort both the API's returned withdrawals and the local `withdrawalParams` list by amount for same-asset entries and match by position. Until the POA bridge API supports returning a per-withdrawal correlation id, `PoaBridge` should detect duplicate `assetId` withdrawals within the same intent transaction and either refuse to disambiguate (return `pending`/throw an explicit `AmbiguousWithdrawalMatchError`) rather than silently returning a possibly-wrong match, or implement the sort-by-amount matching heuristic across all withdrawals of that asset in the batch.

### Proof of Concept
Vitest test in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts` (mocking only `poaBridge.httpClient.getWithdrawalStatus`):

```ts
it("BUG: reports identical txHash for two distinct same-asset withdrawals", async () => {
  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });

  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          near_token_id: "btc.omft.near",
          transfer_tx_hash: "0xonly-one-payout-seen",
          chain: "btc:mainnet",
        },
      },
    ],
  });

  const tx = { hash: "same-intent-tx", accountId: "user.near" };
  const wid0 = bridge.createWithdrawalIdentifier({
    withdrawalParams: {
      assetId: "nep141:btc.omft.near",
      amount: 100n,
      destinationAddress: "bc1qDestinationA...",
      feeInclusive: false,
    },
    index: 0,
    tx,
  });
  const wid1 = bridge.createWithdrawalIdentifier({
    withdrawalParams: {
      assetId: "nep141:btc.omft.near",
      amount: 200n,
      destinationAddress: "bc1qDestinationB...",
      feeInclusive: false,
    },
    index: 1,
    tx,
  });

  const status0 = await bridge.describeWithdrawal(wid0);
  const status1 = await bridge.describeWithdrawal(wid1);

  // Assert the broken equality: both indices report the SAME txHash,
  // even though they represent two different on-chain destinations/amounts.
  expect(status0).toEqual({ status: "completed", txHash: "0xonly-one-payout-seen" });
  expect(status1).toEqual({ status: "completed", txHash: "0xonly-one-payout-seen" });
  expect(status0).toEqual(status1); // STATUS TRUTH equality violated
});
```

This confirms `watchWithdrawal`/`createWithdrawalCompletionPromises` (which call `describeWithdrawal` per index) would resolve both promises with identical `{hash: "0xonly-one-payout-seen"}`, letting an integrator double-credit destination B's expected payout using destination A's actual (or an indeterminate) transaction.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-311)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		const assetInfo = this.parseAssetId(args.withdrawalParams.assetId);
		assert(assetInfo != null, "Asset is not supported");

		const landingChain = assetInfo.blockchain;

		return {
			landingChain,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
	}
```

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-417)
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
