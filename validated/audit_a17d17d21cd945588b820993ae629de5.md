### Title
`describeWithdrawal` in `PoaBridge` matches withdrawal status by `assetId` only, causing status/hash misattribution for duplicate-asset withdrawals in the same transaction - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves the status of a specific withdrawal (identified by `WithdrawalIdentifier.index`) by calling `findMatchingWithdrawal`, which ignores the `index` field entirely and matches purely on `assetId`. When a NEAR transaction contains multiple withdrawal intents for the same token, `waitForWithdrawalCompletion`/`describeWithdrawal` for withdrawal #2 can return the completion status (and destination `txHash`) that actually belongs to withdrawal #1.

### Finding Description
`createWithdrawalIdentifier` returns a `WithdrawalIdentifier` that carries a per-withdrawal `index`: [1](#0-0) 

`describeWithdrawal` then looks up status via `findMatchingWithdrawal`, but the comment and implementation explicitly discard `index` and only compare `assetId`: [2](#0-1) [3](#0-2) 

This mirrors the reported bug class: an identity field that should be bound into the lookup/verification (here, the withdrawal `index`, analogous to `leaf_idx` in the report) is silently ignored, so two different withdrawal instances can resolve to the same underlying record. The code comment even acknowledges: *"multiple withdrawals of the same token in a single transaction are not supported"*, confirming this is a known, reachable gap rather than a hypothetical.

This is invoked from `sdk.waitForWithdrawalCompletion`, which is explicitly designed to support arrays of withdrawal params (multiple withdrawals) and returns a matched array of results, as shown in its own test suite: [4](#0-3) 

If a caller submits two `ft_withdraw` intents for the same `assetId` in one NEAR transaction (e.g., splitting a withdrawal across two destination legs, or two sequential withdrawals of the same token), `findMatchingWithdrawal` returns the *first* withdrawal in the (unordered) API response for both `describeWithdrawal` calls. Once the first withdrawal completes, both `describeWithdrawal(index=0)` and `describeWithdrawal(index=1)` report `status: "completed"` with the *same* `txHash`, even though the second withdrawal may still be pending, failed, or refunded on-chain.

### Impact Explanation
An integrator relying on `waitForWithdrawalCompletion`/`describeWithdrawal` to confirm on-chain settlement before releasing a corresponding off-chain credit (e.g., crediting a user's balance, marking an order fulfilled, or unlocking a matched leg of a swap) would be told that withdrawal #2 completed with a specific destination hash while, in reality, no such completion happened for that withdrawal — the reported `txHash` belongs to a different withdrawal. This is a status/hash misreport that can cause an integrator to credit or release funds for a withdrawal that has not actually completed, matching the "status or hash misreport making an integrator credit or refund twice" category.

### Likelihood Explanation
This requires no privileged access — any unprivileged user (or an integrator building multi-leg withdrawal flows) can trigger the condition by submitting a NEAR transaction with two `ft_withdraw` intents for the same `assetId`. The SDK explicitly supports batched/array withdrawal params in `waitForWithdrawalCompletion`, making this a directly reachable path rather than a purely theoretical scenario. It is somewhat narrowed by the precondition of "same token withdrawn more than once in the same tx," which the developers acknowledge is currently unsupported/untested — but it is not otherwise blocked or validated against.

### Recommendation
Incorporate `claim`-equivalent disambiguation into `findMatchingWithdrawal`: use the POA API's per-withdrawal ordering/amount, or reject/queue distinct handling when multiple withdrawals share the same `assetId` in one transaction, instead of silently returning the first match for every `index`. At minimum, `describeWithdrawal` should assert that at most one candidate withdrawal matches per transaction+assetId, or explicitly track already-consumed withdrawal records so the same underlying withdrawal cannot be attributed to two different `index` values.

### Proof of Concept
1. User submits one NEAR transaction with two `ft_withdraw` intents, both for `assetId = "nep141:foo.omft.near"` (e.g., withdrawal A to address X, withdrawal B to address Y).
2. Integrator calls `sdk.waitForWithdrawalCompletion({ intentTx, withdrawalParams: [paramsA, paramsB] })`, which internally calls `PoaBridge.describeWithdrawal` for index 0 and index 1.
3. The POA bridge indexer reports withdrawal A as `COMPLETED` with `transfer_tx_hash = "hashA"`; withdrawal B is still `PENDING`.
4. `findMatchingWithdrawal` for both index 0 and index 1 filters `withdrawals` by `assetId` only [5](#0-4) , so both calls find the same completed record and return `{ status: "completed", txHash: "hashA" }` for both index 0 and index 1.
5. The integrator's code treats withdrawal B as completed with `hashA`, even though withdrawal B has not settled on-chain, potentially triggering a duplicate/incorrect off-chain credit or reconciliation action for funds that have not actually moved to destination Y.

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

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L43-68)
```typescript
	it("supports multiple withdrawals (preserving tx info order)", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal)
			.mockImplementationOnce(() =>
				wait(300).then(() => ({
					status: "completed" as const,
					txHash: "fake-dest-hash-1",
				})),
			)
			.mockResolvedValueOnce({
				status: "completed",
				txHash: "fake-dest-hash-2",
			});

		const result = sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams],
		});

		await expect(result).resolves.toEqual([
			{ hash: "fake-dest-hash-1" },
			{ hash: "fake-dest-hash-2" },
		]);
		expect(mockBridge.describeWithdrawal).toHaveBeenCalledTimes(2);
	});
```
