# [H] 6.1 ImmutableProxy Is Unnecessary

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

The ImmutableProxy is designed as a small proxy contract which delegatecalls into a fixed
implementation address. Except for the implementation() getter, its functionality is identical to the
minimal proxy contract described in EIP1167.

OpenZeppelin's Clones library, which is used to deploy clones of the ImmutableProxy contract, deploys
clones by using the contract described in EIP1167 - so it simply deploys a contract which delegatecalls
the target contract. All in all, this means that we have a minimal proxy, which calls the ImmutableProxy,
which then calls the AccountImplementation. This double proxy setup is unnecessary and wastes gas.

Instead, it would be much simpler and cheaper to directly clone the AccountImplementation and discard
the ImmutableProxy contract. The minimal proxy contract is hand-written bytecode which is designed to
be as cheap as possible both to deploy and execute.


Code corrected

The ImmutableProxy contract was removed. Instead, the Clones library is used to directly clone the
AccountImplementation.
