# Q5863: Amount edge nep245:v2_1.omni.hot.tg:56_1 feeInclusive: false `amount` = 0n with `feeInclusi (processWithdrawal)

## Question
For `nep245:v2_1.omni.hot.tg:56_11111111111111111111` via HotBridge with `feeInclusive: false` and `amount` = 0n with `feeInclusive: false` (`skipMinAmountValidation` path in `_estimateWithdrawalFee`), can an unprivileged caller of `IntentsSDK.processWithdrawal` produce intents whose total debit (withdraw amount + `token_diff` amount_in + storage deposit) differs from `withdrawalParams.amount` plus the displayed `feeEstimation.amount`, given that HotBridge `feeAmount` in the chain's native fee asset; added to `amount` only when the asset is native, else swapped via `token_diff`, so the user is overcharged or the bridge receives an amount it refunds to intents.near instead of the user?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: `skipMinAmountValidation` path in `_estimateWithdrawalFee`. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `feeAmount` in the chain's native fee asset; added to `amount` only when the asset is native, else swapped via `token_diff`.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.processWithdrawal` with a mocked `FeeEstimation` for HotBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
