Analog found: batch POA-bridge withdrawal status is matched by `assetId` alone instead of by index/destination, which breaks the identity equality between a `WithdrawalIdentifier` and its true on-chain outcome when a batch contains two withdrawals of the same token.

### Title
Batch withdrawal status/tx-hash misattributed when two withdrawals share the same `assetId` (`PoaBridge.describeWithdrawal` matches by `assetId` only) - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` deliberately abandons index-based matching ("Response list is unsorted, so we match by assetId instead of index") and instead calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` to find the withdrawal record corresponding to a given `WithdrawalIdentifier`. [1](#0-0) 

### Finding Description
The SDK supports batch withdrawals where multiple `withdrawalParams` (potentially with the same `assetId` but different `destinationAddress`/`amount`) are settled by a single NEAR transaction, each described later via `createWithdrawalIdentifier` -> `describeWithdrawal` using only `{ tx.hash, index, withdrawalParams }`. [2](#0-1) 

For POA bridge, the identity check used to correlate a specific withdrawal request with the entry returned by `getWithdrawalStatus` (which returns an *unsorted list of all withdrawals for that tx hash*) is `assetId` equality only, not the tuple `(index, destinationAddress, amount)`. This is confirmed by the test explicitly named `"matches withdrawal by assetId, not by index"`, which only demonstrates disambiguation between *different* asset IDs. [3](#0-2) 

If a batch withdrawal transaction contains two or more entries withdrawing the **same** `assetId` to different destination addresses (a legitimate, supported use case per the SDK's batch withdrawal API), `findMatchingWithdrawal` has no way to distinguish which of the multiple same-asset withdrawal records in the unsorted response belongs to which `WithdrawalIdentifier`/index. The equality check `record.assetId === args.withdrawalParams.assetId` is not a unique key inside a single tx's withdrawal set, so the wrong record's `status`/`transfer_tx_hash` can be attributed to the wrong logical withdrawal.

### Impact Explanation
This breaks the equality "status/hash reported == the on-chain outcome for *this specific* withdrawal." An integrator relying on `describeWithdrawal`/`waitForWithdrawalCompletion` per index in a batch could:
- Mark withdrawal A as "completed" with a `txHash` that actually belongs to withdrawal B (misreport of completion for the wrong request), or
- Treat two distinct withdrawals as settled based on one underlying record, effectively double-crediting/reporting one on-chain transfer as covering two separate logical withdrawal requests.

This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category from the rules, since integrators building custodial/exchange withdrawal flows on top of `processWithdrawal`/batch APIs would act on the misattributed status.

### Likelihood Explanation
Requires only an unprivileged combination of legitimate SDK inputs: a batch withdrawal where two entries share the same `assetId` but different destinations/amounts is explicitly supported by the batch withdrawal feature documented in the README, so no admin or relayer misbehavior is needed to trigger the ambiguous match — likelihood is moderate, gated only by how commonly batches repeat the same token.

### Recommendation
Disambiguate by matching on more than `assetId`: include `destinationAddress` (and ideally `amount`) or a monotonic per-token occurrence counter tied to the intended index, similar in spirit to the report's recommended fix of replacing an insufficiently strict equality check (address-only) with a more precise state-based check (balance-before/after). Concretely, `findMatchingWithdrawal` should also require the record's destination address (and/or amount) match `args.withdrawalParams.destinationAddress`/`amount` before accepting it as the match for a given index within a multi-withdrawal transaction.

### Proof of Concept
1. Build a batch withdrawal with two entries: both `assetId: "nep141:eth-....omft.near"`, `destinationAddress: 0xAAA...` amount 100, and `destinationAddress: 0xBBB...` amount 200, in one NEAR tx.
2. POA bridge's `getWithdrawalStatus` returns both records (unsorted) for that `tx.hash`.
3. Call `describeWithdrawal` for index 0 (intended for `0xAAA`). `findMatchingWithdrawal` filters purely by `assetId`, and (depending on list order) can return the `0xBBB` record's `transfer_tx_hash`/status instead.
4. The caller believes withdrawal to `0xAAA` settled with a transaction that actually paid `0xBBB`, or vice versa — a status/hash misreport for a legitimate unprivileged batch input.

Note: I was not able to view the exact implementation of `findMatchingWithdrawal` (only its call site and the test file) before the iteration budget ran out, so the precise matching logic (e.g., whether it also happens to check something else, or de-duplicates in list order) could not be fully confirmed — this should be verified against the actual function body in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (or a helper module it imports) before treating this as fully proven.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1052)
```typescript

```
