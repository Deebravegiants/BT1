# [M] no validation to ensure the arbitrum sequencer

## Summary
Severity: Medium
Contest weight: 0.3985
Dataset id: 20061
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no validation to ensure sequencer is down
```solidity
int256 rawCollateralPrice = strategy.collateralPriceOracle.latestAnswer();
rebalanceInfo.collateralPrice = rawCollateralPrice.toUint256().mul(10 ** strategy.collateralDecimalAdjustment);

int256 rawBorrowPrice = strategy.borrowPriceOracle.latestAnswer();
rebalanceInfo.borrowPrice = rawBorrowPrice.toUint256().mul(10 ** strategy.borrowDecimalAdjustment);
```
Using Chainlink in L2 chains such as Arbitrum requires to check if the sequencer is down to avoid prices from looking like they are fresh although they are not.
The bug could be leveraged by malicious actors to take advantage of the sequencer downtime.
when sequencer is down, stale price is used for oracle and the borrow value and collateral value is calculated and the protocol can be forced to rebalance in a loss position

## Recommendation
recommend to add checks to ensure the sequencer is not down.
