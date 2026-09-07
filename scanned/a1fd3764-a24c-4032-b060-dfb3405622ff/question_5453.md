# Q5453: Amount edge nep141:eth.bridge.near feeInclusive: false `amount` = 0n with `feeInclusi (processWithdrawal)

## Question
For `nep141:eth.bridge.near` via OmniBridge with `feeInclusive: false` and `amount` = 0n with `feeInclusive: false` (`skipMinAmountValidation` path in `_estimateWithdrawalFee`), can an unprivileged caller of `IntentsSDK.processWithdrawal` produce intents whose total debit (withdraw amount + `token_diff` amount_in + storage deposit) differs from `withdrawalParams.amount` plus the displayed `feeEstimation.amount`, given that OmniBridge `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount, so the user is overcharged or the bridge receives an amount it refunds to intents.near instead of the user?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: `skipMinAmountValidation` path in `_estimateWithdrawalFee`. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.processWithdrawal` with a mocked `FeeEstimation` for OmniBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
