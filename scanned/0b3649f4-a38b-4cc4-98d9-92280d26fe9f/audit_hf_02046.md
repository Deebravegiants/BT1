# [M] Non ERC20-Compliance Of AToken

## Summary
Severity: Medium
Contest weight: 0.1307
Dataset id: 11661
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each asset supported by the Atlantis protocol is integrated through a so-called AToken contract, which is an ERC20 compliant representation of balances supplied to the protocol. By minting ATokens, users can earn interest through the AToken's exchange rate, which increases in value relative to the underlying asset, and further gain the ability to use ATokens as collateral. There are currently two types of ATokens: ABep20 and ABNB. In the following, we examine the ERC20 compliance of these ATokens.

The ERC20 specification defines a list of API functions (and relevant events) that each token contract is expected to implement (and emit). The failure to meet these requirements means the token contract cannot be considered to be ERC20-compliant. Naturally, as part of our audit, we examine the list of API functions defined by the ERC20 specification and validate whether there

## Recommendation
Revise the AToken implementation to ensure its ERC20-compliance.
