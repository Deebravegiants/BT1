# [H] No price scaling in SMAOracle

## Summary
Severity: High
Contest weight: 0.7609
Dataset id: 16070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The update() function of the SMAOracle contract doesn’t scale the latestPrice although a scaler is set in the constructor. On the other hand, the _latestRoundData() function of ChainlinkOracleWrapper contract does scale via toWad().
contract SMAOracle is IOracleWrapper {
    constructor(..., uint256 _spotDecimals, ...) {
        ...
        require(_spotDecimals <= MAX_DECIMALS, "SMA: Decimal precision too high");
        ...
        /* `scaler` is always <= 10^18 and >= 1 so this cast is safe */
        scaler = int256(10**(MAX_DECIMALS - _spotDecimals));
        ...
    }
    function update() internal returns (int256) {
        /* query the underlying spot price oracle */
        IOracleWrapper spotOracle = IOracleWrapper(oracle);
        int256 latestPrice = spotOracle.getPrice();
        ...
        priceObserver.add(latestPrice);
        // doesn't scale latestPrice
        ...
    }
}
contract ChainlinkOracleWrapper is IOracleWrapper {
    function getPrice() external view override returns (int256) {
        (int256 _price, ) = _latestRoundData();
        return _price;
    }
    function _latestRoundData() internal view returns (int256, uint80) {
        (..., int256 price, ..) = AggregatorV2V3Interface(oracle).latestRoundData();
        ...
        return (toWad(price), ...);
    }
}
```

## Recommendation
```solidity
The latestPrice variable in SMAOracle contract should be scaled, and the toWad() function should be re-introduced.
```
