# [?] fix(cheatcodes): prevent panic in expectRevert with empty bytes (#13769)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-03-17
Source: https://github.com/foundry-rs/foundry/commit/dbcdd6d23d62c5062d3875ccdb9a278d95c6bb83
Type: security-commit

## Details
fix(cheatcodes): prevent panic in expectRevert with empty bytes (#13769)

* fix(cheatcodes): prevent panic in expectRevert with empty bytes

When vm.expectRevert(bytes('')) catches a revert with non-empty data,
decode_error in alloy-dyn-abi panics on the empty expected_reason
(slice index out of range). Guard the decode_error call with a
length check.

Closes #13766

Co-Authored-By: zerosnacks <95942363+zerosnacks@users.noreply.github.com>

* test: add regression test for expectRevert empty bytes panic

Co-Authored-By: zerosnacks <95942363+zerosnacks@users.noreply.github.com>

* test: fix snapshot for expectRevert empty bytes regression test

Co-Authored-By: zerosnacks <95942363+zerosnacks@users.noreply.github.com>

---------

Co-authored-by: zerosnacks <95942363+zerosnacks@users.noreply.github.com>
