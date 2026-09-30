# [M] M-04 | Avoid Using _strictStableIds

## Summary
Severity: Medium
Contest weight: 0.1232
Dataset id: 2128
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PricingManager’s pricing logic for stable assets includes a mechanism to use a hardcoded reference value of 1 USD unless there is a major depeg. While intended to maintain stability, this approach causes the protocol to rely on an artificially normalized value rather than accurate market data. This can cause positions backed by these stable assets to appear safer or riskier than they actually are, leading to incorrect margin calculations, mispriced positions, unexpected liquidations or unearned profits. Essentially, traders and LPs might face unfair conditions due to the system forcibly ignoring genuine price signals and relying instead on an arbitrary stable reference price.

## Recommendation
Rather than forcing a stable asset’s price to a hardcoded value, consider a dynamic safeguard that triggers protocol-level responses during actual depeg events. For instance, if the asset’s price deviates too far from its peg, the protocol could pause certain trading operations, tighten collateral requirements, or invoke other protective measures until accurate prices are restored.
