# [M] Underflow/Truncation in internal `OptionMath.ceil64x64()` library function when input is `169710045478127874867200000000000000002` or higher.

## Summary
Severity: Medium
Reporter: shung
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/libraries/OptionMath.sol#L47-L51
Type: audit-issue

## Details
# Underflow/Truncation in internal `OptionMath.ceil64x64()` library function when input is `169710045478127874867200000000000000002` or higher.

## Summary

Underflow/Truncation in internal `OptionMath.ceil64x64()` library function when input is `169710045478127874867200000000000000002` or higher.

## Vulnerability Detail

To replicate make `OptionMath.ceil64x64()` function public and deploy `OptionMath.sol` on Remix. Execute the function with `OptionMath.ceil64x64(169710045478127874867200000000000000002)`. The output will underflow and return a negative value `-168727647035439633434574607431768211456`. This invalid value will be stored as the strike price parameter.

## Impact

When the strike price is sufficiently high, it will overflow and be stored as a negative value. This can disrupt the auction process and might lead to exploits.

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/libraries/OptionMath.sol#L47-L51

## Tool used

Manual Review

## Recommendation

To prevent truncation, ensure `integer` fits 128 bits before doing the type casting.

```diff
diff --git a/knox-contracts/contracts/libraries/OptionMath.sol b/knox-contracts/contracts/libraries/OptionMath.sol
index 746dd78..797ddaa 100644
--- a/knox-contracts/contracts/libraries/OptionMath.sol
+++ b/knox-contracts/contracts/libraries/OptionMath.sol
@@ -44,11 +44,10 @@ library OptionMath {
             return int128((integer << 64) / ONE);
         }
 
-        return
-            int128(
-                (((values[0].ruler * values[0].value) +
-                    (values[1].ruler * (values[1].value + 1))) << 64) / ONE
-            );
+        integer = (((values[0].ruler * values[0].value) +
+            (values[1].ruler * (values[1].value + 1))) << 64) / ONE;
+        require(integer <= type(int128).max);
+        return int128(integer);
     }
 
     /**
```
