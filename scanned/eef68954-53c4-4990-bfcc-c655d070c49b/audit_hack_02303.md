# [M] \[M09\] Variables are not initialized

## Summary
Severity: Medium
Source: https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/NoteERC20.sol#L11
Type: audit-issue

## Details
In the [NoteERC20 contract](https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/NoteERC20.sol#L11) a [for statement is used](https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/NoteERC20.sol#L92) to distribute the grant tokens between all the initial accounts.

However, the index `i` used to cycle among all the elements is not initialized with zero and its default value is used instead. Relying on the default value of a variable is not a recommended and secure methodology to perform due to the unexpected effects that may occur when this is not true, whether it is the result of a compilation bug or the outcome of a security issue.

Similarly, during the contract [initialization](https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/NoteERC20.sol#L83), the [totalGrants variable](https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/NoteERC20.sol#L91) is used as a counter for all the distributed grant tokens but it is not initialized with a zero value before its usage.

Consider initializing all variables, specially indexes and counters, that will use their initial value during operation.

_**Update:** Fixed in [pull request 23](https://github.com/notional-finance/contracts-v2/pull/23/files)._
