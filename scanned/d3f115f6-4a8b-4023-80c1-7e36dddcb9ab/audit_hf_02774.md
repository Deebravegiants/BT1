# [M] Possible Theft Of Contract Balance Due To Lack Of Access Control

## Summary
Severity: Medium
Contest weight: 0.3977
Dataset id: 15168
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The
executeAndTransfer() function allows the caller to execute a
call, then transfer the contract's native token
balance as well as the balance of a token of their choosing to an address specified by the caller.
```solidity
function executeAndTransfer(address token, address to, address target, bytes calldata data) external payable {
    (bool success,) = target.call{ value: msg.value }(data);
    if (!success) revert CallFailed();
    if (token == address(0)) SafeTransferLib.safeTransferAllETH(to);
    else token.safeTransferAll(to);
}
```
However, this function has no access control. This means that anyone is able to invoke it and wipe the contract's
balance in the process. Since the contract has both a receive() and fallback() function, it is assumed that it is
expected to hold value at some point in time.

## Recommendation
Implement access control on the function by limiting the addresses that are able to invoke it.
