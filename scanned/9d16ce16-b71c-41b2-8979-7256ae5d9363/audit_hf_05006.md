# [M] TwapOracle should set SMR_BASE_UNIT to 1e18

## Summary
Severity: Medium
Contest weight: 0.4363
Dataset id: 22995
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TwapOracle should set SMR_BASE_UNIT to 1e18 instead of 1e6 on IotaEVM chain. The TwapOracle is used to calculate the TWAP price by querying DEX pools. There are two options to query the price for a token:
1. Through a stablecoin pool.
2. Through a native ERC20 token pool and then multiply by the price of the native ERC20 token.
The issue arises in the second scenario and differs between ShimmerEVM and IotaEVM.
1. For ShimmerEVM, the native ERC20 token is SMR, which is a 6-decimal token and uses the "magic contract".
2. For IotaEVM, the native ERC20 token is WIOTA, which is an 18-decimal token.
Examples of the SMR and WIOTA pools on Magicsea are:
1. SMR-LUM pool
2. MLUM-IOTA pool
The issue is simple. For the ShimmerEVM chain, using 1e6 for SMR_BASE_UNIT is correct because its native ERC20 token is 6 decimals. However, for the IotaEVM chain, it should use 1e18 instead. This discrepancy causes the TWAP price calculated from an Iota pair on IotaEVM to always be incorrect.

```solidity
uint256 public constant SMR_BASE_UNIT = 1e6;
// Normalize average price with 18 decimals of precision
uint256 pairedTokenBaseUnit = config.isSmrBased ? SMR_BASE_UNIT : BUSD_BASE_UNIT;
uint256 anchorPriceMantissa;
if (config.baseUnit > pairedTokenBaseUnit) {
    anchorPriceMantissa = (priceAverageMantissa * config.baseUnit) / pairedTokenBaseUnit;
} else {
    anchorPriceMantissa = priceAverageMantissa / (pairedTokenBaseUnit / config.baseUnit);
}
```
Querying TWAP prices from Iota pair on IotaEVM will always return the incorrect result.

## Recommendation
Make SMR_BASE_UNIT a configurable parameter, and set it to 1e18 on IotaEVM.
