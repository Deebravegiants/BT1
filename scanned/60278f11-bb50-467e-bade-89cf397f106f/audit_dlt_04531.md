# [M] Accounting issue in MarketCore.sol#_rebalancePoolsAndExecuteBatchedAction

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/12
Type: sherlock-finding

## Details
ctf_sec

medium

# Accounting issue in MarketCore.sol#_rebalancePoolsAndExecuteBatchedAction

## Summary

MarketCore.sol#_rebalancePoolsAndExecuteBatchedAction has accounting issue.

## Vulnerability Detail

Let us check the implementation below:

```solidity
        if (poolType != FLOAT_TYPE) {
          // To correctly apportion funding owed for the underblananced tiers, we need to remove the float liquidity contribution
          int256 actualTotalEffectiveLiquidityForPoolType = int256(
            (uint256(totalEffectiveLiquidityPoolType[poolType]) -
              (poolType == params.underBalancedSide ? uint256(pools[PoolType.FLOAT][0].value).mul(floatPoolLeverage.abs()) : 0))
          );

          // Long and short pools both pay funding
          poolValue +=
            (((poolValue * poolFixedConfig.leverage * params.valueChange) / int128(totalEffectiveLiquidityPoolType[poolType])) -
              ((poolValue * poolFixedConfig.leverage * params.fundingAmount[poolType]) / (actualTotalEffectiveLiquidityForPoolType))) /
            1e18;
        } else {
          // Float pool recieves all funding and fees.
          poolValue +=
            ((poolValue * floatPoolLeverage * params.valueChange) /
              (int256(uint256(totalEffectiveLiquidityPoolType[params.underBalancedSide])) * 1e18)) +
            -params.fundingAmount[SHORT_TYPE] + // funding value is negative for short side (double negative to add it)
            params.fundingAmount[LONG_TYPE] +
            int256(feesToDistribute[epochIndex & 1]);

          feesToDistribute[epochIndex & 1] = 0;
        }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/12_
