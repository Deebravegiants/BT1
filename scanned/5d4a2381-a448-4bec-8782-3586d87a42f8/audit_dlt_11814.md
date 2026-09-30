# [?] Merge pull request #1894 from crytic/fix-operations-with-overflow-protection

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2023-05-12
Source: https://github.com/crytic/slither/commit/11d5607f83b4be3f6420bd82c6a7ace950f01e64
Type: security-commit

## Details
Merge pull request #1894 from crytic/fix-operations-with-overflow-protection

remove modulo binop from `can_be_checked_for_overflow`

## Patch
### slither/slithir/operations/binary.py
```diff
@@ -94,7 +94,6 @@ def can_be_checked_for_overflow(self) -> bool:
         return self in [
             BinaryType.POWER,
             BinaryType.MULTIPLICATION,
-            BinaryType.MODULO,
             BinaryType.ADDITION,
             BinaryType.SUBTRACTION,
             BinaryType.DIVISION,
```
