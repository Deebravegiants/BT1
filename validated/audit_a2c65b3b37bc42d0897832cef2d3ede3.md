### Title
`getFeeQuote` exact-in fallback validates only `amount_out` against `feeAmount`, never validates `amount_in` against the requested `exact_amount_in`, letting a malicious solver quote overcharge the withdrawing user - ([File: packages/intents-sdk/src/lib/estimate-fee.ts])

### Summary
In the exact-in fallback path of `getFeeQuote`, the sanity checks at `packages/intents-sdk/src/lib/estimate-fee.ts:142-159` only bound `quote.amount_out` to `[feeAmount, 1.5*feeAmount]`. They never check that the returned `quote.amount_in` matches the `exactAmountIn` value that was actually requested from the solver relay. Since the solver relay response is fully attacker-controlled, a malicious/permissionless solver can return a `quote.amount_in` far larger than `exactAmountIn` while keeping `amount_out` inside the checked bound (e.g. exactly `1500n`), passing all guards.

### Finding Description
The broken equality: `feeEstimation.amount` (which becomes `quote.amount_in`, the exact value later debited from the user via the `token_diff` intent, see `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts:208-219` and `estimateWithdrawalFee` at line 349: `amount: feeQuote ? BigInt(feeQuote.amount_in) : feeAmount`) should equal the real market cost of acquiring `feeAmount` of `feeAssetId`, i.e. approximately `exactAmountIn` (the 1.2x-buffered amount computed from oracle prices at `estimate-fee.ts:105-119`, which is what is actually sent to the solver as `exact_amount_in`).

However, after the `QuoteError` on the initial `exact_amount_out` call, the code computes `exactAmountIn` and sends it to `solverRelay.getQuote` with `exact_amount_in: exactAmountIn.toString()` (`estimate-fee.ts:121-137`). The response `quote` returned by the (attacker-controlled) solver relay is trusted verbatim: only `quote.amount_out` is checked, via `actualRatio = amount_out * 1000 / feeAmount` and `if (actualRatio > 1500n) throw` (`estimate-fee.ts:142-151`), plus a lower-bound check `amount_out < feeAmount` (`estimate-fee.ts:153-159`). Nowhere is `quote.amount_in` compared against the `exactAmountIn` that was requested. The function then returns `quote` unmodified, and callers use `quote.amount_in` directly as the amount debited from the user (`hot-bridge.ts:212-213`, `feeEstimation.amount` at line 349), and the same pattern is used by `OmniBridge`, `DirectBridge`, and `AuroraEngineBridge`.

A malicious solver can therefore respond to the `exact_amount_in` request with a crafted quote where `amount_in` is inflated arbitrarily (e.g. 1.5x, 2x, or more of the true `exactAmountIn`) while setting `amount_out` at exactly the boundary `1500n` (or anywhere in `[feeAmount, 1.5*feeAmount]`) to satisfy the only checks present. None of `validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()`, or `FeeExceedsAmountError` inspect the internal consistency between the requested `exact_amount_in` and the returned `amount_in`/`amount_out` pair — they operate on destination addresses and total fee-vs-withdrawal-amount, not on this specific quote-integrity invariant.

### Impact Explanation
The `quote.amount_in` value flows unchanged into `FeeEstimation.amount` and into the signed `token_diff` intent that debits the user's balance (`hot-bridge.ts:208-219`, similarly in `OmniBridge`/`DirectBridge`/`AuroraEngineBridge`). Because only `amount_out` is bounded and `amount_in` is never cross-checked against the requested `exactAmountIn`, a malicious solver can materially inflate the amount debited from the withdrawing user beyond the legitimate cost of the fee, for every withdrawal where the fee token differs from `feeAssetId` and the initial `exact_amount_out` request fails with `QuoteError`. This is a fee overcharge draining a material share of the withdrawal amount from the user, repeatable on every such withdrawal serviced by the malicious solver — matching the Critical/High "fee overcharge" impact category.

### Likelihood Explanation
Preconditions required: (1) a HOT/Omni/Direct/Aurora withdrawal where `feeAssetId !== tokenAssetId` (fee paid in a different asset than the amount being withdrawn), and (2) the solver relay's initial `exact_amount_out` quote request throws `QuoteError`, forcing the exact-in fallback path. Both conditions are realistic/frequent (fee-asset mismatches are common for gas-sponsored withdrawals, and `exact_amount_out` quotes can legitimately fail for illiquid pairs, triggering the documented fallback). The attacker only needs to control (or compromise) one permissionless solver's response to the relay to exploit every fallback quote it services — no privileged access is required, and the exploit is repeatable per withdrawal request.

### Recommendation
After receiving the exact-in quote, validate that `BigInt(quote.amount_in) === exactAmountIn` (or within a small, explicit tolerance) before accepting it; reject/`throw err` otherwise, exactly as is already done for the `amount_out` ratio check. This closes the gap where `amount_in` is implicitly trusted while only `amount_out` is validated.

### Proof of Concept
```ts
// packages/intents-sdk/src/lib/estimate-fee.poc.test.ts
import { describe, it, expect, vi } from "vitest";
import { QuoteError, solverRelay } from "@defuse-protocol/internal-utils";
import { getFeeQuote } from "./estimate-fee";
import * as pricesModule from "./tokensUsdPricesHttpClient";

describe("getFeeQuote amount_in integrity", () => {
	it("should reject a quote whose amount_in is inflated relative to the requested exact_amount_in, even when amount_out sits at the 1.5x boundary", async () => {
		const feeAmount = 1_000_000n;
		const feeAssetId = "nep141:fee.token";
		const tokenAssetId = "nep141:token.in";

		vi.spyOn(pricesModule, "tokens").mockResolvedValue({
			items: [
				{ defuse_asset_id: feeAssetId, price: 1, decimals: 6 },
				{ defuse_asset_id: tokenAssetId, price: 1, decimals: 6 },
			],
		} as any);

		let call = 0;
		vi.spyOn(solverRelay, "getQuote").mockImplementation(async (args: any) => {
			call++;
			if (call === 1) {
				// initial exact_amount_out fails
				throw new QuoteError("no quote");
			}
			// exact-in fallback: solver returns amount_in far above the
			// requested exact_amount_in (e.g. 3x), but amount_out sits at
			// exactly the 1.5x boundary so the existing check passes.
			const requestedExactIn = BigInt(args.quoteParams.exact_amount_in);
			return {
				amount_in: (requestedExactIn * 3n).toString(), // attacker-inflated
				amount_out: (feeAmount * 1500n / 1000n).toString(), // = 1.5x, actualRatio == 1500n
				defuse_asset_identifier_in: tokenAssetId,
				defuse_asset_identifier_out: feeAssetId,
			};
		});

		const quote = await getFeeQuote({
			feeAmount,
			feeAssetId,
			tokenAssetId,
			envConfig: {} as any,
		});

		// EQUALITY UNDER TEST:
		// LHS: amount actually debited from user = BigInt(quote.amount_in)
		// RHS: real cost of feeAmount worth of feeAssetId ≈ exactAmountIn (1.2x buffered)
		// This assertion FAILS today because estimate-fee.ts never checks amount_in
		// against the requested exact_amount_in, only amount_out against feeAmount.
		const impliedExactIn = feeAmount; // price=1, decimals equal => exactAmountIn ≈ feeAmount*1.2
		expect(BigInt(quote.amount_in)).toBeLessThanOrEqual((impliedExactIn * 12n) / 10n);
	});
});
```
This test demonstrates that `getFeeQuote` currently accepts a solver quote whose `amount_in` is inflated 3x relative to the value it requested via `exact_amount_in`, solely because the only validation performed (`estimate-fee.ts:142-159`) checks `amount_out`, not `amount_in`.