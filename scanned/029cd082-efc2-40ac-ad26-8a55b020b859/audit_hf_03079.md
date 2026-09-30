# [M] Product owner can collude to force liquidations.

## Summary
Severity: Medium
Contest weight: 0.1437
Dataset id: 17391
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious/compromised product owner can collude with liquidators to force liquidations by suddenly increasing maintenance. Product owners are semi-trusted in the protocol (per protocol design) because they can provide custom code and arbitrarily change their product parameters. While this is recognized in the protocol to implement safeguards against fee ranges of funding, maker and taker, the maintenance and maker limits are not protected against malicious/compromised owners of products whose providers allow modifications of product parameters. A malicious/compromised product owner can collude with liquidators to force liquidations by suddenly increasing maintenance requirements for their product. Given that this change can be effected immediately without any time-delay, users may not have the time to react to increase their collateral deposits and prevent liquidations of their positions.

## Recommendation
Consider a design choice where product maintenance can only be increased in certain predefined amounts if it does not lead to immediate liquidations. Add a timelock to this function so users have enough time to react if they are susceptible to liquidations because of this change.
