# [H] 5.3 StringT Not Handled in HashMap Access

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1


```
CS-VYPER_MARCH_2023-
```
The code generation for index HashMap index should treat in the same way StringT and BytesT. The
condition at line 337 of vyper.codegen.expr only checks isinstance(index.typ, BytesT),
instead of isinstance(index.typ, _BytesArray). BytesLike got incorrectly turned into BytesT
in the context of PR3182. As a consequence, the pointer to a string is used to access a HashMap,
instead of its hash.
