# Q0288: Amount edge nep141:usdt.tether-token.nea feeInclusive: true `amount` above the token's `mi (processWithdrawal)

## Question
Take `nep141:usdt.tether-token.near` on DirectBridge, `feeInclusive: true`, and `amount` above the token's `min_withdrawal_amount` but below it after fee subtraction. DirectBridge `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near. Through `IntentsSDK.processWithdrawal`, does `actualAmount = amount - feeEstimation.amount` (min check runs against `actualAmount` in `createWithdrawalIntents` but against the fee-less amount elsewhere) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: min check runs against `actualAmount` in `createWithdrawalIntents` but against the fee-less amount elsewhere. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.processWithdrawal` with a mocked `FeeEstimation` for DirectBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
