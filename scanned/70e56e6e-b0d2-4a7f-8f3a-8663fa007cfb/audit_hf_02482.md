# [M] Lack of frozen Update in FundV5

## Summary
Severity: Medium
Contest weight: 0.4169
Dataset id: 13280
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The latest Tranchess protocol features a core FundV5 contract with wstETH as the underlying asset. The new fund benchmarks the share's net asset values against ETH as well as replaces the protocol fee and daily settlement with a fixed yearly rebalance. It also supports the frozen flag to pause the fund operation permanently. While examining the frozen support, we notice the related update logic is missing. To elaborate, we show below the related settle() function, which has a onlyNotFrozen modifier. When the fund contract is frozen, it will not be able to perform any settlement. However, it comes to our attention the frozen flag behind this modifier is never updated.
```solidity
function settle() external nonReentrant onlyNotFrozen {
uint256 day = currentDay;
require(day != 0, "Not initialized");
require(block.timestamp >= day, "The current trading year does not end yet");
uint256 price = twapOracle.getTwap(day);
require(price != 0, "Underlying price for settlement is not ready yet");
IPrimaryMarketV3(_primaryMarket).settle(day);
Calculate NAV
uint256 underlying = getTotalUnderlying();
}
...
modifier onlyNotFrozen() {
Public require(!frozen, "Frozen");
```

## Recommendation
Properly update the frozen flag with necessary caller verification.
