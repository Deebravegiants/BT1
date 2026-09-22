# [M] 6.1 Missing Documentation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

The requirements about the oracles for the underlying tokens are not documented. In the supplied test
file we see following oracles:

```
address constant USDC_ORACLE = 0x77b68899b99b686F415d074278a9a16b336085A0;
address constant DAI_ORACLE = 0x47c3dC029825Da43BE595E21fffD0b66FfcB7F6e;
address constant ETH_ORACLE = 0x81FE72B5A8d1A857d176C3E7d5Bd2679A9B85763;
```
The oracles for USDC and DAI return the unit value of one. The ETH oracle is updated roughly once an
hour hence the price returned is not live. For the proper working of the GUniLPOracle a live price feed is
required, frequently updated and without a time delay. When GUniLPOracle.seek() is executed, the
underlying price feeds must return live values.

Furthermore the underlying principle how the price is determined could be described more clearly in the
Readme:

This price feed works by determining how many of token0 and token1 the underlying liquidity position in
UniswapV3 held by the GUniPool has at the current price. This current price is solely determined by
Maker oracles and independent of the current state of the UniswapV3 pool. The assumption is that

```
1.The Maker oracles for the underlying tokens return the current market rate
2.In general, e.g. outside flashloan scenarios, the UniswapV3 pool will be balanced at the current
market rate. This means that the GUnipool tokens can be redeemed at this current market rate.
```
Hence such a GUnipool token collateral is priced based on its underlying tokens, independent of the
state of the GUni/Uniswap V3 pool. The documentation may be expanded to explain and motivate this.

Specification changed:

Maker responded:

```
It was a mistake that the test was referring to the ETH/USD OSM. It should have
referenced the ETH/USD Medianizer to get a live price feed.
```

Furthermore the readme has been updated and now contains:

```
Underlying price oracles `orb0` and `orb1` should refer to either a Medianizer,
DSValue or some other `read()` compliant oracle. OSMs should not be used to
the double delay.
```
