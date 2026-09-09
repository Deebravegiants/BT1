### Title
Positional (index-based) matching of unsorted Omni Bridge transfer list can report a withdrawal as `completed` using another transfer's destination status/tx hash - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal` selects the transfer to report on purely by array position (`args.index`) from `omniBridgeAPI.getTransfer({ transactionHash })`, with no verification that the transfer at that position actually corresponds to the withdrawal being described (asset, recipient, amount). The sibling PoA bridge implementation had exactly this defect and was patched (changelog `8bbd5c6`: "Fix POA bridge withdrawal matching to use assetId instead of index" — because "Response list is unsorted"), but the fix was never applied to `OmniBridge`.

### Finding Description
In `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts` (`describeWithdrawal`, lines 691-731):

```ts
const transfer = (
    await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash })
)[args.index];
```

The result is used directly to decide `status: "completed"` and to pick `txHash` — the value an integrator uses to credit the destination-chain payment as done — with no cross-check against `args.withdrawalParams.assetId`, `destinationAddress`, or `amount`.

Contrast with `PoaBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`), which explicitly does:
```ts
// Response list is unsorted, so we match by assetId instead of index
const withdrawal = findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId);
```
with a helper (`findMatchingWithdrawal`, `poa-bridge.ts:418-427`) whose docstring records that the API returns an unsorted list and multiple withdrawals of the same token cannot be disambiguated — the exact defect class the maintainers had already found and fixed once, in the sibling bridge.

`OmniBridge` never received the analogous fix. For a batch withdrawal (`sdk.processWithdrawal` with an array of `WithdrawalParams`, or any transaction that emits multiple Omni transfers, e.g. multiple `ft_withdraw` intents in one NEAR tx), `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` call `describeWithdrawal` once per withdrawal with the withdrawal's `index` (see `omni-bridge.test.ts:515` "returns correct transfer by index", which encodes the (unverified) assumption that API order equals intent order). If the Omni relayer's `getTransfer` response is not guaranteed ordered identically to the intents submitted in the transaction — which is precisely the assumption that was proven false for the PoA API — `describeWithdrawal(index=i)` can return the `finalised`/`utxo_meta` data of a *different* transfer than the one requested.

This breaks the equality "status/txHash reported for withdrawal N == the on-chain outcome of withdrawal N": the SDK can report withdrawal N as `completed` with a `txHash` that actually belongs to withdrawal M's on-chain settlement.

### Impact Explanation
`processWithdrawal`/`waitForWithdrawalCompletion` results (`status: "completed", txHash`) are exactly the data an integrator uses to mark a withdrawal as settled and release funds/credit accounting on their side. If the wrong transfer's `finalised.transaction_hash` is attributed to the wrong withdrawal in a batch:
- An integrator could mark withdrawal N complete using a `txHash` that pays out withdrawal M's destination address, before N's own transfer is actually settled (or ever settles) — a status misreport that can cause double-crediting/incorrect settlement bookkeeping (mirrors the report's high-severity example: "a status or hash misreport making an integrator credit or refund twice").
- Because HOT/POA/Omni "batch" withdrawal APIs shown in this SDK explicitly support multiple items in one NEAR transaction (`BatchWithdrawalResult`, `withdrawalParamsArray`), this path is reachable in normal SDK usage, not merely theoretical.

This satisfies the required impact bucket: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Likelihood depends on whether the Omni relayer's `getTransfer` endpoint always returns transfers in the exact submission order for a given `transactionHash`. This is unverified in the available code/tests — the only evidence is the analogous, already-fixed bug in `PoaBridge`, and the fact that `OmniBridge`'s test suite (`omni-bridge.test.ts:515`) hard-codes the "index==order" assumption without asserting any ordering guarantee from the underlying relayer API. Given the project's own admission (in the PoA fix) that at least one bridge's underlying list is unsorted, treating Omni's list as reliably ordered without an explicit match key is an unverified equality that is risky specifically for multi-transfer/batch withdrawals in a single transaction.

### Recommendation
- Do not rely on array position from `omniBridgeAPI.getTransfer()` to select the transfer for a given withdrawal.
- Match by a positive identifier available on the transfer record — e.g. `token_id`/`recipient`/`amount` compared against `args.withdrawalParams.assetId`/`destinationAddress`/`amount`, or `destination_nonce`/`transfer_id` if it can be correlated to the intent that was submitted — mirroring `PoaBridge`'s `findMatchingWithdrawal`.
- Add a regression test with multiple transfers in one `getTransfer` response returned in an order that differs from submission order, asserting `describeWithdrawal` still returns the correct transfer's status/txHash for each `index`/withdrawal.

### Proof of Concept
1. Submit a batch withdrawal with two Omni Bridge transfers in a single NEAR transaction: withdrawal A (destination `0xAAA`) at index 0, withdrawal B (destination `0xBBB`) at index 1.
2. Suppose the relayer's `getTransfer({ transactionHash })` returns the two transfer records in an order that does not match submission order (analogous to the documented "unsorted" behavior fixed for PoA) — e.g. B's record first, A's second.
3. `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` calls `describeWithdrawal({ index: 0, withdrawalParams: A, tx })`, which does `getTransfer(...)[0]`, returning B's `finalised.transaction_hash`.
4. The SDK/integrator now reports withdrawal A as `completed` with a `txHash` that is actually B's destination-chain transaction — a status/hash misattribution that can be leveraged to make an integrator credit/settle the wrong withdrawal as done.

(Note: exploitability strictly depends on the omni relayer's ordering guarantee for `getTransfer`, which could not be confirmed from in-scope code; this is flagged as the key uncertainty.)