# [?] Fix overflow of ExpiryUtilsLib

## Summary
Severity: Unknown
Chain: Pendle
Component: pendle-finance/pendle-core-v2-public
Published: 2022-04-07
Source: https://github.com/pendle-finance/pendle-core-v2-public/commit/ff717764d6e38fa828865ab10129366c3f9090b1
Type: security-commit

## Details
Fix overflow of ExpiryUtilsLib

## Patch
### contracts/libraries/helpers/ExpiryUtilsLib.sol
```diff
@@ -157,7 +157,8 @@ library ExpiryUtils {
         bytes memory bstr = new bytes(len);
         uint256 k = len - 1;
         while (_i != 0) {
-            bstr[k--] = bytes1(uint8(48 + (_i % 10)));
+            bstr[k] = bytes1(uint8(48 + (_i % 10)));
+            if (k != 0) k--;
             _i /= 10;
         }
         return string(bstr);
```
