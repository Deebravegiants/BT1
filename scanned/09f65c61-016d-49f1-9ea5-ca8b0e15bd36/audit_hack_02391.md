# [M] Missing docstrings

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
All the contracts and functions in Arro’s code base lack proper documentation. This hinders reviewers’ understanding of the code’s intention, which is fundamental to correctly assess not only security, but also correctness. Additionally, docstrings improve readability and ease maintenance. They should explicitly explain the purpose or intention of the functions, the scenarios under which they can fail, the roles allowed to call them, the values returned and the events emitted.

Consider thoroughly documenting all functions (and their parameters) that are part of the contracts’ public API. Functions implementing sensitive functionality, even if not public, should be clearly documented as well. When writing docstrings, consider following the [Ethereum Natural Specification Format](https://solidity.readthedocs.io/en/v0.5.15/natspec-format.html) (NatSpec).

_**Update:** Partially fixed in [pull request #1](https://github.com/pjsimpkins/ArroERC20Code/pull/1). Arro’s statement for this issue:_

> The project structure has been changed to rely heavily on the OpenZeppelin ERC20 implementation. This provides a well-documented base of most of the contract functionality. The rest of the structure of the documentation has been changed to follow a consistent structure but will be updated in the future to follow the Ethereum Natural Specification Format (NatSpec).
