### Title
Whitespace `destinationMemo` bypasses XRPL destination-tag validation, producing a malformed on-chain tag - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.validateWithdrawal` guards against a missing XRPL destination tag using the JS-falsy check `!args.destinationMemo`, while `createWithdrawMemo` in `poa-bridge-utils.ts` only excludes `undefined`/`""` via `xrpMemo != null && xrpMemo !== ''`. A `destinationMemo` value like a single space `" "` is truthy (passes validation) but is not a valid numeric XRP destination tag, and it will be encoded verbatim into the on-chain memo.

### Finding Description
The claimed broken equality: `destinationMemo passed validation` should imply `destinationMemo is a valid numeric XRP destination tag accepted by the account`. These are not equal.

- `PoaBridge.validateWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:242-245`) checks only `requireDestinationTag && !args.destinationMemo`. For `destinationMemo = " "` (a non-empty string), `!args.destinationMemo` is `false`, so no `XrplDestinationTagRequiredError` is thrown.
- `createWithdrawMemo` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts:44-46`) checks `xrpMemo != null && xrpMemo !== ''`. `" "` passes this check too, so it is appended: `memo.join(":")` produces `"WITHDRAW_TO:<addr>: "` (with a literal space as the tag component), as seen in `createWithdrawIntentPrimitive` (`poa-bridge-utils.ts:20-23`).
- Nowhere in the reachable path (`validateWithdrawal`, `createWithdrawMemo`, `createWithdrawIntentPrimitive`) is `destinationMemo` validated to be a numeric string representing a valid uint32 XRP destination tag. No such check exists in `errors.ts`, `poa-bridge-utils.ts`, or `poa-bridge.ts`.
- Both checks agree only on the `undefined`/`""` case; they diverge on any other falsy-looking-but-truthy string (whitespace, non-numeric text, etc.), so the "both agree" claim in the question does not hold for all inputs — it fails specifically for values like `" "`.

### Impact Explanation
The intent is signed and submitted to `intents.near` with a malformed memo, then the relayer/bridge attempts an XRPL payment with a non-numeric destination tag. Since the destination account has `requireDestinationTag` set and the tag format is invalid, the XRPL payment/relayer flow will reject or fail to complete the transfer, leaving the withdrawal in a stuck/pending state requiring manual intervention (matches the "High" impact category: withdrawal stuck until manual intervention). This is repeatable for any caller (end user or an integrator forwarding a counterparty-controlled memo string) who supplies a non-numeric, non-empty `destinationMemo` against an XRPL account with `requireDestinationTag` enabled.

### Likelihood Explanation
Preconditions: withdrawal targets an XRPL asset, destination account has `requireDestinationTag` enabled, and caller supplies `destinationMemo` as a non-empty, non-numeric string (e.g. `" "`, `"abc"`). This requires no special privilege — any SDK caller or an integrator passing through a counterparty-supplied memo can trigger it with zero cost, and it is trivially repeatable per call.

### Recommendation
Validate `destinationMemo` for XRPL withdrawals as a well-formed destination tag (e.g., a string matching `/^\d+$/` within uint32 range) in `validateWithdrawal`, and make `createWithdrawMemo`'s inclusion condition consistent with that validation (trim and reject whitespace-only/non-numeric memos) rather than only excluding `null`/`""`.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (illustrative)
it("accepts whitespace destinationMemo for XRPL account requiring destination tag", async () => {
  // mock xrpl.httpClient.getAccountInfo to return account_flags.requireDestinationTag = true
  // call bridge.validateWithdrawal({ assetId: xrpAssetId, amount, destinationAddress, destinationMemo: " " })
  await expect(bridge.validateWithdrawal({
    assetId: XRP_ASSET_ID,
    amount: 100n,
    destinationAddress: FRESH_XRPL_ACCOUNT,
    destinationMemo: " ",
  })).resolves.toBeUndefined(); // does NOT throw XrplDestinationTagRequiredError

  const intent = createWithdrawIntentPrimitive({
    assetId: XRP_ASSET_ID,
    destinationAddress: FRESH_XRPL_ACCOUNT,
    destinationMemo: " ",
    amount: 100n,
  });
  expect(intent.memo).toBe(`WITHDRAW_TO:${FRESH_XRPL_ACCOUNT}: `); // literal space encoded as tag
});
```
This demonstrates both sides of the equality: `validateWithdrawal` resolves without throwing (treats `" "` as a present tag) while the encoded memo contains a non-numeric tag value, confirming no numeric-tag format validation exists in the reachable path.