# Q0603: Missing invariant [amount + fee] DirectBridge a single wit (createWithdrawalIntents)

## Question
Because no check ties the intents produced by `createWithdrawalIntents` to the `feeEstimation` passed alongside them, can an unprivileged caller of `IntentsSDK.createWithdrawalIntents` on DirectBridge submitting a single withdrawal craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `amount + fee` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: no check ties the intents produced by `createWithdrawalIntents` to the `feeEstimation` passed alongside them. Bridge specifics: always `completed` with `args.tx.hash`.
- Invariant to test: `amount + fee` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
