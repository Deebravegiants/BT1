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
...
    uint256 private constant _PRECISION = 18;

    function _getPriceInternal(uint256 age) private view returns (IOracle.Price memory outPrice) {
        PythStructs.Price memory price = age == 0 ? 
            _pyth.getPriceUnsafe(_priceID): 
            _pyth.getPriceNoOlderThan(_priceID, age);

        if (price.expo >= 0) {
            outPrice.price =
                uint64(price.price) *
                uint256(10 ** (_PRECISION + uint32(price.expo)));
        } else {
            outPrice.price =
                uint64(price.price) *
                uint256(10 ** (_PRECISION - uint32(-price.expo)));
        }
        outPrice.lastUpdate = price.publishTime;
    }
```

Since a different precision is used, then the calculation of `totalCollateralInEth` at `StrategyLeverage` will be wrong.

```solidity
    function _getPosition(
        uint256 priceMaxAge
    ) internal view returns (uint256 totalCollateralInEth, uint256 totalDebtInEth) {
...
        totalCollateralInEth = 0;
        totalDebtInEth = 0;

        (uint256 collateralBalance,  uint256 debtBalance ) = _getMMPosition();
    
        if (collateralBalance != 0) {            
            IOracle.Price memory ethPrice = priceMaxAge == 0 ?
                _ethUSDOracle.getLatestPrice():
                _ethUSDOracle.getSafeLatestPrice(priceMaxAge);
            IOracle.Price memory collateralPrice = priceMaxAge == 0 ? 
                _collateralOracle.getLatestPrice():
                _collateralOracle.getSafeLatestPrice(priceMaxAge);
            if (
                !(priceMaxAge == 0 ||
                    (priceMaxAge > 0 && (ethPrice.lastUpdate >= (block.timestamp - priceMaxAge))) ||
                    (priceMaxAge > 0 &&
                        (collateralPrice.lastUpdate >= (block.timestamp - priceMaxAge))))
            ) {
                revert PriceOutdated();
            }
@>          totalCollateralInEth = (collateralBalance * collateralPrice.price) / ethPrice.price;
        }
        if (debtBalance != 0) {
            totalDebtInEth = debtBalance;
        }
    }
```



## Impact

 Incorrect calculation of `totalCollateralInEth`, affecting borrowing judgment, e.g. overvaluation overborrowing, etc.

## Recommended Mitigation

 convert to 18 decimals


## Assessed type

Context
