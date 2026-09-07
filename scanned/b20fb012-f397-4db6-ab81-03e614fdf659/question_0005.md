# Q0005: Amount edge nep141:wrap.near feeInclusive: true `amount` == `feeEstimation.amo (signAndSendWithdrawalIntent)

## Question
Take `nep141:wrap.near` on DirectBridge, `feeInclusive: true`, and `amount` == `feeEstimation.amount`. DirectBridge `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near. Through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `actualAmount = amount - feeEstimation.amount` (actualAmount becomes 0n) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes 0n. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with a mocked `FeeEstimation` for DirectBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
