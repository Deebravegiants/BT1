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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1336_
