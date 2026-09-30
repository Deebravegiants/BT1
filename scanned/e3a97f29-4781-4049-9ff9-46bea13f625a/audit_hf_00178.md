# [M] ConcentratedLiquidityPoolManager.sol `claimReward

## Summary
Severity: Medium
Contest weight: 0.5948
Dataset id: 946
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `ConcentratedLiquidityPosition.collect()`, balances of `token0` and `token1` in bento will be used to pay the fees.

[`ConcentratedLiquidityPosition.sol#L103` L116](https://github.com/sushiswap/trident/blob/c405f3402a1ed336244053f8186742d2da5975e9/contracts/pool/concentrated/ConcentratedLiquidityPosition.sol#L103-L116)

```solidity
uint256 balance0 = bento.balanceOf(token0, address(this));
uint256 balance1 = bento.balanceOf(token1, address(this));
if (balance0 < token0amount || balance1 < token1amount) {
    (uint256 amount0fees, uint256 amount1fees) = position.pool.collect(position.lower, position.upper, address(this), false);

    uint256 newBalance0 = amount0fees + balance0;
    uint256 newBalance1 = amount1fees + balance1;

    /// @dev Rounding errors due to frequent claiming of other users in the same position may cost us some raw
    if (token0amount > newBalance0) token0amount = newBalance0;
    if (token1amount > newBalance1) token1amount = newBalance1;
}
_transfer(token0, address(this), recipient, token0amount, unwrapBento);
_transfer(token1, address(this), recipient, token1amount, unwrapBento);
```

In the case of someone add an incentive with `token0` or `token1`, the incentive in the balance of bento will be used to pay fees until the balance is completely consumed.

As a result, when a user calls `claimReward()`, the contract may not have enough balance to pay (it supposed to have it), cause the transaction to fail.

[`ConcentratedLiquidityPoolManager.sol#L78` L100](https://github.com/sushiswap/trident/blob/c405f3402a1ed336244053f8186742d2da5975e9/contracts/pool/concentrated/ConcentratedLiquidityPoolManager.sol#L78-L100)

```solidity
function claimReward(
    uint256 positionId,
    uint256 incentiveId,
    address recipient,
    bool unwrapBento
) public {
    require(ownerOf[positionId] == msg.sender, "OWNER");
    Position memory position = positions[positionId];
    IConcentratedLiquidityPool pool = position.pool;
    Incentive storage incentive = incentives[position.pool][positionId];
    Stake storage stake = stakes[positionId][incentiveId];
    require(stake.initialized, "UNINITIALIZED");
    uint256 secondsPerLiquidityInside = pool.rangeSecondsInside(position.lower, position.upper) - stake.secondsInsideLast;
    uint256 secondsInside = secondsPerLiquidityInside * position.liquidity;
    uint256 maxTime = incentive.endTime < block.timestamp ? block.timestamp : incentive.endTime;
    uint256 secondsUnclaimed = (maxTime - incentive.startTime) << (128 - incentive.secondsClaimed);
    uint256 rewards = (incentive.rewardsUnclaimed * secondsInside) / secondsUnclaimed;
    incentive.rewardsUnclaimed -= rewards;
    incentive.secondsClaimed += uint160(secondsInside);
    stake.secondsInsideLast += uint160(secondsPerLiquidityInside);
    _transfer(incentive.token, address(this), recipient, rewards, unwrapBento);
    emit ClaimReward(positionId, incentiveId, recipient, rewards);
}
```

The same issue applies to `reclaimIncentive()` as well. [`ConcentratedLiquidityPoolManager.sol` L49 L62](https://github.com/sushiswap/trident/blob/c405f3402a1ed336244053f8186742d2da5975e9/contracts/pool/concentrated/ConcentratedLiquidityPoolManager.sol#L49-L62)

```solidity
function reclaimIncentive(
    IConcentratedLiquidityPool pool,
    uint256 incentiveId,
    uint256 amount,
    address receiver,
    bool unwrapBento
) public {
    Incentive storage incentive = incentives[pool][incentiveId];
    require(incentive.owner == msg.sender, "NOT_OWNER");
    require(incentive.expiry < block.timestamp, "EXPIRED");
    require(incentive.rewardsUnclaimed >= amount, "ALREADY_CLAIMED");
    _transfer(incentive.token, address(this), receiver, amount, unwrapBento);
    emit ReclaimIncentive(pool, incentiveId, amount);
}
```

## Recommendation
Consider making adding `token0` or `token1` as incentives disallowed, or keep a record of total remaining incentive amounts for the incentive tokens and avoid consuming these revered balances when `collect()`.
