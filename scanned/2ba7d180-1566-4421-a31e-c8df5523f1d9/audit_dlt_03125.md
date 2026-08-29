# [H] ETHOracle.getLatestPrice need to convert to 18 decimals

## Summary
Severity: High
Chain: Smart contract
Component: 2024-05-bakerfi
Published: 2024-06-03
Source: https://github.com/code-423n4/2024-05-bakerfi-findings/issues/47
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-05-bakerfi/blob/59b1f70cbf170871f9604e73e7fe70b70981ab43/contracts/oracles/EthOracle.sol#L30


# Vulnerability details

## Vulnerability details
in `ETHOracle.sol` 
`getPrecision()` is defined as `10 ** 18`, but the actual oracle used is 8-decimals
https://data.chain.link/feeds/arbitrum/mainnet/eth-usd
this data feeds 's decimals` is 8
```solidity
/**
 *  ETH/USD Oracle using chainlink data feeds
 * 
 *  For more information about the feed go to 
@> *  https://data.chain.link/feeds/arbitrum/mainnet/eth-usd
 * 
 **/
contract ETHOracle is IOracle {
    IChainlinkAggregator private immutable _ethPriceFeed;
@>  uint256 private constant _PRECISION = 10 ** 18;
....
    function getLatestPrice() public view override returns (IOracle.Price memory price) {
        (, int256 answer, uint256 startedAt, uint256 updatedAt,) = _ethPriceFeed.latestRoundData();
        if ( answer<= 0 ) revert InvalidPriceFromOracle();        
        if ( startedAt ==0 || updatedAt == 0 ) revert InvalidPriceUpdatedAt();    

@>      price.price = uint256(answer);  //@audit 8 decimals
        price.lastUpdate = updatedAt;
    }
```

`PythOracle` is used to get prices for other tokens, also `getPrecision() == 18`

```solidity
contract PythOracle is IOracle {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-bakerfi-findings/issues/47_
