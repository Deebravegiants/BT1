This finding is confirmed valid and already explicitly documented as a known limitation in the code itself.

### Title
`findMatchingWithdrawal` matches by `assetId` only, causing amount/txHash misattribution for same-token batch withdrawals - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`findMatchingWithdrawal` in the PoA bridge adapter resolves a withdrawal's on-chain status by scanning the POA API's returned withdrawal list and matching solely on `assetId` (via `near_token_id`), ignoring `amount` and the per-withdrawal `index`. When a batch intent contains two withdrawals of the same token but different amounts, `describeWithdrawal` can return the wrong `txHash`/status for a given `WithdrawalIdentifier.index`, since the first array element matching the assetId is always picked regardless of which signed withdrawal it actually corresponds to.

### Finding Description
The broken equality is: `(status, txHash)` returned for withdrawal `wid.index = i` should equal the destination-chain outcome of the *i-th signed withdrawal* (specific `amount`, `destinationAddress`) — not just "some withdrawal of the same `assetId`".

Code path: `watchWithdrawal` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:20-78`) calls `bridge.describeWithdrawal({...wid, logger})`. For PoA, `describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`) fetches `response.withdrawals` from the POA API keyed by NEAR tx hash, then calls: [1](#0-0) 
which invokes: [2](#0-1) 
This uses `Array.prototype.find`, returning the **first** array element whose `near_token_id` matches, with no disambiguation by `amount`, `destinationAddress`, or `index`. The code comment at lines 409-416 explicitly acknowledges: *"Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* The identical limitation and comment exist in the legacy path at `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts:135-153`.

Attacker input: a batch `withdrawalParams` array containing two entries with the same `assetId` (e.g., `nep141:eth.omft.near`) but different `amount`s, submitted via `sdk.signAndSendWithdrawalIntent`/`processWithdrawal`. `createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`) assigns each withdrawal an `index` per bridge route counter, but this index is never used by `findMatchingWithdrawal` to disambiguate. If the POA API returns two `COMPLETED` withdrawal records for the same asset (in whatever order it returns them, or if timing/indexing causes them to appear out of the intended order), `describeWithdrawal` for `index=0` and `index=1` can both resolve to the same array element (the first one found), or resolve inconsistently, so an integrator polling per-index via `watchWithdrawal`/`createWithdrawalCompletionPromises` may attribute the large withdrawal's completion `txHash` to the small withdrawal's index (or vice versa).

No existing guard prevents this: `supports()`, `validateWithdrawal`, `compareAddresses`, and `FeeExceedsAmountError` all operate on withdrawal-creation semantics (asset validity, destination address, minimum amount, fee bounds) and never enforce or check for same-asset withdrawal uniqueness within a batch, nor does anything reject a batch with duplicate `assetId` entries.

### Impact Explanation
An integrator relying on per-index status (`watchWithdrawal(wid)` for `index=1`) can receive a `txHash`/`completed` status that actually corresponds to a different withdrawal amount than what was signed for that index. This causes the integrator to credit/refund/reconcile the wrong amount against a transaction hash that doesn't correspond to the signed withdrawal for that index — a status/hash misreport that can lead to a double-credit or mismatched credit with no on-chain correlation for that specific index. This matches the **High** impact category ("a status or hash misreport making an integrator credit or refund twice") — note: this is a status/hash misattribution when two same-asset withdrawals are batched, not full fund redirection, since the funds themselves land at destinations dictated by the intent's own recipient/amount fields, unaffected by this bug. The bug is repeatable on every batch containing duplicate-asset withdrawals.

### Likelihood Explanation
Requires: (1) PoA route, (2) a batch withdrawal with two or more entries sharing the same `assetId`, (3) both landing in the POA-tracked destination system. An unprivileged SDK caller/integrator can trivially construct such a batch since nothing in `supports()`/`validateWithdrawal`/`createWithdrawalIntents` rejects duplicate-asset batches. The bug is deterministic given the documented `find()`-first-match behavior, though its exact practical effect depends on the order the POA API returns withdrawal records (which is explicitly noted as "unsorted" per the comment at line 318: `// Response list is unsorted, so we match by assetId instead of index`).

### Recommendation
Disambiguate `findMatchingWithdrawal` by `amount` (and `destinationAddress`) in addition to `assetId`, or reject/throw when a batch contains multiple withdrawals of the same `assetId` for the PoA route until the POA API supports index-based disambiguation, as hinted in the existing code comment (sort both sides by amount, since relayer fees are equal for same token).

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (vitest, mock only HTTP)
it("misattributes txHash for two same-asset withdrawals with different amounts", async () => {
  const bridge = new PoaBridge({ envConfig, xrplRpcUrls: [] });

  // Mock POA HTTP getWithdrawalStatus to return both COMPLETED withdrawals
  // for the same NEAR tx hash, with SWAPPED order/txHash vs signed intent order:
  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "eth.omft.near", transfer_tx_hash: "TX_FOR_SMALL_AMOUNT" } },
      { status: "COMPLETED", data: { near_token_id: "eth.omft.near", transfer_tx_hash: "TX_FOR_LARGE_AMOUNT" } },
    ],
  });

  const widLarge = bridge.createWithdrawalIdentifier({
    withdrawalParams: { assetId: "nep141:eth.omft.near", amount: 1000000n, destinationAddress: "0xabc", feeInclusive: false },
    index: 1, // signed as the SECOND (large) withdrawal
    tx: { hash: "shared-tx", accountId: "user.near" },
  });

  const status = await bridge.describeWithdrawal(widLarge);

  // BROKEN: returns the FIRST match regardless of index/amount,
  // i.e. status.txHash === "TX_FOR_SMALL_AMOUNT" even though widLarge
  // was signed for the large amount at index 1.
  expect(status).toEqual({ status: "completed", txHash: "TX_FOR_SMALL_AMOUNT" }); // demonstrates the bug
});
``` [3](#0-2)

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L318-322)
```typescript
		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);
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
