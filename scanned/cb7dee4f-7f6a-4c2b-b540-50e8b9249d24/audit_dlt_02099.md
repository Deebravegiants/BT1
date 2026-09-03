# [?] Merge pull request from GHSA-j2x6-9323-fp7h

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-04-13
Source: https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b
Type: security-commit

## Details
Merge pull request from GHSA-j2x6-9323-fp7h

This commit addresses two issues in validating returndata, both related
to the inferred type of the external call return.

First, it addresses an issue with interfaces imported from JSON. The
JSON_ABI encoding type was added in 0.3.0 as part of the calling
convention refactor to mimic the old code's behavior when the signature
of a function had `is_from_json` toggled to True. However, both
implementations were a workaround for the fact that in
FunctionSignatures from JSON with Bytes return types, length is set to 1
as a hack to ensure they always typecheck - almost always resulting in a
runtime revert.

This commit removes the JSON_ABI encoding type, so that dynamic
returndata from an interface defined with .json ABI file cannot result
in a buffer overrun(!). To avoid the issue with always runtime
reverting, codegen uses the uses the inferred ContractFunction type of
the Call.func member (which is both more accurate than the inferred type
of the Call expression, and the return type on the FunctionSignature!)
to calculate the length of the external Bytes array.

Second, this commit addresses an issue with validating call returns in
complex expressions. In the following examples, the type of the call
return is either inferred incorrectly or it takes a path through codegen
which avoids generating runtime clamps:

```
interface Foo:
    def returns_int128() -> int128: view
    def returns_Bytes3() -> Bytes[3]: view

foo: Foo
...
x: uint256 = convert(self.foo.returns_int128(), uint256)
y: Bytes[32] = concat(self.foo.returns_Bytes3(), b"")
```


_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b_
