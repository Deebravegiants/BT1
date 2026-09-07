# Q0051: Missing invariant [amount + fee] PoaBridge a single wit (signAndSendWithdrawalIntent)

## Question
Because no check ties the intents produced by `createWithdrawalIntents` to the `feeEstimation` passed alongside them, can an unprivileged caller of `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` on PoaBridge submitting a single withdrawal craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `amount + fee` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: no check ties the intents produced by `createWithdrawalIntents` to the `feeEstimation` passed alongside them. Bridge specifics: `findMatchingWithdrawal` matches by `nep141:<near_token_id>` only; not-found for 3s returns `[]` -> pending.
- Invariant to test: `amount + fee` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
