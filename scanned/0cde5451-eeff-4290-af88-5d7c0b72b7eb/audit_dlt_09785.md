# [?] use mulDiv to avoid overflows

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2023-06-15
Source: https://github.com/gmx-io/gmx-synthetics/commit/8e795761aefc8d7fb9b932d58f4ca584632e38fe
Type: security-commit

## Details
use mulDiv to avoid overflows

## Patch
### contracts/deposit/ExecuteDepositUtils.sol
```diff
@@ -189,7 +189,7 @@ library ExecuteDepositUtils {
                 prices.longTokenPrice,
                 prices.shortTokenPrice,
                 cache.longTokenAmount,
-                Precision.mulDiv(cache.longTokenUsd, cache.priceImpactUsd, cache.longTokenUsd + cache.shortTokenUsd)
+                Precision.mulDiv(cache.priceImpactUsd, cache.longTokenUsd, cache.longTokenUsd + cache.shortTokenUsd)
             );
 
             cache.receivedMarketTokens += _executeDeposit(params, _params);
@@ -206,7 +206,7 @@ library ExecuteDepositUtils {
                 prices.shortTokenPrice,
                 prices.longTokenPrice,
                 cache.shortTokenAmount,
-                Precision.mulDiv(cache.shortTokenUsd, cache.priceImpactUsd, cache.longTokenUsd + cache.shortTokenUsd)
+                Precision.mulDiv(cache.priceImpactUsd, cache.shortTokenUsd, cache.longTokenUsd + cache.shortTokenUsd)
             );
 
             cache.receivedMarketTokens += _executeDeposit(params, _params);
```

### contracts/market/MarketUtils.sol
```diff
@@ -146,7 +146,7 @@ library MarketUtils {
     // @param shortTokenPrice the price of the short token
     // @param indexTokenPrice the price of the index token
     // @param maximize whether to maximize or minimize the market token price
-    // @return returns the market token's price
+    // @return returns (the market token's price, MarketPoolValueInfo.Props)
     function getMarketTokenPrice(
         DataStore dataStore,
         Market.Props memory market,
@@ -175,7 +175,8 @@ library MarketUtils {
 
         if (poolValueInfo.poolValue == 0) { return (0, poolValueInfo); }
 
-        return (poolValueInfo.poolValue * Precision.WEI_PRECISION.toInt256() / supply.toInt256(), poolValueInfo);
+        int256 marketTokenPrice = Precision.mulDiv(Precision.WEI_PRECISION, poolValueInfo.poolValue, supply);
+        return (marketTokenPrice, poolValueInfo);
     }
 
     // @dev get the total supply of the marketToken
@@ -2073,7 +2074,7 @@ library MarketUtils {
 
         uint256 totalBorrowing = getTotalBorrowing(dataStore, market.marketToken, isLong);
 
-        return (openInterest * nextCumulativeBorrowingFactor) / Precision.FLOAT_PRECISION - totalBorrowing;
+        return Precision.applyFactor(openInterest, nextCumulativeBorrowingFactor) - totalBorrowing;
     }
 
     // @dev get the total borrowing value
@@ -2122,7 +2123,7 @@ library MarketUtils {
         }
 
         // round market tokens down
-        return supply * usdValue / poolValue;
+        return Precision.mulDiv(supply, usdValue, poolValue);
     }
 
     // @dev convert a number of market tokens to its USD value
@@ -2137,7 +2138,7 @@ library MarketUtils {
     ) internal pure returns (uint256) {
         if (supply == 0) { revert Errors.EmptyMarketTokenSupply(); }
 
-        return marketTokenAmount * poolValue / supply;
+        return Precision.mulDiv(poolValue, marketTokenAmount, supply);
     }
 
     // @dev validate that the specified market exists and is enabled
```

### contracts/oracle/Oracle.sol
```diff
@@ -543,7 +543,7 @@ contract Oracle is RoleModule {
         uint256 price = SafeCast.toUint256(_price);
         uint256 precision = getPriceFeedMultiplier(dataStore, token);
 
-        uint256 adjustedPrice = price * precision / Precision.FLOAT_PRECISION;
+        uint256 adjustedPrice = Precision.mulDiv(price, precision, Precision.FLOAT_PRECISION);
 
         return (true, adjustedPrice);
     }
```

### contracts/position/DecreasePositionUtils.sol
```diff
@@ -107,7 +107,7 @@ library DecreasePositionUtils {
                 params.position.sizeInUsd()
             );
 
-            cache.estimatedRealizedPnlUsd = cache.estimatedPositionPnlUsd * params.order.sizeDeltaUsd().toInt256() / params.position.sizeInUsd().toInt256();
+            cache.estimatedRealizedPnlUsd = Precision.mulDiv(cache.estimatedPositionPnlUsd, params.order.sizeDeltaUsd(), params.position.sizeInUsd());
             cache.estimatedRemainingPnlUsd = cache.estimatedPositionPnlUsd - cache.estimatedRealizedPnlUsd;
 
             PositionUtils.WillPositionCollateralBeSufficientValues memory positionValues = PositionUtils.WillPositionCollateralBeSufficientValues(
```

### contracts/position/PositionUtils.sol
```diff
@@ -215,7 +215,7 @@ library PositionUtils {
             }
         }
 
-        cache.positionPnlUsd = cache.totalPositionPnl * cache.sizeDeltaInTokens.toInt256() / position.sizeInTokens().toInt256();
+        cache.positionPnlUsd = Precision.mulDiv(cache.totalPositionPnl, cache.sizeDeltaInTokens, position.sizeInTokens());
 
         return (cache.positionPnlUsd, cache.sizeDeltaInTokens);
     }
```

### contracts/utils/Precision.sol
```diff
@@ -60,6 +60,10 @@ library Precision {
         return Math.mulDiv(value, numerator, denominator);
     }
 
+    function mulDiv(int256 value, uint256 numerator, uint256 denominator) internal pure returns (int256) {
+        return mulDiv(numerator, value, denominator);
+    }
+
     function mulDiv(uint256 value, int256 numerator, uint256 denominator) internal pure returns (int256) {
         uint256 result = mulDiv(value, numerator.abs(), denominator);
         return numerator > 0 ? result.toInt256() : -result.toInt256();
```
