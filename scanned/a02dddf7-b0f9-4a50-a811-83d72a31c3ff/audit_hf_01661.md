# [H] Missing payable function

## Summary
Severity: High
Contest weight: 0.5399
Dataset id: 9002
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_call() could send native token via .call{ value: _callRequest.value }, however, none of the contracts can receive native token, including Main.sol, PreauthorizedCalls.sol, SessionCalls.sol, Calls.sol, Controllers.sol.
File: contracts\modules\Calls\Calls.sol
```solidity
80: function _call
(CallsStructs.CallRequest calldata _callRequest) internal returns (bytes memory) {
81: (
bool success,
bytes memory result
) = _callRequest.target.call{ value: _callRequest.value }(_callRequest.data
```

## Recommendation
Add payable modifier to the related functions
Add receive() function
