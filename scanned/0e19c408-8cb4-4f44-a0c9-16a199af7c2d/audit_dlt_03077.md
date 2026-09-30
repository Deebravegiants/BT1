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

With `liquidate()` and `repay()` paused, the situation with the risky collateral will be exacerbated, causing further damage to the users and protocol.

When the pause is activated for an extended period of time, borrowers will not be incentivised to repay their loans if the interest accumulated significantly, thereby worsening the situation with bad debts.

Eventually it could also affect the stability of USDO.


## Proof of Concept
Imagine the following scenario,

1. Collateral X has dropped by 50% within short span of time, and outlook is bleak with more bad news coming up.
2. Protocol deemed Collateral X to be too risky and paused the Singularity market for Collateral X to prevent further borrowing.
3. However, the SGL market is still holding the collateral X and there are no way to reduce it as `repay()` and `liquidate()`. The protocol could minimize losses if the collateral are reduced.
4. Eventually, Collateral X dropped to 0 and now all the collateral X in SGL market are worthless. The protocol will have to write the loans off as bad debts and accept 100% loss as borrowers/liquidators are no longer incentivised to remove them.

## Recommended Mitigation Steps
Remove `notPaused` from `repay()` and `liquidate()`.


## Assessed type

Other
