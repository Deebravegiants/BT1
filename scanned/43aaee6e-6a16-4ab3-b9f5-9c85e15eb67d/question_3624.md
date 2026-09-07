# Q3624: Batch pairing: a batch mixing HOT, PoA and Om / one `FeeEstimation` object is reused

## Question
For a batch mixing HOT, PoA and Omni routes (indexes are per-route in `createWithdrawalIdentifiers` but per-tx in bridge status APIs) submitted through `IntentsSDK.signAndSendWithdrawalIntent`, when one `FeeEstimation` object is reused for every element, does `zip(withdrawalParamsArray, feeEstimations)` and the `relayParamsFn` quote-hash aggregation let a fee computed for one withdrawal be applied to another, so one user-signed payload debits amount_i + fee_j and the relayer executes a `token_diff` the user never priced?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `signAndSendWithdrawalIntent` (zip, relayParamsFn), `processWithdrawal`; packages/intents-sdk/src/lib/array.ts `zip`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` / `processWithdrawal` with arrays
- Attacker controls: order and content of `feeEstimation[]`, `intent.relayParams`
- Exploit idea: Pairing is positional; no check that `feeEstimation[i]` was produced for `withdrawalParams[i]` (asset, route, address). Quote hashes are concatenated blindly.
- Invariant to test: For each i, the fee applied to withdrawal i equals the fee estimated for (assetId_i, route_i, destination_i); quoteHashes == set of quotes actually used.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: pass swapped feeEstimations and assert the produced intents per withdrawal.
