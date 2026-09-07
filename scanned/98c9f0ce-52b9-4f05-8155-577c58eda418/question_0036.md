# Q0036: Decimals/min nep141:zec.omft.near feeInclusive: true: `origin_decimals` < NEAR decimals 

## Question
For `nep141:zec.omft.near` via OmniBridge with `feeInclusive: true`, when `origin_decimals` < NEAR decimals so `verifyTransferAmount(amount, 0n, origin, near)` truncates dust, can an unprivileged user sign a withdrawal whose amount passes `validateWithdrawal` but normalises to less than the destination's minimum or to zero (the truncated remainder is burned at the bridge), so the tokens are debited on intents.near and never credited on Zcash?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` (verifyTransferAmount, getMinimumTransferableAmount, MIN_AMOUNT_SOL_OMNI_WITHDRAWAL, UTXO min_amount), `getCachedTokenDecimals`; sdk.ts `_estimateWithdrawalFee` skipMinAmountValidation
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` then `signAndSendWithdrawalIntent` / `processWithdrawal`
- Attacker controls: `amount`, `feeInclusive`, reuse of a FeeEstimation across amounts
- Exploit idea: the truncated remainder is burned at the bridge
- Invariant to test: normalised destination amount > 0 and >= destination minimum for every withdrawal the SDK signs.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: mock decimals and getFee; sweep amounts around the boundary; assert throws vs intents produced.
