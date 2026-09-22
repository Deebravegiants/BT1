# [M] 6.2 BNT Burned Twice

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

Withdrawals from PoolCollection can result in the burning of double the amount of BNT than
intended. This happens any time a withdrawal occurs that results in the protocol removing BNT from the
protocol equity. In this case, both amounts.bntProtocolHoldingsDelta.value and
amounts.bntTradingLiquidityDelta.value are set to the same value greater than 0, resulting in
a call to BNTPool.renounceFunding which burns the amount of BNT and a call to
BNTPool.burnFromVault which burns the same amount of BNT again.

Code corrected:


If both amounts.bntTradingLiquidityDelta.value and
amounts.bntTradingLiquidityDelta.value are greater than 0, only the former value triggers
token burning (via BNTPool.renounceFunding).
