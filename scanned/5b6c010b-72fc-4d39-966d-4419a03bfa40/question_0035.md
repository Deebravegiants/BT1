# Q0035: Amount edge nep141:wrap.near feeInclusive: true `amount` < `feeEstimation.amou (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` with `nep141:wrap.near` (DirectBridge), `feeInclusive: true` and `amount` < `feeEstimation.amount`: because actualAmount becomes negative and is serialised as a '-N' string and DirectBridge `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near, can the withdrawal be signed with an amount that is negative, zero, or below the bridge minimum after fee adjustment, so that intents.near debits the user while the bridge refunds to `intents.near` rather than to the signer?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes negative and is serialised as a '-N' string. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `storageDepositFee` = `minStorageBalance - userStorageBalance` in wrap.near, quoted via `token_diff` when the asset is not wrap.near.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.createWithdrawalIntents` with a mocked `FeeEstimation` for DirectBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
