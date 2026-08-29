# [?] fix[codegen]: relax the filter for augassign oob check (#4497)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2025-02-27
Source: https://github.com/vyperlang/vyper/commit/b11775676e466c1cd1488f2565806c0f4c0b2076
Type: security-commit

## Details
fix[codegen]: relax the filter for augassign oob check (#4497)

this commit relaxes the filter introduced in dd5a3d9e0f1e8685. the
filter was valid, but blocked too many user programs. this commit
updates the filter so that the external call check is only applied if
there is a state variable on the lhs. it also updates the external call
check to only consider state-modifying calls, since staticcalls cannot
modify the lhs.

---------

Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>
