# Q2912: Missing invariant [reported == signed] AuroraEngineBridge a batch of t (processWithdrawal)

## Question
Because `describeWithdrawal` never compares the reported transfer's recipient/amount with the signed intent, can an unprivileged caller of `IntentsSDK.processWithdrawal` on AuroraEngineBridge submitting a batch of two withdrawals of the same token to two addresses craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `reported == signed` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: `describeWithdrawal` never compares the reported transfer's recipient/amount with the signed intent. Bridge specifics: always `completed` with `txHash: null`.
- Invariant to test: `reported == signed` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
