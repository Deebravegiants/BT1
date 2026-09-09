### Title
`findMatchingWithdrawal` matches solely on `assetId`, misreporting txHash across sibling withdrawals of the same token in a batch - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` identifies the correct API record purely by `assetId`, ignoring `amount`/`destinationAddress`/`index`. When a batch withdrawal contains two or more payouts of the same PoA token (e.g., same USDC to two different destination addresses/amounts), `describeWithdrawal({index: 0, ...})` can return the `transfer_tx_hash` that actually belongs to a different withdrawal in the same batch, since the underlying bridge API's `withdrawals` array is documented as unsorted and the code does not disambiguate by amount or address.

### Finding Description
The equality that must hold is: `describeWithdrawal({index: i, withdrawalParams: paramsᵢ}).txHash == destination-chain tx corresponding to paramsᵢ's amount/destinationAddress`.

In `describeWithdrawal`, the record is selected via: [1](#0-0) 

and `findMatchingWithdrawal` matches only by `assetId`: [2](#0-1) 

The function's own comment explicitly acknowledges the flaw: *"multiple withdrawals of the same token in a single transaction are not supported"* and that a fix would require sorting both API results and withdrawal params by amount, which is not implemented. Since `Array.prototype.find` returns the first matching element in whatever order the (documented-as-unsorted) API response returns them, if two withdrawals in the same NEAR transaction share the same `assetId` (`nep141:<token>.omft.near`) but differ in `amount`/`destinationAddress`, `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` can both resolve to the *same* matched record (the first one found), and depending on API ordering, index 0's call can surface index 1's `transfer_tx_hash`/amount/address instead of its own.

None of the existing guards prevent this: `validateAddress`/`compareAddresses` validate a single address in isolation and do not cross-check against sibling withdrawals in the same batch; `supports()` only checks route/asset compatibility; there is no `matchesRequest`-style check comparing `amount`/`address` from `args.withdrawalParams` against the API record's `data.amount`/`data.address` before accepting it as the match for a given `index`.

### Impact Explanation
An integrator using `createWithdrawalCompletionPromises`/`watchWithdrawal` for a batch that contains two same-token payouts (a legitimate, SDK-supported feature per the batch-withdrawal RFC) can receive `{status:'completed', txHash: X}` for index 0 where `X` is actually the destination-chain transaction paying out index 1's amount to index 1's address. This is a status/txHash misreport that can cause the integrator to credit or refund the wrong recipient/amount, matching the **High/Critical** category "a status or hash misreport making an integrator credit or refund twice" (here, crediting the wrong recipient based on a swapped hash). This is repeatable any time a batch withdrawal contains ≥2 payouts of the same POA `assetId`.

### Likelihood Explanation
Preconditions: a single NEAR intent transaction contains two or more withdrawal legs routed through `PoaBridge` for the *same* `assetId` but different `amount`/`destinationAddress` — this is a normal, documented usage pattern (batch withdrawals, e.g., splitting a payout to two recipients of the same token), not an attack requiring a malicious API or relayer. The POA bridge status API's `withdrawals` array is documented in-code as unsorted, so no adversarial manipulation of the API is needed — ordinary indexing/return order is sufficient to trigger the mismatch. The cost to trigger it is simply constructing such a batch, which any SDK caller/integrator can do legitimately.

### Recommendation
Disambiguate `findMatchingWithdrawal` by more than `assetId`: match against `withdrawal.data.amount` and `withdrawal.data.address` (normalized/compared the same way as `compareAddresses`) in addition to `assetId`, or track already-consumed API records per `describeWithdrawal` call sequence so that a batch of same-asset withdrawals is deterministically paired index-by-index (e.g., sort both the API `withdrawals` list and the batch's same-asset `withdrawalParams` by amount, as the code comment itself suggests, and enforce a strict 1:1 match check with an `assert`/`FeeExceedsAmountError`-style fatal check when no unique corresponding record can be found).

### Proof of Concept
```ts
// vitest, mocking only poaBridge.httpClient.getWithdrawalStatus
vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
  withdrawals: [
    // Note: order returned by real API is documented as unsorted/arbitrary
    {
      status: "COMPLETED",
      data: {
        tx_hash: "near-tx-hash",
        transfer_tx_hash: "dest-tx-hash-for-index-1", // belongs to withdrawal #1
        chain: "eth",
        defuse_asset_identifier: "nep141:usdc.omft.near",
        near_token_id: "usdc.omft.near",
        decimals: 6,
        amount: 500_000, // index 1's amount
        account_id: "test.near",
        address: "0xIndex1Address...", // index 1's destination
        created: "2024-01-01T00:00:00Z",
      },
    },
    {
      status: "COMPLETED",
      data: {
        tx_hash: "near-tx-hash",
        transfer_tx_hash: "dest-tx-hash-for-index-0", // belongs to withdrawal #0
        chain: "eth",
        defuse_asset_identifier: "nep141:usdc.omft.near",
        near_token_id: "usdc.omft.near",
        decimals: 6,
        amount: 100_000, // index 0's amount
        account_id: "test.near",
        address: "0xIndex0Address...", // index 0's destination
        created: "2024-01-01T00:00:00Z",
      },
    },
  ],
});

const bridge = new PoaBridge({ envConfig, xrplRpcUrls });

const result0 = await bridge.describeWithdrawal({
  landingChain: Chains.Ethereum,
  index: 0,
  withdrawalParams: {
    assetId: "nep141:usdc.omft.near",
    amount: 100_000n,
    destinationAddress: "0xIndex0Address...",
    feeInclusive: false,
  },
  tx: { hash: "near-tx-hash", accountId: "test.near" },
});

// EXPECTED: txHash for index 0's own payout ("dest-tx-hash-for-index-0")
// ACTUAL (bug): returns "dest-tx-hash-for-index-1" because `.find()`
// matches the FIRST array element with the same assetId, regardless of
// which amount/address it actually corresponds to.
expect(result0).toEqual({ status: "completed", txHash: "dest-tx-hash-for-index-0" }); // fails today
```

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-337)
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
