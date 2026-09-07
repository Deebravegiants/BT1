# Q3165: Amount edge nep141:gnosis-0xe91d153e0b41 feeInclusive: false `amount` == `feeEstimation.amo (signAndSendWithdrawalIntent)

## Question
For `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` via PoaBridge with `feeInclusive: false` and `amount` == `feeEstimation.amount` (actualAmount becomes 0n), can an unprivileged caller of `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` produce intents whose total debit (withdraw amount + `token_diff` amount_in + storage deposit) differs from `withdrawalParams.amount` plus the displayed `feeEstimation.amount`, given that PoaBridge adds `relayerFee` back onto `amount` in `createWithdrawalIntents`; fee is paid in the withdrawn token, so the user is overcharged or the bridge receives an amount it refunds to intents.near instead of the user?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `createWithdrawalIntents` (actualAmount), `_estimateWithdrawalFee` (FeeExceedsAmountError); packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `amount`, `feeInclusive`, and (for signAndSendWithdrawalIntent) the `feeEstimation` object itself
- Exploit idea: actualAmount becomes 0n. `createWithdrawalIntents` subtracts the fee without the `FeeExceedsAmountError` guard that only `_estimateWithdrawalFee` applies. adds `relayerFee` back onto `amount` in `createWithdrawalIntents`; fee is paid in the withdrawn token.
- Invariant to test: sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee) and destination receives amount - (feeInclusive ? fee : 0), both non-negative; else throw before signing.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with a mocked `FeeEstimation` for PoaBridge, parse the returned intents and sum amounts as BigInt; assert against the formula.
