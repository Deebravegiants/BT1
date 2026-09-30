# [M] Hardcoded deadline in the DEX interaction

## Summary
Severity: Medium
Contest weight: 0.5639
Dataset id: 6026
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the DexSwapperUManager.sol contract, specifically in the swapWithUniswapV3 function, the deadline parameter for the IUniswapV3Router.ExactInputParams struct is set to block.timestamp. This means that the deadline for the trade is set to the current block timestamp, which could lead to issues if the trade execution is delayed due to network congestion or other factors.  
Hardcoding the deadline in this manner can result in failed transactions if the deadline is exceeded before the trade is executed. This can cause users to lose their funds or incur additional transaction fees when attempting to resubmit the trade.  
```solidity
IUniswapV3Router.ExactInputParams memory params = IUniswapV3Router.ExactInputParams({
    path: packedPath,
    recipient: boringVault,
    deadline: block.timestamp,
    amountIn: amountIn,
    amountOutMinimum: amountOutMinimum
});
```

## Recommendation
Instead of hardcoding the deadline parameter to block.timestamp, it is recommended to pass the deadline as a separate parameter to the swapWithUniswapV3 function. This will allow the caller to set an appropriate deadline based on their requirements and expectations for trade execution time.  
Here's an example of how the function signature and implementation could be modified:  
```solidity
function swapWithUniswapV3(
    bytes32[][] calldata manageProofs,
    address[] calldata decodersAndSanitizers,
    ERC20[] memory path,
    uint24[] memory fees,
    uint256 amountIn,
    uint256 amountOutMinimum,
    uint256 deadline
) external requiresAuth {
    // ... (existing code)
    IUniswapV3Router.ExactInputParams memory params = IUniswapV3Router.ExactInputParams({
```
