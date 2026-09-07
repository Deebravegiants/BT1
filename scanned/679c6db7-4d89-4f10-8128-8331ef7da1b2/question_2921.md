# Q2921: Omni hidden fee nep141:aptos.omft.near: `fee.native_token_fee` returne

## Question
For `nep141:aptos.omft.near` through OmniBridge, when `fee.native_token_fee` returned as 0n for a non-UTXO chain, is the amount displayed by `estimateWithdrawalFee` (`feeEstimation.amount`) smaller than what the produced intents actually move (`storage_deposit.amount` = nativeFee in wrap.near plus `ft_withdraw.storage_deposit`), because `validateWithdrawal` asserts relayerFee > 0 for non-UTXO unless subsidised; check `estimateWithdrawalFee` path returns amount 0 with quote null, so a user with `feeInclusive: true` is charged NEAR they were told was zero?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `estimateWithdrawalFee`, `validateWithdrawal`; omni-withdraw-params.ts `deriveOmniWithdrawIntentParams` (storageDepositAccountId when nativeFee > 0); omni-bridge-utils.ts `createWithdrawIntentsPrimitive`
- Entrypoint: `IntentsSDK.processWithdrawal`
- Attacker controls: `bridgeConfigs.prefundedNativeFeeTokens` (integrator config) plus user-chosen token; `feeInclusive`
- Exploit idea: `validateWithdrawal` asserts relayerFee > 0 for non-UTXO unless subsidised; check `estimateWithdrawalFee` path returns amount 0 with quote null
- Invariant to test: feeEstimation.amount == total value leaving the user's balance beyond `amount`, across all assets.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: mock `getFee` with native_token_fee > 0, construct with prefundedNativeFeeTokens, assert intents include `storage_deposit` while fee.amount == 0.
