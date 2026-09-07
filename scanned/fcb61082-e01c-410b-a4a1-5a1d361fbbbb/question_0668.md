# Q0668: Missing invariant [amount + fee] DirectBridge a batch of t (estimateWithdrawalFee)

## Question
Because no check ties the intents produced by `createWithdrawalIntents` to the `feeEstimation` passed alongside them, can an unprivileged caller of `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on DirectBridge submitting a batch of two withdrawals of the same token to two addresses craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `amount + fee` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: no check ties the intents produced by `createWithdrawalIntents` to the `feeEstimation` passed alongside them. Bridge specifics: always `completed` with `args.tx.hash`.
- Invariant to test: `amount + fee` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
