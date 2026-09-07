# Q4945: Amount edge nep141:starknet.omft.near feeInclusive: true `amount` = 0n with `feeInclusi (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` with `nep141:starknet.omft.near` (OmniBridge), `feeInclusive: true` and `amount` = 0n with `feeInclusive: false`: because `skipMinAmountValidation` path in `_estimateWithdrawalFee` and OmniBridge `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount, can the withdrawal be signed with an amount that is negative, zero, or below the bridge minimum after fee adjustment, so that intents.near debits the user while the bridge refunds to `intents.near` rather than to the signer?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: `skipMinAmountValidation` path in `_estimateWithdrawalFee`. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.processWithdrawal` with a mocked `FeeEstimation` for OmniBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
