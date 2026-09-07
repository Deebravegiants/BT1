# Q5772: Amount edge nep245:v2_1.omni.hot.tg:56_1 feeInclusive: true `amount` = 0n with `feeInclusi (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` with `nep245:v2_1.omni.hot.tg:56_11111111111111111111` (HotBridge), `feeInclusive: true` and `amount` = 0n with `feeInclusive: false`: because `skipMinAmountValidation` path in `_estimateWithdrawalFee` and HotBridge `feeAmount` in the chain's native fee asset; added to `amount` only when the asset is native, else swapped via `token_diff`, can the withdrawal be signed with an amount that is negative, zero, or below the bridge minimum after fee adjustment, so that intents.near debits the user while the bridge refunds to `intents.near` rather than to the signer?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: `skipMinAmountValidation` path in `_estimateWithdrawalFee`. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. `feeAmount` in the chain's native fee asset; added to `amount` only when the asset is native, else swapped via `token_diff`.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.createWithdrawalIntents` with a mocked `FeeEstimation` for HotBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
