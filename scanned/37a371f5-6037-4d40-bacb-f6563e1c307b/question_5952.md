# Q5952: Amount edge nep245:v2_1.omni.hot.tg:137_ feeInclusive: true `amount` = 1n with a large fee (signAndSendWithdrawalIntent)

## Question
Take `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` on HotBridge, `feeInclusive: true`, and `amount` = 1n with a large fee. HotBridge `feeAmount` in the chain's native fee asset; added to `amount` only when the asset is native, else swapped via `token_diff`. Through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `actualAmount = amount - feeEstimation.amount` (rounding in `verifyTransferAmount` / minimums) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: rounding in `verifyTransferAmount` / minimums. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `feeAmount` in the chain's native fee asset; added to `amount` only when the asset is native, else swapped via `token_diff`.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with a mocked `FeeEstimation` for HotBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
