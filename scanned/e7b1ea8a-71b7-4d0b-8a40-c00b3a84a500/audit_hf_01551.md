# [M] swapOn1INCH() slippage may be ineffective

## Summary
Severity: Medium
Contest weight: 0.5637
Dataset id: 8285
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The swapOn1INCH() function attempts to check for slippage as follows:
```solidity
function swapOn1INCH(
    address _assetIn,
    uint256 _amountIn,
    address _assetOut,
    uint256 _minAmountOut,
    bytes calldata _swapData
) external {
    IERC20(_assetIn).approve(ONEINCH_AGGREGATION_ROUTER, _amountIn);
    (bool success, bytes memory data) = ONEINCH_AGGREGATION_ROUTER.call(_swapData);
    require(IERC20(_assetOut).balanceOf(address(this)) >= _minAmountOut, "Slippage Exceeded");
}
```
This slippage check may be ineffective when there are already tokens of _assetOut in the contract. Here's a simple example to illustrate the issue:
The owner wants to swap 1000 token1 for token2.
Assume there are already 500 token2 in the contract.
The owner sets _minAmountOut to 995.
The swap returns 500 token2 for the 1000 token1.
The slippage check will pass because the total token2 balance (1000) exceeds _minAmountOut (995).

## Recommendation
To ensure the slippage check is effective, consider updating the swapOn1INCH() function as follows:
```solidity
function swapOn1INCH(
    address _assetIn,
    uint256 _amountIn,
    address _assetOut,
    uint256 _minAmountOut,
    bytes calldata _swapData
) external {
    uint256 balBefore = IERC20(_assetOut).balanceOf(address(this));
    IERC20(_assetIn).approve(ONEINCH_AGGREGATION_ROUTER, _amountIn);
    (bool success, bytes memory data) = ONEINCH_AGGREGATION_ROUTER.call(_swapData);
    uint256 balAfter = IERC20(_assetOut).balanceOf(address(this));
    require((balAfter - balBefore) >= _minAmountOut, "Slippage Exceeded");
}
```
