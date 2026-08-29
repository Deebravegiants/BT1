# [M] Multihop buying and selling of collateral will fail due to missing gas payment

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1264
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/BaseTOFT.sol#L156
https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTLeverageModule.sol#L139-L145
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/BaseUSDO.sol#L215
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L123-L130
https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/MagnetarV2.sol#L667


# Vulnerability details


`BaseUSDO.initMultiHopBuy()`and `BaseTOFT.initMultiSell()` are used to trigger multihop buying and selling of collateral from another chain.

However, at the destination chain, these operations will fail due to missing gas payment when calling `Singularity.multiHopBuyCollateral()` and `Singularity.multiHopSellCollateral()` respectively. As both `multiHopBuyCollateral()` and `multiHopSellCollateral()` are cross chain operations, they require gas payment for sending via Layer Zero.

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L123-L130
```Solidity
        //@audit - missing {value: address(this).balance }
        ISingularity(externalData.srcMarket).multiHopBuyCollateral(
            from,
            collateralAmount,
            borrowAmount,
            swapData,
            lzData,
            externalData
        );
```

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTLeverageModule.sol#L139-L145
```Solidity
        //@audit - missing {value: address(this).balance }
        ISingularity(externalData.srcMarket).multiHopSellCollateral(
            from,
            share,
            swapData,
            lzData,
            externalData
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1264_
