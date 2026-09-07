# [H] Calls to `get_virtual_price()` are vulnerable to read-only reentrancy

## Summary
Severity: High
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-20
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/376
Type: code-finding

## Details
### Lines of code

--------------

[117](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/implementations/ARBTriCryptoOracle.sol#L117-L142)

### Vulnerability details

-------------

`get_virtual_price()` was originally considered to be a manipulation-resistant price - suitable as a price oracle, but it was later found to be vulnerable to a [read-only reentrancy](https://chainsecurity.com/curve-lp-oracle-manipulation-post-mortem/) attack, where the Curve contract could be put into a partially-modified state, and an attacker could gain control via the raw external call `remove_liquidity()` makes. The attacker could use this to artificially inflate the price of the LP token/its balance, and use the inflated balance to take out loans which become undercollateralized at the end of the transaction, or to buy assets at exchange rates not actually available on the open market. In order to protect against the attack, many protocols call `uint256[2] calldata amts; ICurvePool(token).remove_liquidity(0, amts);` prior to calling `get_virtual_price()` since calling `remove_liquidity()` will ensure, via a reentrancy guard, that the user isn't currently manipulating the value, and since amounts are zero, it has no other effect. Another alternative is to call v1 [`pool.claim_admin_fees()`](https://etherscan.io/token/0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511#code#L1104) or to call v2 `ICurveOwner(pool.owner()).withdraw_admin_fees(address(pool))`.

```solidity
File: contracts/oracle/implementations/ARBTriCryptoOracle.sol

117      function _get() internal view returns (uint256 _maxPrice) {
118          uint256 _vp = TRI_CRYPTO.get_virtual_price();
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
137          uint256 _discount = Math.max((_g ** 2 / 1 ether) * _a, 1e34); // handle qbrt nonconvergence
138          // if discount is small, we take an upper bound
139          _discount = (FixedPointMathLib.sqrt(_discount) * DISCOUNT0) / 1 ether;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/376_
