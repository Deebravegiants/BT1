# [M] Improper Fee Accumulation Logic in FeeDistributor

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 12802
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a core FeeDistributor contract that is designed to accumulate and distribute protocol fees. In the process of examining current fee accumulation logic, we notice its implementation has a flaw that needs to be fixed. In the following, we show the implementation of the affected routine `accumulateFees()`. It has a rather straightforward logic in collecting the given fee amount (`_wethAmount` and `_usdcAmount`) and then updating the cumulative fee amount as well as the tokens per interval for distribution. While the cumulative fee amount is properly updated, the tokens per interval is not. Instead, the correct approach to update them are the following: `accumulatedFees[vault].wethTokensPerInterval = (_wethAmount + wethRemaining) / SECONDS_PER_WEEK` and `accumulatedFees[vault].usdcTokensPerInterval = (_usdcAmount + usdcRemaining) / SECONDS_PER_WEEK` (lines 75-76).
```solidity
function accumulateFees(uint256 _wethAmount, uint256 _usdcAmount) external {
    address vault = msg.sender;
    if (!isVault[vault]) revert FeeDistributor_InvalidVault();
    // Transfer in the WETH and USDC
    IERC20(weth).safeTransferFrom(msg.sender, address(this), _wethAmount);
    IERC20(usdc).safeTransferFrom(msg.sender, address(this), _usdcAmount);
    // Get remaining rewards from last distribution period
    (uint256 distributedWeth, uint256 distributedUsdc) = pendingRewards(vault);
    uint256 wethRemaining = accumulatedFees[vault].wethAmount - distributedWeth;
    uint256 usdcRemaining = accumulatedFees[vault].usdcAmount - distributedUsdc;
    // Accumulate the fees
    accumulatedFees[vault].wethAmount += _wethAmount;
    accumulatedFees[vault].usdcAmount += _usdcAmount;
    accumulatedFees[vault].lastDistributionTime = block.timestamp;
    // Set the Tokens per interval (week) for WETH and USDC
    accumulatedFees[vault].wethTokensPerInterval = _wethAmount + wethRemaining / SECONDS_PER_WEEK;
    accumulatedFees[vault].usdcTokensPerInterval = _usdcAmount + usdcRemaining / SECONDS_PER_WEEK;
    // Emit an event
    emit FeesAccumulated(vault, _wethAmount, _usdcAmount);
}
```

## Recommendation
Improve the above-mentioned routine to properly accumulate fee and update tokens per internal for distribution.
