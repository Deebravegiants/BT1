# Q5988: Missing invariant [route(estimate) == route(sign) == route(watch)] AuroraEngineBridge a single wit (signAndSendWithdrawalIntent)

## Question
Because `supports()` exceptions from one bridge do not stop the loop in `createWithdrawalIdentifiers`/`createWithdrawalIntents` consistently (some throw, some return false), can an unprivileged caller of `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` on AuroraEngineBridge submitting a single withdrawal craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `route(estimate) == route(sign) == route(watch)` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: `supports()` exceptions from one bridge do not stop the loop in `createWithdrawalIdentifiers`/`createWithdrawalIntents` consistently (some throw, some return false). Bridge specifics: always `completed` with `txHash: null`.
- Invariant to test: `route(estimate) == route(sign) == route(watch)` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
