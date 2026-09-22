# [M] `BaseTOFTSTrategyModule.strategyWithdraw()` cross chain call will fail due to missing approvals

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1209
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTStrategyModule.sol#L206


# Vulnerability details


`BaseTOFTStrategyModule.strategyWithdraw()` performs the YieldBox withdrawal on the destination chain. Howwever, it is missing permit approval to allow the withdrawal, causing the withdrawal to revert.


https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/modules/BaseTOFTStrategyModule.sol#L206
```Solidity
    function strategyWithdraw(
        ...

        //@audit missing permit() before withdrawal from YieldBox
        _retrieveFromYieldBox(_assetId, _amount, _share, _from, address(this));

```

## Impact
`BaseTOFT.retrieveFromStrategy()` will fail due to the missing permit approval.


## Recommended Mitigation Steps
Allow user to pass in permit approval calls such as the ones in [BaseTOFTLeverageModule.sol#284](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTLeverageModule.sol#L284)



## Assessed type

DoS
