# [?] fix: refresh quote will cause crash (#3892)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2026-07-10
Source: https://github.com/RabbyHub/Rabby/commit/4f6d13e661ec0ed9a74babfa19fade7a353bf8aa
Type: security-commit

## Details
fix: refresh quote will cause crash (#3892)

* fix: refresh quote will cause crash

* chore: remove console

## Patch
### src/ui/views/Swap/Component/Quotes.tsx
```diff
@@ -84,10 +84,9 @@ export const Quotes = ({
             (bestQuote?.data?.toTokenDecimals || other.receiveToken.decimals)
         )
         .toString() || '0';
-
     return [
       inSufficient
-        ? new BigNumber(bestQuote.data?.toTokenAmount || 0)
+        ? new BigNumber(bestQuote?.data?.toTokenAmount || 0)
             .div(
               10 **
                 (bestQuote?.data?.toTokenDecimals ||
@@ -96,7 +95,7 @@ export const Quotes = ({
             )
             .toString(10)
         : receiveTokenAmount,
-      bestQuote?.isDex ? bestQuote.preExecResult?.gasUsdValue || '0' : '0',
+      bestQuote?.isDex ? bestQuote?.preExecResult?.gasUsdValue || '0' : '0',
     ];
   }, [inSufficient, other?.receiveToken, sortedList]);
 
```
