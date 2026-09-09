### Title
Unbounded `amount_in` accepted for exact-out fee quotes lets a solver overcharge the fee - (File: `packages/internal-utils/src/solverRelay/getQuote.ts`, `packages/intents-sdk/src/lib/estimate-fee.ts`)

### Summary
For the primary `exact_amount_out` fee-quote request in `getFeeQuote`, `handleQuoteResult`/`matchesRequest` only validate that `quote.amount_out` equals the requested `feeAmount` exactly; there is no upper bound on `quote.amount_in`. Only the fallback (`exact_amount_in`) branch, entered when the primary quote fails, has a sanity ratio cap (`actualRatio > 1500n`) and a `< feeAmount` rejection. Consequently, in the primary path a permissionless solver can return `amount_out === feeAmount` with an arbitrarily large `amount_in`, and if it is the only (or cheapest by the wrong metric) valid quote, it is accepted as the "true" fee quote.

### Finding Description
The claimed equality is: `feeEstimation.amount` (== `quote.amount_in`) should represent the minimal cost, in `tokenAssetId`, to cover `feeAmount` of `feeAssetId` — i.e., it should reflect a fair market rate, bounded above by some reasonable multiple of the true fee value.

Tracing the code:
- `getFeeQuote` (`packages/intents-sdk/src/lib/estimate-fee.ts:63-80`) first requests an `exact_amount_out: feeAmount` quote via `solverRelay.getQuote`.
- `handleQuoteResult` (`packages/internal-utils/src/solverRelay/getQuote.ts:32-94`) filters quotes with `matchesRequest`, which for the `exact_amount_out` case only checks `BigInt(quote.amount_out) === BigInt(quoteParams.exact_amount_out)` (`getQuote.ts:135-138`). It does **not** bound `amount_in` at all.
- `sortQuotes` for `exact_out` sorts by ascending `amount_in` (`getQuote.ts:108-111`), which is correct *if multiple honest solvers compete*, but provides no protection if the attacker is the only (or the cheapest-looking) responding solver — a permissionless solver can simply be the sole quote source for a given token pair/route, especially for a less-liquid pair like `nep141:zec.omft.near`.
- The returned `Quote` (with attacker-chosen `amount_in`) is used directly as `solverRelay.Quote`, feeding `feeEstimation.amount` downstream (used in `token_diff` per the bridge code, e.g. `omni-bridge.ts`, which calls `getFeeQuote`/`getUnderlyingFee`).
- Only the *fallback* branch (`estimate-fee.ts:139-159`), reached only when the primary exact-out request throws a `QuoteError`, has sanity checks: `actualRatio > 1500n` (1.5x cap) and `quote.amount_out < feeAmount` rejection. These checks are absent from the primary, and more commonly hit, exact-out path.

This means the guard described in the question ("`< feeAmount` check rejects; exact match with huge `amount_in` is accepted") is real, but it only exists in the fallback branch — the primary path (which is used whenever a solver responds successfully to `exact_amount_out`) has no upper-bound guard on `amount_in` whatsoever. A solver can return a valid, non-`FailedQuote` response with `amount_out` exactly `feeAmount` and an inflated `amount_in`, and it passes `isValidQuote`, `matchesRequest`, and becomes the `bestQuote` if no competing (cheaper) quote exists.

### Impact Explanation
`feeEstimation.amount` derived from this quote is used as the fee charged in `token_diff` intents constructed by the bridges (e.g., `OmniBridge`), meaning the user's withdrawal intent would debit `amount_in` of `tokenAssetId` to cover the fee. If a colluding/malicious solver is the sole responder for a given `feeAssetId`/`tokenAssetId` pair, they can set `amount_in` far above the fair value, and the surplus is captured by that solver when the resulting intent settles. This matches "fee overcharge / solver overpaid beyond the displayed fee," a High-severity category per the rubric.

However, exploitability is fundamentally bounded by whether the SDK/caller cross-checks the quote against expectations (e.g., `FeeExceedsAmountError` in `packages/intents-sdk/src/classes/errors.ts` guarding against fee exceeding the withdrawal amount) before constructing intents. I was not able to fully confirm within the available context whether `omni-bridge.ts` or `sdk.ts` applies an independent sanity/price check on the returned `quote.amount_in` before using it to build `token_diff`, or whether it trusts the solver relay's aggregated quote uncritically for the exact-out path. This is a material open question that determines whether the primary code path truly lacks *any* mitigating check downstream.

### Likelihood Explanation
Preconditions: attacker must control the only (or best by `amount_in`) solver response for the specific asset pair being fee-estimated — plausible for lower-liquidity routes/tokens where legitimate solver coverage is thin. Attacker cost: none beyond running a solver that responds to relay quote requests; this is a normal, permissionless capability, not requiring privilege escalation. Repeatable per withdrawal-fee-estimation call.

### Recommendation
Add the same sanity bound already present in the fallback branch (ratio cap relative to `feeAmount`, e.g., using price data from `tokens()`) to the primary `exact_amount_out` quote path in `getFeeQuote`, or add an upper-bound check in `matchesRequest`/`handleQuoteResult` comparing `amount_in` against an expected/oracle-derived ceiling before accepting a quote as `bestQuote`.

### Proof of Concept
Vitest plan (mock only HTTP `quote` JSON-RPC responses):
1. Mock the solver relay `quote` endpoint to return a single valid quote for `exact_amount_out: feeAmount` request: `{ amount_in: "<huge>", amount_out: "<feeAmount>", ... }`.
2. Call `getFeeQuote({ feeAmount, feeAssetId: "nep141:zec.omft.near", tokenAssetId, envConfig, ... })`.
3. Assert `quote.amount_out === feeAmount` (equality holds) but `quote.amount_in` is unbounded/huge, with no rejection thrown — demonstrating the missing upper-bound check in the primary path.
4. Contrast with a second test using the fallback (`exact_amount_in`) path where an equally huge `amount_in`/`amount_out` ratio *is* rejected via `actualRatio > 1500n`, showing the asymmetry between the two code paths.

Given the inability to fully verify how downstream bridge code (`omni-bridge.ts`, `sdk.ts`) consumes this unbounded `amount_in` (whether an independent guard like `FeeExceedsAmountError` catches the abuse before intent construction), this finding should be treated as **suspected but not fully confirmed** — the root-cause asymmetry in `getQuote.ts`/`estimate-fee.ts` is confirmed, but end-to-end exploitability through to signed/debited funds requires further tracing of `sdk.ts`'s use of `FeeEstimation.amount` that I could not complete within available context.