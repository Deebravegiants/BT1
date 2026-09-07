# Q1766: Amount edge nep141:tron-d28a265909efecdc feeInclusive: false `amount` < `feeEstimation.amou (createWithdrawalIntents)

## Question
Take `nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near` on PoaBridge, `feeInclusive: false`, and `amount` < `feeEstimation.amount`. PoaBridge adds `relayerFee` back onto `amount` in `createWithdrawalIntents`; fee is paid in the withdrawn token. Through `IntentsSDK.createWithdrawalIntents`, does `actualAmount = amount - feeEstimation.amount` (actualAmount becomes negative and is serialised as a '-N' string) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes negative and is serialised as a '-N' string. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. adds `relayerFee` back onto `amount` in `createWithdrawalIntents`; fee is paid in the withdrawn token.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.createWithdrawalIntents` with a mocked `FeeEstimation` for PoaBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
