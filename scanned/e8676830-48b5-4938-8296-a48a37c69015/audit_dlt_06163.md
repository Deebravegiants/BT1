# [M] UniV3 oracle price is incorrect if `token0.decimals() > token1.decimals()`

## Summary
Severity: Medium
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-04
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/20
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0xabe8d559e0ca80944ca2508da2b8de07c40377ef426f15ad2f9541311e683354
**Severity:** medium

**Description:**
**Description**\
The function [`_getV3Price()`](https://github.com/Cvg-Finance/hats-audit/blob/581c763c7265e142ad868b574ee5e8cd302f9472/contracts/Oracles/CvgOracle.sol#L90) of `CvgOracle` will return an incorrect result depending on the order of the tokens if they have different decimals. The result is correct only if the token0 is the one with the smaller amount of decimals, and incorrect otherwise.

The issue comes from the scaling factor computed in [`_getDecimalsDelta()`](https://github.com/Cvg-Finance/hats-audit/blob/581c763c7265e142ad868b574ee5e8cd302f9472/contracts/Oracles/CvgOracle.sol#L211), which is independent of the order of the tokens, while it should be dependent.

**Attack Scenario**\
The issue is confirmed by the PoC attached where, as an example, the price of UniV3 ETH/USDC and ETH/USDT is computed. The 2 pools have ETH as token1 and token0 respectively:

```
Logs:
  ETH/USDC price: 1632116256333849412388
  ETH/USDT price: 0
```
The value for ETH/USDT price is incorrect, and this will make the oracle calls fail during the comparison to the ETH Chainlink price.

**Recommendation**
Change the `_getDecimalsDelta()` so that it returns the correct amount if `token0Decimals > token1Decimals`.

```diff
    function _getDecimalsDelta(address uniswapPool) internal view returns (uint256 decimalsDelta) {
        uint256 token0Decimals = IERC20Metadata(IUniswapV3Pool(uniswapPool).token0()).decimals();
        uint256 token1Decimals = IERC20Metadata(IUniswapV3Pool(uniswapPool).token1()).decimals();
        decimalsDelta = token0Decimals <= token1Decimals
            ? 18 - (token1Decimals - token0Decimals)
-           ? 18 - (token0Decimals - token1Decimals)
+           : 18 + (token0Decimals - token1Decimals);
    }
```

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/20_
