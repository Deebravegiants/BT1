# [H] Storage slot collision

## Summary
Severity: High
Contest weight: 0.7563
Dataset id: 8398
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
There is a miscalculation in the storage layout allocation for the
PriceAggregatorStorage struct, which leads to a potential storage slot
collision with OtcStorage.
The key issue is with the bytes32[2] jobIds field. It's incorrectly calculated as
taking up 64 bits, but in reality, it occupies 64 bytes (512 bits), spanning 2 full
storage slots.
struct PriceAggregatorStorage {
    IChainlinkFeed linkUsdPriceFeed; // 160 bits
    uint24 twapInterval; // 24 bits
    uint8 minAnswers; // 8 bits
    bytes32[2] jobIds; // 64 bits @audit 64 bytes instead of 64 bits
    // ... other fields
    uint256[41] __gap;
```
This miscalculation causes the PriceAggregatorStorage to actually occupy 52
slots instead of the intended 50 slots. The storage slots are allocated as follows:
```solidity
uint256 internal constant GLOBAL_PRICE_AGGREGATOR_SLOT = 551;
uint256 internal constant GLOBAL_OTC_SLOT = 601;
```
With PriceAggregatorStorage occupying 52 slots starting from slot 551, it will
overlap with the first two slots of OtcStorage, which starts at slot 601. This
overlap will cause data corruption, as the first two slots of OtcStorage will be
overwritten by the last two slots of PriceAggregatorStorage.

## Recommendation
Reduce the __gap array size to 39 in PriceAggregatorStorage or change
GLOBAL_OTC_SLOT to start from slot 603 to ensure no overlap.
