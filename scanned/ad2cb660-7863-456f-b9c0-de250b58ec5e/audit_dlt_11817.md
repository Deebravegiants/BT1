# [?] Merge branch 'laudiacay-fix-exponent-dos' into dev

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2020-08-31
Source: https://github.com/crytic/slither/commit/2452037f8e83058c6118426c433530e3029a9ace
Type: security-commit

## Details
Merge branch 'laudiacay-fix-exponent-dos' into dev

## Patch
### README.md
```diff
@@ -123,7 +123,7 @@ See the [Printer documentation](https://github.com/crytic/slither/wiki/Printer-d
 - `slither-check-upgradeability`: [Review `delegatecall`-based upgradeability](https://github.com/crytic/slither/wiki/Upgradeability-Checks)
 - `slither-prop`: [Automatic unit tests and properties generation](https://github.com/crytic/slither/wiki/Properties-generation)
 - `slither-flat`: [Flatten a codebase](https://github.com/crytic/slither/wiki/Contract-Flattening)
-- `slither-erc`: [Check the ERC's conformance](https://github.com/crytic/slither/wiki/ERC-Conformance)
+- `slither-check-erc`: [Check the ERC's conformance](https://github.com/crytic/slither/wiki/ERC-Conformance)
 - `slither-format`: [Automatic patches generation](https://github.com/crytic/slither/wiki/Slither-format)
 
 See the [Tool documentation](https://github.com/crytic/slither/wiki/Tool-Documentation) for additional tools.
```

### slither/slithir/variables/constant.py
```diff
@@ -4,6 +4,8 @@
 from .variable import SlithIRVariable
 from slither.core.solidity_types.elementary_type import ElementaryType, Int, Uint
 from slither.utils.arithmetic import convert_subdenomination
+from ..exceptions import SlithIRError
+
 
 @total_ordering
 class Constant(SlithIRVariable):
@@ -25,12 +27,20 @@ def __init__(self, val, type=None, subdenomination=None):
                 if val.startswith('0x') or val.startswith('0X'):
                     self._val = int(val, 16)
                 else:
-                    if 'e' in val:
-                        base, expo = val.split('e')
-                        self._val = int(Decimal(base) * (10 ** int(expo)))
-                    elif 'E' in val:
-                        base, expo = val.split('E')
-                        self._val = int(Decimal(base) * (10 ** int(expo)))
+                    if 'e' in val or 'E' in val:
+                        base, expo = val.split('e') if 'e' in val else val.split('E')
+                        base, expo = Decimal(base), int(expo)
+                        # The resulting number must be < 2**256-1, otherwise solc
+                        # Would not be able to compile it
+                        # 10**77 is the largest exponent that fits
+                        # See https://github.com/ethereum/solidity/blob/9e61f92bd4d19b430cb8cb26f1c7cf79f1dff380/libsolidity/ast/Types.cpp#L1281-L1290
+                        if expo > 77:
+                            if base != Decimal(0):
+                                raise SlithIRError(f"{base}e{expo} is too large to fit in any Solidity integer size")
+                            else:
+                                self._val = 0
+                        else:
+                            self._val = int(Decimal(base) * Decimal(10 ** expo))
                     else:
                         self._val = int(Decimal(val))
             elif type.type == 'bool':
```

### slither/tools/erc_conformance/__main__.py
```diff
@@ -31,7 +31,7 @@ def parse_args():
     :return: Returns the arguments for the program.
     """
     parser = argparse.ArgumentParser(
-        description="Check the ERC 20 conformance", usage="slither-erc project contractName"
+        description="Check the ERC 20 conformance", usage="slither-check-erc project contractName"
     )
 
     parser.add_argument("project", help="The codebase to be tested.")
```
