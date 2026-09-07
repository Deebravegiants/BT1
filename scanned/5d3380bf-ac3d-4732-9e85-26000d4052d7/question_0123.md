# Q0123: Amount edge nep141:wrap.near feeInclusive: false `amount` < `feeEstimation.amou (processWithdrawal)

## Question
For `nep141:wrap.near` via DirectBridge with `feeInclusive: false` and `amount` < `feeEstimation.amount` (actualAmount becomes negative and is serialised as a '-N' string), can an unprivileged caller of `IntentsSDK.processWithdrawal` produce intents whose total debit (withdraw amount + `token_diff` amount_in + storage deposit) differs from `withdrawalParams.amount` plus the displayed `feeEstimation.amount`, given that DirectBridge `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near, so the user is overcharged or the bridge receives an amount it refunds to intents.near instead of the user?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes negative and is serialised as a '-N' string. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.processWithdrawal` with a mocked `FeeEstimation` for DirectBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
