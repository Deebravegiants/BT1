Confirmed. This is the code's own documented limitation and constitutes a real bug.

### Title
`describeWithdrawal` matches withdrawals by `assetId` only, misreporting `txHash` across same-asset withdrawals with different amounts/destinations - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` calls `findMatchingWithdrawal`, which selects a record from the PoA indexer's unordered `withdrawals` list purely by `nep141:${w.data.near_token_id} === assetId`, ignoring `amount`, `destinationAddress`, and the requested `index`. When two withdrawals in the same intent share an `assetId` but differ in `amount` (or `destinationAddress`), `describeWithdrawal({index:0})` and `describeWithdrawal({index:1})` can both resolve to the same first-found record, causing the wrong `txHash`/status to be reported for a given index.

### Finding Description
The broken equality is: the withdrawal record returned for `WithdrawalIdentifier{index: i}` should correspond to the record whose settled `amount` (and `destinationAddress`) equals the `amount`/`destinationAddress` signed for at index `i`. Instead, `findMatchingWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts, lines 418-427) does: [1](#0-0) 
which returns `withdrawals.find(w => nep141:${w.data.near_token_id} === assetId)` — the first array element matching only `assetId`, with no comparison of `amount` or `destinationAddress`, and `index` from `WithdrawalIdentifier` is never consulted in matching at all (`args.withdrawalParams.assetId` is the only field used, per line 321).

The code's own comment acknowledges this: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" (lines 409-416). Given an intent with two POA withdrawals of the same `assetId` (e.g., 100000n to index 0, 50000n to index 1) to the same or even different `destinationAddress`, if the indexer returns the array with the 50000-amount record first, `describeWithdrawal({index:0, withdrawalParams:{amount:100000n,...}})` will match and report that record's `transfer_tx_hash`/status as if it were the 100000n withdrawal, and the subsequent call for index 1 will resolve to the same or wrong record. `validateAddress`, `compareAddresses`, `validateWithdrawal`, and `supports()` operate only at withdrawal-creation time on assetId/destination validity and do not participate in the post-hoc status-matching path, so none of them prevent this divergence. `watchWithdrawal` (packages/intents-sdk/src/core/withdrawal-watcher.ts, lines 20-78) directly forwards whatever `txHash`/status `describeWithdrawal` returns to the caller with no independent verification against the amount/index that was actually signed.

### Impact Explanation
An integrator (or the SDK's own `waitForWithdrawalCompletion`/`processWithdrawal` orchestration) receives a `txHash` for withdrawal index 0 that actually corresponds to a different withdrawal (index 1) with a different amount and/or destination. This is a status/hash misreport that can cause an integrator to credit the wrong amount against the wrong withdrawal id — matching the High/Critical category of "a status or hash misreport making an integrator credit or refund twice" (here, crediting the wrong amount to the wrong id). It is repeatable on every batch withdrawal call that includes ≥2 same-asset legs, whenever the indexer response ordering does not match request ordering (which the code explicitly says is not guaranteed).

### Likelihood Explanation
Preconditions: a caller must submit a batch/multi-withdrawal intent containing two or more POA-bridge withdrawals of the same `assetId` with differing `amount` (a legitimate, unprivileged use case explicitly named in this question and acknowledged as unsupported in the code comment). No special privileges are needed — an ordinary user or an integrator forwarding user-supplied `withdrawalParams` can trigger this by design of the batch API surface, and the indexer's return ordering is out of the caller's control, making mis-matching a function of ordinary indexer behavior, not an attack requiring bridge-API compromise. Given the code explicitly states this scenario is unsupported today, occurrence is plausible under normal operation whenever same-asset multi-leg withdrawals are used.

### Recommendation
Extend `findMatchingWithdrawal` (and its caller `describeWithdrawal`) to disambiguate among same-`assetId` candidates using additional fields available in both the request and indexer response — e.g., match on `amount` and `destinationAddress` in addition to `assetId`, or, if the API doesn't expose enough fields to uniquely identify a leg pre-completion, track already-consumed records so each is matched at most once (e.g., sort both the indexer results and the local per-asset withdrawal params by amount, consistent with the fee-ordering note already in the comment) and assert a match is unique before returning it. Until then, `describeWithdrawal`/`supports` should either reject (throw) multi-leg batches sharing the same POA `assetId`, or clearly document/guard against this at the batch-construction layer (e.g., `createWithdrawalIdentifiers` in `withdrawal-watcher.ts`) rather than silently reporting an unverified match.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (new test)
import { describe, it, expect, vi } from "vitest";
// mock poaBridge.httpClient.getWithdrawalStatus to return, in this order:
// [{ status: "COMPLETED", data: { near_token_id: "token.omft.near", amount: "50000", transfer_tx_hash: "tx_for_50000" } },
//  { status: "COMPLETED", data: { near_token_id: "token.omft.near", amount: "100000", transfer_tx_hash: "tx_for_100000" } }]

it("must not report the 50000-amount record for the withdrawal that requested 100000", async () => {
  const bridge = new PoaBridge({ envConfig, xrplRpcUrls: [] });
  const wid0 = { landingChain: ..., index: 0, withdrawalParams: { assetId: "nep141:token.omft.near", amount: 100000n, destinationAddress: "...", feeInclusive: true }, tx: { hash: "h", accountId: "a" } };
  const wid1 = { ...wid0, index: 1, withdrawalParams: { ...wid0.withdrawalParams, amount: 50000n } };

  const status0 = await bridge.describeWithdrawal(wid0);
  const status1 = await bridge.describeWithdrawal(wid1);

  // Equality that must hold: the txHash returned for index 0 must correspond to the
  // record whose settled amount (100000) equals wid0's requested amount, not wid1's (50000).
  expect(status0).toEqual({ status: "completed", txHash: "tx_for_100000" });
  expect(status1).toEqual({ status: "completed", txHash: "tx_for_50000" });
  // Current implementation returns status0.txHash === "tx_for_50000" (first array match),
  // which fails this assertion, proving the mismatch.
});
```

### Citations

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
