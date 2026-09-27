# [H] 6.6 No Slippage Protection

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

```
Version 1
```
All transactions have a lag between the time they are sent and the time they are executed as they remain
in the mem pool for some time prior to being executed. Between sending and execution, other
transaction might change the contract's state. This is critical for all transaction where the user receives or
has to pay funds. In all action function in the Engine contract except for supply and claim do
not offer any protection against slippage. In VERSION4 this affects allocate, remove, and swap.
Without checking if the transaction is still executed under the desired conditions, the user may suffer
losses.

This issue can be maliciously exploited by front running certain transactions. However, as the system is
designed to interact with smart contracts, the slippage protection could be implemented on their side.

Code corrected

The user is now able to define the delta in and delta out when swapping. Hence, the user either gets the
defined values or the swap will revert due to a violation of the invariant check. The check verifies that the
invariant can only increase.
