# Q5755: Missing invariant [route(estimate) == route(sign) == route(watch)] DirectBridge a batch of t (estimateWithdrawalFee)

## Question
Because `supports()` exceptions from one bridge do not stop the loop in `createWithdrawalIdentifiers`/`createWithdrawalIntents` consistently (some throw, some return false), can an unprivileged caller of `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on DirectBridge submitting a batch of two withdrawals of the same token to two addresses craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `route(estimate) == route(sign) == route(watch)` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: `supports()` exceptions from one bridge do not stop the loop in `createWithdrawalIdentifiers`/`createWithdrawalIntents` consistently (some throw, some return false). Bridge specifics: always `completed` with `args.tx.hash`.
- Invariant to test: `route(estimate) == route(sign) == route(watch)` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
