# Q4617: IntentsBridge status a batch mixing HOT, PoA an: reports `completed` with another w

## Question
For a batch mixing HOT, PoA and Omni routes (indexes are per-route in `createWithdrawalIdentifiers` but per-tx in bridge status APIs) tracked through `waitForWithdrawalCompletion` -> `watchWithdrawal` -> `IntentsBridge.describeWithdrawal`, can an unprivileged user shape the batch (order, duplicate tokens, mixed routes) so that the SDK reports `completed` with another withdrawal's `txHash`, given that always `completed` with `args.tx.hash`, causing an integrator that credits or refunds on the returned (status, txHash) to pay out twice?

## Target
- File/function: packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts `describeWithdrawal`, `createWithdrawalIdentifier`; packages/intents-sdk/src/core/withdrawal-watcher.ts `createWithdrawalIdentifiers` (per-route index), `watchWithdrawal`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` / `processWithdrawal`
- Attacker controls: batch composition (`withdrawalParams[]`), which is fully user-controlled at the integrator's API boundary
- Exploit idea: always `completed` with `args.tx.hash`
- Invariant to test: (status, txHash) returned for index i corresponds to the i-th withdrawal the user signed for that route, and `completed` is returned only after the destination transfer is final.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock the IntentsBridge status API with permuted/duplicated results and assert per-index output.
