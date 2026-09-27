# [M] \[M04\] Missing docstrings and comments

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Most of the contracts and functions in the audited code base lack documentation. This hinders reviewers’ understanding of the code’s intention, which is fundamental to correctly assess not only security, but also correctness. Additionally, docstrings improve readability and ease maintenance. They should explicitly explain the purpose or intention of the functions, the scenarios under which they can fail, the roles allowed to call them, the values returned and the events emitted.

Consider thoroughly documenting all functions (and their parameters) that are part of the contracts’ public API. Functions implementing sensitive functionality, even if not public, should be clearly documented as well. When writing docstrings, consider following the [Ethereum Natural Specification Format](https://solidity.readthedocs.io/en/develop/natspec-format.html) (NatSpec).

Additionally, the OpenZeppelin team found a notable lack of comments throughout the audited code. Well-commented code not only improves audit speed and depth, but it also helps to reveal what developer intentions may be and thus helps identify issues of misalignment between intention and implementation. Without comments, identifying issues in the code is much more difficult. Aside from benefiting auditors, code comments also benefit future developers and users, by clearly defining the functionality of the code and by reducing the risk of bugs.

Consider thoroughly commenting the existing code, and adding regular commenting to the software development process. We specifically recommend commenting every line of assembly code and commenting all complex math operations.

**Update:** _Fixed. Many parts of the codebase have been documented and commented._
