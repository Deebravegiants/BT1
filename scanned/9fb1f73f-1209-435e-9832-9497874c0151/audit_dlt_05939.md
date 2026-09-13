# [?] fix[stdlib]: fix panic in `abi_encode` (#5154)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-07-20
Source: https://github.com/vyperlang/vyper/commit/36b5ad4d9f0134faa7d14e1588de740aff7ff57b
Type: security-commit

## Details
fix[stdlib]: fix panic in `abi_encode` (#5154)

fixes the assumption that the argument of 'ensure_tuple' is always a
literal. this is done by querying the folded value instead of the node
itself. the xfail tests are added to document an issue surrounding
constant folding 'empty', which predates this commit. cleanup: some
comments were converted to docstrings for compiler UX.
