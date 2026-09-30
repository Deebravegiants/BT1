# [?] Numeric bound testing cases where the Numeric under/overflow by 1 and by a lot. (#21326)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2025-06-10
Source: https://github.com/digital-asset/daml/commit/4316608447c0426aefa39cb81b14cd3cd317cb6c
Type: security-commit

## Details
Numeric bound testing cases where the Numeric under/overflow by 1 and by a lot. (#21326)

## Patch
### sdk/compiler/damlc/tests/daml-test-files/HexString.daml
```diff
@@ -54,6 +54,22 @@ n7 = 0.12345_67
 n10: Numeric 10
 n10 = 0.12345_67890
 
+-- Following values represent the hex for `minBound (@Numeric n)`, but with a digit modified to simulate underflow by subtracting 1
+
+hexMinM1_0: BytesHex
+hexMinM1_0 = "2d393939393939393939393939393939393939393939393939393939393939393939393939393a2e30"
+
+hexMinM1_37: BytesHex
+hexMinM1_37 = "2d3a2e39393939393939393939393939393939393939393939393939393939393939393939393939"
+
+-- Following values represent the hex for `maxBound (@Numeric n)`, but with a digit modified to simulate overflow by adding 1
+
+hexMaxP1_0: BytesHex
+hexMaxP1_0 = "393939393939393939393939393939393939393939393939393939393939393939393939393a2e30"
+
+hexMaxP1_37: BytesHex
+hexMaxP1_37 = "3a2e39393939393939393939393939393939393939393939393939393939393939393939393939"
+
 main =
   script do
     -- `HasToHex Int` and `HasFromHex Int`
@@ -146,6 +162,10 @@ main =
     numericViaStringFromHex "302e31323334353637" === (None: Optional (Numeric 3))
     numericViaStringFromHex "302e313233343536373839" === (None: Optional (Numeric 3))
     numericViaStringFromHex "302e313233343536373839" === (None: Optional (Numeric 7))
+    numericViaStringFromHex hexMinM1_0 === (None: Optional (Numeric 0))
+    numericViaStringFromHex hexMinM1_37 === (None: Optional (Numeric 37))
+    numericViaStringFromHex hexMaxP1_0 === (None: Optional (Numeric 0))
+    numericViaStringFromHex hexMaxP1_37 === (None: Optional (Numeric 37))
 
     -- byteCount
     byteCount "" === 0
```
