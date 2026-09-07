# Q5487: Fee quote nep245:v2_1.omni.hot.tg:11: the quote `expiration_time` has alre

## Question
While estimating the fee for `nep245:v2_1.omni.hot.tg:1117_`, when the quote `expiration_time` has already passed when the intent is published, can an unprivileged user or a permissionless solver make `getFeeQuote` return a quote whose `amount_in` (what the user sells in the withdrawn token) exceeds the true fee by more than the displayed `feeEstimation.amount` implies, because expiry is never checked by `getQuote`/`getFeeQuote`, so the surplus accrues to the solver?

## Target
- File/function: packages/intents-sdk/src/lib/estimate-fee.ts `getFeeQuote`; packages/internal-utils/src/solverRelay/getQuote.ts `handleQuoteResult`, `matchesRequest`, `sortQuotes`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` -> bridge `estimateWithdrawalFee` -> `getFeeQuote`
- Attacker controls: the solver-side quote payload (amount_in, amount_out, expiration_time), and `quoteOptions`
- Exploit idea: expiry is never checked by `getQuote`/`getFeeQuote`
- Invariant to test: quote.amount_out >= feeAmount and quote.amount_in is the minimum across matching quotes; feeEstimation.amount == quote.amount_in used in token_diff.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: mock `quote` JSON-RPC responses with crafted quotes and `tokens()` prices; assert the selected quote and resulting FeeEstimation.amount.
