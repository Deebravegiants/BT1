### Title
Malicious solver can inflate `amount_in` on an exact-out quote, causing `getFeeQuote` to return an unbounded fee - (`packages/internal-utils/src/solverRelay/getQuote.ts`, `packages/intents-sdk/src/lib/estimate-fee.ts`)

### Summary
`matchesRequest` in `getQuote.ts` only verifies the side of the quote fixed by the request (tokens and `amount_out` for exact-out requests); it never validates that `amount_in` is close to fair market value. The primary exact-out branch of `getFeeQuote` in `estimate-fee.ts` (lines 63-80) returns whatever `amount_in` the solver relay gives back with zero price sanity check, unlike the exact-in fallback branch which explicitly checks the ratio against oracle prices (lines 139-159).

### Finding Description
The broken equality: the debited `amount_in` (used as `-amount_in` in the `token_diff` intent and as `feeEstimation.amount`) should be bounded by the fair market cost of `feeAmount` units of `feeAssetId`, but nothing in the traced path enforces this bound for the primary exact-out quote path.

Trace:
- `getFeeQuote` (`packages/intents-sdk/src/lib/estimate-fee.ts:63-80`) calls `solverRelay.getQuote` with `exact_amount_out: feeAmount.toString()` and, on success, returns the quote object directly — no check on `amount_in` at all in this branch.
- `getQuote`'s `handleQuoteResult` (`packages/internal-utils/src/solverRelay/getQuote.ts:32-94`) filters quotes via `matchesRequest`, which for exact-out requests only checks `quote.defuse_asset_identifier_in/out` equality and `BigInt(quote.amount_out) === BigInt(quoteParams.exact_amount_out)` (`getQuote.ts:119-138`). `amount_in` is untouched.
- `sortQuotes` (`getQuote.ts:96-113`) picks the quote with the smallest `amount_in` among *competing* quotes, but with a single (malicious) solver response there is no competitor, so the inflated `amount_in` simply wins by default.
- Callers such as `direct-bridge.ts:246-267`, `aurora-engine-bridge.ts:183-204`, `omni-bridge.ts:622-631` set `feeEstimation.amount = BigInt(quote.amount_in)` unconditionally.
- `sdk.ts:_estimateWithdrawalFee` (`packages/intents-sdk/src/sdk.ts:408-454`) only throws `FeeExceedsAmountError` when `feeInclusive === true` and `fee.amount >= withdrawalParams.amount`; for `feeInclusive === false` there is no bound at all, and even for `feeInclusive === true` the attacker can set `amount_in` up to just under the withdrawal amount and still pass.
- `createWithdrawalIntents` (e.g., `direct-bridge.ts:120-131`) embeds `feeEstimation.quote.amount_in` directly as the debited amount in the `token_diff` intent that gets signed and submitted.

Root cause: only the exact-in *fallback* path in `getFeeQuote` (triggered after a `QuoteError`) has a price-based sanity check (`RATIO_SCALE`/`actualRatio` bound to 1.5x, `estimate-fee.ts:139-159`); the primary exact-out path that is hit whenever the solver relay successfully returns any single quote has no equivalent check.

Attacker input: a permissionless solver responds to the relay's exact-out quote request with a `Quote` whose `defuse_asset_identifier_in/out` match and `amount_out === exact_amount_out`, but `amount_in` is set arbitrarily (e.g., 1000x fair value).

Exploit flow: user/integrator calls `estimateWithdrawalFee`/`createWithdrawalIntents` → SDK requests exact-out quote from solver relay → malicious solver's inflated quote is the only (or best "cheapest" among colluding) result → `matchesRequest` accepts it → `getFeeQuote` returns it unmodified → SDK signs a `token_diff` intent debiting the inflated `amount_in` from the user.

Why existing guards fail: `matchesRequest` was designed on the assumption that competing solvers bound the unfixed side via `sortQuotes`; that assumption fails when there's only one (malicious) solver. `FeeExceedsAmountError` only guards against fee ≥ full withdrawal amount, not against an inflated-but-still-smaller-than-amount fee.

### Impact Explanation
The user signs and submits a `token_diff` intent debiting an attacker-chosen `amount_in` of `tokenAssetId`, up to (but not including) the entire withdrawal amount when `feeInclusive=true`, or fully on top of the withdrawal amount when `feeInclusive=false`. This is funds moved that the user did not authorize at a fair rate — a fee error draining a material, attacker-controlled share of the amount, repeatable on every quote request the solver answers.

### Likelihood Explanation
Requires only that the attacker operate a permissionless solver reachable by the relay and be the (or the "best") responder for a given quote request — no special privileges, no interaction with contract admins, no relayer/RPC compromise. Feasible any time a low-liquidity/low-competition route is quoted, which is a realistic operating condition for a permissionless network.

### Recommendation
Add a price-sanity check on `amount_in` in the primary exact-out branch of `getFeeQuote` (mirroring the existing `RATIO_SCALE`/oracle-price check already used in the exact-in fallback branch), rejecting or falling back when `amount_in` deviates materially from the price-oracle-implied fair value for `feeAmount` of `feeAssetId` in terms of `tokenAssetId`.

### Proof of Concept
```ts
// packages/internal-utils/src/solverRelay/getQuote.test.ts style
it("accepts an exact-out quote with an inflated amount_in from a single solver", async () => {
  const inflatedQuote: Quote = {
    ...validQuote,
    quote_hash: "hash-inflated",
    amount_out: "26000000000000", // matches exact_amount_out
    amount_in: "1000000000000000", // 1000x fair rate (fair ~= 1000000000000)
  };
  vi.mocked(quoteWithLogModule.quoteWithLog).mockResolvedValueOnce([inflatedQuote]);

  const result = await getQuote({
    quoteParams: { ...baseParams, exact_amount_out: "26000000000000" },
    config,
  });

  // matchesRequest passes it through unbounded
  expect(result.amount_in).toBe("1000000000000000");
});

// packages/intents-sdk/src/lib/estimate-fee.test.ts style
it("getFeeQuote returns solver-controlled inflated amount_in without rejection", async () => {
  vi.spyOn(solverRelay, "getQuote").mockResolvedValue({
    quote_hash: "h",
    defuse_asset_identifier_in: tokenAssetId,
    defuse_asset_identifier_out: feeAssetId,
    amount_in: "1000000000000000", // attacker-controlled, 1000x fair
    amount_out: feeAmount.toString(), // exactly matches request
    expiration_time: new Date(Date.now() + 60_000).toISOString(),
  });

  const feeEstimation = await getFeeQuote({ feeAmount, feeAssetId, tokenAssetId, envConfig });

  expect(BigInt(feeEstimation.amount_in)).toBe(1000000000000000n); // no bound enforced
});
```