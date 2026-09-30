# [M] 5.1 Incorrect Liquidity Decrease

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 2 Risk Accepted

PoolCollection._calcTargetTradingLiquidity decreases the BNT trading liquidity if the
current funding of a certain pool is greater than its funding limit. This is done in a way that could possibly
reset the pool:

```
uint256 excessFunding = currentFunding - fundingLimit;
targetBNTTradingLiquidity = MathEx.subMax0(liquidity.bntTradingLiquidity, excessFunding);
```
Consider the following example:

- The funding limit is 40,000 BNT.
- The current funding of the pool is 40,000 BNT.
- bntTradingLiquidity is 20,000 BNT (for example after the value of BNT to the corresponding
    token has quadrupled).
- The funding limit is now lowered to 20,000 BNT by governance.
- bntTradingLiquidity is now set to 0 and the pool is reset on the next deposit.


Risk accepted

Bancor plans to fix this issue in a future version and accepts the risk for now.
