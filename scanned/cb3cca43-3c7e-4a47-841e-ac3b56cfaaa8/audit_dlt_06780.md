# [M] Multicall does not work as intended

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-06-size
Published: 2024-07-08
Source: https://github.com/code-423n4/2024-06-size-findings/issues/238
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-06-size/blob/main/src/libraries/Multicall.sol#L29
https://github.com/code-423n4/2024-06-size/blob/main/src/libraries/Multicall.sol#L37


# Vulnerability details

## Overview
The ```multicall(bytes[] calldata _data)``` function in the Size.sol contract does not work as intended. The intention of the ```multicall(bytes[] calldata _data)``` function is to allow users to access multiple functionalities of the Size protocol, such as a (deposit and repay) pair, by a single transaction to Size.sol:

https://github.com/code-423n4/2024-06-size/blob/main/src/Size.sol#L142
```solidity
    function multicall(bytes[] calldata _data)
        public
        payable
        override(IMulticall)
        whenNotPaused
        returns (bytes[] memory results)
    {
        results = state.multicall(_data);
    }
```
The multicall function allows batch processing of multiple interactions with the protocol in a single transaction. This also allows users to take actions that would otherwise be denied due to deposit limits. One of these actions is a (deposit and repay) pair.

Let's say a credit-debt pair exists. Assume that the tenor of the debt is 1 year and the future value is 100ke6 USDC. Let's say the borrower decides to repay the loan just 1 day before the maturity ends. During this 1 year, the total supply of borrowAToken had increased so much that the total supply of borrowAToken was just 10e6 USDC worth below the cap (that is, just below the cap) at the time when the borrower decided to repay the loan. 

To repay a loan, Size requires the user to have sufficient borrowAToken:

https://github.com/code-423n4/2024-06-size/blob/main/src/libraries/actions/Repay.sol#L49
```solidity
    function executeRepay(State storage state, RepayParams calldata params) external {
        DebtPosition storage debtPosition = state.getDebtPosition(params.debtPositionId);

        state.data.borrowAToken.transferFrom(msg.sender, address(this), debtPosition.futureValue);
        debtPosition.liquidityIndexAtRepayment = state.data.borrowAToken.liquidityIndex();
        state.repayDebt(params.debtPositionId, debtPosition.futureValue);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-06-size-findings/issues/238_
