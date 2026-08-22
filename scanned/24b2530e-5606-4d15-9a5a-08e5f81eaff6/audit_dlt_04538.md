# [H] Curve Metapool does not support rebasing token

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-sentiment
Published: 2022-12-02
Source: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/22
Type: sherlock-finding

## Details
w42d3n

high

# Curve Metapool does not support rebasing token

## Summary

Curve Metapool does not support rebasing token which 

## Vulnerability Detail

The function getPrice() calls the Curve pool as oracle price feed.
However this function will fell with rebasing tokens according to Curve official doc (link below).

https://curve.readthedocs.io/factory-deployer.html#factory-deployer-limitations

_Token balances must not change without a transfer. Rebasing tokens are not supported!_


## Impact

Without digging into Curve's math, including a rebasing token into a Curve metapool will allow attacker siphon value from the pool by backrunning oracle update.


## Code Snippet

https://github.com/sentimentxyz/oracle/blob/ff82367f48a0524f7438f10ec60ad024b3e04bae/src/convex/ConvexRewardPoolOracle.sol#L44-L48

    function getPrice(address token) external view returns (uint) {
        return oracleFacade.getPrice(
            IGauge(IRewardPool(token).curveGauge()
        ).lp_token());
    }


## Tool used


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/22_
