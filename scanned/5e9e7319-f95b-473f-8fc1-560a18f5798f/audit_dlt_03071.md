# [M] `BaseTOFT.sendToYBAndBorrow()` will fail when withdrawing the borrowed asset to another chain

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1212
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/BaseTOFT.sol#L290
https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTMarketModule.sol#L192-L201
https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/modules/MagnetarMarketModule.sol#L197-L205
https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/modules/MagnetarMarketModule.sol#L751


# Vulnerability details


`BaseTOFT.sendToYBAndBorrow()` is used to send TOFT to a specific chain and perform a borrow operation. It also provides the ability to withdraw the borrowed asset to another chain.

On the destination chain, `BaseTOFT` will call `BaseTOFTMarketModule.borrowInternal()`, which uses the `MagnetarV2.depositAddCollateralAndBorrowFromMarket()` to add collateral and borrow from SGL/BigBang. 

The issue is that it uses `msg.value` instead of `address(this).balance` to send gas to `MagnetarV2.depositAddCollateralAndBorrowFromMarket()`. That is incorrect as `msg.value` will be zero as `borrowInternal()` is triggered by LayerZero contract and not an EOA.

WIth that, `MagnetarV2` contract will receive zero gas value, which will then cause the cross chain withdrawal to fail when performed by `_withdraw()` in `depositAddCollateralAndBorrowFromMarket()`.


https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTMarketModule.sol#L192-L201
```Solidity
    function borrowInternal(
        bytes32 _to,
        ITapiocaOFT.IBorrowParams memory borrowParams,
        ICommonData.IWithdrawParams memory withdrawParams,
        ICommonData.IApproval[] memory approvals
    ) public payable {
        if (approvals.length > 0) {
            _callApproval(approvals);
        }

        // Use market helper to deposit, add collateral to market and withdrawTo
        approve(address(borrowParams.marketHelper), borrowParams.amount);

        //@audit value should be address(this).balance
        IMagnetar(borrowParams.marketHelper)
            .depositAddCollateralAndBorrowFromMarket{value: msg.value}(
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1212_
