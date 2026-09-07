# Q1501: Missing invariant [validated amount == signed amount] OmniBridge a single wit (estimateWithdrawalFee)

## Question
Because `validateWithdrawal` runs on `actualAmount` before the bridge adds fees back (PoA relayerFee, UTXO fees), so minimums and address checks see a different number than what is signed, can an unprivileged caller of `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on OmniBridge submitting a single withdrawal craft inputs (asset, address, routeConfig, fee object, batch order) so that the equality `validated amount == signed amount` silently fails at exactly one step, and no later step of `processWithdrawal` detects or reverses it, resulting in funds moved to an unintended destination or amount, or an integrator paying twice?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `processWithdrawal`, `createWithdrawalIntents`, `_estimateWithdrawalFee`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts; packages/intents-sdk/src/core/withdrawal-watcher.ts
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: all public parameters of the entrypoint
- Exploit idea: `validateWithdrawal` runs on `actualAmount` before the bridge adds fees back (PoA relayerFee, UTXO fees), so minimums and address checks see a different number than what is signed. Bridge specifics: `getTransfer({transactionHash})[args.index]`; unknown chain kinds -> `completed, txHash: null`.
- Invariant to test: `validated amount == signed amount` must hold at estimate, sign and watch time for the same withdrawal.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: end-to-end with mocked HTTP; assert the equality at each step and inject a divergence to confirm detection is absent.
