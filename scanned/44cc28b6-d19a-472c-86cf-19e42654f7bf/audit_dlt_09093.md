# [?] fix(ethereum): out of bounds check

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-05-05
Source: https://github.com/trezor/trezor-firmware/commit/2c9b35be1b70f5c30d7aa72947877a2ae2b677de
Type: security-commit

## Details
fix(ethereum): out of bounds check

[no changelog]

## Patch
### core/src/apps/ethereum/clear_signing.py
```diff
@@ -445,7 +445,7 @@ def __init__(self, parser: Parser) -> None:
         self.parser = parser
 
     def parse(self, raw_data: memoryview, offset: int) -> tuple[AnyValue, int]:
-        if offset > len(raw_data):
+        if offset + 32 > len(raw_data):
             raise OutOfBounds
         return self.parser(raw_data[offset : offset + 32]), 32
 
```
