# [M] Unsafe downcasting operation result in unsafe number truncation.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/7
Type: sherlock-finding

## Details
ctf_sec

medium

# Unsafe downcasting operation result in unsafe number truncation.

## Summary

Unsafe downcasting operation result in unsafe number truncation. 

## Vulnerability Detail

The unsafe dowcasting operation from uint256 to uint128 and int128 or uint112 is used in MarketCore.sol

```solidity
uint256 fees = _calculateStabilityFees(uint256(amount).mul(int256(pools[poolType][poolTier].fixedConfig.leverage).abs()));
amount -= uint112(fees);
```

```solidity
contracts\market\template\MarketCore.sol:
  127      // Correctly account for liquidity in long and short by adding the float liquidity to the underbalanced side.
  128:     totalEffectiveLiquidityPoolType[params.underBalancedSide] += uint128(uint256(pools[PoolType.FLOAT][0].value).mul(floatPoolLeverage.abs()));
  129  

  146            poolValue +=
  147:             (((poolValue * poolFixedConfig.leverage * params.valueChange) / int128(totalEffectiveLiquidityPoolType[poolType])) -
  148                ((poolValue * poolFixedConfig.leverage * params.fundingAmount[poolType]) / (actualTotalEffectiveLiquidityForPoolType))) /

  169          if (poolType != FLOAT_TYPE)
  170:           nextTotalEffectiveLiquidityPoolType[poolType] += uint128(uint256(poolValue).mul(int256(poolFixedConfig.leverage).abs()));
  171  

  576      if (batch.paymentToken_deposit > 0 || batch.poolToken_redeem > 0) {
  577:       changeInMarketValue_inPaymentToken = int128(batch.paymentToken_deposit) - int256(uint256(batch.poolToken_redeem).mul(price));
  578  
  579:       int256 changeInSupply_poolToken = int256(uint256(batch.paymentToken_deposit).div(price)) - int128(batch.poolToken_redeem);
  580  
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/7_
