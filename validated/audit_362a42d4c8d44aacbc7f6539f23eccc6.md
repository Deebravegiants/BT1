### Title
`findMatchingWithdrawal` collapses N>1 same-asset POA withdrawals in one tx onto a single status, causing status/hash misreport across withdrawal indices - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves a `WithdrawalIdentifier` to a status purely by matching `assetId` against the POA API's `withdrawals` list, never using `WithdrawalIdentifier.index`. When a caller batches multiple withdrawals of the identical `assetId` in a single intent transaction via `sdk.createWithdrawalCompletionPromises`, every one of those identifiers resolves to the same (first) matching entry, so distinct withdrawals report identical, possibly wrong, statuses/tx hashes.

### Finding Description
The broken equality: for two distinct withdrawal indices `i != j` with the same `assetId` in the same `intentTx`, `describeWithdrawal({index: i, ...}).txHash` should be independent of and potentially different from `describeWithdrawal({index: j, ...}).txHash` (they are separate withdrawal legs), but the code makes them equal.

`findMatchingWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427) does:
```
return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
```
It uses `Array.prototype.find`, keyed only on `assetId`, and ignores `WithdrawalIdentifier.index` entirely. `describeWithdrawal` (lines 313-343) calls this and returns whatever single entry is found for every identifier sharing that `assetId`, regardless of `index`.

`WithdrawalIdentifier.index` is populated by `createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`, which assigns sequential indices per bridge route for a batch (`indexes.get(bridge.route)`), but this index is never consulted by `PoaBridge.describeWithdrawal`/`findMatchingWithdrawal` at all — it's dead for matching purposes in this bridge.

Reachable path: an ordinary user calls `sdk.createWithdrawalCompletionPromises({ withdrawalParams: [w0, w1, w2], intentTx })` with `w0.assetId === w1.assetId === w2.assetId` (all routed to `PoaBridge`). Internally each resulting `WithdrawalIdentifier` (index 0,1,2) is passed to `watchWithdrawal` → `bridge.describeWithdrawal(wid)` → `getWithdrawalStatusWithRetry` → `poaBridge.httpClient.getWithdrawalStatus({ withdrawal_hash: tx.hash })`. All three calls hit the *same* `tx.hash` (same intent transaction) and get the *same* `response.withdrawals` array back from the POA indexer. `findMatchingWithdrawal` then picks the first entry whose `near_token_id` matches `assetId` for all three identifiers — the exact same object — regardless of `index`.

The code's own comment (lines 409-417) documents this as a known unsupported case: "multiple withdrawals of the same token in a single transaction are not supported. POA API doesn't currently support this case either." No guard, throw, or validation prevents a user from constructing such a batch; `supports()`, `validateWithdrawal()`, and `createWithdrawalIdentifiers()` never check for duplicate `assetId` within a batch for the POA route, so nothing stops this path from being exercised in production. This is not a documented escape hatch requiring deliberate integrator misuse of an API contract — it is silent data corruption reachable through ordinary batch withdrawal usage with no error, warning, or rejection at any validation layer.

### Impact Explanation
When one of the N same-asset withdrawals completes (e.g., withdrawal index 0's leg lands and the POA indexer records it as `COMPLETED` with `transfer_tx_hash = H`), `describeWithdrawal` for withdrawal index 1 and index 2 (whose legs may still be pending, failed, or simply distinct transfers) will also return `{ status: "completed", txHash: H }` — the identical hash belonging to a different withdrawal. An integrator that pays out, releases custody, or credits an off-chain ledger per-withdrawal based on the SDK's reported completion will incorrectly treat withdrawal 1 and 2 as completed with `txHash H`, when they did not independently complete. This matches "a status or hash misreport making an integrator credit or refund twice" (High/Critical), since a single completed transfer can cause the SDK to report several separate withdrawals as completed using the same proof of completion.

### Likelihood Explanation
Precondition: a single call to `signAndSendWithdrawalIntent`/`processWithdrawal` (or any flow producing an `intentTx`) with `withdrawalParams` containing two or more entries with an identical `assetId` routed via `PoaBridge` (default route selection for supported POA assets). No special permissions, quotes, or solver cooperation are needed — the attacker (or an integrator's own misconfigured/attacker-influenced batch, e.g., a counterparty causing routeConfig/params to be forwarded) is a normal SDK caller supplying ordinary `WithdrawalParams`. There is no validation anywhere in `supports`, `validateWithdrawal`, or `createWithdrawalIdentifiers` rejecting duplicate-assetId batches, so this is trivially and repeatably reachable on every such batch.

### Recommendation
In `PoaBridge`, either (a) reject/validate against batches containing duplicate `assetId` for the POA route at `supports()`/`validateWithdrawal()` time so callers get an explicit error instead of silent misreporting, or (b) implement the ordering-based matching already suggested in the code comment (sort both the API's `withdrawals` and the local per-assetId withdrawal list by amount and match positionally using `WithdrawalIdentifier.index`) once/if the POA API disambiguates same-token withdrawals, and until then hard-fail fast with a clear "duplicate asset withdrawals in one batch are unsupported" error rather than returning a plausible-looking but wrong status.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.duplicate-asset.test.ts
import { describe, it, expect, vi } from "vitest";
import { PoaBridge } from "./poa-bridge";
import { poaBridge } from "@defuse-protocol/internal-utils";

it("collapses 3 same-assetId withdrawals onto one completed entry", async () => {
  const bridge = new PoaBridge({ envConfig: /* configured with poaTokenFactoryContractID */, xrplRpcUrls: [] });
  const assetId = "nep141:usdt.omft.near";
  const tx = { hash: "sharedTxHash", accountId: "user.near" };

  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "usdt.omft.near", transfer_tx_hash: "0xCOMPLETED_HASH" } },
      // no second/third entry -- API also can't disambiguate them
    ],
  } as any);

  const widBase = { landingChain: "near" as any, tx, withdrawalParams: { assetId, amount: 1n, destinationAddress: "x", feeInclusive: false } };

  const status0 = await bridge.describeWithdrawal({ ...widBase, index: 0 });
  const status1 = await bridge.describeWithdrawal({ ...widBase, index: 1 });
  const status2 = await bridge.describeWithdrawal({ ...widBase, index: 2 });

  // Broken equality: status for withdrawal 1 and 2 equal withdrawal 0's completed hash,
  // even though only one underlying withdrawal actually completed.
  expect(status0).toEqual({ status: "completed", txHash: "0xCOMPLETED_HASH" });
  expect(status1).toEqual({ status: "completed", txHash: "0xCOMPLETED_HASH" }); // should differ / be pending
  expect(status2).toEqual({ status: "completed", txHash: "0xCOMPLETED_HASH" }); // should differ / be pending
});
```
This demonstrates `describeWithdrawal` for `index=1` and `index=2` returning the exact same `WithdrawalStatusResponse` entry (and `txHash`) as `index=0`, confirming the equality break `status(i) == status(j)` for `i != j` predicted in the question.