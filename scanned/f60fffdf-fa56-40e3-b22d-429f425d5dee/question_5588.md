# Q5588: Amount edge nep141:lsd-usdt.rhealab.near feeInclusive: true `amount` above the token's `mi (signAndSendWithdrawalIntent)

## Question
Take `nep141:lsd-usdt.rhealab.near` on OmniBridge, `feeInclusive: true`, and `amount` above the token's `min_withdrawal_amount` but below it after fee subtraction. OmniBridge `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount. Through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `actualAmount = amount - feeEstimation.amount` (min check runs against `actualAmount` in `createWithdrawalIntents` but against the fee-less amount elsewhere) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: min check runs against `actualAmount` in `createWithdrawalIntents` but against the fee-less amount elsewhere. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with a mocked `FeeEstimation` for OmniBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
