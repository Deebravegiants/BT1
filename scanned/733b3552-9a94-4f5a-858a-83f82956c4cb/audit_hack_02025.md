# [M] 6.6 Contracts Implement Proxy Pattern

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

All adapters and the YearnPriceFeed contract inherit from OpenZeppelin's abstract Proxy contract and
implement an _implementation function pointing to the address of the 3rd party system contract the
adapter connects to. However, this proxy functionality is not needed nor used. The intended functionality
of the adapter is implemented in functions inside the adapter contract itself.

Inheriting the proxy contract, however, has serious consequences. Calls to non-existing functions in the
contract execute the fallback function, which is implemented by the inherited proxy. This function
forwards the call by delegate-calling into the implementation contract. During a delegate-call, the code at
the target is executed in the context of the caller. Notably, it is read from and written to the storage of the
caller, the adapter contract. This can have an adverse effect on the stored variables of the adapter
contract. For example the stored values for the creditManager or the creditFilter.

Code corrected:

The adapter contracts were rewritten and the proxy pattern was removed.
