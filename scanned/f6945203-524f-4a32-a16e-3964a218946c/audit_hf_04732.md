# [M] buyCollateral() does not work properly

## Summary
Severity: Medium
Contest weight: 0.6110
Dataset id: 22550
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BBLeverage.buyCollateral() function does not work as expected.
The implementation of BBLeverage.buyCollateral() is as follows:
```solidity
function buyCollateral(address from, uint256 borrowAmount, uint256 supplyAmount, bytes calldata data)
    external
    optionNotPaused(PauseType.LeverageBuy)
    solvent(from, false)
    notSelf(from)
    returns (uint256 amountOut)
{
    if (address(leverageExecutor) == address(0)) {
        revert LeverageExecutorNotValid();
    }
    // Stack too deep fix
    _BuyCollateralCalldata memory calldata_;
    _BuyCollateralMemoryData memory memoryData;
    {
        calldata_.from = from;
        calldata_.borrowAmount = borrowAmount;
        calldata_.supplyAmount = supplyAmount;
        calldata_.data = data;
    }
    {
        uint256 supplyShare = yieldBox.toShare(assetId, calldata_.supplyAmount, true);
        if (supplyShare > 0) {
            (memoryData.supplyShareToAmount,) = yieldBox.withdraw(assetId, calldata_.from, address(leverageExecutor), 0, supplyShare);
        }
    }
    {
        (, uint256 borrowShare) = _borrow(
            calldata_.from,
            address(this),
            calldata_.borrowAmount,
            _computeVariableOpeningFee(calldata_.borrowAmount)
        );
        (memoryData.borrowShareToAmount,) = yieldBox.withdraw(assetId, address(this), address(leverageExecutor), 0, borrowShare);
    }
    {
        amountOut = leverageExecutor.getCollateral(
            collateralId,
            address(asset),
            address(collateral),
            memoryData.supplyShareToAmount + memoryData.borrowShareToAmount,
            calldata_.from,
            calldata_.data
        );
    }
    uint256 collateralShare = yieldBox.toShare(collateralId, amountOut, false);
    address(asset).safeApprove(address(yieldBox), type(uint256).max);
    yieldBox.depositAsset(collateralId, address(this), address(this), 0, collateralShare); // TODO Check for rounding attack?
    address(asset).safeApprove(address(yieldBox), 0);
    if (collateralShare == 0) revert CollateralShareNotValid();
    _allowedBorrow(calldata_.from, collateralShare);
    _addCollateral(calldata_.from, calldata_.from, false, 0, collateralShare);
}
```
The code above has several issues:
1. leverageExecutor.getCollateral() receiver should be address(this). ---> for 2th step deposit to YB
2. address(asset).safeApprove() should use address(collateral).safeApprove().
3. yieldBox.depositAsset() receiver should be calldata_.from. ----> for next execute addCollateral(calldata.from)
buyCollateral() does not work properly.

## Recommendation
```solidity
function buyCollateral(address from, uint256 borrowAmount, uint256 supplyAmount, bytes calldata data)
    external
    optionNotPaused(PauseType.LeverageBuy)
    solvent(from, false)
    notSelf(from)
    returns (uint256 amountOut)
{
    ....
    {
        (, uint256 borrowShare) = _borrow(
            calldata_.from,
            address(this),
            calldata_.borrowAmount,
            _computeVariableOpeningFee(calldata_.borrowAmount)
        );
        (memoryData.borrowShareToAmount,) = yieldBox.withdraw(assetId, address(this), address(leverageExecutor), 0, borrowShare);
    }
    {
        amountOut = leverageExecutor.getCollateral(
            collateralId,
            address(asset),
            address(collateral),
            memoryData.supplyShareToAmount + memoryData.borrowShareToAmount,
            calldata_.from,
            calldata_.data
        );
    }
    uint256 collateralShare = yieldBox.toShare(collateralId, amountOut, false);
    address(collateral).safeApprove(address(yieldBox), type(uint256).max);
    yieldBox.depositAsset(collateralId, address(this), calldata_.from, 0, collateralShare);
    address(collateral).safeApprove(address(yieldBox), 0);
    if (collateralShare == 0) revert CollateralShareNotValid();
    _allowedBorrow(calldata_.from, collateralShare);
    _addCollateral(calldata_.from, calldata_.from, false, 0, collateralShare);
}
```
