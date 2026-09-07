# Q5605: Missing invariant [route(estimate) == route(sign) == route(watch)] DirectBridge a single wit (processWithdrawal)

## Question
Because `supports()` exceptions from one bridge do not stop the loop in `createWithdrawalIdentifiers`/`createWithdrawalIntents` consistently (some throw, some return false), can an unprivileged caller of `IntentsSDK.processWithdrawal` on DirectBridge submitting a single withdrawal craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `route(estimate) == route(sign) == route(watch)` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: `supports()` exceptions from one bridge do not stop the loop in `createWithdrawalIdentifiers`/`createWithdrawalIntents` consistently (some throw, some return false). Bridge specifics: always `completed` with `args.tx.hash`.
- Invariant to test: `route(estimate) == route(sign) == route(watch)` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
