### Title
`describeWithdrawal()` in PoaBridge can report the wrong withdrawal status for a batched same-asset withdrawal - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` matches a POA-bridge withdrawal-status entry to a specific batch index by asset id only, not by index, destination address, or amount. This is analogous to the reported `NoteERC20.getPriorVotes` issue: two different code paths (the direct index-based checkpoint and the binary-search branch) return inconsistent results for the "same" logical query, and one branch's output can be substituted for the wrong query. Here, when a batch withdrawal contains multiple withdrawals of the *same* `assetId` to different destinations/amounts, the by-asset lookup can bind the completion status/tx-hash of one withdrawal to the `WithdrawalIdentifier` of another, breaking the equality "status reported == actual on-chain outcome for this specific withdrawal".

### Finding Description
`describeWithdrawal` calls: [1](#0-0) 

The relevant match is done via:
```
// Response list is unsorted, so we match by assetId instead of index
const withdrawal = findMatchingWithdrawal(
    response.withdrawals,
    args.withdrawalParams.assetId,
);
``` [2](#0-1) 

The comment itself acknowledges that the API's `withdrawals` array is unordered and correlation with a specific batch index is done solely through `assetId`, ignoring `destinationAddress` and `amount`, which are also part of `WithdrawalIdentifier.withdrawalParams`. `WithdrawalIdentifier` is produced from `createWithdrawalIdentifier`, which carries the full `withdrawalParams` (assetId, amount, destinationAddress) and the batch `index`: [3](#0-2) 

When an intent bundles two or more withdrawals of the *same* `assetId` (a supported, common use case per the batch-withdrawal design docs), asset-id-only matching cannot disambiguate which server-side withdrawal record corresponds to which batch index. If the matching helper returns the first (or any) record with a matching `assetId` regardless of which index already consumed it, `describeWithdrawal({index: 0, ...})` and `describeWithdrawal({index: 1, ...})` can both resolve to the same underlying withdrawal record — i.e., both indices report identical `status`/`txHash`, even though only one of the two withdrawals has actually settled on-chain.

I could not retrieve the full body of `findMatchingWithdrawal` (only its usage and the explanatory comment were available), so I cannot confirm whether it deduplicates already-consumed entries. The comment explicitly documents the design choice to match on `assetId` alone rather than `index`, which is the root cause regardless of the exact matching algorithm's dedup behavior.

### Impact Explanation
`WithdrawalStatus` (status + txHash) returned by `describeWithdrawal` is consumed by callers such as `watchWithdrawal`/`waitForWithdrawalCompletion` to decide when a withdrawal has settled: [4](#0-3) 

If two same-asset withdrawals in a batch are conflated, an integrator polling per-index completion (as designed in the granular batch-withdrawal RFC) could be told that both withdrawals completed with the same `txHash`/status while only one has actually landed on the destination chain — i.e., "a status or hash misreport making an integrator credit or refund twice," which is explicitly named as a High-impact bucket in the rules.

### Likelihood Explanation
Batched same-asset withdrawals are a supported, ordinary use case (not requiring any malicious actor), so this can be triggered by a normal user/integrator simply submitting two withdrawals of the same token to different addresses in one intent — no cooperation from relayer/bridge operator/admin required.

### Recommendation
Match POA bridge withdrawal-status entries deterministically per batch index — e.g., by also filtering on `destinationAddress` and `amount` (and if the upstream API doesn't expose a stable per-index correlation id, request one), and/or consume matched entries so the same record cannot be attributed to two different indices in the same batch.

### Proof of Concept
1. Submit a batched withdrawal intent with two `withdrawalParams` entries both using `assetId: "nep141:btc.omft.near"` but different `destinationAddress` values (e.g., `addrA`, `addrB`).
2. Call `bridge.describeWithdrawal({ index: 0, withdrawalParams: { assetId, destinationAddress: addrA, ... }, tx })` and `bridge.describeWithdrawal({ index: 1, withdrawalParams: { assetId, destinationAddress: addrB, ... }, tx })`.
3. If the POA API's `withdrawals` response contains one `COMPLETED` record for `addrA` and one still-`PENDING` for `addrB`, observe whether `findMatchingWithdrawal` (matching by `assetId` only) returns the `COMPLETED` record for both index 0 and index 1 calls, causing the caller to conclude `addrB`'s withdrawal is also `completed` with `addrA`'s `transfer_tx_hash`.

Note: I was unable to inspect the full implementation of `findMatchingWithdrawal` (only its call site and doc comment were retrievable in this session), so step 3's exact outcome should be confirmed by reading `findMatchingWithdrawal`'s source directly in a follow-up session.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.test.ts (L62-74)
```typescript
	it("retries on pending status and succeeds when completed", async () => {
		const bridge = createMockBridge();
		vi.spyOn(bridge, "describeWithdrawal")
			.mockResolvedValueOnce({ status: "pending" })
			.mockResolvedValueOnce({ status: "pending" })
			.mockResolvedValueOnce({ status: "completed", txHash: "0xfinal" });

		const wid = createWithdrawalIdentifier();
		const result = await watchWithdrawal({ bridge, wid });

		expect(result).toEqual({ hash: "0xfinal" });
		expect(bridge.describeWithdrawal).toHaveBeenCalledTimes(3);
	});
```
