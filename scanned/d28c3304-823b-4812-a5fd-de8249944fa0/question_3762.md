# Q3762: Missing invariant [local hash == relayer hash] IntentsBridge a batch of t (processWithdrawal)

## Question
Because the local `computeIntentHash` is never reconciled with the relayer's returned hash, can an unprivileged caller of `IntentsSDK.processWithdrawal` on IntentsBridge submitting a batch of two withdrawals of the same token to two addresses craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `local hash == relayer hash` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: the local `computeIntentHash` is never reconciled with the relayer's returned hash. Bridge specifics: always `completed` with `args.tx.hash`.
- Invariant to test: `local hash == relayer hash` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
