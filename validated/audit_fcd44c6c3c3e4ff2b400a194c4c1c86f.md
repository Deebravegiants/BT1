### Title
`getFeeQuote`'s primary `exact_amount_out` request has no upper bound on `amount_in`, letting a solver quote a matching `amount_out` but an inflated `amount_in`, overcharging the user - ([File: packages/intents-sdk/src/lib/estimate-fee.ts])

### Summary
`getFeeQuote` first asks the solver relay for an `exact_amount_out` quote equal to `feeAmount`. `handleQuoteResult`/`matchesRequest` in `packages/internal-utils/src/solverRelay/getQuote.ts` only validate that the *fixed* side (`amount_out`) equals the requested `feeAmount`; the competing side (`amount_in`) is accepted at whatever value the solver supplies, with no reasonableness/ratio check. The only such ratio guard (`actualRatio > 1500n`, i.e. the 1.5x cap) exists solely in the `exact_amount_in` fallback branch that runs after a `QuoteError`, not in the primary `exact_amount_out` path.

### Finding Description
The broken equality: the code implicitly assumes `feeEstimation.amount` (== `quote.amount_in`) is a fair market price for `feeAmount` of `feeAssetId`, i.e. `amount_in ≈ feeAmount converted at market price`. Nothing enforces this for the primary quote path.

Trace:
1. `getFeeQuote` (packages/intents-sdk/src/lib/estimate-fee.ts:64-80) issues `solverRelay.getQuote` with `exact_amount_out: feeAmount.toString()`.
2. `handleQuoteResult` (packages/internal-utils/src/solverRelay/getQuote.ts:32-94) filters quotes via `isValidQuote` and `matchesRequest`.
3. `matchesRequest` (packages/internal-utils/src/solverRelay/getQuote.ts:119-138) for the `exact_amount_out` case only checks `BigInt(quote.amount_out) === BigInt(quoteParams.exact_amount_out)`. It never bounds `quote.amount_in`.
4. `sortQuotes` (packages/internal-utils/src/solverRelay/getQuote.ts:96-113) for `exact_out` sorts by ascending `amount_in` and `handleQuoteResult` returns `sortQuotes(validQuotes, "exact_out")[0]` — the *lowest* `amount_in` among *valid* quotes. If the malicious/permissionless solver is the only one (or the fastest) to respond for the given `(tokenAssetId, feeAssetId)` pair — plausible for exotic/illiquid pairs such as `nep245:v2_1.omni.hot.tg:56_...` — its inflated quote is the only, hence the "best", candidate and is selected.
5. The chosen quote is returned unmodified from `getFeeQuote`, and every bridge caller (`hot-bridge.ts:349`, `direct-bridge.ts:260`, `aurora-engine-bridge.ts:197`, `omni-bridge.ts:622-631`) sets `feeEstimation.amount = BigInt(feeQuote.amount_in)` and `feeEstimation.quote = feeQuote` directly, with no additional bound check.
6. `sdk.ts`'s `_estimateWithdrawalFee` (packages/intents-sdk/src/sdk.ts:408-454) only checks `FeeExceedsAmountError` (i.e., `fee.amount >= withdrawal amount`), not whether the fee itself is a reasonable market price. No check compares the quoted `amount_in` to an expected fee-equivalent computed from prices (that logic — `tokens()` price lookup and the `1.5x` ratio guard — exists only in the fallback branch of `estimate-fee.ts:139-159`, which is never reached when the exact_out quote succeeds).

Because the primary path never fails with `QuoteError` in this scenario (the solver *did* satisfy `exact_amount_out`), the code never reaches the ratio-check branch that would have caught an unreasonable quote. The comment at getQuote.ts:60-65 explicitly acknowledges the malicious-solver threat model but only guards against asset/amount mismatches on the *fixed* side, not against `amount_in` inflation on the free side.

### Impact Explanation
The user's signed withdrawal intent sells `feeEstimation.amount` (= inflated `quote.amount_in`) of `tokenAssetId` in exchange for `feeAmount` of `feeAssetId`, per the token_diff intent constructed from the accepted quote. If a permissionless/malicious solver is the sole (or winning) quoter for that pair, it can set `amount_in` arbitrarily high while keeping `amount_out == feeAmount` exactly, causing the withdrawing user to be charged far more than the actual fee, with the surplus captured by the solver executing the settlement. This matches "fee overcharge or solver overpaid beyond the displayed fee" (High).

### Likelihood Explanation
Requires: (a) the attacker's solver be selected as the best (lowest `amount_in`) among the valid quotes returned by the relay for the specific `exact_amount_out` request — most easily achieved when it is the only solver quoting that pair (illiquid/exotic assets, e.g., the `nep245:v2_1.omni.hot.tg:56_...` asset in the question), and (b) the request use the primary exact_out path (i.e., not fall into the `QuoteError` catch branch that has the ratio check). Both conditions are plausible without any privileged access — a permissionless solver only needs to answer the public quote RPC. It is repeatable on every fee estimation call for that pair as long as the attacker's solver remains the winning responder.

### Recommendation
Apply the same reasonableness/ratio bound used in the exact_in fallback (`estimate-fee.ts:139-151`) to the primary `exact_amount_out` quote as well: compute an expected `amount_in` ceiling from `tokens()` price data (or a configurable max ratio) and reject/`QuoteError` any quote whose `amount_in` exceeds that bound, before returning it from `getFeeQuote`.

### Proof of Concept
Vitest plan (mock only the solver relay HTTP `quote` call):
1. Mock `quote()` to return, for an `exact_amount_out` request with `exact_amount_out = feeAmount`, a single quote: `{ amount_in: "1000000000000" /* huge */, amount_out: feeAmount.toString(), defuse_asset_identifier_in: tokenAssetId, defuse_asset_identifier_out: feeAssetId, expiration_time: <future>, quote_hash: "x" }`.
2. Call `getFeeQuote({ feeAmount, feeAssetId, tokenAssetId, envConfig, ... })`.
3. Assert: `result.amount_out === feeAmount.toString()` (passes matchesRequest) AND `BigInt(result.amount_in)` equals the crafted huge value — i.e., no rejection occurs despite `amount_in` being wildly disproportionate to `feeAmount` at the mocked/token prices.
4. Contrast with a second test where a second, honest quote with a low `amount_in` is also present — confirm `sortQuotes` picks the lower one (showing the vulnerability only manifests when the attacker's quote is the sole/lowest response), establishing that no absolute-value guard exists independent of competition.
5. Assert the equality `feeEstimation.amount == quote.amount_in` is honored end-to-end in a bridge's `estimateWithdrawalFee` (e.g., `hot-bridge.ts`) with the crafted huge `amount_in`, showing it propagates unchecked into `FeeEstimation.amount`.