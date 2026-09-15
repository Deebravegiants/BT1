# [M] \[M11\] Missing docstrings

## Summary
Severity: Medium
Source: https://github.com/holdefi/Holdefi/tree/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts
Type: audit-issue

## Details
All the contracts and functions in the [Holdefi’s codebase](https://github.com/holdefi/Holdefi/tree/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts) lack documentation. This hinders reviewers’ understanding of the code’s intention, which is fundamental to correctly assess not only security, but also correctness.

Additionally, docstrings improve readability and ease maintenance. They should explicitly explain the purpose or intention of the functions, the scenarios under which they can fail, the roles allowed to call them, the values returned, and the events emitted.

Consider thoroughly documenting all functions (and their parameters) that are part of the contracts’ public API. Functions implementing sensitive functionality, even if those are not public, should be clearly documented as well. When writing docstrings, consider following the [Ethereum Natural Specification Format (NatSpec)](https://solidity.readthedocs.io/en/develop/natspec-format.html).

**Update**: _Not fixed. Holdefi’s statement for this issue:_

> This is not a bug. This is just a suggestion

[< Previous](#high) [next >](#low)
