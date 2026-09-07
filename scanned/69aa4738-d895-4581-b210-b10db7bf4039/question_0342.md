# Q0342: Decimals/min nep141:zec.omft.near feeInclusive: true: `fee.min_amount` from `getFee` is 

## Question
For `nep141:zec.omft.near` via OmniBridge with `feeInclusive: true`, when `fee.min_amount` from `getFee` is lower than `verifyTransferAmount`'s threshold for UTXO chains, can an unprivileged user sign a withdrawal whose amount passes `validateWithdrawal` but normalises to less than the destination's minimum or to zero (amount+fees >= min_amount passes while normalised amount is 0), so the tokens are debited on intents.near and never credited on Zcash?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` (verifyTransferAmount, getMinimumTransferableAmount, MIN_AMOUNT_SOL_OMNI_WITHDRAWAL, UTXO min_amount), `getCachedTokenDecimals`; sdk.ts `_estimateWithdrawalFee` skipMinAmountValidation
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` then `signAndSendWithdrawalIntent` / `processWithdrawal`
- Attacker controls: `amount`, `feeInclusive`, reuse of a FeeEstimation across amounts
- Exploit idea: amount+fees >= min_amount passes while normalised amount is 0
- Invariant to test: normalised destination amount > 0 and >= destination minimum for every withdrawal the SDK signs.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: mock decimals and getFee; sweep amounts around the boundary; assert throws vs intents produced.
