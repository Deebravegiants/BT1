# [?] fix: decimal overflow check

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-04-12
Source: https://github.com/vyperlang/vyper/commit/d5b309e7f40f5cbb6179ad0ecd0020595d9f4073
Type: security-commit

## Details
fix: decimal overflow check

## Patch
### vyper/ast/nodes.py
```diff
@@ -755,7 +755,10 @@ def to_dict(self):
     def validate(self):
         if self.value.as_tuple().exponent < -MAX_DECIMAL_PLACES:
             raise InvalidLiteral("Vyper supports a maximum of ten decimal points", self)
-        super().validate()
+        if self.value < SizeLimits.MIN_INT128:
+            raise OverflowException("Value is below lower bound for decimal types", self)
+        if self.value > SizeLimits.MAX_INT128:
+            raise OverflowException("Value exceeds upper bound for decimal types", self)
 
 
 class Hex(Constant):
```
