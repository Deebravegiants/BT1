# [M] Current logic of the `solvent()` modifier could make users unfairly DOS'd from selling their collateral

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-04
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/18
Type: hats-finding

## Details
**Github username:** @bauchibred
**Twitter username:** bauchibred
**Submission hash (on-chain):** 0x878ab44dc233f89a7e96c4298f9f4126d3e8745fcea5d3e71d7dc726aa3d08e6
**Severity:** medium

**Description:**
**Description**

Take a look at https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/markets/bigBang/BBLeverage.sol#L133-L170

```solidity
    function sellCollateral(address from, uint256 share, bytes calldata data)
        external
        optionNotPaused(PauseType.LeverageSell)
        solvent(from)
        notSelf(from)
        returns (uint256 amountOut)
    {
        if (address(leverageExecutor) == address(0)) {
            revert LeverageExecutorNotValid();
        }
        penrose.reAccrueBigBangMarkets();

        _allowedBorrow(from, share);
        _removeCollateral(from, address(this), share);

        _SellCollateralMemoryData memory memoryData;

        (memoryData.leverageAmount,) =
            yieldBox.withdraw(collateralId, address(this), address(leverageExecutor), 0, share);
        amountOut =
            leverageExecutor.getAsset(from, address(collateral), address(asset), memoryData.leverageAmount, data);
        memoryData.shareOut = yieldBox.toShare(assetId, amountOut, false);
        address(asset).safeApprove(address(yieldBox), type(uint256).max);
        yieldBox.depositAsset(assetId, address(this), from, 0, memoryData.shareOut); // TODO Check for rounding attack?
        address(asset).safeApprove(address(yieldBox), 0);

        memoryData.partOwed = userBorrowPart[from];
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/18_
