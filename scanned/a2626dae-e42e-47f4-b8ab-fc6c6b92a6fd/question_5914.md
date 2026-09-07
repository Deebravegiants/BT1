# Q5914: Batch pairing: a withdrawal composed with `si / `args.intent.relayParams()` returns 

## Question
For a withdrawal composed with `signedIntents.before` / `.after` (pre-signed `MultiPayload`s published atomically via `publishIntents`, ticket taken at `tickets[beforeCount]`) submitted through `IntentsSDK.signAndSendWithdrawalIntent`, when `args.intent.relayParams()` returns `quoteHashes` that overlap with `feeEstimations[*].quote.quote_hash`, does `zip(withdrawalParamsArray, feeEstimations)` and the `relayParamsFn` quote-hash aggregation let a fee computed for one withdrawal be applied to another, so one user-signed payload debits amount_i + fee_j and the relayer executes a `token_diff` the user never priced?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `signAndSendWithdrawalIntent` (zip, relayParamsFn), `processWithdrawal`; packages/intents-sdk/src/lib/array.ts `zip`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` / `processWithdrawal` with arrays
- Attacker controls: order and content of `feeEstimation[]`, `intent.relayParams`
- Exploit idea: Pairing is positional; no check that `feeEstimation[i]` was produced for `withdrawalParams[i]` (asset, route, address). Quote hashes are concatenated blindly.
- Invariant to test: For each i, the fee applied to withdrawal i equals the fee estimated for (assetId_i, route_i, destination_i); quoteHashes == set of quotes actually used.
- Expected Immunefi impact: Critical - fee calculation error draining a material share of the amount (HackenProof: fee calculation errors causing significant losses)
- Fast validation: vitest: pass swapped feeEstimations and assert the produced intents per withdrawal.
