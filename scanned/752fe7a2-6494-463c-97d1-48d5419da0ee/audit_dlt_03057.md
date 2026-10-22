# [M] token mights stuck in MagnetarMarketModule contract if the asset doesn't support cross-chain operation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1336
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L677-L732


# Vulnerability details

## Impact
token mights stuck in MagnetarMarketModule contract if the asset doesn't support cross-chain operation

## Proof of Concept
[MagnetarMarketModule._withdrawToChain] will check if the asset supports a cross chain operation in [L703-L709](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L703-L709), if the asset doesn't support, the function will return.

Taking one of the `_withdrawToChain` callers [MagnetarMarketModule.depositRepayAndRemoveCollateralFromMarket](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L70-L88) as an example:
While `MagnetarMarketModule.depositRepayAndRemoveCollateralFromMarket` is called, the function will call `MagnetarMarketModule._depositRepayAndRemoveCollateralFromMarket`, supposed everything goes well, the control flow will fall into [L258-L289](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L258-L289).
Suppose  `collateralAmount` in [L258](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L258C13-L258C29) is **not zero**, and [withdrawCollateralParams.withdraw](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L259-L260) is **true**, in such case, `collateralWithdrawReceiver` will be `address(this)`. After calling [marketInterface.removeCollateral](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L268-L272), `address(this)` which is `MagnetarMarketModule` contract will own the asset.
Since `withdrawCollateralParams.withdraw` is **true**, [MagnetarMarketModule._withdrawToChain](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L276C17-L287) will be called.
```solidity
212     function _depositRepayAndRemoveCollateralFromMarket(
213         address market,
214         address user,
215         uint256 depositAmount,
216         uint256 repayAmount,
217         uint256 collateralAmount,
218         bool extractFromSender,
219         ICommonData.IWithdrawParams calldata withdrawCollateralParams
220     ) private {

            ...

256         // performs a removeCollateral operation on the market
257         // if `withdrawCollateralParams.withdraw` it uses `withdrawTo` to withdraw collateral on the same chain or to another one
258         if (collateralAmount > 0) {
259             address collateralWithdrawReceiver = withdrawCollateralParams
260                 .withdraw
261                 ? address(this)
262                 : user;
263             uint256 collateralShare = yieldBox.toShare(
264                 marketInterface.collateralId(),
265                 collateralAmount,
266                 false
267             );
268             marketInterface.removeCollateral(
269                 user,
270                 collateralWithdrawReceiver,
271                 collateralShare
272             );
273 
274             //withdraw
275             if (withdrawCollateralParams.withdraw) {
276                 _withdrawToChain(
277                     yieldBox,
278                     collateralWithdrawReceiver,
279                     marketInterface.collateralId(),
280                     withdrawCollateralParams.withdrawLzChainId,
281                     LzLib.addressToBytes32(user),
282                     collateralAmount,
283                     collateralShare,
284                     withdrawCollateralParams.withdrawAdapterParams,
285                     payable(this),
286                     address(this).balance
287                 );
288             }
289         }
290     }
```

In [L703-L709](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L703-L709), the function will return which leaves the asset in the `MagnetarMarketModule `contract
```solidity
677     function _withdrawToChain(
678         IYieldBoxBase yieldBox,
679         address from,
680         uint256 assetId,
681         uint16 dstChainId,
682         bytes32 receiver,
683         uint256 amount,
684         uint256 share,
685         bytes memory adapterParams,
686         address payable refundAddress,
687         uint256 gas
688     ) private {
        ...
702         // make sure the asset supports a cross chain operation
703         try
704             IERC165(address(asset)).supportsInterface(
705                 type(ISendFrom).interfaceId
706             )
707         {} catch {
708             return;        <---------------- here
709         }
710
    ...
```

## Tools Used
VS
## Recommended Mitigation Steps
If the asset doesn't support cross-chain, maybe we can perform a withdraw as [L690-L699](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L690-L699)
```diff
--- MagnetarMarketModule.sol	2023-08-04 17:22:52.272395098 +0800
+++ MagnetarMarketModule_new.sol	2023-08-04 17:34:57.230800699 +0800
@@ -705,6 +705,13 @@
                 type(ISendFrom).interfaceId
             )
         {} catch {
+            yieldBox.withdraw(
+                assetId,
+                from,
+                LzLib.bytes32ToAddress(receiver),
+                amount,
+                share
+            );
             return;
         }
```


## Assessed type

Other
