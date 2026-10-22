# [M] Lack of isLpCreated validation

## Summary
Severity: Medium
Contest weight: 0.3855
Dataset id: 10516
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lack of isLpCreated variable validation in the ContinuosBondingERC20Token contract functions makes it possible to return the bonding token to the purchase phase. This can cause unexpected behavior such as secondary involving _createPair or withdrawing treasury fees but it is almost always economically inefficient. The isLpCreated variable is set to true in the _createPair function but is never checked.
```solidity
function _createPair() internal {
    uint256 currentTokenBalance = getReserve();
    uint256 currentEth = ethBalance - initialTokenBalance;
    isLpCreated = true;
}
```

## Recommendation
Consider checking isLpCreated variable in buyTokens and sellTokens: `if (liquidityGoalReached() || isLpCreated) revert LiquidityGoalReached`
