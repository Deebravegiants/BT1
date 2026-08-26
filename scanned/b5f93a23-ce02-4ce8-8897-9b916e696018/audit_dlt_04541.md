# [H] [WP-H4] `ConvexRewardPoolOracle.getPrice()` implies the assumptions of underlying tokens' decimals

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-sentiment
Published: 2022-12-02
Source: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/18
Type: sherlock-finding

## Details
WATCHPUG

high

# [WP-H4] `ConvexRewardPoolOracle.getPrice()` implies the assumptions of underlying tokens' decimals

## Summary

`ConvexRewardPoolOracle.getPrice()` will return a wrong result when `token.decimals() != curveLpToken.decimals()`.

## Vulnerability Detail

The correctness of `ConvexRewardPoolOracle.sol#getPrice()` relies on:

One whole Convex RewardPool token = $10^{token.decimals()}$ wei RewardPool token

= $10^{token.decimals()}$ wei Curve lp_token

= $\frac{10^{token.decimals()}}{10^{curveLpToken.decimals()}}$ curve lp token

So that:

One whole Convex RewardPool token's value in ETH is `getPrice(token)`.

The expected implementation is:

$$
\frac{10^{token.decimals()}}{10^{curveLpToken.decimals()}} \times oracleFacade.getPrice(curveLpToken)
$$

If and only if `token.decimals() == curveLpToken.decimals()`, the current implementation works as expected.

Otherwise, the current implementation will be way off.

Actually, some Curve lp_token (eg, [crvRenWBTC on mainnet](https://etherscan.io/token/0x49849c98ae39fff122806c06791fa73784fb3675#code))'s contract implementation allows the deployer to specify the decimals in the constructor. So that we believe there is a chance that a future Curve lp_token may have a different decimals than `18`.


## Impact

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/18_
