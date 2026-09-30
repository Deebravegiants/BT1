# [M] Oracle feed not validated enough

## Summary
Severity: Medium
Reporter: Olivierdem
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol?plain=1#L49-L54
Type: audit-issue

## Details
# Oracle feed not validated enough

## Summary
Oracle data feed is insufficiently validated. There is no check for stale price and round completeness.

## Vulnerability Detail
Price can be stale and can lead to wrong spot64x64 return value.

## Impact
Impact could be big since the stale price would happen in the getDeltaStrikePrice64x64 function.

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol?plain=1#L49-L54

 ```solidity
function _latestAnswer64x64() internal view returns (int128) {
        (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
        (, int256 underlyingPrice, , , ) =
            UnderlyingSpotOracle.latestRoundData();

        return ABDKMath64x64.divi(underlyingPrice, basePrice);
    }
```


## Tool used

Manual Review

## Recommendation

The oracle gives back 5 values when called, so don't ignore 4 of them.
Validate Data Feed with some require:

```solidity
function _latestAnswer64x64() internal view returns (int128) {
        (uint80 roundID, int256 basePrice, , uint256 timestamp, uint80 answeredInRound) = 
      BaseSpotOracle.latestRoundData();
         require(basePrice > 0, "ChainLink: basePrice price <= 0");
         require(answeredInRound >= roundID, "ChainLink: Stale price");
         require(timestamp > 0, "ChainLink: Round not complete");

        (roundID, int256 underlyingPrice, , timestamp, answeredInRound ) =
            UnderlyingSpotOracle.latestRoundData();
         require(underlyingPrice > 0, "ChainLink: underlyingPrice price <= 0");
         require(answeredInRound >= roundID, "ChainLink: Stale price");
         require(timestamp > 0, "ChainLink: Round not complete");

        return ABDKMath64x64.divi(underlyingPrice, basePrice);
    }
```
