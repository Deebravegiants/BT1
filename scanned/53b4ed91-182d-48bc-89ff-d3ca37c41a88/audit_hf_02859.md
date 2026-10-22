# [M] TWAP price manipulation

## Summary
Severity: Medium
Contest weight: 0.5965
Dataset id: 16050
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _getTwaPrice(address id, uint32 priceTwa) private view returns (uint160 slotPrice, uint160 twaPrice) {
    // Default TWA price to slot
    twaPrice = slotPrice;
    uint32 secondsAgo = uint32(priceTwa * 60);
    uint32 oldestObservation = 0;
    // Load oldest observation if cardinality greater than zero
    oldestObservation = OracleLibrary.getOldestObservationSecondsAgo(id);
    // Limit to oldest observation (fallback)
    if (oldestObservation < secondsAgo) {
        secondsAgo = oldestObservation; // @audit fallback to oldest observation
    }
```
```solidity
function getQuote(
    address inputTokenAddress,
    address outputTokenAddress,
    uint24 fee,
    uint256 twap,
    uint256 inputTokenAmount
) public view returns (uint256 quote, uint32 secondsAgo) {
    secondsAgo = uint32(twap * 60);
    uint32 oldestObservation = 0;
    // Load oldest observation if cardinality greater than zero
    oldestObservation = OracleLibrary.getOldestObservationSecondsAgo(poolAddress);
    // Limit to oldest observation
    if (oldestObservation < secondsAgo) {
        secondsAgo = oldestObservation; // @audit fallback to oldest observation
    }
    // If TWAP is enabled and price history exists, consult oracle
    if (secondsAgo > 0) {
        // Consult the Oracle Library for TWAP
        (int24 arithmeticMeanTick, ) = OracleLibrary.consult(poolAddress, secondsAgo);
        // Convert tick to sqrtPriceX96
        sqrtPriceX96 = TickMath.getSqrtRatioAtTick(arithmeticMeanTick);
    }
```
The _getTwaPrice function in FarmKeeper and getQuote function in UniversalBuyAndBurn are vulnerable to price manipulation in Uniswap V3 pools with low observation cardinality. This vulnerability can lead to inaccurate price calculations, potentially resulting in unfair token swaps or liquidity provisions. When getting the twap price to prevent slippage in liquidity providing and swapping, the _getTwaPrice and getQuote functions fallback to the oldest observation if the requested time window is greater than the available price history. It's a problem because it doesn't consider the pool cardinality. In newly created pools with cardinality initialized to 1, the oldest observation can be manipulated to be the current block.timestamp, setting the TWAP price to the current (potentially manipulated) price. Because in uniswap v3 pool, an oracle observation is written by the first swap or liquidity provision in the block. Let's say before the UniversalBuyAndBurn contract performs the swap, a malicious actor front-runs and swaps to manipulate the price because the cardinality is 1, and the oldest observation is 0. Another consequence is that the oldestObservation can be equal to cardinality * 12 seconds (time per block) if liquidity changes each block. It means that the TWAP period can be shorter than intended if oldestObservation < secondsAgo, potentially increasing slippage risk.

## Recommendation
It's recommended to either: Revert if oldestObservation < secondsAgo to ensure the full intended TWAP period is used. Require a minimum cardinality (e.g., 10) for pools to be eligible for farming or buy-and-burn operations. Reference: https://docs-v1.euler.finance/euler-protocol/eulers-default-parameters#uniswap-observation-cardinality
