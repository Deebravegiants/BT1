# [?] refactor/security: prevent same execution price exploit within the same ULP (#5693)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-07-02
Source: https://github.com/osmosis-labs/osmosis/commit/cf223be21b8530b28a326c4d0738e8dc5d0f63f2
Type: security-commit

## Details
refactor/security: prevent same execution price exploit within the same ULP (#5693)

* repro infinite loop in swap logic

* precision increase solution to infinite loop bug

* fix

* remove logic

* remove error

* updates

* updates

* updates

* updates

* begin switching zeroForOneStrategy.ComputeSwapWithinBucketInGivenOut

* switch remaining zero for one swap step and add rounding comments

* begin switching cur sqrt price to big dec in swaps

* try adding CalculateSqrtPriceToTickBigDec

* one for zero out given in tests

* fix one for zero tests

* update one for zero tests

* in-progress test

* updates

* fix TestComputeSwapStepOutGivenIn_ZeroForOne

* fix TestComputeSwapStepInGivenOut_ZeroForOne

* convert current sqrt price to BigDec and resolve syntax errors

* updates

* clean up

* clean ups

* clean ups

* fix TestComputeSwapState_Inverse

* comment

* updates

* clean ups

* remove unused function

* remove unused GetNextSqrtPriceFromAmount1OutRoundingDown

* switch GetNextSqrtPriceFromAmount0InRoundingUp to big dec

* fully convert GetNextSqrtPriceFromAmount0OutRoundingUp to big dec

* clean up math tests more

* more math test clean up

* fully convert calc methods to big dec

* fix model package tests

* fix TestAddToPosition

* fix TestCalculateSpotPrice

* fix TestSingleSidedAddToPosition

* fix TestUninitializePool

* go mod update

* big dec comparison correction and prints

* fix equality issues

* convert tests to big dec

* fix a few swap tests

* small e2e fix

* more swap test fixes

* updates

* fix another test

* please get fixed

* fix all out given in swap tests

* e2e

* fix all one for zero in given out

* I can fix you

* clean ups

* MulRoundUp test

* test SDKDecRoundUp

* clean up

* revert launch.json

* comment

* refactor/security: prevent same execution price exploit within the same ULP

* add zero for one swap strategy ULP tests

* typo

* remove errors

* remove prints

* typos

* typo

---------

Co-authored-by: alpo <yukseloglua@berkeley.edu>

### x/concentrated-liquidity/swaps.go
```diff
@@ -369,6 +369,10 @@ func (k Keeper) computeOutAmtGivenIn(
 			swapState.amountSpecifiedRemaining,
 		)
 
+		if err := validateSwapProgressAndAmountConsumption(computedSqrtPrice, sqrtPriceStart, amountIn, amountOut); err != nil {
+			return sdk.Coin{}, sdk.Coin{}, PoolUpdates{}, sdk.Dec{}, err
+		}
+
 		// Update the spread reward growth for the entire swap using the total spread factors charged.
 		swapState.updateSpreadRewardGrowthGlobal(spreadRewardCharge)
 
@@ -507,6 +511,10 @@ func (k Keeper) computeInAmtGivenOut(
 			swapState.amountSpecifiedRemaining,
 		)
 
+		if err := validateSwapProgressAndAmountConsumption(computedSqrtPrice, sqrtPriceStart, amountIn, amountOut); err != nil {
+			return sdk.Coin{}, sdk.Coin{}, PoolUpdates{}, sdk.Dec{}, err
+		}
+
 		swapState.updateSpreadRewardGrowthGlobal(spreadRewardChargeTotal)
 
 		ctx.Logger().Debug("cl calc in given out")
@@ -749,3 +757,22 @@ func (k Keeper) getSwapAccumulators(ctx sdk.Context, poolId uint64) (accum.Accum
 	}
 	return spreadAccum, uptimeAccums, nil
 }
+
+// validateSwapProgressAndAmountConsumption validates that the swap progress and amount consumption are valid. These are valid if:
+// - computedSqrtPrice is not equal to sqrtPriceStart (progress made)
+// - computedSqrtPrice is equals to sqrtPriceStart and both amountIn and amountOut are zero (progress not made AND amounts are not consumed)
+// If swap succeeded within the same ULP while consuming amounts, that would mean that a trader can exploit the pool to
+// continue getting the same execution price. To prevent that, we add this check that fails the swap if amounts
+// in or out are non-zero while swap does not move even by 1 ULP.
+// If no progress is made with zero amounts, there is a risk of running into an infinite loop which we prevent
+// by a constant bound on the the number of iterations without progress.
+// Note that having a single iteration without progress and zero amounts is correct. One good example
+// is swapping one for zero (right) directly to the tick. Then, immediately swapping zero for one (left).
+// After the first swap, our sqrtPriceCurrent is the crossed tick's sqrt price. Also sqrtPriceTarget is the crossed tick's sqrt price.
+// In such a case, no amounts are consumed and the swap step is allowed to succeed.
+func validateSwapProgressAndAmountConsumption(computedSqrtPrice, sqrtPriceStart osmomath.BigDec, amountIn, amountOut sdk.Dec) error {
+	if computedSqrtPrice.Equal(sqrtPriceStart) && !(amountIn.IsZero() && amountOut.IsZero()) {
+		return types.SwapNoProgressWithConsumptionError{ComputedSqrtPrice: computedSqrtPrice, AmountIn: amountIn, AmountOut: amountOut}
+	}
+	return nil
+}
```

### x/concentrated-liquidity/types/errors.go
```diff
@@ -851,3 +851,13 @@ type SwapNoProgressError struct {
 func (e SwapNoProgressError) Error() string {
 	return fmt.Sprintf("ran out of iterations during swap. Possibly entered an infinite loop. Pool id (%d), user provided coin (%s)", e.PoolId, e.UserProvidedCoin)
 }
+
+type SwapNoProgressWithConsumptionError struct {
+	ComputedSqrtPrice osmomath.BigDec
+	AmountIn          sdk.Dec
+	AmountOut         sdk.Dec
+}
+
+func (e SwapNoProgressWithConsumptionError) Error() string {
+	return fmt.Sprintf("did not advance sqrt price after swap step %s, with amounts in (%s), out (%s)", e.ComputedSqrtPrice, e.AmountIn, e.AmountOut)
+}
```
