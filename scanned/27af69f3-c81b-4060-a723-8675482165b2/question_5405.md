# Q5405: Amount edge nep141:eth.bridge.near feeInclusive: false `amount` == `feeEstimation.amo (signAndSendWithdrawalIntent)

## Question
Take `nep141:eth.bridge.near` on OmniBridge, `feeInclusive: false`, and `amount` == `feeEstimation.amount`. OmniBridge `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount. Through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `actualAmount = amount - feeEstimation.amount` (actualAmount becomes 0n) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes 0n. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with a mocked `FeeEstimation` for OmniBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
