# [M] 5.26 TypecheckFailure When Using Address and

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Self Members as Struct Field Name

```
Correctness Low Version 1
CS-VYPER_MAY_2023-025
```
Accessing the field of an enum named after an address or self member (balance, codesize,
is_contract, codehash or code) results in a TypeCheckFailure.

For example, the following contract fails to compile due to
TypeCheckFailure: Attribute node did not produce IR.


```
struct User:
balance:uint256
```
```
@external
def foo():
a:User = User({balance:12})
b:uint256 = a.balance
```
