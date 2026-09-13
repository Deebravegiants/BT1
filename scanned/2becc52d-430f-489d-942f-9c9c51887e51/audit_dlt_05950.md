# [?] Merge pull request from GHSA-4v9q-cgpw-cf38

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-06-06
Source: https://github.com/vyperlang/vyper/commit/6b4d8ff185de071252feaa1c319712b2d6577f8d
Type: security-commit

## Details
Merge pull request from GHSA-4v9q-cgpw-cf38

in external call codegen, when `extcodesize` is called on the target
address, the IR for evaluating the target address can be evaluated
twice. this can result in any side effects (embedded in the evaluation
of the target address) being executed twice.
