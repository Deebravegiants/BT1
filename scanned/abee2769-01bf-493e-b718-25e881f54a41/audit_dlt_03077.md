# [M] BigBang and Singularity should not pause repay() and liquidate()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1169
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L268
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L314
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLBorrow.sol#L50
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L35


# Vulnerability details


BigBang and Singularity have a `updatePaused()` to freeze the market when the specific collateral is deem too risky to allow further borrowing. All borrowing functions will be paused, including `repay()` and `liquidate()`.

However, in that situation, it will be necessary to allow liquidations and repayments as these functions will help reduce the risky collaterals.

Also, it is unfair to the borrowers if they are not allowed to repay their loan as fees are still accruing even when the markets are paused.


https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol
```Solidity
    //@audit - notPaused will freeze repay() when market is paused
    function repay(
        address from,
        address to,
        bool,
        uint256 part
    ) public notPaused allowedBorrow(from, part) returns (uint256 amount) {

    ...
    //@audit - notPaused will freeze liquidate() when market is paused
    function liquidate(
        address[] calldata users,
        uint256[] calldata maxBorrowParts,
        ISwapper swapper,
        bytes calldata collateralToAssetSwapData
    ) external notPaused {
```
## Impact

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1169_
