# [?] [CL]: Fix incorrect bound check/chain halt vector (#5557)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-06-19
Source: https://github.com/osmosis-labs/osmosis/commit/22a41f2e1962dfcab3ba78a879af88b1b37c42ad
Type: security-commit

## Details
[CL]: Fix incorrect bound check/chain halt vector (#5557)

* repro panic trigger and fix bound check

* fix comments

## Patch
### x/concentrated-liquidity/math/math.go
```diff
@@ -181,9 +181,9 @@ func GetLiquidityFromAmounts(sqrtPrice, sqrtPriceA, sqrtPriceB sdk.Dec, amount0,
 	if sqrtPrice.LTE(sqrtPriceA) {
 		// If the current price is less than or equal to the lower tick, then we use the liquidity0 formula.
 		liquidity = Liquidity0(amount0, sqrtPriceA, sqrtPriceB)
-	} else if sqrtPrice.LTE(sqrtPriceB) {
-		// If the current price is between the lower and upper ticks (non-inclusive of the lower tick but inclusive of the upper tick),
-		// then we use the minimum of the liquidity0 and liquidity1 formulas.
+	} else if sqrtPrice.LT(sqrtPriceB) {
+		// If the current price is between the lower and upper ticks (exclusive of both the lower and upper ticks,
+		// as both would trigger a division by zero), then we use the minimum of the liquidity0 and liquidity1 formulas.
 		liquidity0 := Liquidity0(amount0, sqrtPrice, sqrtPriceB)
 		liquidity1 := Liquidity1(amount1, sqrtPrice, sqrtPriceA)
 		liquidity = sdk.MinDec(liquidity0, liquidity1)
```

### x/concentrated-liquidity/math/math_test.go
```diff
@@ -413,6 +413,16 @@ func (suite *ConcentratedMathTestSuite) TestGetLiquidityFromAmounts() {
 			expectedLiquidity0: sdk.MustNewDecFromStr("7.706742302257039729"),
 			expectedLiquidity1: sdk.MustNewDecFromStr("4.828427124746190095"),
 		},
+		"current sqrt price on upper bound": {
+			currentSqrtP:   sqrt5500,
+			sqrtPHigh:      sqrt5500,
+			sqrtPLow:       sqrt4545,
+			amount0Desired: sdk.ZeroInt(),
+			amount1Desired: sdk.NewInt(1000000),
+			// Liquidity1 = amount1 / (sqrtPriceB - sqrtPriceA)
+			// https://www.wolframalpha.com/input?i=1000000%2F%2874.161984870956629487-67.416615162732695594%29
+			expectedLiquidity: "148249.842967213952971325",
+		},
 	}
 
 	for name, tc := range testCases {
```
