# [M] `ARBTriCryptoOracle` is vulnerable to read-only reentrancy

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1211
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-tapioca/blob/7f9fd0f315225b7bd09042b0da8941b93d1b156f/tapioca-periph-audit/contracts/oracle/implementations/ARBTriCryptoOracle.sol#L118


# Vulnerability details

## Impact

`get_virtual_price()` was originally considered to be a manipulation-resistant price - suitable as a price oracle, but it was later found to be vulnerable to a [read-only reentrancy](https://chainsecurity.com/curve-lp-oracle-manipulation-post-mortem/) attack, where the Curve contract could be put into a partially-modified state, and an attacker could gain control via the raw external call `remove_liquidity()` makes. The attacker could use this to artificially inflate the price of the LP token/its balance, and use the inflated balance to take out loans which become undercollateralized at the end of the transaction, or to buy assets at exchange rates not actually available on the open market.


## Proof of Concept
`ARBTriCryptoOracle` calls `get_virtual_price()` without calling any nonreentrant functions:

```solidity
File: contracts/oracle/implementations/ARBTriCryptoOracle.sol

117      function _get() internal view returns (uint256 _maxPrice) {
118 @>       uint256 _vp = TRI_CRYPTO.get_virtual_price();
119  
120          // Get the prices from chainlink and add 10 decimals
121          uint256 _btcPrice = uint256(BTC_FEED.latestAnswer()) * 1e10;
122          uint256 _wbtcPrice = uint256(WBTC_FEED.latestAnswer()) * 1e10;
123          uint256 _ethPrice = uint256(ETH_FEED.latestAnswer()) * 1e10;
124          uint256 _usdtPrice = uint256(USDT_FEED.latestAnswer()) * 1e10;
125  
126          uint256 _minWbtcPrice = (_wbtcPrice < 1e18)
127              ? (_wbtcPrice * _btcPrice) / 1e18
128              : _btcPrice;
129  
130          uint256 _basePrices = (_minWbtcPrice * _ethPrice * _usdtPrice);
131  
132          _maxPrice = (3 * _vp * FixedPointMathLib.cbrt(_basePrices)) / 1 ether;
133  
134          // ((A/A0) * (gamma/gamma0)**2) ** (1/3)
135          uint256 _g = (TRI_CRYPTO.gamma() * 1 ether) / GAMMA0;
136          uint256 _a = (TRI_CRYPTO.A() * 1 ether) / A0;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1211_
