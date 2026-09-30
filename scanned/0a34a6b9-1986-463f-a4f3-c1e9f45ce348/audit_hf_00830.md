# [M] M-01 | reportedDebt Could Report Stale Debt

## Summary
Severity: Medium
Contest weight: 0.0904
Dataset id: 2566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reportedDebt function obtains V2X system debt through debtBalanceOf which does not return the boolean for stale oracle rates. If the rates are stale (e.g. if oracle was frozen), then an inaccurate debt value will be reported to the V3 system which V3 stakers could take advantage of. For example, if the bulk of synths are in ETH, and the price of ETH doubles while the rate is stale, V3 stakers could undelegate in anticipation of a large debt increase to avoid socialization of debt among them.

## Recommendation
Async delegation should address any risk of arbitrage with outdated pricing. Be aware of this risk and closely monitor any oracle outages to take necessary precautions to limit arbitrageable value as a result of stale prices.
