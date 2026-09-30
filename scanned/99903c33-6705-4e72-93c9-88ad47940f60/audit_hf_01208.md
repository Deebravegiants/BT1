# [H] Insufficient slippage protection in mintlvlUSD

## Summary
Severity: High
Contest weight: 0.7705
Dataset id: 5369
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the mintlvlUSD method, the minimum lvlUSDAmount (slippage protection) is overwritten by the allowed slippage amount leading to a negligibly low minimum lvlUSDAmount, which can cause potential losses for the receiver / collateral provider. The mintlvlUSD method of the LevelBaseReserveManager contract is responsible to create and submit a MINT order to the LevelMinting contract to mint the appropriate amount of lvlUSD for the given amount of collateral. This order includes a minimum lvlUSDAmount which serves as a slippage parameter ensuring that the receiver / collateral provider is not at a loss due to an unexpectedly low amount of minted lvlUSD. Of course, one cannot always expect full 1:1 minting therefore an amount proportional to maxSlippageThresholdBasisPoints is intended to be the allowed slippage:
```solidity
// Apply max slippage threshold
lvlUSDAmount = lvlUSDAmount.mulDiv(
    maxSlippageThresholdBasisPoints,
    MAX_BASIS_POINTS
);
```
However, instead of subtracting the allowed slippage amount from the minimum lvlUSDAmount, it is overwritten by this small amount effectively eliminating the slippage protection. Impact: Having a negligibly low minimum lvlUSDAmount exposes the receiver / collateral provider to a maximum slippage risk in terms of minted lvlUSD vs. provided collateral, which can turn out to be a severe loss. Likelihood: With maxSlippageThresholdBasisPoints initially being set to 5 (5 bps = 0.05%), every call to mintlvlUSD is subject to a full slippage risk.

## Recommendation
It is recommended to subtract the slippage amount from lvlUSDAmount to arrive at the desired minimum lvlUSDAmount:
```solidity
// Apply max slippage threshold
- lvlUSDAmount = lvlUSDAmount.mulDiv(
+ lvlUSDAmount -= lvlUSDAmount.mulDiv(
    maxSlippageThresholdBasisPoints,
    MAX_BASIS_POINTS
);
```
