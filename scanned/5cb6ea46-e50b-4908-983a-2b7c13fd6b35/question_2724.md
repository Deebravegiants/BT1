# Q2724: Fee quote nep141:starknet.omft.near: a solver returns a quote with `amoun

## Question
While estimating the fee for `nep141:starknet.omft.near`, when a solver returns a quote with `amount_out` slightly below `feeAmount`, can an unprivileged user or a permissionless solver make `getFeeQuote` return a quote whose `amount_in` (what the user sells in the withdrawn token) exceeds the true fee by more than the displayed `feeEstimation.amount` implies, because rejected by `< feeAmount` check; but `amount_out` exactly equal with huge `amount_in` is accepted, so the surplus accrues to the solver?

## Target
- File/function: packages/intents-sdk/src/lib/estimate-fee.ts `getFeeQuote`; packages/internal-utils/src/solverRelay/getQuote.ts `handleQuoteResult`, `matchesRequest`, `sortQuotes`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` -> bridge `estimateWithdrawalFee` -> `getFeeQuote`
- Attacker controls: the solver-side quote payload (amount_in, amount_out, expiration_time), and `quoteOptions`
- Exploit idea: rejected by `< feeAmount` check; but `amount_out` exactly equal with huge `amount_in` is accepted
- Invariant to test: quote.amount_out >= feeAmount and quote.amount_in is the minimum across matching quotes; feeEstimation.amount == quote.amount_in used in token_diff.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: mock `quote` JSON-RPC responses with crafted quotes and `tokens()` prices; assert the selected quote and resulting FeeEstimation.amount.
