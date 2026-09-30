# [M] Incomplete Validation in isAddress()

## Summary
Severity: Medium
Contest weight: 0.0790
Dataset id: 9801
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The isAddress() function in assertions.lua validates the input and returns whether the input is a valid address string. However, there are two issues in the implementation: 1. At assertions.lua#L10, the comparison not type(addr) == "string" should be type(addr) ~= "string" instead since the not operation has higher precedence than ==. 2. At assertions.lua#L12, the regex check should be string.match(addr, "^[A-z0-9_-]+$"), i.e., including the ^ and $ metacharacters, to ensure that all characters are valid.

## Recommendation
Consider implementing the above suggestions.
