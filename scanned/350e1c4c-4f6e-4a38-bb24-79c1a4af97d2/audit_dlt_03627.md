# [M] [ADRIRO-NEW-H-03] Invalid operation in `withdrawStuckTokens()` will break CVX balance tracking in VotiumStrategy

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/49
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L236


# Vulnerability details

## Summary

The updated code for `withdrawStuckTokens()` contains an update to the `trackedCvxBalance` variable that will break CVX accounting in the VotiumStrategy contract, leading to multiple severe consequences.

## Impact

To mitigate a potential withdrawal of CVX tokens using `withdrawStuckTokens()`, the sponsor has updated the implementation to handle the special case of CVX.

https://github.com/asymmetryfinance/afeth/blob/fe543431677df8273cbb7d2c92f1253956f633bc/contracts/strategies/votium/VotiumStrategyCore.sol#L231-L240

```solidity
236:     function withdrawStuckTokens(address _token) public onlyOwner {
237:         uint256 tokenBalance = IERC20(_token).balanceOf(address(this));
238:         if (_token == CVX_ADDRESS) {
239:             if (tokenBalance <= trackedCvxBalance) revert InvalidAmount();
240:             tokenBalance -= trackedCvxBalance;
241:         }
242: 
243:         IERC20(_token).safeTransfer(msg.sender, tokenBalance);
244:         if (_token == CVX_ADDRESS) trackedCvxBalance -= tokenBalance;
245:     }
```

As we can see in the previous snippet of code, lines 238-241 handle the special case of CVX by subtracting the `trackedCvxBalance` (CVX owned by the protocol depositors) amount to the `tokenBalance` amount, to just remove the excess of CVX and avoid withdrawing protocol owned funds.

However, line 244 updates the `trackedCvxBalance` by subtracting the `tokenBalance` amount. This is wrong, as it is updating the tracked CVX balance by subtracting the excess of tokens.

This will completely break the internal CVX accounting, which tracks user deposits in VotiumStrategy. This is a core variable of the contract, which has impact in different places:

- It is used to calculate `cvxInSystem()`, which also affects `cvxPerVotium()` **that is used to calculate deposits, withdrawals, and the price itself of vAfEth**.
- The tracked balance is also used in `requestWithdraw()`, to calculate the withdrawal epoch based on the requested withdrawal amount.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/49_
