# [M] DoS in BBLeverage and SGLLeverage due to wrong interface used for leverageExecutor

## Summary
Severity: Medium
Contest weight: 0.5935
Dataset id: 22551
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A DoS takes place due to utilizing a wrong interface in the leverage modules.
BBLeverage.sol and SGLLeverage.sol use a wrong interface to interact with the leverageExecutor contract. This will make the sellCollateral() and buyCollateral() functions always fail and render the BBLeverage.sol and SGLLeverage.sol unusable.
As we can see in the following snippets, when these contracts interact with the leverageExecutor to call its getAsset() and getCollateral() functions, they do it passing 6 parameters in each of the functions:
// BBLeverage.sol
```solidity
function buyCollateral(address from, uint256 borrowAmount, uint256 supplyAmount, bytes calldata data)
    external
    optionNotPaused(PauseType.LeverageBuy)
    solvent(from, false)
    notSelf(from)
    returns (uint256 amountOut)
{
    ...
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
    ...
}
function sellCollateral(address from, uint256 share, bytes calldata data)
    external
    optionNotPaused(PauseType.LeverageSell)
    solvent(from, false)
    notSelf(from)
    returns (uint256 amountOut)
{
    ...
    amountOut = leverageExecutor.getAsset(
        assetId, address(collateral), address(asset),
        memoryData.leverageAmount, from, data
    );
    ...
}
```
However, the leverage executor’s getAsset() and getCollateral() functions have just 4 parameters, as seen in the BaseLeverageExecutor.sol base contract used to build all leverage executors:
// BaseLeverageExecutor.sol
```solidity
/**
* @notice Buys an asked amount of collateral with an asset using the ZeroXSwapper.
* @dev Expects the token to be already transferred to this contract.
* @param assetAddress asset address.
* @param collateralAddress collateral address.
* @param assetAmountIn amount to swap.
* @param data SLeverageSwapData.
*/
function getCollateral(address assetAddress, address collateralAddress, uint256 assetAmountIn, bytes calldata data)
    external
    payable
    virtual
    returns (uint256 collateralAmountOut)
{}
/**
* @notice Buys an asked amount of asset with a collateral using the ZeroXSwapper.
* @dev Expects the token to be already transferred to this contract.
* @param collateralAddress collateral address.
* @param assetAddress asset address.
* @param collateralAmountIn amount to swap.
* @param data SLeverageSwapData.
*/
function getAsset(address collateralAddress, address assetAddress, uint256 collateralAmountIn, bytes calldata data)
    external
    virtual
    returns (uint256 assetAmountOut)
{}
```
High. Calls to the leverage modules will always fail, rendering these features unusable.

## Recommendation
Update the interface used in BBLeverage.sol and SGLLeverage.sol and pass the proper parameters so that calls can succeed.
