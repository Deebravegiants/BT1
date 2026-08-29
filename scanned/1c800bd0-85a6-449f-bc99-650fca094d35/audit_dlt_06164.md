# [M] Incorrect UniV2 price oracle for pools with different token decimals

## Summary
Severity: Medium
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-04
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/17
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0x7ede3495d562581e385efabb22d3effb5a1af1814ee65563eba6787760ba2988
**Severity:** medium

**Description:**
**Description**\
`_getV2Price()` in `CvgOracle` can return an incorrect price if the tokens in the pool do not have the same decimals. 

**Attack Scenario**\
Consider a WBTC/USDC pool, where WBTC is `token0`. If the price of BTC is 25_000 USD, then the reserves will be 

reserves WBTC = 1e8

reserves USDC = 25_000 * 1e6

`reserve0 < reserve1`, so `price` = (25_000 * 1e6 / 1e8) *  (1e16) = 2.5

running the coded PoC attached returns:
```Logs:
  BTC price: 2589619085176319273
```
which confirms the issue.

This will make the oracle call fail when checking against the chainlink price of the asset.

**Recommendation**
Normalize the reserves to 18 decimals before dividing to obtain the price:
```diff
...
    (uint112 reserve0, uint112 reserve1, ) = IUniswapV2Pair(uniswapV2Pool).getReserves();
-   uint256 price = reserve0 < reserve1
-       ? (reserve1 * 10 ** _getDecimalsDelta(uniswapV2Pool)) / reserve0
-       : (reserve0 * 10 ** _getDecimalsDelta(uniswapV2Pool)) / reserve1;
+   reserve0 = reserve0 * 10**(18 - IERC20(IUniswapV2Pair(uniswapV2Pool).token0()).decimals());
+   reserve1 = reserve1 * 10**(18 - IERC20(IUniswapV2Pair(uniswapV2Pool).token1()).decimals());
+   uint256 price = reserve1 * 10**18 / reserve0;
    return _postTreatmentAndVerifyEth(price, isReversed, isEthPriceRelated);
...
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/17_
