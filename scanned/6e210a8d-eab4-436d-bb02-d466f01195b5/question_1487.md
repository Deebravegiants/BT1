# Q1487: HotBridge status a batch of two withdrawals: reports `pending` forever for a co

## Question
For a batch of two withdrawals of the same token to two addresses (`withdrawalParams: [a, b]` both `nep141:<same>`) tracked through `waitForWithdrawalCompletion` -> `watchWithdrawal` -> `HotBridge.describeWithdrawal`, can an unprivileged user shape the batch (order, duplicate tokens, mixed routes) so that the SDK reports `pending` forever for a completed withdrawal so the integrator manually re-sends, given that `nonces[args.index]` from `parseWithdrawalNonces(tx.hash, tx.accountId)`; EVM/Stellar/TON use bridge indexer, others `getGaslessWithdrawStatus`, causing an integrator that credits or refunds on the returned (status, txHash) to pay out twice?

## Target
- File/function: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `describeWithdrawal`, `createWithdrawalIdentifier`; packages/intents-sdk/src/core/withdrawal-watcher.ts `createWithdrawalIdentifiers` (per-route index), `watchWithdrawal`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` / `processWithdrawal`
- Attacker controls: batch composition (`withdrawalParams[]`), which is fully user-controlled at the integrator's API boundary
- Exploit idea: `nonces[args.index]` from `parseWithdrawalNonces(tx.hash, tx.accountId)`; EVM/Stellar/TON use bridge indexer, others `getGaslessWithdrawStatus`
- Invariant to test: (status, txHash) returned for index i corresponds to the i-th withdrawal the user signed for that route, and `completed` is returned only after the destination transfer is final.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock the HotBridge status API with permuted/duplicated results and assert per-index output.
