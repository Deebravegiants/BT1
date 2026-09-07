# Q5153: Decimals/min nep141:eth.bridge.near feeInclusive: false: `MIN_AMOUNT_SOL_OMNI_WITHDRAWAL` i

## Question
For `nep141:eth.bridge.near` via OmniBridge with `feeInclusive: false`, when `MIN_AMOUNT_SOL_OMNI_WITHDRAWAL` is hardcoded (890880n) while the live rent-exempt minimum changes, can an unprivileged user sign a withdrawal whose amount passes `validateWithdrawal` but normalises to less than the destination's minimum or to zero (hardcoded constant vs live chain), so the tokens are debited on intents.near and never credited on Ethereum?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` (verifyTransferAmount, getMinimumTransferableAmount, MIN_AMOUNT_SOL_OMNI_WITHDRAWAL, UTXO min_amount), `getCachedTokenDecimals`; sdk.ts `_estimateWithdrawalFee` skipMinAmountValidation
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` then `signAndSendWithdrawalIntent` / `processWithdrawal`
- Attacker controls: `amount`, `feeInclusive`, reuse of a FeeEstimation across amounts
- Exploit idea: hardcoded constant vs live chain
- Invariant to test: normalised destination amount > 0 and >= destination minimum for every withdrawal the SDK signs.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: mock decimals and getFee; sweep amounts around the boundary; assert throws vs intents produced.
