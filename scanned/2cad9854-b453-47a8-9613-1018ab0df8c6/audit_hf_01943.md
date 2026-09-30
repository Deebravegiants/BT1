# [M] Excess ETH is not refunded

## Summary
Severity: Medium
Contest weight: 0.3886
Dataset id: 10720
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In multiple instances, pricefeeds are updated without the excess eth sent being refunded. This will result in the funds being stuck in the contracts forever. NablaRouter.sol - swapExactTokensForTokens NablaBackstopPool.sol - deposit, finalizeWithdrawBackstopLiquidity, redeemSwapPoolShares, finalizeWithdrawExcessSwapLiquidity, redeemCrossSwapPoolShares NablaPortal.sol - swapExactTokensForEth, _updatePriceFeeds

## Recommendation
Two potential fixes:  
1. Implement a check for update fees in these functions, compare that msg.value sent is enough, and refund any excess tokens. A roughly similar logic can be found in swapEthForExactTokens function, or the below code can be adapted.  
```solidity
uint256 updateFee = getUpdateFee(oracleAdapter, _priceUpdateData); //@note a function to query fee can be cr
uint256 refundAmount = msg.value - updateFee;
if (refundAmount > 0) {
    (bool success, ) = msg.sender.call{value: refundAmount}("");
    require(success, "NP:swapEthForExactTokens:REFUND_FAILED");
}
```
2. Creating a sweep function in these contracts, that admin can use to recover any excess tokens in the contracts.
