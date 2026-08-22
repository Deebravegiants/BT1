# [M] [ADRIRO-NEW-M-01] Manager authorization in VotiumStrategy still leaves room for unprotected access

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/51
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L95


# Vulnerability details

## Summary

Access control has been added to the VotiumStrategy contract with the intention of restricting functionality only to AfEth. However, an error in the implementation still leaves the contract publicly accessible.

## Impact

In the updated codebase, the sponsor has introduced access control to the VotiumStrategy contract. This authorization is implemented in the `onlyManager` modifier:

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L95-L99

```solidity
95:     modifier onlyManager() {
96:         if (address(manager) != address(0) && msg.sender != manager)
97:             revert NotManager();
98:         _;
99:     }
```

As we can see in line 96, the check is only executed if `manager` is different from `address(0)`. If this is not the case, then the check is not enforced and the revert in line 97 can never be triggered. This means that when `manager == address(0)` access is still granted for any caller.

This modifier has been added to `depositRewards()`, `deposit()`, `requestWithdraw()` and `withdraw()`, which means that potentially all these functions can still be publicly accessible.

This is particularly relevant in relation to issue [M-07](https://github.com/code-423n4/2023-09-asymmetry-findings/issues/38) of the original report, as access control was introduced to mitigate this issue.

Note, additionally, that the current issue potentially affects [H-05](https://github.com/code-423n4/2023-09-asymmetry-findings/issues/23), since `depositRewards()` could still be publicly accessible and be used to purchase CVX with an arbitrary value for the `_cvxMinout` slippage parameter.

## Recommendation

Remove the condition to allow access if `manager` is `address(0)`. Additionally, check that `manager` is correctly initialized in `initialize()`.

```diff
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/51_
