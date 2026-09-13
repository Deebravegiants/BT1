# [M] liquidate() Inexistent Slippage Protection

## Summary
Severity: Medium
Reporter: bin2chen
Source: https://github.com/sherlock-audit/2023-02-surge/blob/main/surge-protocol-v1/src/Pool.sol#L553
Type: audit-issue

## Details
# liquidate() Inexistent Slippage Protection

## Summary
liquidate() Inexistent Slippage Protection

## Vulnerability Detail
liquidate() Inexistent Slippage Protection
The code is as follows:
```solidity
    function liquidate(address borrower, uint amount) external {  //<------without like minCollateralReward
        uint _loanTokenBalance = LOAN_TOKEN.balanceOf(address(this));
        (address _feeRecipient, uint _feeMantissa) = FACTORY.getFee();
        (  
.....
```
But Slippage is existent
1. Interest becomes higher as time over

In this case, the user may pay for the LoanToken but get less collateral than expected

## Impact

get less collateral than expected

## Code Snippet
https://github.com/sherlock-audit/2023-02-surge/blob/main/surge-protocol-v1/src/Pool.sol#L553
## Tool used

Manual Review

## Recommendation
Suggest adding ```minCollateralReward```
