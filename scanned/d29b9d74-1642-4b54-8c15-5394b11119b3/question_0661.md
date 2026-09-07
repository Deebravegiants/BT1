# Q0661: Amount edge nep141:eth.omft.near feeInclusive: true `amount` = 1n with a large fee (processWithdrawal)

## Question
Take `nep141:eth.omft.near` on PoaBridge, `feeInclusive: true`, and `amount` = 1n with a large fee. PoaBridge adds `relayerFee` back onto `amount` in `createWithdrawalIntents`; fee is paid in the withdrawn token. Through `IntentsSDK.processWithdrawal`, does `actualAmount = amount - feeEstimation.amount` (rounding in `verifyTransferAmount` / minimums) reach `createWithdrawalIntents` unchecked, and what exact string lands in the `amount` field of the signed intent versus what the destination receives?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: rounding in `verifyTransferAmount` / minimums. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. adds `relayerFee` back onto `amount` in `createWithdrawalIntents`; fee is paid in the withdrawn token.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: call `IntentsSDK.processWithdrawal` with a mocked `FeeEstimation` for PoaBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
