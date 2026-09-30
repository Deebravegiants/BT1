# [M] One of the intended functionalities of withdraw() does not work

## Summary
Severity: Medium
Contest weight: 0.6920
Dataset id: 8033
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function withdraw() in FarmKeeper.sol allows a user to withdraw liquidity from a farm:  

```solidity
if (!_farms.contains(id)) revert InvalidFarmId();
Farm storage farm = _farms.get(id);
User storage user = _farms.user(id, msg.sender);
if (user.liquidity < liquidity || liquidity == 0) {
    revert InvalidLiquidityAmount();
}
// Update farms and collect fees
_updateFarm(farm, true);
// Calculate pending rewards and fees
uint256 pendingIncentiveTokens = Math.mulDiv(
    user.liquidity,
    farm.accIncentiveTokenPerShare,
    Constants.SCALE_FACTOR
) - user.rewardCheckpoint;
uint256 pendingFeeToken0 = Math.mulDiv(user.liquidity,
    farm.accFeePerShareForToken0, Constants.SCALE_FACTOR) - user.feeCheckpointToken0;
uint256 pendingFeeToken1 = Math.mulDiv(user.liquidity,
    farm.accFeePerShareForToken1, Constants.SCALE_FACTOR) - user.feeCheckpointToken1;
// Update state
user.liquidity -= liquidity;
user.rewardCheckpoint = Math.mulDiv(user.liquidity,
    farm.accIncentiveTokenPerShare, Constants.SCALE_FACTOR);
user.feeCheckpointToken0 = Math.mulDiv(user.liquidity,
    farm.accFeePerShareForToken0, Constants.SCALE_FACTOR);
user.feeCheckpointToken1 = Math.mulDiv(user.liquidity,
    farm.accFeePerShareForToken1, Constants.SCALE_FACTOR);
// Decrease liquidity
Farms_audit.md
(uint256 amountToken0, uint256 amountToken1) = _decreaseLiquidity(farm, liquidity, msg.sender);
// Payout pending tokens
if (pendingIncentiveTokens > 0) {
    // Mint Incentive Tokens to user
    incentiveToken.mint(msg.sender, pendingIncentiveTokens);
    emit IncentiveTokenDistributed(id, msg.sender, pendingIncentiveTokens);
}
if (pendingFeeToken0 > 0) {
    _safeTransferToken(farm.poolKey.token0, msg.sender, pendingFeeToken0);
    emit FeeDistributed(id, msg.sender, farm.poolKey.token0, pendingFeeToken0);
}
if (pendingFeeToken1 > 0) {
    _safeTransferToken(farm.poolKey.token1, msg.sender, pendingFeeToken1);
    emit FeeDistributed(id, msg.sender, farm.poolKey.token1, pendingFeeToken1);
}
emit Withdraw(id, msg.sender, liquidity, amountToken0, amountToken1);
```

The intended behavior, as described in the NatSpec comments for the withdraw() function, states that:  
Setting liquidity to zero allows to pull fees and incentive tokens without modifying the liquidity position by the user.  
This implies that a user should be able to set the liquidity parameter to 0 to claim accumulated fees and incentive tokens without changing their liquidity position in the farm.  

However, the following check in the function prevents this behavior:  

```solidity
if (user.liquidity < liquidity || liquidity == 0) {
    revert InvalidLiquidityAmount();
}
```

If a user passes 0 as the liquidity parameter, the function reverts with an InvalidLiquidityAmount error.  
This prevents users from pulling their fees and incentive tokens without modifying their liquidity, contradicting the intended behavior stated in the NatSpec.  
As a result, users are unable to claim their accumulated rewards without modifying their liquidity, which can create friction, particularly for users who wish to claim rewards without adjusting their position in the farm.

## Recommendation
Farms_audit.md  
Modify the check to allow liquidity == 0 as a valid input when a user only wants to pull fees and incentive tokens without modifying their liquidity:  

```solidity
if (user.liquidity < liquidity) {
    revert InvalidLiquidityAmount();
}
```
