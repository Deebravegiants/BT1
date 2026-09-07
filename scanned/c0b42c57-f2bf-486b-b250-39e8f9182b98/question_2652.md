# Q2652: Fee quote nep141:starknet.omft.near: exact-out quote fails and the price-

## Question
While estimating the fee for `nep141:starknet.omft.near`, when exact-out quote fails and the price-based exact-in fallback is used with a 1.2x buffer, can an unprivileged user or a permissionless solver make `getFeeQuote` return a quote whose `amount_in` (what the user sells in the withdrawn token) exceeds the true fee by more than the displayed `feeEstimation.amount` implies, because up to 1.5x `amount_out/feeAmount` is accepted, so the user can overpay 50% of the fee, so the surplus accrues to the solver?

## Target
- File/function: packages/intents-sdk/src/lib/estimate-fee.ts `getFeeQuote`; packages/internal-utils/src/solverRelay/getQuote.ts `handleQuoteResult`, `matchesRequest`, `sortQuotes`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` -> bridge `estimateWithdrawalFee` -> `getFeeQuote`
- Attacker controls: the solver-side quote payload (amount_in, amount_out, expiration_time), and `quoteOptions`
- Exploit idea: up to 1.5x `amount_out/feeAmount` is accepted, so the user can overpay 50% of the fee
- Invariant to test: quote.amount_out >= feeAmount and quote.amount_in is the minimum across matching quotes; feeEstimation.amount == quote.amount_in used in token_diff.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: mock `quote` JSON-RPC responses with crafted quotes and `tokens()` prices; assert the selected quote and resulting FeeEstimation.amount.
