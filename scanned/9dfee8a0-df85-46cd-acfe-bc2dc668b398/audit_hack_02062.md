# [M] 6.3 Problematic Revocation of a Collateral

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Partially Corrected

StableMaster allows for revokeCollateral() to be called by the governance. That transfers all the
funds of the pool manager to a settlement contract. Afterwards users can make claims for withdrawing
from the settlement contract. However, some user may lose.

This issue attempts to highlight two key points:

(I).

While this function is part of the emergency shutdown process of a stablecoin, this function can also be
called on a single collateral only. In both situation following scenario (simplified that no HAs exist) which
is mentioned in the documentation may occur:

```
1.revokeCollateral() gets called on a pool with 1000 WETH. 1 WETH is worth 1000 USD. 100
WETH-SanTokens are minted and have value of 200 WETH. The pool manager transfers his
balance to the settlement contract.
2.CollateralSettler.triggerSettlement() is executed. The amount to redistribute is the
balance of the settlement contract. All the rates are frozen.
3.SLPs claim their collateral. totalLpClaims increases.
```
```
4.A day before the claiming period ends, the price of WETH doubles. 1 WETH is worth 2000 USD now
in the current markets.
5.Many users see the bargain and start claiming WETH for their AgUSD.
```

```
6.The claiming period ends. The claim of stable holders is 1000 WETH. The claim by SLPs is 200
WETH.
7.The WETH will be distributed only to stable holders. SLPs do not receive anything.
```
The documentation specifies this behaviour. However, it highly concerning for SLPs and HAs. Anybody
with enough capital could take their investments into the protocol.

(II).

Furthermore, SLPs and HAs could lose funds if an attacker decides to frontrun the
revokeCollateral() call. The pools balance could be moved to another pool using a flashloan and
an external exchange. Then, the revokeCollateral() call will be executed but close to nothing would
be transferred to the settlement contract and SLPs and HAs will not be able to receive their funds.

Code partially corrected:

Different changes have been made:

- As stocksUser now tracks the amount of created stable coins it can also be used to limit the
    claims.
- The oracle value is queried at the end of the claim period to reduce issues due to price fluctuation.

Lastly, the front-running issue will be partially mitigated through pausing, but as in comparable systems
cannot be entirely avoided.
