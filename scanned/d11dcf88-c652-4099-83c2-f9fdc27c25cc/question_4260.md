# Q4260: UTXO nep141:nbtc.bridge.nea utxoProtocolFee feeInclusive: false (the caller passes a `feeEs)

## Question
For UTXO withdrawal of `nep141:nbtc.bridge.near` with `feeInclusive: false`, when the caller passes a `feeEstimation` whose `underlyingFees` has `utxoProtocolFee` inflated far above what `omniBridgeAPI.getFee` returned, does `deriveOmniWithdrawIntentParams` add `utxoMaxGasFee + utxoProtocolFee` to the `ft_withdraw` amount and put `MaxGasFee` in `msg` without re-deriving them from the API, so the relayer may spend up to `MaxGasFee` from the user's BTC/ZEC and the recipient receives less than the amount the SDK displayed?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts `deriveOmniWithdrawIntentParams`; omni-bridge.ts `validateWithdrawal` (UTXO branch), `estimateWithdrawalFee`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` / `createWithdrawalIntents` with caller `feeEstimation`
- Attacker controls: `feeEstimation.underlyingFees[OmniBridge].utxoProtocolFee`, `amount`, `feeInclusive`
- Exploit idea: The intent amount and `MaxGasFee` come straight from the caller-provided `feeEstimation`; `validateWithdrawal` only asserts they are > 0 and that `amount + fees >= min_amount`. Nothing ties them to the live `getFee` result at signing time.
- Invariant to test: recipient_received == withdrawalParams.amount (feeInclusive ? - feeEstimation.amount : unchanged); `MaxGasFee` in msg == utxoMaxGasFee used to size the amount.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: call `deriveOmniWithdrawIntentParams` with a manipulated FeeEstimation and assert `amount`/`msg`; then check what `validateWithdrawal` would have rejected.
