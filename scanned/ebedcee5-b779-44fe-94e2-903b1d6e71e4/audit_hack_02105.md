# [M] 5.2 Assertion Error _abi_encode With Invalid

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Method ID

```
Design Low Version 1
CS-VYPER_DECEMBER_2023-
```
If _abi_encode is given a literal method ID that is not 4 bytes long, the compiler will fail on an assertion
in _parse_method_id during code generation instead of failing at type-checking time with some
meaningful error message.

The following contract would fail to compile with an AssertionError:

```
@external
def foo():
a:Bytes[68] = _abi_encode(b'', method_id=b'')
```
