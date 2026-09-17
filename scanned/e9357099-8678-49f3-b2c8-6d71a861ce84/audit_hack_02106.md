# [M] 5.9 Compiler Panics When Overflowing the

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Memory

```
Design Low Version 1
CS-VYPER_SEPTEMBER_2023-
```
Given some expression that overflows the memory, the compiler panics instead of exiting with some
custom error.

For example, compiling the following contract results in
vyper.exceptions.CompilerPanic: out of range.

```
@external
def bar():
s:String[max_value(uint256)] = "a"
```
