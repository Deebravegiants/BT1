# Q5978: AuroraEngineBridge status a withdrawal composed with: reports `completed` for a withdraw

## Question
For a withdrawal composed with `signedIntents.before` / `.after` (pre-signed `MultiPayload`s published atomically via `publishIntents`, ticket taken at `tickets[beforeCount]`) tracked through `waitForWithdrawalCompletion` -> `watchWithdrawal` -> `AuroraEngineBridge.describeWithdrawal`, can an unprivileged user shape the batch (order, duplicate tokens, mixed routes) so that the SDK reports `completed` for a withdrawal the bridge refunded or never executed, given that always `completed` with `txHash: null`, causing an integrator that credits or refunds on the returned (status, txHash) to pay out twice?

## Target
- File/function: packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts `describeWithdrawal`, `createWithdrawalIdentifier`; packages/intents-sdk/src/core/withdrawal-watcher.ts `createWithdrawalIdentifiers` (per-route index), `watchWithdrawal`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` / `processWithdrawal`
- Attacker controls: batch composition (`withdrawalParams[]`), which is fully user-controlled at the integrator's API boundary
- Exploit idea: always `completed` with `txHash: null`
- Invariant to test: (status, txHash) returned for index i corresponds to the i-th withdrawal the user signed for that route, and `completed` is returned only after the destination transfer is final.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock the AuroraEngineBridge status API with permuted/duplicated results and assert per-index output.
