# [M] Incorrect deviation calculation in isDeviating-

## Summary
Severity: Medium
Contest weight: 0.5942
Dataset id: 20428
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the isDeviatingWithBpsCheck function in the codebase leads to inaccurate deviation calculations, potentially allowing deviations beyond the specified limits. The function isDeviatingWithBpsCheck checks if the deviation between two values exceeds a defined threshold. This function incorrectly calculates the deviation, considering only the deviation from the larger value to the smaller one, instead of the deviation from the mean (or TWAP).
```solidity
function isDeviatingWithBpsCheck(
    uint256 value0_,
    uint256 value1_,
    uint256 deviationBps_,
    uint256 deviationMax_
) internal pure returns (bool) {
    if (deviationBps_ > deviationMax_)
        revert Deviation_InvalidDeviationBps(deviationBps_, deviationMax_);
    return isDeviating(value0_, value1_, deviationBps_, deviationMax_);
}
function isDeviating(
    uint256 value0_,
    uint256 value1_,
    uint256 deviationBps_,
    uint256 deviationMax_
) internal pure returns (bool) {
    return
        (value0_ < value1_)
        ? _isDeviating(value1_, value0_, deviationBps_, deviationMax_)
        : _isDeviating(value0_, value1_, deviationBps_, deviationMax_);
}
ies/Deviation.sol#L23-L52
```
The function then call _isDeviating to calculate how much the smaller value is deviated from the bigger value.
```solidity
function _isDeviating(
    uint256 value0_,
    uint256 value1_,
    uint256 deviationBps_,
    uint256 deviationMax_
) internal pure returns (bool) {
    return ((value0_ - value1_) * deviationMax_) / value0_ > deviationBps_;
}
ies/Deviation.sol#L63-L70
```
The function isDeviatingWithBpsCheck is usually used to check how much the current value is deviated from the TWAP value to make sure that the value is not manipulated. Such as spot price and twap price in UniswapV3.
```solidity
if (
    // `isDeviatingWithBpsCheck()` will revert if `deviationBps` is invalid.
    Deviation.isDeviatingWithBpsCheck(
        baseInQuotePrice,
        baseInQuoteTWAP,
        params.maxDeviationBps,
        DEVIATION_BASE
    )
) {
    revert UniswapV3_PriceMismatch(address(params.pool), baseInQuoteTWAP, baseInQuotePrice);
}
ules/PRICE/submodules/feeds/UniswapV3Price.sol#L225-L235
```
The issue is isDeviatingWithBpsCheck is not check the deviation of current value to the TWAP but deviation from the bigger value to the smaller value. This leads to an incorrect allowance range for the price, permitting deviations that exceed the acceptable threshold.

Example:
TWAP price: 1000 Allow deviation: 10%. The correct deviation calculation will use deviation from the mean. The allow price will be from 900 to 1100 since:
• |1100 - 1000| / 1000 = 10%
• |900 - 1000| / 1000 = 10%
However the current calculation will allow the price from 900 to 1111
• (1111 - 1000) / 1111 = 10%
• (1000 - 900) / 1000 = 10%
Even though the actual deviation of 1111 to 1000 is |1111 - 1000| / 1000 = 11.11% > 10%
This miscalculation allows for greater deviations than intended, increasing the vulnerability to price manipulation and inaccuracies in Oracle price reporting.

## Recommendation
To accurately measure deviation, the isDeviating function should be revised to calculate the deviation based on the mean value: | spot value - twap value | / twap value.
