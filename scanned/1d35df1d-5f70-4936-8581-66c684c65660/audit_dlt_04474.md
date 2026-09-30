# [M] `setOTCPriceTolerance()` got the wrong original value

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/106
Type: sherlock-finding

## Details
8olidity

medium

# `setOTCPriceTolerance()` got the wrong original value

## Summary
`setOTCPriceTolerance()` got the wrong original value
## Vulnerability Detail
In the `setOTCPriceTolerance` function, the previous value of `otcPriceTolerance` will be assigned to `previousOtcTolerance`, but the value of `auctionTwapPeriod` is taken in the code.

```solidity
    function setOTCPriceTolerance(uint256 _otcPriceTolerance) external onlyOwner {
        // Tolerance cannot be more than 20%
        require(_otcPriceTolerance <= MAX_OTC_PRICE_TOLERANCE, "Price tolerance has to be less than 20%");
        uint256 previousOtcTolerance = auctionTwapPeriod; //@audit 

        otcPriceTolerance = _otcPriceTolerance;

        emit SetOTCPriceTolerance(previousOtcTolerance, _otcPriceTolerance);
    }
```
## Impact
`setOTCPriceTolerance()` got the wrong original value
## Code Snippet
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L744
## Tool used

Manual Review

## Recommendation
```solidity
uint256 previousOtcTolerance = otcPriceTolerance
```
