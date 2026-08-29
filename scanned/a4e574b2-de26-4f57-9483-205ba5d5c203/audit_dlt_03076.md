# [M] Incorrect refund address for `BaseTOFT.retrieveFromStrategy()` prevents gas refund to user

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1174
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTStrategyModule.sol#L222


# Vulnerability details


`BaseTOFT.retrieveFromStrategy()` requires user to provide gas for the cross chain call to withdraw TOFT from YieldBox strategy. 

However, at the destination chain, `BaseTOFTStrategyModule.strategyWithdraw()` incorrectly sets the refund address to be `payable(this)` instead of user provide adddress. That means any excess gas are refunded to the contract and is not returned back to the user.

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/modules/BaseTOFTStrategyModule.sol#L206
```Solidity
    function strategyWithdraw(
        ...

        //@audit refund address is incorrectly set to payable(this)
        _lzSend(
            _srcChainId,
            lzSendBackPayload,
            payable(this),
            _zroPaymentAddress,
            "",
            address(this).balance
        );

```

## Impact
`BaseTOFT.retrieveFromStrategy()` will not refund gas to the user.


## Recommended Mitigation Steps
Allow user to pass in a refund address for receiving the un-used gas.




_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1174_
