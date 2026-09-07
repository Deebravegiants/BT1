# Q4802: Amount edge nep141:aptos.omft.near feeInclusive: false `amount` == `feeEstimation.amo (createWithdrawalIntents)

## Question
For `nep141:aptos.omft.near` via OmniBridge with `feeInclusive: false` and `amount` == `feeEstimation.amount` (actualAmount becomes 0n), can an unprivileged caller of `IntentsSDK.createWithdrawalIntents` produce intents whose total debit (withdraw amount + `token_diff` amount_in + storage deposit) differs from `withdrawalParams.amount` plus the displayed `feeEstimation.amount`, given that OmniBridge `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount, so the user is overcharged or the bridge receives an amount it refunds to intents.near instead of the user?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes 0n. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `nativeFee` (wrap.near) via `token_diff` + `storage_deposit`; UTXO chains add `utxoMaxGasFee + utxoProtocolFee` to the token amount.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.createWithdrawalIntents` with a mocked `FeeEstimation` for OmniBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
