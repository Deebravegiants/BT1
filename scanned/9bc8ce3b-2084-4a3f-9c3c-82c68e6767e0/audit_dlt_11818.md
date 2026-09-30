# [?] fixing exponent dos by adding limits on size of exponent

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2020-08-28
Source: https://github.com/crytic/slither/commit/246a4baa0e8f5dcc57400127c483b2c10b039c5d
Type: security-commit

## Details
fixing exponent dos by adding limits on size of exponent

## Patch
### slither/slithir/variables/constant.py
```diff
@@ -27,10 +27,16 @@ def __init__(self, val, type=None, subdenomination=None):
                 else:
                     if 'e' in val:
                         base, expo = val.split('e')
-                        self._val = int(Decimal(base) * (10 ** int(expo)))
+                        expo = int(expo)
+                        if expo > 80:
+                            raise ValueError("exponent is too large to fit in any Solidity integer size")
+                        self._val = int(Decimal(base) * (10 ** expo))
                     elif 'E' in val:
                         base, expo = val.split('E')
-                        self._val = int(Decimal(base) * (10 ** int(expo)))
+                        expo = int(expo)
+                        if expo > 80:
+                            raise ValueError("exponent is too large to fit in any Solidity integer size")
+                        self._val = int(Decimal(base) * (10 ** expo)) 
                     else:
                         self._val = int(Decimal(val))
             elif type.type == 'bool':
```
