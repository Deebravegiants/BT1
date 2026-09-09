### Title
`describeWithdrawal` mismatches same-asset withdrawals in a batch, causing status/txHash cross-attribution - (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`) resolves a `WithdrawalIdentifier` to a relayer-reported outcome using `findMatchingWithdrawal`, which matches purely by `assetId` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427`), ignoring `args.index` and `destinationAddress`. When a batch contains two withdrawals of the same `assetId`, both queries hit the same NEAR tx hash and both resolve to the *same* first-matching entry in `response.withdrawals`, so one withdrawal's real on-chain outcome gets reported for both.

### Finding Description
The broken equality: for `wid0` (index=0, destinationAddress=userA) and `wid1` (index=1, destinationAddress=userB), both created for the same `assetId`, the claimed invariant is `describeWithdrawal(wid0).txHash == on-chain outcome of withdrawal 0` AND `describeWithdrawal(wid1).txHash == on-chain outcome of withdrawal 1`. In the code, both calls use the identical `withdrawal_hash: args.tx.hash` (`poa-bridge.ts:353`), since both withdrawals originate from one NEAR intent tx (`intentTx` is shared across all withdrawals — see `createWithdrawalIdentifiers`, `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`, and `sdk.createWithdrawalCompletionPromises`, `packages/intents-sdk/src/sdk.ts:557-609`, which pass the same `intentTx` for every withdrawal in the batch). This means `getWithdrawalStatus` returns the exact same `response.withdrawals` list for both calls. `findMatchingWithdrawal` (`poa-bridge.ts:418-427`) then does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)`, which returns the *first* entry matching the shared `assetId` for both `wid0` and `wid1` regardless of `index` or destination address. The code comment at `poa-bridge.ts:409-416` explicitly acknowledges this limitation ("multiple withdrawals of the same token in a single transaction are not supported").

Attacker input: a batch of two `WithdrawalParams` with identical `assetId` (e.g. `nep141:btc.omft.near`) but different `destinationAddress` (userA, userB), submitted as one call to `sdk.createWithdrawalCompletionPromises` or `waitForWithdrawalCompletion`. No malicious relayer is required — this is a deterministic consequence of the SDK's own matching logic given a normal, honestly-reporting relayer response list containing two entries for the same asset (order is documented as unsorted, but even sorted order does not fix the ambiguity since both entries have the same `near_token_id`).

Existing guards do not prevent this: `validateWithdrawal`, `compareAddresses`, `supports()`, and `FeeExceedsAmountError` operate on withdrawal creation/fee estimation, not on post-hoc status matching; there is no check anywhere in `describeWithdrawal` correlating `index` or `destinationAddress` to the returned relayer entry.

### Impact Explanation
Because `watchWithdrawal` (`packages/intents-sdk/src/core/withdrawal-watcher.ts`) resolves each promise with the `(status, txHash)` returned by `describeWithdrawal`, an integrator processing `promises[0]` and `promises[1]` from `createWithdrawalCompletionPromises` will get identical `(status, txHash)` for two distinct withdrawals whenever they share `assetId`. This is a status/hash misreport that can cause an integrator to credit or refund twice against a single physical settlement (one destination gets falsely marked completed with someone else's txHash, while the other may be reported as still pending or with a duplicated hash). This matches the **High** impact category ("a status or hash misreport making an integrator credit or refund twice"). It is not a fund-authorization bypass at the intents-contract level (the underlying withdrawal intents/signatures are unaffected), but it directly corrupts the SDK-reported completion state that integrators rely on for crediting funds.

### Likelihood Explanation
Preconditions are trivial and fully attacker/integrator-controlled: any batch with ≥2 withdrawals of the same `assetId` (e.g., two BTC withdrawals to different users, or a common integrator pattern of processing multiple user withdrawals of the same token in one signed intent) triggers this. No special relayer misbehavior is needed — the relayer will legitimately report two separate entries for the same `near_token_id`, and the SDK cannot disambiguate them. This is deterministic and repeatable every time an integrator batches same-asset withdrawals to different destinations, which is a realistic operational pattern (batching for gas/tx efficiency).

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId` alone. Options:
- If the relayer response includes `destination_address`, match on `(assetId, destinationAddress)` (and amount if available) instead of `assetId` alone.
- If no other distinguishing field exists in the relayer response, as the code comment suggests, sort both the relayer's returned withdrawal list and the SDK's list of same-asset `WithdrawalIdentifier`s by amount (since relayer fees are equal for the same token, relative amount ordering is preserved), and match by ordinal position within that sorted subset rather than picking the first match unconditionally.
- At minimum, until a correlating field is available from the relayer API, `createWithdrawalIdentifier`/`describeWithdrawal` should detect and reject (throw) when multiple same-`assetId` withdrawals exist in one batch, rather than silently returning an unverified status/txHash pairing.

### Proof of Concept
```typescript
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (illustrative, HTTP-only mock)
import { poaBridge } from "@defuse-protocol/internal-utils";

it("BUG: describeWithdrawal returns identical (status,txHash) for two same-asset withdrawals with different destinations", async () => {
  const bridge = new PoaBridge({ envConfig, xrplRpcUrls: [] });

  // Mock relayer: only withdrawal index=0 (userA) actually completed on-chain.
  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: { near_token_id: "btc.omft.near", transfer_tx_hash: "0xUSERA_TX" },
      },
      // withdrawal index=1 (userB) is still pending on-chain / not in list, or
      // has a different actual outcome — but findMatchingWithdrawal never sees it
      // because .find() stops at the first assetId match.
    ],
  });

  const widA = bridge.createWithdrawalIdentifier({
    withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: "userA-addr", ... },
    index: 0,
    tx: { hash: "shared-tx-hash", accountId: "acct.near" },
  });
  const widB = bridge.createWithdrawalIdentifier({
    withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: "userB-addr", ... },
    index: 1,
    tx: { hash: "shared-tx-hash", accountId: "acct.near" },
  });

  const resultA = await bridge.describeWithdrawal(widA);
  const resultB = await bridge.describeWithdrawal(widB);

  // BROKEN EQUALITY: resultB should reflect userB's own on-chain outcome,
  // but instead equals userA's:
  expect(resultA).toEqual({ status: "completed", txHash: "0xUSERA_TX" });
  expect(resultB).toEqual({ status: "completed", txHash: "0xUSERA_TX" }); // STATUS_TRUTH violated:
  // resultB.txHash ("0xUSERA_TX") !== actual on-chain tx for withdrawal index=1 (userB),
  // yet the SDK reports them as equal.
});
```
This demonstrates that `describeWithdrawal` cannot distinguish `wid0` from `wid1` when `assetId` is shared, directly violating STATUS_TRUTH and enabling an integrator to mistakenly credit userB using userA's completed transfer.