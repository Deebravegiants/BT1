# [C] Oracle price manipulation attack can be executed on ChainlinkLPOracleGMU

## Summary
Severity: Critical
Contest weight: 0.0442
Dataset id: 10115
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The formula that ChainlinkLPOracleGMU uses in fetchPrice goes through the _fetchPrice, tokenAGMUInLP and tokenBGMUInLP methods, where they have calls to lp.totalSupply and lp.getReserves. The problem is that the result of those functions is easily manipulatable by taking a flash loan and providing liquidity or buying/selling either of the pair's tokens. This means that any malicious user can easily manipulate the fetchPrice answer, which can have devastating consequences for the protocols that use the oracle.

## Recommendation
Pricing LP tokens is a tough problem to solve, here is a solution: link
